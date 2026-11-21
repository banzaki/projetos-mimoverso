"""Parts kit: named, reusable pieces for clay creatures. Units are millimetres.
Front faces -Y, Z is up, the base rests on Z = 0. Every part takes the Clay `c` first.
A new creature should be an assembly of these parts, not new geometry."""
import math
from .face import ellipsoid_front


# --- bodies ---------------------------------------------------------------
def body(c, center, radii, blend=1.0):
    """Main volume. Returns the front-surface function used to place a face on it."""
    c.blob(center, radii, blend=blend)
    return ellipsoid_front(center, radii)


def heavy_base(c, radii=(20, 16, 6), y=2.0, blend=4.0):
    """Wide low volume that keeps a piece stable on a table."""
    c.blob((0, y, radii[2] - 1), radii, blend=blend)


# --- limbs ----------------------------------------------------------------
def feet(c, x=7.0, y=-8.0, size=1.0):
    for s in (-1, 1):
        c.blob((s * x, y, 2.5 * size), (5 * size, 6.5 * size, 3.2 * size), blend=2)


def arms_on_belly(c, shoulder=(9, -3, 15), hand=(5.5, -9.5, 10), thick=2.9):
    for s in (-1, 1):
        c.horn((s * shoulder[0], shoulder[1], shoulder[2]), (s * hand[0], hand[1], hand[2]), thick, thick - 0.2, blend=1.8)
        c.blob((s * hand[0], hand[1] - 0.5, hand[2] - 0.4), (thick + 0.1, thick - 0.3, thick + 0.1), blend=1.2)


def arms_down(c, shoulder=(15.5, -3, 14), hand=(19.5, -7, 9.5), thick=2.9):
    for s in (-1, 1):
        c.horn((s * shoulder[0], shoulder[1], shoulder[2]), (s * hand[0], hand[1], hand[2]), thick, thick - 0.2, blend=2)
        c.blob((s * hand[0], hand[1] - 0.4, hand[2] - 0.5), (thick + 0.2,) * 3, blend=0.8)


def legs_four(c, front=(9, -8), back=(11, 16), size=1.0):
    """Short legs of a four-legged animal lying or standing low."""
    for s in (-1, 1):
        c.blob((s * front[0], front[1], 3 * size), (5 * size, 6 * size, 4 * size), blend=2)
        c.blob((s * back[0], back[1], 3 * size), (5.5 * size, 7 * size, 4 * size), blend=2)


def tail(c, start, end, thick=3.0, tip_ball=0.0):
    c.horn(start, end, thick, thick * 0.85, blend=2)
    if tip_ball:
        c.blob(end, (tip_ball,) * 3, blend=1.2)


# --- head tops ------------------------------------------------------------
def ears_round(c, x, y, z, size=3.0):
    for s in (-1, 1):
        c.blob((s * x, y, z), (size, size * 0.8, size * 1.1), blend=size * 0.6)


def ears_cat(c, x, y, z, height=10.0, width=5.5):
    for s in (-1, 1):
        c.horn((s * x, y, z), (s * (x + height * 0.3), y, z + height), width, 1.8, blend=2.5)


def horns(c, x, y, z, length=10.0, lean=3.0, thick=3.9):
    for s in (-1, 1):
        c.horn((s * x, y, z), (s * (x + lean), y, z + length), thick, thick * 0.45, blend=2.5)


def antennae_fan(c, y, z, fan=((0, 10), (34, 8), (-34, 8), (68, 6), (-68, 6)), thick=2.4, ball=2.7):
    """Antennae opened like a fan in the X-Z plane. `fan` is a list of (angle, length)."""
    for ang, length in fan:
        a = math.radians(ang)
        base = (math.sin(a) * 5.0, y, z - abs(math.sin(a)) * 2.5)
        tip = (base[0] + math.sin(a) * length, y, base[2] + math.cos(a) * length)
        c.horn(base, tip, thick, thick * 0.85, blend=1.2)
        b = ball * (1.15 if ang == 0 else 1.0)
        c.blob((tip[0] + math.sin(a) * 0.8, y, tip[2] + math.cos(a) * 0.8), (b, b, b), blend=0.6)


