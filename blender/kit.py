"""Blender modelling kit for the "brush" style: rounded boxes, balls, rods, rings, colour per part,
export (one piece and one file per colour) and a soft studio render.
Units: 1 Blender unit = 1 mm. Front faces -Y, Z is up, the base rests on Z = 0."""
import math
import bpy
import bmesh
from mathutils import Vector

COLOURS = {}


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def material(name):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = COLOURS.get(name, (0.8, 0.8, 0.8, 1))
        b.inputs["Roughness"].default_value = 0.2 if name in ("black", "white") else 0.55
    return m


def _finish(obj, colour, rot=(0, 0, 0), loc=(0, 0, 0)):
    bpy.context.collection.objects.link(obj)
    obj.rotation_euler = [math.radians(a) for a in rot]
    obj.location = loc
    obj.data.materials.append(material(colour))
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def _apply(obj, mod):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)


def _mesh(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return me


def rbox(name, size, loc, radius, colour, taper=(1.0, 1.0), rot=(0, 0, 0)):
    """Box with rounded edges; taper scales the top face in X and Y."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]; v.co.y *= size[1]; v.co.z *= size[2]
        if v.co.z > 0:
            v.co.x *= taper[0]; v.co.y *= taper[1]
    obj = _finish(bpy.data.objects.new(name, _mesh(name, bm)), colour, rot, loc)
    r = min(radius, min(size) / 2 - 0.05)
    mod = obj.modifiers.new("round", "BEVEL")
    mod.width = r; mod.segments = 10; mod.limit_method = "NONE"
    _apply(obj, mod)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def ball(name, radius, loc, colour, scale=(1, 1, 1)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=20, radius=radius)
    for v in bm.verts:
        v.co.x *= scale[0]; v.co.y *= scale[1]; v.co.z *= scale[2]
    return _finish(bpy.data.objects.new(name, _mesh(name, bm)), colour, loc=loc)


def rod(name, a, b, radius, colour):
    """Capsule from point a to point b."""
    a, b = Vector(a), Vector(b)
    d = b - a
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=radius, radius2=radius, depth=d.length)
    obj = _finish(bpy.data.objects.new(name, _mesh(name, bm)), colour, loc=(a + b) / 2)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    caps = [ball(name + "_cap", radius, a, colour), ball(name + "_cap", radius, b, colour)]
    return merge([obj] + caps)


def ring(name, center, hole_r, wire_r, colour):
    """Standing loop (in the X-Z plane) for a key ring."""
    bpy.ops.mesh.primitive_torus_add(major_radius=hole_r + wire_r, minor_radius=wire_r,
                                     major_segments=48, minor_segments=16, location=center,
                                     rotation=(math.radians(90), 0, 0))
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material(colour))
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def boolean(base, other, op, keep=False):
    mod = base.modifiers.new("b", "BOOLEAN")
    mod.operation = op; mod.solver = "EXACT"; mod.object = other
    _apply(base, mod)
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


def fit_height(parts, height):
    bpy.context.view_layer.update()
    corners = [(o.matrix_world @ Vector(c)) for o in parts.values() for c in o.bound_box]
    low, top = min(c.z for c in corners), max(c.z for c in corners)
    k = height / (top - low)
    for o in parts.values():
        o.location.z -= low
        o.location = o.location * k
        o.scale = (k, k, k)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


def export(objs, path):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True)


def export_all(parts, prefix, order):
    """One-piece STL plus one STL per colour; each colour is cut out of the ones listed before it."""
    whole = merge([clone(o) for o in parts.values()])
    mod = whole.modifiers.new("closed", "REMESH")      # voxel remesh: one closed shell for single-colour printing
    mod.mode = "VOXEL"; mod.voxel_size = 0.12; mod.use_smooth_shade = True
    _apply(whole, mod)
    dec = whole.modifiers.new("lighter", "DECIMATE")    # fewer triangles, same shape
    dec.ratio = 0.2
    _apply(whole, dec)
    export([whole], prefix + ".stl")
    bpy.data.objects.remove(whole, do_unlink=True)
    present = [c for c in order if c in parts]
    for i, colour in enumerate(present):
        piece = clone(parts[colour])
        for other in present[:i]:
            boolean(piece, parts[other], "DIFFERENCE", keep=True)
        export([piece], f"{prefix}-{colour}.stl")
        bpy.data.objects.remove(piece, do_unlink=True)


def render(prefix, height, background=(0.60, 0.52, 0.78, 1)):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 96
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = 1000, 750
    scene.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("w"); scene.world = world; world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = background
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.9
    bpy.ops.mesh.primitive_plane_add(size=4000, location=(0, 0, 0))
    fm = bpy.data.materials.new("floor"); fm.use_nodes = True
    fm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = background
    fm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.9
    bpy.context.object.data.materials.append(fm)
    sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 3.2; sun.angle = math.radians(25)
    so = bpy.data.objects.new("sun", sun); scene.collection.objects.link(so)
    so.rotation_euler = (math.radians(48), 0, math.radians(38))
    target = bpy.data.objects.new("target", None); scene.collection.objects.link(target)
    target.location = (0, 0, height * 0.48)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scene.collection.objects.link(cam)
    cam.data.lens = 75
    con = cam.constraints.new("TRACK_TO"); con.target = target
    con.track_axis = "TRACK_NEGATIVE_Z"; con.up_axis = "UP_Y"
    scene.camera = cam
    d = height * 3.8
    for name, pos in (("tres-quartos", (d * 0.62, -d * 0.72, d * 0.42)), ("frente", (0, -d, d * 0.22)),
                      ("costas", (-d * 0.5, d * 0.85, d * 0.35))):
        cam.location = pos
        scene.render.filepath = f"{prefix}-{name}.png"
        bpy.ops.render.render(write_still=True)
