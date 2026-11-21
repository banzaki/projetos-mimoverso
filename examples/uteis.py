"""Useful creatures (sketches): two cable holders and a rest. Original designs.
Usage: python examples/uteis.py   (writes out/util-<n>-<name>.stl)"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from studio.clay import Clay
from studio.face import ellipsoid_front, eye, arc, cheek

CABLE = 4.2      # cable diameter the biters are made for (mm, at the sketch's own scale)
REST = 9.0       # diameter of what lies on the rest


def new():
    return Clay((-34, -34, -1), (34, 34, 48), 0.4)


def _biter(c, body):
    """Shared part of the cable biters: a channel across the mouth and a slot to press the cable in."""
    mz, my = 10.5, body[0][1] - body[1][1] + 6.5              # channel sits 6.5 mm behind the front
    c.carve(c._taper((-40, my, mz), (40, my, mz), CABLE / 2 + 0.3, CABLE / 2 + 0.3), soft=0.4)   # the channel
    c.carve(c._box((0, my - 12, mz), (40, 12, CABLE / 2 - 0.5), 0.6), soft=0.4)                  # the mouth slot
    for s in (-1, 1):                                          # two teeth narrow the entry: the cable clicks in
        c.blob((s * 4.5, my - 5.2, mz + CABLE / 2 + 0.6), (1.9, 1.6, 2.0), blend=0.5)


def sapo_morde_cabo():
    c = new()
    body = ((0, 0, 13), (18, 15, 14))
    c.blob(*body, blend=1)
    c.blob((0, 2, 5), (20, 16, 6), blend=4)                    # wide heavy bottom
    surf = ellipsoid_front(*body)
    for s in (-1, 1):
        c.blob((s * 9, -2, 26), (6.5, 6, 6.5), blend=3)        # eye bumps on top
        eye(c, ellipsoid_front((s * 9, -2, 26), (6.5, 6, 6.5)), s * 9, 27, r=3.6, pupil=0.55)
        cheek(c, surf, s * 12, 16.5)
        c.blob((s * 12, -11, 2.4), (5.5, 6, 3.2), blend=2)     # feet
    _biter(c, body)
    return c


def gato_morde_cabo():
    c = new()
    body = ((0, 0, 13.5), (17.5, 15, 14.5))
    c.blob(*body, blend=1)
    c.blob((0, 2, 5), (19.5, 16, 6), blend=4)
    surf = ellipsoid_front(*body)
    for s in (-1, 1):
        c.horn((s * 10, 1, 24), (s * 13, 1, 34), 5.5, 1.8, blend=2.5)   # ears
        eye(c, surf, s * 6.5, 19.5, r=3.6, lid=0.3, tilt=s * 0.25, pupil=0.6)   # focused, biting hard
        c.blob((s * 11.5, -11, 2.4), (5.2, 6, 3.2), blend=2)            # paws
        for dz in (-1.2, 1.2):                                          # whiskers
            x0 = s * 10.5
            c.groove([(x0, surf(x0, 15 + dz) - 0.1, 15 + dz), (x0 + s * 5, surf(x0 + s * 5, 15.3 + dz * 1.6) - 0.1, 15.3 + dz * 1.6)],
                     0.5, soft=0.3)
    c.blob((0, surf(0, 15.8) + 0.5, 15.8), (1.8, 1.5, 1.3), blend=0.6)   # nose
    c.horn((12, 12, 5), (22, 15, 7), 3.0, 2.8, blend=2)                   # tail lying on the table
    c.blob((24, 14, 7), (3.2, 3.2, 3.2), blend=1.5)
    _biter(c, body)
    return c


def bichinho_descanso():
    """Creature lying on its back; its four paws make a cradle across the belly."""
    c = new()
    c.blob((0, 4, 8), (15, 20, 9.5), blend=1)                  # body lying down
    head = ((0, -17, 12), (12.5, 10.5, 11.5))
    c.blob(*head, blend=4)
    hs = ellipsoid_front(*head)
    for s in (-1, 1):
        c.blob((s * 8, -15, 23.5), (3.4, 3.0, 3.8), blend=2)   # ears
        eye(c, hs, s * 5, 14.5, r=3.4, lid=0.55, tilt=-s * 0.15)
        cheek(c, hs, s * 8.5, 9.5, 0.9)
        for y in (-2.5, 11.5):                                 # four paws up, holding the cradle
            c.horn((s * 10, y, 10), (s * 9.5, y, 21), 4.0, 3.2, blend=2)
    arc(c, hs, 0, 9, 3.2, 1.3, radius=0.8)
    c.carve(c._taper((-40, 4.5, 19.5), (40, 4.5, 19.5), REST / 2, REST / 2), soft=0.6)   # the cradle
    c.horn((0, 22, 6), (0, 30, 4), 3.6, 2.6, blend=3)          # tail
    return c


IDEAS = [("sapo-morde-cabo", sapo_morde_cabo), ("gato-morde-cabo", gato_morde_cabo), ("bichinho-descanso", bichinho_descanso)]

if __name__ == "__main__":
    out = Path("out"); out.mkdir(exist_ok=True)
    for i, (name, fn) in enumerate(IDEAS, 1):
        c = fn()
        m = c.to_mesh(None, smooth_iters=6)
        m.export(out / f"util-{i}-{name}.stl")
        print(name, "closed:", m.is_watertight, "crumbs:", c.crumbs, "size:", [round(float(v), 1) for v in m.extents])
