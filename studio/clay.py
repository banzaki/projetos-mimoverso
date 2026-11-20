"""Sculpt creatures as one smooth "clay" volume (signed distance field), then mesh it.
Units are millimetres. Front faces -Y, Z is up, base rests on Z = 0."""
import numpy as np
import trimesh
from skimage import measure


class Clay:
    def __init__(self, bounds_min, bounds_max, step=0.3):
        self.step = step
        self.origin = np.array(bounds_min, np.float32)
        axes = [np.arange(lo, hi + step, step, dtype=np.float32) for lo, hi in zip(bounds_min, bounds_max)]
        self.X, self.Y, self.Z = np.meshgrid(*axes, indexing="ij")
        self.D = np.full(self.X.shape, 1e3, np.float32)

    # --- distance functions -------------------------------------------------
    def _ellipsoid(self, c, r):
        r = np.array(r, np.float32)
        q = np.sqrt(((self.X - c[0]) / r[0]) ** 2 + ((self.Y - c[1]) / r[1]) ** 2 + ((self.Z - c[2]) / r[2]) ** 2)
        return (q - 1.0) * r.min()

    def _taper(self, a, b, ra, rb):
        """Rounded cone from point a (radius ra) to point b (radius rb)."""
        a, b = np.array(a, np.float32), np.array(b, np.float32)
        ab = b - a
        t = ((self.X - a[0]) * ab[0] + (self.Y - a[1]) * ab[1] + (self.Z - a[2]) * ab[2]) / (ab @ ab)
        t = np.clip(t, 0, 1)
        d = np.sqrt((self.X - a[0] - t * ab[0]) ** 2 + (self.Y - a[1] - t * ab[1]) ** 2 + (self.Z - a[2] - t * ab[2]) ** 2)
        return d - (ra + t * (rb - ra))

    @staticmethod
    def _smin(a, b, k):
        h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
        return b + (a - b) * h - k * h * (1 - h)

    # --- sculpting ----------------------------------------------------------
    def add(self, d, blend=3.0):
        self.D = self._smin(self.D, d, blend)

    def carve(self, d, soft=1.0):
        self.D = -self._smin(-self.D, d, soft)

    def blob(self, center, radii, blend=3.0):
        self.add(self._ellipsoid(center, radii), blend)

    def horn(self, base, tip, r_base, r_tip, blend=2.0):
        self.add(self._taper(base, tip, r_base, r_tip), blend)

    def dent(self, center, radii, soft=1.0):
        self.carve(self._ellipsoid(center, radii), soft)

    def groove(self, points, radius, soft=0.8):
        d = np.full(self.X.shape, 1e3, np.float32)
        for a, b in zip(points[:-1], points[1:]):
            d = np.minimum(d, self._taper(a, b, radius, radius))
        self.carve(d, soft)

    # --- output -------------------------------------------------------------
    def to_mesh(self, height_mm, smooth_iters=10):
        D = np.maximum(self.D, -self.Z)                  # flat base at Z = 0
        D = np.pad(D, 1, constant_values=1e3)            # close the mesh at the grid border
        v, f, _, _ = measure.marching_cubes(D, level=0.0, spacing=(self.step,) * 3)
        m = trimesh.Trimesh(v + self.origin - self.step, f, process=False)
        m.merge_vertices()
        parts = m.split(only_watertight=False)
        m = max(parts, key=lambda p: len(p.faces))       # drop stray crumbs
        trimesh.smoothing.filter_taubin(m, iterations=smooth_iters)
        b = m.bounds
        m.apply_translation((-(b[0][0] + b[1][0]) / 2, -(b[0][1] + b[1][1]) / 2, -b[0][2]))
        m.apply_scale(height_mm / m.extents[2])
        self.crumbs = len(parts) - 1
        return m