def beanie(c, center, radii, stripes=3, slouch=0.0):
    """Knitted hat sitting on a head: an ellipsoid with grooved stripes on the front half."""
    cx, cy, cz = center
    rx, ry, rz = radii
    c.blob(center, radii, blend=0.8)
    if slouch:
        c.blob((cx, cy + slouch, cz), (rx * 0.8, ry * 0.82, rz * 0.9), blend=3)
    for i in range(stripes):
        z = cz - rz * 0.27 + i * (rz * 0.36)
        rr = math.sqrt(max(1 - ((z - cz) / rz) ** 2, 0))
        ring = [(cx + (rx + 0.2) * rr * math.cos(math.radians(a)), cy + (ry + 0.2) * rr * math.sin(math.radians(a)), z)
                for a in range(170, 371, 10)]
        c.groove(ring, 0.7, soft=0.3)


def ball_on_top(c, center, radius, stem=True):
    """A round thing balanced on the head (fruit, pompom)."""
    c.blob(center, (radius, radius, radius * 0.93), blend=0.6)
    if stem:
        c.blob((center[0] + radius * 0.2, center[1], center[2] + radius * 0.98), (radius * 0.23,) * 3, blend=0.6)


# --- face extras ----------------------------------------------------------
def nose(c, surf, x, z, size=1.0):
    c.blob((x, surf(x, z) + 0.5, z), (1.8 * size, 1.5 * size, 1.3 * size), blend=0.6)


def nostrils(c, surf, z, gap=2.2):
    for s in (-1, 1):
        c.dent((s * gap, surf(s * gap, z) - 0.2, z), (1.0, 1.2, 1.0), soft=0.4)


def whiskers(c, surf, x, z, length=5.0):
    for s in (-1, 1):
        for dz in (-1.2, 1.2):
            x0, x1 = s * x, s * (x + length)
            c.groove([(x0, surf(x0, z + dz) - 0.1, z + dz), (x1, surf(x1, z + dz * 1.6) - 0.1, z + dz * 1.6)], 0.5, soft=0.3)


# --- functions (what makes a piece useful) -------------------------------
def keyring(c, y, z, hole=5.4, thick=2.3):
    """Standing loop for a key ring. `z` is where the loop meets the piece."""
    big_r = hole / 2 + thick
    cz = z + big_r - 2.0
    ring = ((((c.X ** 2 + (c.Z - cz) ** 2) ** 0.5 - big_r) ** 2 + (c.Y - y) ** 2) ** 0.5) - thick
    c.add(ring, blend=1.5)


def cable_channel(c, y, z, cable=4.2, teeth=True):
    """Channel across the piece (along X) with a slot from the front to press a cable in."""
    c.carve(c._taper((-60, y, z), (60, y, z), cable / 2 + 0.3, cable / 2 + 0.3), soft=0.4)
    c.carve(c._box((0, y - 12, z), (60, 12, cable / 2 - 0.5), 0.6), soft=0.4)
    if teeth:                                               # two teeth narrow the entry so the cable clicks in
        for s in (-1, 1):
            c.blob((s * 4.5, y - 5.2, z + cable / 2 + 0.6), (1.9, 1.6, 2.0), blend=0.5)


def cradle(c, y, z, diameter=9.0):
    """Round groove across the top (along X) where something long can rest."""
    c.carve(c._taper((-60, y, z), (60, y, z), diameter / 2, diameter / 2), soft=0.6)


def round_pocket(c, center, diameter, depth):
    """Vertical round hole from the top, for holding a cylinder (a lighter, a pen)."""
    x, y, top = center
    c.carve(c._taper((x, y, top - depth + diameter / 2), (x, y, top + 40), diameter / 2, diameter / 2), soft=0.5)
