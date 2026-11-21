"""Six quick idea sketches (rough, low resolution). Usage: python examples/ideias.py
Writes out/ideia-<n>-<name>.stl. These are sketches to choose from, not print-ready models."""
import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from studio.clay import Clay

STEP = 0.5


def new():
    return Clay((-38, -36, -1), (38, 36, 54), STEP)


def fy(c, r, x, z):
    """Y of the front surface of an ellipsoid (centre c, radii r) at (x, z)."""
    v = 1 - ((x - c[0]) / r[0]) ** 2 - ((z - c[2]) / r[2]) ** 2
    return c[1] - r[1] * math.sqrt(max(v, 0.0))


def eye(c, on, x, z, size=1.0):
    c.dent((x, fy(*on, x, z) - 0.2, z), (2.0 * size, 2.0, 2.7 * size), soft=0.6)


def arc(c, on, x0, z0, half, bend, radius=0.9, tilt=0.0):
    """Curved groove on a surface: bend > 0 smiles, bend < 0 frowns; tilt slants it."""
    pts = []
    for i in range(13):
        t = i / 6 - 1
        x, z = x0 + t * half, z0 + bend * (t * t - 1) + tilt * t
        pts.append((x, fy(*on, x, z) - 0.1, z))
    c.groove(pts, radius, soft=0.6)


def pao_bravo():
    c = new()
    body = ((0, 0, 15), (19, 14, 16))
    c.blob(*body, blend=1)
    c.blob((0, 0, 27), (22, 16, 9), blend=4)                       # loaf top
    face = ((0, 0, 17), (20, 15, 17))
    for s in (-1, 1):
        eye(c, face, s * 7, 21)
        arc(c, face, s * 7.5, 26.5, 4, 0, radius=1.0, tilt=-s * 2.2)   # angry brows
        c.blob((s * 9, -6, 2.5), (5.5, 7, 3.5), blend=2)               # feet
    arc(c, face, 0, 16.5, 4, -1.6)                                     # frown
    c.horn((-17, -6, 11), (5, -15.5, 11.5), 3.2, 2.8, blend=2)         # crossed arms
    c.horn((17, -6, 9), (-5, -16, 8.5), 3.2, 2.8, blend=2)
    return c


def fantasma_preguicoso():
    c = new()
    c.blob((0, 6, 7), (20, 20, 9), blend=1)                        # melted body
    head = ((0, -12, 12), (15, 13, 13))
    c.blob(*head, blend=6)
    c.horn((4, 20, 5), (16, 30, 3), 7, 2.5, blend=5)               # tail
    for a in range(0, 360, 45):                                    # wavy hem
        c.blob((22 * math.cos(math.radians(a)), 6 + 21 * math.sin(math.radians(a)), 2), (5, 5, 3), blend=3)
    for s in (-1, 1):
        c.blob((s * 16, -14, 3), (5, 7, 3.5), blend=3)             # arms flopped forward
    eye(c, head, -6, 15)
    arc(c, head, 6, 15, 2.6, 1.2)                                  # half-closed eye
    c.dent((0, fy(*head, 0, 9) - 0.2, 9), (2.2, 2, 1.6), soft=0.6)  # tiny yawn
    return c


def capivara_zen():
    c = new()
    c.blob((0, 6, 13), (15, 19, 13), blend=1)                      # body
    head = ((0, -13, 25), (11.5, 12, 10.5))
    c.blob(*head, blend=5)
    snout = ((0, -21, 22.5), (9, 8, 7.5))
    c.blob(*snout, blend=4)
    for s in (-1, 1):
        c.blob((s * 8, -8, 35), (2.8, 2.2, 3), blend=1.5)          # ears
        c.blob((s * 9, -8, 3), (5, 6, 4), blend=2)                 # front legs
        c.blob((s * 11, 16, 3), (5.5, 7, 4), blend=2)              # back legs
        arc(c, head, s * 7, 28, 2.4, -1.0, radius=0.8)             # closed happy eyes
        c.dent((s * 2.2, fy(*snout, s * 2.2, 25) - 0.2, 25), (1.0, 1.2, 1.0), soft=0.4)  # nostrils
    c.blob((0, -12, 40), (6.5, 6.5, 6), blend=0.6)                 # the orange
    c.blob((1.5, -12, 46.5), (1.6, 1.6, 1.6), blend=0.6)           # stem
    return c


