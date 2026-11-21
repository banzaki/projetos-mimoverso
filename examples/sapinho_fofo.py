SIZE_MM = 60  # total height in mm. Bigger/smaller = change this number (or use --size).

"""Kawaii frog with two small horns. Original design: big head, tiny body, small low-set
eyes, blush cheeks. Every proportion below is a number you can edit."""
import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from studio.clay import Clay

HEAD = (25, 21, 19)      # head radii (wide, deep, tall)
EYE_BUMP = 7.5           # radius of the two bumps on top of the head
EYE_GAP = 13             # half distance between the eyes
HORN_LEN = 9             # horn length
HORN_LEAN = 3            # how much the horns open outward
CHEEK = 1.0              # 0 = no cheeks
SMILE = 3.0              # mouth curve (negative = grumpy)


def build(size_mm=SIZE_MM, step=0.3, no_supports=True):
    c = Clay((-34, -28, -1), (34, 26, 66), step)
    hx, hy, hz = HEAD
    head_z = 33
    c.blob((0, 0, 11), (17, 14, 13), blend=1)                      # body
    c.blob((0, -1, head_z), HEAD, blend=4)                         # head
    for s in (-1, 1):
        c.blob((s * EYE_GAP, -3, head_z + hz - 3), (EYE_BUMP,) * 3, blend=5)          # eye bumps
        c.horn((s * 5, 1, head_z + hz - 2), (s * (5 + HORN_LEAN), 1, head_z + hz - 2 + HORN_LEN + 2), 3.9, 1.8, blend=2.5)
        c.blob((s * 15, -8, 13), (5, 5, 6.5), blend=3)             # arms
        c.blob((s * 11, -12, 3), (7, 8.5, 4.5), blend=3)           # feet
        if CHEEK:
            c.blob((s * 16.5, -12.6, head_z - 5), (4.6 * CHEEK, 3.0, 3.6 * CHEEK), blend=3)
        # engraved oval eyes on the front of each bump
        c.dent((s * EYE_GAP, -3 - EYE_BUMP - 0.6, head_z + hz - 2.5), (2.4, 2.0, 3.3), soft=0.8)

    def front_y(x, z):
        return -1 - hy * max(0.0, 1 - (x / hx) ** 2 - ((z - head_z) / hz) ** 2) ** 0.5

    pts = []
    for i in range(25):
        t = i / 12 - 1
        x, z = t * 6.5, head_z - 6 + SMILE * t * t
        pts.append((x, front_y(x, z) - 0.2, z))
    c.groove(pts, 1.0, soft=0.8)
    if no_supports:
        c.self_support(40)
    return c.to_mesh(size_mm)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=float, default=SIZE_MM)
    ap.add_argument("--raw", action="store_true", help="keep overhangs (needs supports)")
    a = ap.parse_args()
    out = Path("out"); out.mkdir(exist_ok=True)
    name = out / f"sapinho-fofo-{a.size:g}mm{'-raw' if a.raw else ''}.stl"
    m = build(a.size, no_supports=not a.raw)
    m.export(name)
    print("wrote", name, len(m.faces), "triangles")
