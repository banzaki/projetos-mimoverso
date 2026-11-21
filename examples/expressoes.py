"""Expression sheet: the same little body with six different faces.
Shows that personality is a set of numbers. Usage: python examples/expressoes.py"""
import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from studio.clay import Clay

HEAD = ((0, 0, 20), (21, 19, 20))

#            eye size, lid (0 open..1 shut), lid tilt, brow tilt, brow height, mouth, head tilt
FACES = {
    "feliz":      dict(eye=1.0, lid=0.0, lid_tilt=0,  brow=0,   brow_h=0,  mouth="smile", lean=0),
    "bravo":      dict(eye=1.0, lid=0.35, lid_tilt=-1, brow=-1, brow_h=-2, mouth="frown", lean=0),
    "sono":       dict(eye=1.0, lid=0.75, lid_tilt=0.4, brow=0.5, brow_h=1, mouth="yawn",  lean=6),
    "susto":      dict(eye=1.3, lid=0.0, lid_tilt=0,  brow=0.3, brow_h=3,  mouth="o",     lean=-3),
    "convencido": dict(eye=1.0, lid=0.5, lid_tilt=0.6, brow=0.8, brow_h=1,  mouth="smirk", lean=4),
    "choro":      dict(eye=1.15, lid=0.2, lid_tilt=1, brow=1,   brow_h=1,  mouth="wobble", lean=0),
}


def fy(x, z):
    c, r = HEAD
    v = 1 - ((x - c[0]) / r[0]) ** 2 - ((z - c[2]) / r[2]) ** 2
    return c[1] - r[1] * math.sqrt(max(v, 0.0))


def build(face):
    f = FACES[face]
    c = Clay((-32, -30, -1), (32, 28, 52), 0.4)
    lean = f["lean"]
    c.blob((lean * 0.5, 0, 20), HEAD[1], blend=1)
    for s in (-1, 1):
        c.blob((s * 9, -9, 2.5), (6, 7.5, 3.5), blend=2.5)                  # feet
        c.blob((s * 20, -4, 12), (4, 4.5, 6), blend=3)                       # arms
        c.blob((s * 10, 2, 38), (5, 4, 5), blend=2.5)                        # little ears
        ex, ez, e = s * 8.5, 24, 5.2 * f["eye"]
        ey = fy(ex, ez)
        c.blob((ex, ey + 1.5, ez), (e, e * 0.8, e * 1.1), blend=1.0)         # raised eyeball
        c.dent((ex + s * -0.6, ey + 1.5 - e * 0.8, ez - 0.5), (e * 0.45, 1.6, e * 0.55), soft=0.5)  # pupil
        if f["lid"] > 0:                                                     # eyelid covers the top of the eye
            drop = e * 2.2 * f["lid"]
            tilt = f["lid_tilt"] * s * 2.0
            c.horn((ex - s * e * 1.1, ey + 0.6, ez + e * 1.25 - drop - tilt), (ex + s * e * 1.1, ey + 0.9, ez + e * 1.25 - drop + tilt),
                   e * 0.75, e * 0.75, blend=1.2)
        bz = ez + e * 1.1 + 3.5 + f["brow_h"]                                # raised eyebrow
        bt = f["brow"] * s * 2.2
        c.horn((ex - s * 4, fy(ex - s * 4, bz - bt) + 0.3, bz - bt), (ex + s * 4, fy(ex + s * 4, bz + bt) + 0.3, bz + bt), 1.5, 1.2, blend=0.8)
        if face in ("feliz", "choro", "convencido"):
            c.blob((s * 15, fy(s * 15, 15) + 1.2, 15), (3.6, 2.2, 2.6), blend=1.5)   # cheeks
        if face == "choro":
            c.blob((ex + s * 2, fy(ex + s * 2, 15) + 0.3, 15.5), (1.8, 1.6, 2.8), blend=0.8)  # tear

    def groove(pts, r=1.0):
        c.groove([(x, fy(x, z) - 0.1, z) for x, z in pts], r, soft=0.5)

    m, mz = f["mouth"], 12.5
    ts = [i / 8 - 1 for i in range(17)]
    if m == "smile":
        groove([(t * 6, mz + 3 * t * t) for t in ts], 1.2)
    elif m == "frown":
        groove([(t * 5.5, mz + 2 - 2.6 * t * t) for t in ts], 1.2)
    elif m == "smirk":
        groove([(t * 5 + 1.5, mz + 1 + 1.8 * max(t, 0) ** 2 * 1.6) for t in ts], 1.1)
    elif m == "wobble":
        groove([(t * 5.5, mz + 1.5 + 1.1 * math.sin(t * 6.3)) for t in ts], 1.0)
    elif m == "o":
        c.dent((0, fy(0, mz) - 0.3, mz), (3.0, 3.0, 3.8), soft=0.6)
    elif m == "yawn":
        c.dent((0, fy(0, mz) - 0.3, mz + 0.5), (4.2, 3.2, 3.2), soft=0.6)
    return c.to_mesh(None, smooth_iters=6)


if __name__ == "__main__":
    out = Path("out"); out.mkdir(exist_ok=True)
    for i, name in enumerate(FACES, 1):
        m = build(name)
        m.export(out / f"expressao-{i}-{name}.stl")
        print(name, "closed:", m.is_watertight)