def ovo_frito():
    c = new()
    for x, y, rx, ry in [(0, 0, 24, 20), (16, 11, 13, 11), (-15, -9, 13, 12), (-8, 15, 11, 10), (14, -13, 11, 9)]:
        c.blob((x, y, 2.5), (rx, ry, 3.6), blend=3)                # the white
    yolk = ((-2, -1, 8), (12, 12, 9.5))
    c.blob(*yolk, blend=2.5)
    c.blob((9, 4, 7), (13, 10, 5.5), blend=3)                      # blanket fold over the yolk
    for s in (-1, 1):
        arc(c, yolk, -2 + s * 4.5, 10.5, 2.2, 1.0, radius=0.8)     # sleeping eyes
    c.dent((-2, fy(*yolk, -2, 6.5) - 0.2, 6.5), (1.4, 1.5, 1.0), soft=0.4)
    return c


def diabinho():
    c = new()
    body = ((0, 0, 17), (18, 17, 17))
    c.blob(*body, blend=1)
    for s in (-1, 1):
        c.horn((s * 8, 0, 31), (s * 13, 0, 42), 4.2, 1.6, blend=2.5)   # horns
        eye(c, body, s * 7, 21, 1.1)
        arc(c, body, s * 7.5, 27, 4, 0, radius=1.0, tilt=-s * 2.0)     # "evil" brows
        c.blob((s * 9, -8, 2.5), (5.5, 7, 3.5), blend=2)               # feet
        c.blob((s * 17, -6, 13), (4, 4.5, 5.5), blend=2.5)             # tiny arms
    c.blob((0, fy(*body, 0, 13.5) + 0.5, 13.5), (3.0, 2.4, 2.2), blend=1.2)   # pout
    c.horn((10, 14, 6), (24, 20, 8), 2.6, 2.4, blend=2)                # tail
    c.horn((24, 20, 8), (27, 16, 20), 2.4, 2.2, blend=1.5)
    c.blob((27.5, 15.5, 23), (4.2, 3.2, 4.2), blend=1)                 # tail tip
    return c


def gatinho_capsula():
    c = new()
    body = ((0, 0, 18), (18.5, 18.5, 18.5))
    c.blob(*body, blend=1)
    for s in (-1, 1):
        c.horn((s * 10, 0, 31), (s * 13.5, 0, 42), 6.0, 1.8, blend=2.5)   # ears
        eye(c, body, s * 6.5, 25, 1.1)
        c.blob((s * 6, -15, 2.5), (5, 5.5, 3.5), blend=2)                  # paws
        arc(c, body, s * 2.2, 19.5, 2.2, 1.0, radius=0.7)                  # cat mouth
    c.blob((0, fy(*body, 0, 21.5) + 0.6, 21.5), (1.7, 1.5, 1.2), blend=0.6)    # nose
    ring = [(18.9 * math.cos(math.radians(a)), 18.9 * math.sin(math.radians(a)), 15) for a in range(0, 361, 10)]
    c.groove(ring, 0.9, soft=0.6)                                          # capsule seam
    c.horn((12, 12, 6), (23, 16, 9), 3.0, 2.8, blend=2)                    # tail
    c.horn((23, 16, 9), (24, 12, 20), 2.8, 2.4, blend=1.5)
    return c


IDEAS = [("pao-bravo", pao_bravo), ("fantasma-preguicoso", fantasma_preguicoso), ("capivara-zen", capivara_zen),
         ("ovo-frito", ovo_frito), ("diabinho", diabinho), ("gatinho-capsula", gatinho_capsula)]

if __name__ == "__main__":
    out = Path("out"); out.mkdir(exist_ok=True)
    for i, (name, fn) in enumerate(IDEAS, 1):
        m = fn().to_mesh(None, smooth_iters=6)
        path = out / f"ideia-{i}-{name}.stl"
        m.export(path)
        print(path, len(m.faces), "triangles, closed:", m.is_watertight, "size:", [round(float(v), 1) for v in m.extents])
