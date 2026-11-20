"""Check an STL: closed mesh, single body, real size in mm. Usage: python -m studio.check file.stl [...]"""
import sys
import numpy as np
import trimesh


def report(path):
    m = trimesh.load(path)
    ok = bool(m.is_watertight and m.is_winding_consistent and m.volume > 0)
    bodies = len(m.split(only_watertight=False))
    print(path)
    print("  closed mesh:", m.is_watertight, "| consistent:", m.is_winding_consistent, "| bodies:", bodies)
    print("  size mm (X wide, Y deep, Z tall):", np.round(m.extents, 2), "| base at Z:", round(float(m.bounds[0][2]), 3))
    print("  volume cm3:", round(float(m.volume) / 1000, 2), "| triangles:", len(m.faces))
    return ok and bodies == 1


if __name__ == "__main__":
    sys.exit(0 if all([report(p) for p in sys.argv[1:]]) else 1)
