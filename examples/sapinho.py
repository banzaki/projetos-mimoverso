SIZE_MM = 60  # default total height in mm. Bigger/smaller = change this number (or use --size).

import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from studio.shapes import ellipsoid, cone, union, subtract, finish

# A "style" is just a set of numbers. Same creature, different audience.
STYLES = {
    "cute": dict(eye=7.0, pupil=1.0, horn_r=4.6, horn_h=15.0, horn_lean=16, head=(22, 18, 16), cheeks=True, smile=2.6),
    "edgy": dict(eye=5.2, pupil=0.8, horn_r=3.4, horn_h=24.0, horn_lean=28, head=(19, 15, 12), cheeks=False, smile=-1.2),
}


def build(style="cute", size_mm=None):
    s = STYLES[style]
    hx, hy, hz = s["head"]
    e = s["eye"]
    parts = [ellipsoid((0, 0, 14), (21, 18, 17)), ellipsoid((0, -2, 17 + hz), (hx, hy, hz))]
    top = 17 + 2 * hz  # top of the head
    for sx in (-1, 1):
        parts += [ellipsoid((sx * 0.62 * hx, -5, top - 3 + 0.3 * e), (e, e, e)),
                  ellipsoid((sx * 0.62 * hx, -5 - e * 0.8, top - 2.5 + 0.3 * e), (3.2 * s["pupil"], 2.6 * s["pupil"], 3.6 * s["pupil"])),
                  cone((sx * 7, -3, top - 4.5), s["horn_r"], s["horn_h"], -sx * s["horn_lean"]),
                  ellipsoid((sx * 14, -15, 4.5), (7, 8.5, 4.5)),
                  ellipsoid((sx * 20, 3, 10), (8, 10, 9))]
        if s["cheeks"]:
            parts.append(ellipsoid((sx * 15, -14.5, 30), (4.2, 2.2, 3.4)))
    frog = union(parts)
    mouth_z = 17 + hz - 5
    def front_y(x, z):  # y of the head surface at (x, z), so the groove follows the curve
        dz = z - (17 + hz)
        return -2 - hy * max(0.0, 1 - (x / hx) ** 2 - (dz / hz) ** 2) ** 0.5

    smile = []
    for t in [i / 40 - 1 for i in range(81)]:
        x, z = t * 8, mouth_z + s["smile"] * t * t
        smile.append(ellipsoid((x, front_y(x, z) - 0.1, z), (1.1, 1.6, 1.1), subdiv=2))
    frog = subtract(frog, smile)
    return finish(frog, size_mm or SIZE_MM)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--style", choices=STYLES, default="cute")
    ap.add_argument("--size", type=float, default=SIZE_MM, help="total height in mm")
    a = ap.parse_args()
    out = Path("out"); out.mkdir(exist_ok=True)
    name = out / f"sapinho-{a.style}-{a.size:g}mm.stl"
    build(a.style, a.size).export(name)
    print("wrote", name)
