"""Printability report for an STL (FDM). Usage: python -m studio.printability file.stl [...]
Estimates only: the slicer has the final word."""
import sys
import numpy as np
import trimesh

PLA = 1.24          # g/cm3 (typical PLA density, assumption)
WALL = 0.8          # mm, 2 walls with a 0.4 mm nozzle (assumption)
INFILL = 0.15       # 15 % infill (assumption)


def report(path, max_deg=45.0):
    m = trimesh.load(path)
    n, a = m.face_normals, m.area_faces
    zc = m.triangles_center[:, 2]
    base = (zc < 0.05) & (n[:, 2] < -0.99)
    limit = -np.sin(np.radians(max_deg))            # face tilts below horizontal more than allowed
    over = (n[:, 2] < limit) & ~base
    steep = (n[:, 2] < -np.sin(np.radians(60))) & ~base
    shell = min(m.area * WALL, m.volume)
    grams = (shell + INFILL * (m.volume - shell)) / 1000 * PLA
    print(path)
    print(f"  height {m.extents[2]:.1f} mm | base contact {a[base].sum():.0f} mm2")
    print(f"  overhang beyond {max_deg:.0f} deg: {a[over].sum():.0f} mm2 ({100 * a[over].sum() / m.area:.1f} % of surface)"
          f" | beyond 60 deg: {a[steep].sum():.0f} mm2")
    print(f"  estimated weight: {grams:.1f} g (2 walls, 15 % infill, PLA; solid would be {m.volume / 1000 * PLA:.1f} g)")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        report(p)
