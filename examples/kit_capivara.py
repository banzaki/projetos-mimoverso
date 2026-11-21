SIZE_MM = 45  # total height in mm. Bigger/smaller = change this number.

"""Zen capybara, assembled only from the parts kit (no new geometry). Original design.
Usage: python examples/kit_capivara.py   (writes out/kit-capivara.stl)"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from studio.clay import Clay
from studio.face import closed_eye, arc, cheek
from studio import parts

FRUIT = 5.0        # size of the fruit on the head (0 = none)
KEYRING = False    # True adds a loop on the back


def build(size_mm=SIZE_MM, step=0.4):
    c = Clay((-32, -34, -1), (32, 34, 56), step)
    parts.body(c, (0, 6, 13), (15, 19, 13))
    head = parts.body(c, (0, -13, 25), (12, 12.5, 11), blend=5)
    snout = parts.body(c, (0, -21.5, 22), (9.5, 8, 7.5), blend=4)
    parts.legs_four(c)
    parts.ears_round(c, 8.5, -8, 35.5, size=3.0)
    parts.tail(c, (0, 23, 12), (0, 27, 13), thick=3.0)
    for s in (-1, 1):
        closed_eye(c, head, s * 7.2, 28.5, half=2.8, bend=-1.2, radius=0.9)   # happy closed eyes
        cheek(c, head, s * 10, 23.5, 0.9)
    parts.nostrils(c, snout, 25.2)
    arc(c, snout, 0, 19.5, 3.4, 1.2, radius=0.8)                              # peaceful smile
    if FRUIT:
        parts.ball_on_top(c, (0, -12, 36 + FRUIT * 0.85), FRUIT)
    if KEYRING:
        parts.keyring(c, 8, 25.5)
    c.self_support(50)
    return c.to_mesh(size_mm, smooth_iters=6)


if __name__ == "__main__":
    out = Path("out"); out.mkdir(exist_ok=True)
    m = build()
    m.export(out / "kit-capivara.stl")
    print("wrote out/kit-capivara.stl closed:", m.is_watertight, "size:", [round(float(v), 1) for v in m.extents])
