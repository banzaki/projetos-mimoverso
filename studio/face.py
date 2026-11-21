"""Face and detail kit for clay creatures. `surf(x, z)` returns the Y of the front surface."""
import math
import numpy as np

SEVEN = [(0, 1.0), (32, 0.88), (-32, 0.88), (64, 0.66), (-64, 0.66), (98, 0.42), (-98, 0.42)]


def ellipsoid_front(center, radii):
    def surf(x, z):
        v = 1 - ((x - center[0]) / radii[0]) ** 2 - ((z - center[2]) / radii[2]) ** 2
        return center[1] - radii[1] * math.sqrt(max(v, 0.0))
    return surf


def eye(c, surf, x, z, r=4.0, lid=0.0, tilt=0.0, pupil=0.5, look=0.0):
    """Raised eyeball. lid 0..1 closes it from the top (part of the eye, not glued on);
    tilt slants the lid line."""
    y = surf(x, z)
    centre = (x, y + r * 0.35, z)
    c.blob(centre, (r, r * 0.8, r * 1.05), blend=0.8)
    pz = z
    if lid > 0:
        big = c._ellipsoid(centre, (r * 1.2, r * 0.98, r * 1.25))
        cut_z = z + r * 1.05 * (1 - 2 * lid)
        plane = (cut_z + tilt * (c.X - x)) - c.Z          # negative above the lid line
        c.add(np.maximum(big, plane), blend=0.4)
        pz = min(z, cut_z - pupil * r * 0.75)
    c.dent((x + look, y + r * 0.35 - r * 0.8 + 0.2, pz), (r * pupil * 0.8, 1.4, r * pupil), soft=0.4)


def arc(c, surf, x0, z0, half, bend, radius=1.0):
    """Groove on the surface. bend > 0 smiles, bend < 0 is a happy closed eye or a frown."""
    pts = []
    for i in range(17):
        t = i / 8 - 1
        x, z = x0 + t * half, z0 + bend * (t * t - 1)
        pts.append((x, surf(x, z) - 0.1, z))
    c.groove(pts, radius, soft=0.5)


def closed_eye(c, surf, x, z, half=2.4, bend=-1.0, radius=0.8):
    arc(c, surf, x, z, half, bend, radius)


def cheek(c, surf, x, z, size=1.0):
    c.blob((x, surf(x, z) + 1.0, z), (3.4 * size, 2.0, 2.4 * size), blend=1.5)


def leaf(c, base, length, thick, leaflets=SEVEN, blend=2.0, veins=True):
    """Flat fan leaf standing in the X-Z plane (facing front), made of pointed leaflets."""
    bx, by, bz = base
    d = np.full(c.X.shape, 1e3, np.float32)
    for ang, k in leaflets:
        a = math.radians(ang)
        L = length * k
        dx, dz = math.sin(a), math.cos(a)
        mid = (bx + dx * L * 0.45, by, bz + dz * L * 0.45)
        tip = (bx + dx * L, by, bz + dz * L)
        w = 0.15 * L + 0.6
        d = np.minimum(d, c._taper(base, mid, 0.08 * L + 0.8, w))
        d = np.minimum(d, c._taper(mid, tip, w, 0.5))
    d = np.maximum(d, np.abs(c.Y - by) - thick / 2)            # flatten into a slab
    c.add(d, blend)
    if veins:
        for ang, k in leaflets:
            a = math.radians(ang)
            L = length * k * 0.8
            y = by - thick / 2 - 0.1
            c.groove([(bx + math.sin(a) * L * 0.2, y, bz + math.cos(a) * L * 0.2),
                      (bx + math.sin(a) * L, y, bz + math.cos(a) * L)], 0.55, soft=0.3)
