"""Tiny z-buffer preview renderer (orthographic, flat shading). Usage: render_preview.py model.stl prefix"""
import sys
import numpy as np
import trimesh
from PIL import Image

W = H = 900
BASE = np.array([150, 205, 170], float)   # pastel green


def render(mesh, az_deg, el_deg, path):
    az, el = np.radians(az_deg), np.radians(el_deg)
    # camera direction (from object to camera); az=0 looks from -Y (front), 90 from +X (side)
    cam = np.array([np.sin(az) * np.cos(el), -np.cos(az) * np.cos(el), np.sin(el)])
    right = np.cross([0, 0, 1], cam); right /= np.linalg.norm(right)
    up = np.cross(cam, right)
    v = mesh.vertices - mesh.bounds.mean(axis=0)
    sx, sy, sz = v @ right, v @ up, v @ cam
    scale = 0.8 * W / max(np.ptp(sx), np.ptp(sy))
    px = sx * scale + W / 2
    py = H / 2 - sy * scale
    light = np.array([0.4, -0.6, 0.8]); light /= np.linalg.norm(light)
    img = np.full((H, W, 3), 245, np.uint8)
    zbuf = np.full((H, W), -1e9)
    for f, n in zip(mesh.faces, mesh.face_normals):
        if n @ cam <= 0:
            continue
        shade = 0.45 + 0.55 * max(0.0, n @ light)
        col = np.clip(BASE * shade + 20 * max(0, n @ cam) ** 8, 0, 255).astype(np.uint8)
        x = px[f]; y = py[f]; z = sz[f]
        x0, x1 = int(max(0, np.floor(x.min()))), int(min(W - 1, np.ceil(x.max())))
        y0, y1 = int(max(0, np.floor(y.min()))), int(min(H - 1, np.ceil(y.max())))
        if x1 < x0 or y1 < y0:
            continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        d = (y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2])
        if abs(d) < 1e-12:
            continue
        a = ((y[1] - y[2]) * (xs - x[2]) + (x[2] - x[1]) * (ys - y[2])) / d
        b = ((y[2] - y[0]) * (xs - x[2]) + (x[0] - x[2]) * (ys - y[2])) / d
        c = 1 - a - b
        inside = (a >= 0) & (b >= 0) & (c >= 0)
        zz = a * z[0] + b * z[1] + c * z[2]
        sub = zbuf[y0:y1 + 1, x0:x1 + 1]
        m = inside & (zz > sub)
        sub[m] = zz[m]
        img[y0:y1 + 1, x0:x1 + 1][m] = col
    Image.fromarray(img).save(path)


if __name__ == "__main__":
    mesh = trimesh.load(sys.argv[1])
    prefix = sys.argv[2]
    render(mesh, 0, 8, f"{prefix}-frente.png")
    render(mesh, 90, 8, f"{prefix}-lado.png")
    render(mesh, 35, 22, f"{prefix}-tres-quartos.png")
