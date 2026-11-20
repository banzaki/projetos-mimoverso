SIZE_MM = 60  # total height in mm. Change only this number to make it bigger or smaller.

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from studio.shapes import ellipsoid, cone, union, subtract, finish


def build():
    parts = [ellipsoid((0, 0, 14), (21, 18, 17)), ellipsoid((0, -2, 33), (22, 18, 16))]
    for sx in (-1, 1):
        parts += [ellipsoid((sx * 13.5, -5, 46), (7, 7, 7)),
                  ellipsoid((sx * 13.5, -10.5, 46.5), (3.2, 2.6, 3.6)),
                  cone((sx * 7, -3, 44.5), 4.6, 15.0, -sx * 16),
                  ellipsoid((sx * 15, -14.5, 30), (4.2, 2.2, 3.4)),
                  ellipsoid((sx * 14, -15, 4.5), (7, 8.5, 4.5)),
                  ellipsoid((sx * 20, 3, 10), (8, 10, 9))]
    frog = union(parts)
    smile = [ellipsoid((t * 8, -19.2, 27.8 + 2.6 * t * t), (1.1, 1.6, 1.1), subdiv=2)
             for t in [i / 40 - 1 for i in range(81)]]
    return finish(subtract(frog, smile), SIZE_MM)


if __name__ == "__main__":
    out = Path("out"); out.mkdir(exist_ok=True)
    build().export(out / "sapinho.stl")
    print("wrote out/sapinho.stl")
