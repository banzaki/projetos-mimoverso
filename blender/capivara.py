"""Capybara with an orange on its head, modelled in Blender by script. Original design.
Run:  blender -b -P blender/capivara.py -- out/capivara-b
Writes <prefix>.stl (one piece), <prefix>-<colour>.stl (one file per colour) and two renders.
Units: 1 Blender unit = 1 mm. Front faces -Y, Z is up, the base rests on Z = 0."""
import math
import sys
import bpy
import bmesh
from mathutils import Vector

SIZE_MM = 50          # total height. Bigger/smaller = change this number.
FRUIT = True          # the orange on the head

COLOURS = {
    "tan": (0.78, 0.63, 0.44, 1), "brown": (0.36, 0.23, 0.17, 1), "black": (0.015, 0.015, 0.02, 1),
    "orange": (0.95, 0.47, 0.08, 1), "green": (0.25, 0.55, 0.22, 1),
}
BACKGROUND = (0.60, 0.52, 0.78, 1)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def material(name):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = COLOURS[name]
        b.inputs["Roughness"].default_value = 0.25 if name == "black" else 0.55
    return m


def finish(obj, colour, rot=(0, 0, 0), loc=(0, 0, 0)):
    bpy.context.collection.objects.link(obj)
    obj.rotation_euler = [math.radians(a) for a in rot]
    obj.location = loc
    obj.data.materials.append(material(colour))
    obj["colour"] = colour
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def apply_modifier(obj, mod):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)


def rbox(name, size, loc, radius, colour, taper=(1.0, 1.0), rot=(0, 0, 0)):
    """Box with rounded edges. taper scales the top face in X and Y."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]; v.co.y *= size[1]; v.co.z *= size[2]
        if v.co.z > 0:
            v.co.x *= taper[0]; v.co.y *= taper[1]
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    obj = finish(bpy.data.objects.new(name, me), colour, rot, loc)
    mod = obj.modifiers.new("round", "BEVEL")
    mod.width = radius; mod.segments = 12; mod.limit_method = "NONE"
    apply_modifier(obj, mod)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def ball(name, radius, loc, colour, scale=(1, 1, 1)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=radius)
    for v in bm.verts:
        v.co.x *= scale[0]; v.co.y *= scale[1]; v.co.z *= scale[2]
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return finish(bpy.data.objects.new(name, me), colour, loc=loc)


def boolean(base, other, op, keep=False):
    mod = base.modifiers.new("b", "BOOLEAN")
    mod.operation = op; mod.solver = "EXACT"; mod.object = other
    apply_modifier(base, mod)
    if not keep:
        bpy.data.objects.remove(other, do_unlink=True)


def merge(objs):
    base = objs[0]
    for o in objs[1:]:
        boolean(base, o, "UNION")
    return base


def clone(obj):
    c = obj.copy(); c.data = obj.data.copy()
    bpy.context.collection.objects.link(c)
    return c


def build():
    tan = [rbox("body", (27, 40, 24), (0, 6, 19), 9.5, "tan", taper=(0.9, 0.94)),
           rbox("head", (28, 26, 24), (0, -18, 32), 9.5, "tan", taper=(0.86, 0.9), rot=(-4, 0, 0))]
    brown = [rbox("snout", (20.5, 7, 13.5), (0, -31.2, 28), 3.2, "brown", rot=(-4, 0, 0))]
    for s in (-1, 1):
        boolean(brown[0], ball("nostril", 1.35, (s * 3.6, -34.9, 30.5), "brown", scale=(1, 1, 1.4)), "DIFFERENCE")
        brown.append(rbox("ear", (6.5, 3.2, 7.5), (s * 9.8, -12.5, 45.2), 1.5, "brown", rot=(0, s * 18, 0)))
        for y in (-7, 19):
            tan.append(rbox("leg", (9.2, 9.2, 13), (s * 8, y, 6.5), 3.2, "tan"))
            brown.append(rbox("hoof", (9.9, 9.9, 3.6), (s * 8, y, 1.8), 1.6, "brown"))
    black = [ball("eye", 2.9, (s * 13.4, -24.5, 35.5), "black", scale=(0.55, 1, 1.05)) for s in (-1, 1)]
    parts = {"tan": merge(tan), "brown": merge(brown), "black": merge(black)}
    if FRUIT:
        parts["orange"] = ball("fruit", 6.6, (0, -17.5, 49.0), "orange", scale=(1, 1, 0.9))
        parts["green"] = merge([rbox("stem", (1.8, 1.8, 3), (0, -17.5, 55.3), 0.7, "green"),
                                rbox("leaf", (6.5, 3.4, 1.5), (3.2, -17.5, 55.6), 0.7, "green", rot=(0, -22, 0))])
    return parts


def fit_height(parts, height):
    bpy.context.view_layer.update()
    top = max((o.matrix_world @ Vector(c)).z for o in parts.values() for c in o.bound_box)
    k = height / top
    for o in parts.values():
        o.scale = (k, k, k); o.location = o.location * k
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


def export(objs, path):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True)


def export_all(parts, prefix):
    # one piece (single colour print)
    whole = merge([clone(o) for o in parts.values()])
    export([whole], prefix + ".stl")
    bpy.data.objects.remove(whole, do_unlink=True)
    # one file per colour, with no overlaps: each colour is cut out of the ones before it
    order = ["green", "orange", "black", "brown", "tan"]
    present = [c for c in order if c in parts]
    for i, colour in enumerate(present):
        piece = clone(parts[colour])
        for other in present[:i]:
            boolean(piece, parts[other], "DIFFERENCE", keep=True)
        export([piece], f"{prefix}-{colour}.stl")
        bpy.data.objects.remove(piece, do_unlink=True)


def render(prefix, height):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 96
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = 1000, 750
    scene.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("w"); scene.world = world; world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = BACKGROUND
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.9
    bpy.ops.mesh.primitive_plane_add(size=4000, location=(0, 0, 0))
    floor = bpy.context.object
    fm = bpy.data.materials.new("floor"); fm.use_nodes = True
    fm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = BACKGROUND
    fm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.9
    floor.data.materials.append(fm)
    sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 3.2; sun.angle = math.radians(25)
    so = bpy.data.objects.new("sun", sun); scene.collection.objects.link(so)
    so.rotation_euler = (math.radians(48), 0, math.radians(38))
    target = bpy.data.objects.new("target", None); scene.collection.objects.link(target)
    target.location = (0, 0, height * 0.46)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scene.collection.objects.link(cam)
    cam.data.lens = 75
    con = cam.constraints.new("TRACK_TO"); con.target = target
    con.track_axis = "TRACK_NEGATIVE_Z"; con.up_axis = "UP_Y"
    scene.camera = cam
    d = height * 3.6
    for name, pos in (("tres-quartos", (d * 0.62, -d * 0.72, d * 0.42)), ("frente", (0, -d, d * 0.22)),
                      ("lado", (d, -d * 0.05, d * 0.22))):
        cam.location = pos
        scene.render.filepath = f"{prefix}-{name}.png"
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    import os
    prefix = os.path.abspath(sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "out/capivara-b")
    reset()
    parts = build()
    fit_height(parts, SIZE_MM)
    export_all(parts, prefix)
    render(prefix, SIZE_MM)
    print("DONE", prefix)
