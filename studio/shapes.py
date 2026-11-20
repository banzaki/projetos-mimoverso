"""Small helpers to build printable creatures from rounded shapes. Units are millimetres.
Convention: the front of a creature faces -Y, Z is up, the base rests on Z = 0."""
import numpy as np
import trimesh

ENGINE = "manifold"


def ellipsoid(center, radii, subdiv=4):
    m = trimesh.creation.icosphere(subdivisions=subdiv)
    m.vertices = m.vertices * np.array(radii)
    m.apply_translation(center)
    return m


def cone(base_center, radius, height, lean_deg=0.0):
    """Cone pointing up; lean_deg tilts it sideways around the Y axis."""
    c = trimesh.creation.cone(radius=radius, height=height, sections=48)
    c.apply_transform(trimesh.transformations.rotation_matrix(np.radians(-lean_deg), [0, 1, 0]))
    c.apply_translation(base_center)
    return c


def union(parts):
    return trimesh.boolean.union(parts, engine=ENGINE)


def subtract(base, cutters):
    return trimesh.boolean.difference([base, union(cutters)], engine=ENGINE)


def finish(mesh, height_mm):
    """Cut below Z = 0, centre on X/Y, rest on the plate, scale to the requested height."""
    cutter = trimesh.creation.box(extents=(500, 500, 200))
    cutter.apply_translation((0, 0, -100))
    mesh = trimesh.boolean.difference([mesh, cutter], engine=ENGINE)
    b = mesh.bounds
    mesh.apply_translation((-(b[0][0] + b[1][0]) / 2, -(b[0][1] + b[1][1]) / 2, -b[0][2]))
    mesh.apply_scale(height_mm / mesh.extents[2])
    return mesh
