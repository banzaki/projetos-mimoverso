"""Printability report for an STL (FDM). Usage: python -m studio.printability file.stl [...]
Estimates only: the slicer has the final word. Every number comes from printer_profile.json."""
import json
import sys
from pathlib import Path
import numpy as np
import trimesh

PROFILE = json.loads((Path(__file__).parent / "printer_profile.json").read_text(encoding="utf-8"))


def report(path, profile=PROFILE):
    m = trimesh.load(path)
    n, a = m.face_normals, m.area_faces
    zc = m.triangles_center[:, 2]
    base = (zc < 0.05) & (n[:, 2] < -0.99)
    max_deg = profile["max_overhang_deg"]
    over = (n[:, 2] < -np.sin(np.radians(max_deg))) & ~base   # faces tilting below horizontal more than allowed
    steep = (n[:, 2] < -np.sin(np.radians(60))) & ~base
    wall = profile["walls"] * profile["nozzle_mm"]
    shell = min(m.area * wall, m.volume)
    grams = (shell + profile["infill"] * (m.volume - shell)) / 1000 * profile["filament_density_g_cm3"]
    cost = grams / 1000 * profile["filament_price_per_kg"]
    print(path, f"(profile: {profile['status']}, printer: {profile['printer']})")
    print(f"  height {m.extents[2]:.1f} mm | base contact {a[base].sum():.0f} mm2")
    print(f"  overhang beyond {max_deg:.0f} deg: {a[over].sum():.0f} mm2 ({100 * a[over].sum() / m.area:.1f} % of surface)"
          f" | beyond 60 deg: {a[steep].sum():.0f} mm2")
    print(f"  estimated weight: {grams:.1f} g ({profile['walls']} walls, {profile['infill'] * 100:.0f} % infill)"
          f" | filament cost about {cost:.2f} {profile['currency']} (no supports, no failures)")
    return grams


if __name__ == "__main__":
    for p in sys.argv[1:]:
        report(p)
