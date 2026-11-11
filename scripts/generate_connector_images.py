#!/usr/bin/env python3
"""
Generate the connector drawings displayed for power port and power outlet types.

Each drawing depicts the mating face of a connector as a 64x64 SVG: the face is outlined and its contacts are
filled solid black, on a transparent background (the UI inverts the drawings in dark mode). Outlets are drawn as
seen from the front; ports (plugs and inlets) are drawn as the mirror image of the face they mate with. Geometry
is defined in millimetres (x right, y down, origin at the face's centre) and each face is scaled to fill the frame,
so relative physical size is not conveyed. Contacts too small to read at icon size may be exaggerated.

Usage: python scripts/generate_connector_images.py
"""
import math
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / 'netbox' / 'project-static' / 'img' / 'connectors'
SIZE = 64          # Frame size (px)
CONTENT = 56       # Size of the face's longest dimension within the frame
OUTLINE = 3        # Stroke width of face outlines
DETAIL = 2         # Stroke width of secondary lines


def fmt(n):
    """Format a number compactly and deterministically."""
    s = f'{n:.2f}'.rstrip('0').rstrip('.')
    return '0' if s == '-0' else s


def polar(cx, cy, radius, angle):
    """Return the point at the given radius and clock angle (degrees clockwise from 12 o'clock) about a centre."""
    rad = math.radians(angle)
    return cx + radius * math.sin(rad), cy - radius * math.cos(rad)


def rotate(point, angle, about=(0, 0)):
    """Rotate a point clockwise (on screen) by the given angle in degrees."""
    rad = math.radians(angle)
    x, y = point[0] - about[0], point[1] - about[1]
    return (
        about[0] + x * math.cos(rad) - y * math.sin(rad),
        about[1] + x * math.sin(rad) + y * math.cos(rad),
    )


#
# Shapes
#

class Path:
    """
    A path made of move (M), line (L), circular arc (A) and close (Z) segments. Arc segments are
    ('A', radius, large_arc, sweep, x, y).
    """
    def __init__(self, segments):
        self.segments = segments

    def svg(self, tx):
        out = []
        for seg in self.segments:
            if seg[0] in ('M', 'L'):
                x, y = tx.point(seg[1], seg[2])
                out.append(f'{seg[0]}{fmt(x)} {fmt(y)}')
            elif seg[0] == 'A':
                _, r, large, sweep, x, y = seg
                x, y = tx.point(x, y)
                sweep = 1 - sweep if tx.mirror else sweep
                out.append(f'A{fmt(r * tx.scale)} {fmt(r * tx.scale)} 0 {large} {sweep} {fmt(x)} {fmt(y)}')
            else:
                out.append('Z')
        return f'<path d="{"".join(out)}"/>'


class Circle:
    def __init__(self, cx, cy, r):
        self.cx, self.cy, self.r = cx, cy, r

    def svg(self, tx):
        x, y = tx.point(self.cx, self.cy)
        return f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="{fmt(self.r * tx.scale)}"/>'


def polygon(points):
    return Path([('M', *points[0]), *(('L', *p) for p in points[1:]), ('Z',)])


def rect(cx, cy, w, h, r=0, angle=0):
    """A rectangle centred on (cx, cy), optionally with rounded corners and rotated clockwise by angle degrees."""
    r = min(r, w / 2, h / 2)
    x0, x1, y0, y1 = -w / 2, w / 2, -h / 2, h / 2

    def pt(x, y):
        x, y = rotate((x, y), angle)
        return cx + x, cy + y

    if not r:
        return polygon([pt(x0, y0), pt(x1, y0), pt(x1, y1), pt(x0, y1)])
    return Path([
        ('M', *pt(x0 + r, y0)), ('L', *pt(x1 - r, y0)), ('A', r, 0, 1, *pt(x1, y0 + r)),
        ('L', *pt(x1, y1 - r)), ('A', r, 0, 1, *pt(x1 - r, y1)),
        ('L', *pt(x0 + r, y1)), ('A', r, 0, 1, *pt(x0, y1 - r)),
        ('L', *pt(x0, y0 + r)), ('A', r, 0, 1, *pt(x0 + r, y0)), ('Z',),
    ])


def chamfered_rect(cx, cy, w, h, tl=0, tr=0, br=0, bl=0):
    """A rectangle with the given corners (top-left, top-right, bottom-right, bottom-left) chamfered."""
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    points = [
        (x0 + tl, y0), (x1 - tr, y0), (x1, y0 + tr), (x1, y1 - br),
        (x1 - br, y1), (x0 + bl, y1), (x0, y1 - bl), (x0, y0 + tl),
    ]
    # Drop duplicate points where a corner isn't chamfered
    deduped = [p for i, p in enumerate(points) if p != points[i - 1]]
    return polygon(deduped)


def rounded_polygon(points, radii=0):
    """A polygon whose corners are rounded by the given radius (or per-vertex radii; 0 leaves a corner sharp)."""
    if not isinstance(radii, (list, tuple)):
        radii = [radii] * len(points)
    segments = []
    for i, (p, r) in enumerate(zip(points, radii)):
        if not r:
            segments.append(('L', *p))
            continue
        a, b = points[i - 1], points[(i + 1) % len(points)]
        ux, uy = a[0] - p[0], a[1] - p[1]
        vx, vy = b[0] - p[0], b[1] - p[1]
        lu, lv = math.hypot(ux, uy), math.hypot(vx, vy)
        ux, uy, vx, vy = ux / lu, uy / lu, vx / lv, vy / lv
        theta = math.acos(max(-1, min(1, ux * vx + uy * vy)))
        t = r / math.tan(theta / 2)
        # A right turn (on screen) is a clockwise arc
        sweep = 1 if (p[0] - a[0]) * (b[1] - p[1]) - (p[1] - a[1]) * (b[0] - p[0]) > 0 else 0
        segments.append(('L', p[0] + ux * t, p[1] + uy * t))
        segments.append(('A', r, 0, sweep, p[0] + vx * t, p[1] + vy * t))
    segments[0] = ('M', *segments[0][1:3])
    return Path([*segments, ('Z',)])


def arc_to(cx, cy, r, start, end, clockwise=True):
    """An arc segment along the given circle from start to end."""
    a0 = math.atan2(start[1] - cy, start[0] - cx)
    a1 = math.atan2(end[1] - cy, end[0] - cx)
    sweep = (a1 - a0) % (2 * math.pi) if clockwise else (a0 - a1) % (2 * math.pi)
    return ('A', r, 1 if sweep > math.pi else 0, 1 if clockwise else 0, *end)


def circle_intersections(c0, r0, c1, r1):
    """Return the two intersections of two circles, ordered left-hand then right-hand of the line c0 -> c1."""
    dx, dy = c1[0] - c0[0], c1[1] - c0[1]
    d = math.hypot(dx, dy)
    a = (r0 ** 2 - r1 ** 2 + d ** 2) / (2 * d)
    h = math.sqrt(r0 ** 2 - a ** 2)
    mx, my = c0[0] + a * dx / d, c0[1] + a * dy / d
    return (mx + h * dy / d, my - h * dx / d), (mx - h * dy / d, my + h * dx / d)


def keyed_circle(r, key_r, key_offset):
    """A circle with a semicircular key bump at 6 o'clock, centred key_offset below the circle's centre."""
    right, left = circle_intersections((0, 0), r, (0, key_offset), key_r)
    left, right = sorted((left, right))
    return Path([
        ('M', *left), arc_to(0, 0, r, left, right), arc_to(0, key_offset, key_r, right, left), ('Z',),
    ])


def arc_slot(cx, cy, radius, start, end, width):
    """A curved slot following a circle of the given radius from clock angle start to end (clockwise)."""
    ro, ri = radius + width / 2, radius - width / 2
    large = 1 if (end - start) % 360 > 180 else 0
    return Path([
        ('M', *polar(cx, cy, ro, start)), ('A', ro, large, 1, *polar(cx, cy, ro, end)),
        ('L', *polar(cx, cy, ri, end)), ('A', ri, large, 0, *polar(cx, cy, ri, start)), ('Z',),
    ])


#
# Drawings
#

class Transform:
    def __init__(self, scale, mirror):
        self.scale = scale
        self.mirror = mirror

    def point(self, x, y):
        x *= self.scale
        return SIZE / 2 + (-x if self.mirror else x), SIZE / 2 + y * self.scale


class Drawing:
    """
    The face of a connector. width and height give the extent of the face (in mm) about its centre, which is
    scaled to fill the frame.
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.elements = []

    def outline(self, *shapes):
        self.elements.extend(('outline', s) for s in shapes)
        return self

    def detail(self, *shapes):
        self.elements.extend(('detail', s) for s in shapes)
        return self

    def fill(self, *shapes):
        self.elements.extend(('fill', s) for s in shapes)
        return self

    def svg(self, mirror=False):
        tx = Transform(CONTENT / max(self.width, self.height), mirror)
        groups = {
            'outline': f'<g fill="none" stroke="#000" stroke-width="{OUTLINE}" stroke-linejoin="round">',
            'detail': f'<g fill="none" stroke="#000" stroke-width="{DETAIL}" stroke-linejoin="round">',
            'fill': '<g fill="#000">',
        }
        lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}">']
        for style, opening in groups.items():
            shapes = [s.svg(tx) for st, s in self.elements if st == style]
            if shapes:
                lines.append(opening + ''.join(shapes) + '</g>')
        lines.append('</svg>')
        return '\n'.join(lines) + '\n'


def mirrored(func):
    """Mark a face drawing to be rendered as its mirror image (i.e. the face of the mating connector)."""
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs), True
    return wrapper


#
# IEC 60320 appliance couplers (earth at the top; outlets are female connectors, ports are male inlets)
#

def iec_c13_family(male=False, earth=True, notch=False):
    """C13/C14 (and the C15/C16 and C17/C18 variants): a rectangle with chamfered top corners."""
    if male:
        w, h, chamfer_x, chamfer_y, pin = 24, 16, 7, -3, (2.0, 4.0)
    else:
        w, h, chamfer_x, chamfer_y, pin = 23, 15.8, 6.1, -2.5, (2.5, 5.0)
    x, y = w / 2, h / 2
    points = [(-chamfer_x, -y), (chamfer_x, -y), (x, chamfer_y), (x, y)]
    radii = [1.5, 1.5, 1.5, 3]
    if notch:
        nw, apex = (2.25, 3.3) if male else (2.5, 3.0)
        points.append((nw, y))
        radii.append(0.8)
        for angle in range(0, 181, 15):
            points.append((nw * math.cos(math.radians(angle)), apex + nw - nw * math.sin(math.radians(angle))))
            radii.append(0)
        points.append((-nw, y))
        radii.append(0.8)
    points += [(-x, y), (-x, chamfer_y)]
    radii += [3, 1.5]
    drawing = Drawing(w, h).outline(rounded_polygon(points, radii))
    drawing.fill(rect(-7, 2, *pin), rect(7, 2, *pin))
    if earth:
        drawing.fill(rect(0, -2, *pin))
    return drawing


def iec_c19_family(male=False, chamfer=False):
    """C19/C20 (and the C21/C22 variants): a rectangle with horizontal contacts."""
    if male:
        w, h, chamfer_x, chamfer_y, earth, line, thickness = 29, 21, 7.5, -3.5, 6, 5, 2.0
    else:
        w, h, chamfer_x, chamfer_y, earth, line, thickness = 28, 20, 7, -3, 7, 6, 2.5
    x, y = w / 2, h / 2
    if chamfer:
        outline = rounded_polygon(
            [(-chamfer_x, -y), (chamfer_x, -y), (x, chamfer_y), (x, y), (-x, y), (-x, chamfer_y)],
            [1.5, 1.5, 1.5, 3, 3, 1.5],
        )
    else:
        outline = rect(0, 0, w, h, 3)
    return Drawing(w, h).outline(outline).fill(
        rect(0, -4, earth, thickness), rect(-6.5, 4, line, thickness), rect(6.5, 4, line, thickness),
    )


def iec_c5_family(male=False):
    """C5/C6 ("cloverleaf"): the union of three circular lobes."""
    earth, live, neutral = ((0, -2), 4.5), ((-5, 2.5), 4.0), ((5, 2.5), 4.0)
    en_top, en_bottom = circle_intersections(earth[0], earth[1], neutral[0], neutral[1])
    el_bottom, el_top = circle_intersections(earth[0], earth[1], live[0], live[1])
    outline = Path([
        ('M', *el_top),
        arc_to(*earth[0], earth[1], el_top, en_top),
        arc_to(*neutral[0], neutral[1], en_top, en_bottom),
        arc_to(*earth[0], earth[1], en_bottom, el_bottom),
        arc_to(*live[0], live[1], el_bottom, el_top),
        ('Z',),
    ])
    earth_r, line_r = (1.6, 1.18) if male else (1.9, 1.45)
    return Drawing(18, 13).outline(outline).fill(
        Circle(0, -2, earth_r), Circle(-5, 2.5, line_r), Circle(5, 2.5, line_r),
    )


def iec_c7_family(male=False):
    """C7/C8 ("figure 8"): two overlapping circular lobes."""
    r, pin_r = (4.1, 1.18) if male else (4.0, 1.45)
    top, bottom = circle_intersections((-3.6, 0), r, (3.6, 0), r)
    outline = Path([
        ('M', *top), arc_to(3.6, 0, r, top, bottom), arc_to(-3.6, 0, r, bottom, top), ('Z',),
    ])
    return Drawing(7.2 + 2 * r, 2 * r).outline(outline).fill(Circle(-4.3, 0, pin_r), Circle(4.3, 0, pin_r))


#
# IEC 60309 pin & sleeve (16 A). Viewed from the front of the socket with the keyway at 6 o'clock, the earth
# contact sits at the clock hour given by the type and the remaining contacts follow it clockwise.
#

IEC_60309_SIZES = {
    # Contacts: (recess radius, key bump offset, pin circle radius, plug shroud inner/outer radii)
    3: (22.15, 21.85, 8.75, (18.95, 21.75)),
    4: (25.2, 25.3, 10.75, (21.4, 24.75)),
    5: (28.65, 29.15, 13.25, (24.4, 28.05)),
}


def iec_60309(contacts, hour, male=False):
    radius, key_offset, pin_circle, shroud = IEC_60309_SIZES[contacts]
    if male:
        outer = shroud[1]
        drawing = Drawing(2 * outer, 2 * outer).outline(keyed_circle(outer, 3, outer + 0.2))
        drawing.detail(Circle(0, 0, shroud[0]))
        earth_r, line_r = 3.5, 2.5
    else:
        drawing = Drawing(2 * radius, 2 * radius).outline(keyed_circle(radius, 3.5, key_offset))
        earth_r, line_r = 4.0, 3.0
    for i in range(contacts):
        x, y = polar(0, 0, pin_circle, hour * 30 + i * 360 / contacts)
        drawing.fill(Circle(x, y, earth_r if i == 0 else line_r))
    return drawing


#
# IEC 60906-1 & NBR 14136 (three round contacts within a flattened hexagon; earth offset towards the top)
#

def iec_60906(pin_r):
    outline = rounded_polygon([(-9.9, -8.5), (9.9, -8.5), (18.4, 0), (9.9, 8.5), (-9.9, 8.5), (-18.4, 0)], 1.5)
    return Drawing(35.5, 17).outline(outline).fill(Circle(-9.5, 0, pin_r), Circle(9.5, 0, pin_r), Circle(0, -3, pin_r))


#
# NEMA straight-blade receptacles (face radius = 1; oriented as on the NEMA configuration chart, ground at the top)
#

NEMA_SLOT = 0.15


def nema_v(x, y, length):
    """A vertical slot."""
    return rect(x, y, NEMA_SLOT, length)


def nema_h(x, y, length):
    """A horizontal slot."""
    return rect(x, y, length, NEMA_SLOT)


def nema_arm(x0, x1, y):
    """A horizontal arm extending from a vertical slot at x0 to x1 (forming a T- or L-shaped slot)."""
    return rect((x0 + x1) / 2, y, abs(x1 - x0), NEMA_SLOT)


def nema_ground(y=-0.58):
    """A U-shaped ground hole, flat side towards the rim."""
    return Path([
        ('M', -0.15, y - 0.14), ('L', 0.15, y - 0.14), ('L', 0.15, y), arc_to(0, y, 0.15, (0.15, y), (-0.15, y)),
        ('Z',),
    ])


def nema(*slots, ground=-0.58):
    drawing = Drawing(2, 2).outline(Circle(0, 0, 1)).fill(*slots)
    if ground is not None:
        drawing.fill(nema_ground(ground))
    return drawing


def nema_10(neutral):
    return nema(*neutral, rect(0.39, 0.25, NEMA_SLOT, 0.5, angle=30), rect(-0.37, 0.23, NEMA_SLOT, 0.5, angle=-30),
                ground=None)


NEMA_STRAIGHT = {
    '1-15': lambda: nema(nema_v(0.38, 0, 0.76), nema_v(-0.38, 0, 0.48), ground=None),
    '5-15': lambda: nema(nema_v(0.38, 0.12, 0.76), nema_v(-0.38, 0.12, 0.47)),
    '5-20': lambda: nema(nema_v(0.29, 0.12, 0.7), nema_arm(0.29, 0.75, 0.1), nema_v(-0.38, 0.12, 0.47)),
    '5-30': lambda: nema(nema_v(0.375, 0.11, 0.47), nema_arm(0.375, 0.1, -0.02), nema_v(-0.38, 0.12, 0.47)),
    '5-50': lambda: nema(nema_v(0.38, 0.16, 0.76), nema_v(-0.57, 0.13, 0.48)),
    '6-15': lambda: nema(nema_h(0.43, 0.23, 0.48), nema_h(-0.43, 0.23, 0.48)),
    '6-20': lambda: nema(nema_v(0.25, 0.115, 0.75), nema_arm(0.25, 0.79, 0.13), nema_h(-0.42, 0.15, 0.47)),
    '6-30': lambda: nema(nema_h(0.43, 0.14, 0.47), nema_h(-0.43, 0.14, 0.47)),
    '6-50': lambda: nema(nema_v(-0.46, 0.17, 0.76), nema_v(0.48, 0.12, 0.48)),
    '10-30': lambda: nema_10([nema_v(-0.08, -0.52, 0.44), nema_arm(-0.08, 0.28, -0.37)]),
    '10-50': lambda: nema_10([nema_v(0.01, -0.46, 0.66)]),
    '14-20': lambda: nema(
        nema_v(0.55, -0.06, 0.47), nema_v(-0.55, -0.06, 0.47), nema_h(0, 0.45, 0.47), ground=-0.63
    ),
    '14-30': lambda: nema(
        nema_v(0.53, -0.04, 0.65), nema_v(-0.51, -0.04, 0.65), nema_v(0.135, 0.51, 0.48), nema_arm(0.135, -0.2, 0.37),
        ground=-0.63,
    ),
    '14-50': lambda: nema(
        nema_v(0.53, -0.04, 0.66), nema_v(-0.53, -0.04, 0.66), nema_v(0.01, 0.51, 0.66), ground=-0.63
    ),
    '14-60': lambda: nema(
        nema_v(0.53, -0.04, 0.66), nema_v(-0.53, -0.04, 0.66), nema_h(0.03, 0.56, 0.65), ground=-0.63
    ),
    '15-15': lambda: nema(nema_v(-0.58, 0, 0.48), nema_h(0.55, 0, 0.48), nema_h(0, 0.58, 0.48)),
    '15-20': lambda: nema(nema_v(-0.57, 0, 0.66), nema_h(0.45, 0, 0.64), nema_h(0, 0.59, 0.64)),
    '15-30': lambda: nema(nema_h(-0.52, 0, 0.47), nema_h(0.55, 0, 0.47), nema_h(0, 0.58, 0.47)),
    '15-50': lambda: nema(nema_v(0.6, 0, 0.48), nema_h(-0.51, 0, 0.47), nema_h(0, 0.58, 0.47)),
    '15-60': lambda: nema(
        nema_v(-0.52, -0.04, 0.66), nema_h(0.45, 0, 0.65), nema_h(0.03, 0.56, 0.65), ground=-0.63
    ),
}


#
# NEMA locking ("twist-lock") receptacles (face radius = 1; oriented as on the NEMA configuration chart). Each
# slot is an arc between two clock angles, optionally with a tab at one end stepping in or out to a given radius.
#

LOCKING_SLOT = 0.15
TAB_SPAN = 15
TAB_EXAGGERATION = 0.04


def locking_slot(start, end, radius=0.555, width=LOCKING_SLOT, tab=None):
    """
    A curved slot. tab is (end, radius): the angle of the slot end at which a tab extends radially to the given
    radius.
    """
    shapes = [arc_slot(0, 0, radius, start, end, width)]
    if tab:
        at, to = tab
        # Tabs are exaggerated slightly to remain legible at small sizes
        to += TAB_EXAGGERATION if to > radius else -TAB_EXAGGERATION
        edge = radius + width / 2 if to > radius else radius - width / 2
        span = (at - TAB_SPAN, at) if at % 360 == end % 360 else (at, at + TAB_SPAN)
        shapes.append(arc_slot(0, 0, (edge + to) / 2, *span, abs(to - edge) + 0.02))
    return shapes


def locking(*slots, center_ground=False):
    drawing = Drawing(2, 2).outline(Circle(0, 0, 1))
    for slot in slots:
        drawing.fill(*slot)
    if center_ground:
        drawing.fill(Circle(0, 0, 0.1))
    return drawing


def l_14(w, ground_tab):
    return locking(
        locking_slot(331, 26), locking_slot(*w), locking_slot(152, 208), locking_slot(238, 298, tab=ground_tab),
    )


def l_15(ground_tab):
    return locking(
        locking_slot(330, 13), locking_slot(65, 124), locking_slot(152, 208), locking_slot(242, 297, tab=ground_tab),
    )


def l_21(x, y, z, neutral_tab):
    return locking(
        locking_slot(*x), locking_slot(*y), locking_slot(*z),
        locking_slot(237, 297, radius=0.52, tab=neutral_tab), center_ground=True,
    )


NEMA_LOCKING = {
    'l1-15': lambda: locking(locking_slot(329, 31, 0.605), locking_slot(145, 214, 0.54, tab=(145, 0.69))),
    'l5-15': lambda: locking(
        locking_slot(16, 85, 0.525), locking_slot(139, 200, 0.605), locking_slot(254, 317, 0.56, tab=(254, 0.41)),
    ),
    'l5-20': lambda: locking(locking_slot(10, 44), locking_slot(116, 181), locking_slot(234, 299, tab=(299, 0.39))),
    'l5-30': lambda: locking(locking_slot(7, 45), locking_slot(122, 174), locking_slot(234, 300, tab=(300, 0.39))),
    'l6-15': lambda: locking(
        locking_slot(15, 84, 0.54), locking_slot(138, 202, 0.565), locking_slot(253, 321, 0.55, tab=(321, 0.7)),
    ),
    'l6-20': lambda: locking(locking_slot(0, 53), locking_slot(126, 168), locking_slot(235, 298, tab=(298, 0.39))),
    'l6-30': lambda: locking(locking_slot(0, 53), locking_slot(126, 168), locking_slot(235, 298, tab=(298, 0.39))),
    'l10-30': lambda: locking(
        locking_slot(0, 43, 0.68), locking_slot(119, 162, 0.68), locking_slot(238, 287, 0.68, tab=(238, 0.51)),
    ),
    'l14-20': lambda: l_14((68, 112), (298, 0.68)),
    'l14-30': lambda: l_14((69, 107), (298, 0.4)),
    'l15-20': lambda: l_15((297, 0.68)),
    'l15-30': lambda: l_15((297, 0.4)),
    'l21-20': lambda: l_21((327, 21), (67, 105), (147, 201), (237, 0.69)),
    'l21-30': lambda: l_21((327, 21), (67, 105), (147, 201), (237, 0.38)),
    'l22-20': lambda: l_21((337, 14), (58, 116), (151, 207), (237, 0.69)),
    'l22-30': lambda: l_21((337, 14), (58, 116), (151, 207), (237, 0.38)),
}


#
# California Style 50 A locking connectors (Hubbell; face radius = 1). Three curved contacts around a centre post
# (a hole on the plug). Three-pole types have keying lugs around the rim and a recessed sector.
#

CS_SLOT = 0.17


def cs_slot(start, end, tab=None, step=None):
    """A curved contact. step is (start, end, radius): a portion of the slot widened outward to the given radius."""
    shapes = locking_slot(start, end, 0.525, CS_SLOT, tab)
    if step:
        a0, a1, to = step
        edge = 0.525 + CS_SLOT / 2
        shapes.append(arc_slot(0, 0, (edge + to) / 2, a0, a1, to - edge + 0.02))
    return shapes


def cs_outline(lugs, recess):
    """A circular rim with semicircular lugs at the given angles and a recessed sector (start, end)."""
    lug_r, recess_r = 0.125, 0.93
    delta = math.degrees(2 * math.asin(lug_r / 2))
    events = sorted([(a % 360, 'lug') for a in lugs] + [(recess[0], 'recess')])
    start = polar(0, 0, 1, events[0][0] - delta - 1)
    segments = [('M', *start)]
    point = start
    for angle, kind in events:
        if kind == 'lug':
            p0, p1 = polar(0, 0, 1, angle - delta), polar(0, 0, 1, angle + delta)
            segments += [arc_to(0, 0, 1, point, p0), arc_to(*polar(0, 0, 1, angle), lug_r, p0, p1)]
            point = p1
        else:
            p0 = polar(0, 0, 1, recess[0])
            q0, q1 = polar(0, 0, recess_r, recess[0]), polar(0, 0, recess_r, recess[1])
            point = polar(0, 0, 1, recess[1])
            segments += [arc_to(0, 0, 1, segments[-1][-2:], p0), ('L', *q0), arc_to(0, 0, recess_r, q0, q1),
                         ('L', *point)]
    segments += [arc_to(0, 0, 1, point, start), ('Z',)]
    return Path(segments)


def california(slots, male=False, lugs=None, recess=None):
    outline = cs_outline(lugs, recess) if lugs else Circle(0, 0, 1)
    drawing = Drawing(2.25 if lugs else 2, 2.25 if lugs else 2).outline(outline)
    for slot in slots:
        drawing.fill(*slot)
    if male:
        drawing.detail(Circle(0, 0, 0.12))
    else:
        drawing.fill(Circle(0, 0, 0.14))
    return drawing


CALIFORNIA_STYLE = {
    # Connector (female), plug (male): (contacts, rim lugs, recessed sector)
    ('CS6360C', 'cs6361c'): ([cs_slot(5, 56), cs_slot(117, 185), cs_slot(247, 300, tab=(247, 0.72))], None, None),
    ('CS8264C', 'cs8265c'): ([cs_slot(9, 60), cs_slot(119, 188), cs_slot(247, 300, tab=(247, 0.72))], None, None),
    ('CS8464C', 'cs8465c'): ([cs_slot(6, 57), cs_slot(113, 188), cs_slot(235, 299, tab=(235, 0.36))], None, None),
    ('CS6364C', 'cs6365c'): (
        [cs_slot(359, 59, step=(359, 29, 0.66)), cs_slot(126, 175), cs_slot(239, 294, step=(239, 266, 0.7))],
        (5, 35, 205, 238), (89, 155),
    ),
    ('CS8364C', 'cs8365c'): (
        [cs_slot(3, 71, tab=(3, 0.33)), cs_slot(125, 176), cs_slot(232, 299, tab=(232, 0.34))],
        (13, 41, 204, 234), (90, 158),
    ),
    ('CS8164C', 'cs8165c'): (
        [cs_slot(1, 58, step=(1, 30, 0.66)), cs_slot(127, 181), cs_slot(230, 295, step=(230, 262, 0.7))],
        (330, 8, 189, 226), (87, 160),
    ),
}


#
# International (ITA/IEC World Plugs types). Sockets are drawn as seen from the front; plugs whose face differs
# from the mirror image of the socket are drawn separately.
#

def ita_c_plug():
    """Europlug (CEE 7/16)."""
    outline = rounded_polygon(
        [(-10.8, -6.85), (10.8, -6.85), (17.65, 0), (10.8, 6.85), (-10.8, 6.85), (-17.65, 0)], 1.5
    )
    return Drawing(35.3, 13.7).outline(outline).fill(Circle(-9.25, 0, 2), Circle(9.25, 0, 2))


def schuko_plug(strips=True, earth_hole=False):
    """CEE 7/4 (with earth strips at 12 and 6 o'clock), CEE 7/6 (with an earth hole), and CEE 7/7 (both)."""
    r = 18.25
    # Round body with guide grooves at 3 and 9 o'clock
    groove = math.degrees(math.asin(1.6 / r))
    points = [polar(0, 0, r, a) for a in (90 - groove, 90 + groove, 270 - groove, 270 + groove)]
    inner = [(p[0] - math.copysign(2, p[0]), p[1]) for p in points]
    outline = Path([
        ('M', *points[3]), arc_to(0, 0, r, points[3], points[0]), ('L', *inner[0]), ('L', *inner[1]),
        ('L', *points[1]), arc_to(0, 0, r, points[1], points[2]), ('L', *inner[2]), ('L', *inner[3]), ('Z',),
    ])
    drawing = Drawing(2 * r, 2 * r).outline(outline).fill(Circle(-9.5, 0, 2.4), Circle(9.5, 0, 2.4))
    if strips:
        drawing.fill(rect(0, -r + 1, 6, 2), rect(0, r - 1, 6, 2))
    if earth_hole:
        drawing.detail(Circle(0, -10, 2.6))
    return drawing


def ita_e_socket():
    """CEE 7/5: a round recess with a projecting earth pin."""
    return Drawing(40, 40).outline(Circle(0, 0, 20)).fill(
        Circle(-9.5, 0, 2.75), Circle(9.5, 0, 2.75), Circle(0, -10, 2.4),
    ).detail(Circle(0, -10, 3.8))


def ita_f_socket():
    """CEE 7/3 (Schuko): a round recess with earth clips at 12 and 6 o'clock."""
    return Drawing(40, 40).outline(Circle(0, 0, 20)).fill(
        Circle(-9.5, 0, 2.75), Circle(9.5, 0, 2.75), rect(0, -18, 6, 2.4), rect(0, 18, 6, 2.4),
    )


def ita_g(socket=True):
    """BS 1363."""
    earth, line = ((4.5, 8.5), (7, 4.5)) if socket else ((4, 8), (6.4, 4))
    outline = rect(0, 0, 48, 48, 5) if socket else rect(0, 1.5, 48, 45, 5)
    return Drawing(48, 48).outline(outline).fill(
        rect(0, -11.1, *earth), rect(-11.1, 11.1, *line), rect(11.1, 11.1, *line),
    )


def ita_h(socket=True):
    """SI 32 (round pins)."""
    r = 2.6 if socket else 2.25
    return Drawing(38, 38).outline(Circle(0, 0, 19)).fill(
        Circle(-9.5, -4.75, r), Circle(9.5, -4.75, r), Circle(0, 4.75, r),
    )


def ita_i(socket=True):
    """AS/NZS 3112."""
    length, thickness = (7, 2.2) if socket else (6.35, 2)
    outline = rect(0, 0, 38, 38, 4) if socket else rect(0, 0, 36, 38, 9)
    return Drawing(38, 38).outline(outline).fill(
        rect(-6.86, -7.2, thickness, length, angle=30), rect(6.86, -7.2, thickness, length, angle=-30),
        rect(0, 7.1, thickness, length),
    )


def ita_j(socket=True):
    """SN 441011 (T12 plug/T13 socket): a hexagonal profile with the earth offset below the line contacts."""
    r = 2.25 if socket else 2
    outline = rounded_polygon(
        [(-8.38, -10), (8.38, -10), (18, -0.38), (18, 0.38), (8.38, 10), (-8.38, 10), (-18, 0.38), (-18, -0.38)],
        [3, 3, 0.9, 0.9, 3, 3, 0.9, 0.9] if socket else [10, 10, 0.9, 0.9, 10, 10, 0.9, 0.9],
    )
    return Drawing(36, 20).outline(outline).fill(Circle(-9.5, 0, r), Circle(9.5, 0, r), Circle(0, 5, r))


def ita_k(socket=True):
    """DS 107-2-D1 (Danish): a D-shaped earth contact below the line contacts."""
    r = 2.65 if socket else 2.4
    cy, earth_r = 7.5, 3.25
    chord = math.sqrt(earth_r ** 2 - 0.75 ** 2)
    earth = Path([
        ('M', -chord, cy - 0.75), ('L', chord, cy - 0.75),
        arc_to(0, cy, earth_r, (chord, cy - 0.75), (-chord, cy - 0.75)), ('Z',),
    ])
    return Drawing(40, 40).outline(Circle(0, 0, 20)).fill(Circle(-9.5, -5.5, r), Circle(9.5, -5.5, r), earth)


def ita_l_plug():
    """CEI 23-50 S11 (10 A): three contacts in line."""
    outline = rounded_polygon([(-10.5, -7), (10.5, -7), (17.5, 0), (10.5, 7), (-10.5, 7), (-17.5, 0)], 1.5)
    return Drawing(35, 14).outline(outline).fill(Circle(-9.5, 0, 2), Circle(0, 0, 2), Circle(9.5, 0, 2))


def ita_l_socket():
    """CEI 23-50 P17/11 ("bipasso"), mounted vertically: accepts both 10 A and 16 A plugs."""
    drawing = Drawing(22, 44).outline(rect(0, 0, 22, 44, 4)).fill(Circle(0, 0, 2.25))
    for sign in (-1, 1):
        drawing.fill(Circle(0, sign * 9.5, 2.25), Circle(0, sign * 13, 2.75))
    return drawing


def ita_m(socket=True):
    """BS 546 (15 A)."""
    line_r, earth_r = (3.8, 4.6) if socket else (3.53, 4.36)
    outline = rect(0, 0, 54, 54, 6) if socket else Circle(0, 0, 27)
    return Drawing(54, 54).outline(outline).fill(
        Circle(-12.7, 14.3, line_r), Circle(12.7, 14.3, line_r), Circle(0, -14.3, earth_r),
    )


def ita_o(socket=True):
    """TIS 166-2549 (Thai)."""
    r = 2.65 if socket else 2.4
    return Drawing(39, 39).outline(Circle(0, 0, 19.5)).fill(
        Circle(-9.5, 5.95, r), Circle(9.5, 5.95, r), Circle(0, -5.95, r),
    )


#
# USB (receptacle openings)
#

def usb_a():
    return Drawing(12, 4.5).outline(rect(0, 0, 12, 4.5, 0.3)).fill(rect(0, -0.85, 10, 1.9))


def usb_b():
    return Drawing(8.5, 7.8).outline(chamfered_rect(0, 0, 8.5, 7.8, tl=1.4, tr=1.4)).fill(rect(0, 0.4, 5.2, 3.2))


def usb_3_b():
    outline = polygon([
        (-2.9, -5.6), (2.9, -5.6), (2.9, -2.4), (4.25, -2.4), (4.25, 5.6), (-4.25, 5.6), (-4.25, -2.4),
        (-2.9, -2.4),
    ])
    return Drawing(8.5, 11.2).outline(outline).fill(rect(0, 1.2, 5.2, 3.2), rect(0, -3.8, 3.6, 1.6))


def usb_c():
    return Drawing(8.4, 2.6).outline(rect(0, 0, 8.4, 2.6, 1.3)).fill(rect(0, 0, 6.6, 0.7, 0.15))


def usb_mini_a():
    outline = Path([
        ('M', -3.5, -1.5), ('L', 3.5, -1.5), ('L', 3.5, 0.3), ('A', 1.2, 0, 1, 2.3, 1.5),
        ('L', -2.3, 1.5), ('A', 1.2, 0, 1, -3.5, 0.3), ('Z',),
    ])
    return Drawing(7, 3).outline(outline).fill(rect(0, -0.6, 5, 0.6))


def usb_mini_b():
    outline = polygon([
        (-3.5, -1.5), (3.5, -1.5), (3.5, 0.2), (2.9, 0.2), (2.3, 1.5), (-2.3, 1.5), (-2.9, 0.2), (-3.5, 0.2),
    ])
    return Drawing(7, 3).outline(outline).fill(rect(0, -0.6, 5, 0.6))


def usb_micro_a():
    return Drawing(6.9, 1.85).outline(rect(0, 0, 6.9, 1.85, 0.2)).fill(rect(0, -0.45, 5, 0.45))


def usb_micro_b():
    return Drawing(6.9, 1.85).outline(chamfered_rect(0, 0, 6.9, 1.85, br=0.7, bl=0.7)).fill(rect(0, -0.45, 5, 0.45))


def usb_3_micro_b():
    outline = polygon([
        (-6.1, -0.92), (6.1, -0.92), (6.1, 0.22), (5.4, 0.92), (1.9, 0.92), (1.9, 0.1), (0.9, 0.1), (0.9, 0.92),
        (-5.4, 0.92), (-6.1, 0.22),
    ])
    return Drawing(12.2, 1.85).outline(outline).fill(rect(-2.6, -0.45, 5, 0.45), rect(3.9, -0.45, 3.3, 0.45))


#
# Molex Micro-Fit 3.0 (3 mm pitch; cavities alternate square and rounded for polarization)
#

def molex_micro_fit(rows, columns):
    pitch = 3.0
    width, height = columns * pitch + 1.4, rows * pitch + 1.4
    drawing = Drawing(width, height + 2.4)
    top = -(height + 2.4) / 2 + 2.4
    drawing.outline(
        rect(0, top + height / 2, width, height, 0.4),
        rect(0, top - 1.2, min(4, width - 1), 2.4, 0.3),  # Latch
    )
    for row in range(rows):
        for column in range(columns):
            cx = (column - (columns - 1) / 2) * pitch
            cy = top + 0.7 + pitch / 2 + row * pitch
            rounded = (row + column) % 2
            drawing.fill(rect(cx, cy, 2.1, 2.1, 0.9 if rounded else 0.15))
    return drawing


#
# Proprietary
#

def powercon_chassis(flange=(26, 31), holes=(9.5, 12)):
    """The square flange and mounting holes common to powerCON chassis connectors."""
    w, h = flange
    return Drawing(w, h).outline(rect(0, 0, w, h, 3.5)).detail(
        Circle(-holes[0], -holes[1], 1.7), Circle(holes[0], holes[1], 1.7),
    )


def powercon_20a():
    """NAC3MPA (power in); the power out variant (NAC3MPB) is its mirror image."""
    drawing = powercon_chassis().detail(Circle(0, 0, 11.8), Circle(0, 0, 6.4))
    return drawing.fill(
        rect(0, -9.5, 5.6, 1.9),                                    # Latch
        rect(-9.4, 0, 1.6, 3.8),                                    # Keying notch
        arc_slot(0, 0, 2.8, 45, 315, 0.8),                          # Centre insulator
        rect(*polar(0, 0, 4.5, 315), 0.8, 2.8, angle=315),          # Long rib
        rect(*polar(0, 0, 3.8, 45), 0.8, 1.4, angle=45),            # Short rib
        arc_slot(0, 0, 5.95, 65, 115, 0.9), arc_slot(0, 0, 5.95, 245, 295, 0.9),
    )


def powercon_32a():
    """NAC3MP-HC (power in only)."""
    drawing = powercon_chassis((32, 37), (12.5, 15)).detail(Circle(0, 0, 14.8), Circle(0, 0, 10.5), Circle(0, 0, 4.65))
    drawing.fill(arc_slot(0, 0, 13.6, -14, 14, 1.4), rect(0, 11.8, 3.5, 1.9))
    for angle in (0, 90, 180, 270):
        x, y = rotate((-0.85, -3.9), angle)
        drawing.fill(rect(x, y, 3.2, 0.9, angle=angle))
    return drawing


def powercon_true1_inlet():
    """NAC3MPX (also TRUE1 TOP, whose face differs only in a small centre detail)."""
    drawing = powercon_chassis().detail(Circle(0, 0, 11.8), Circle(0, 0, 6.45))
    drawing.fill(arc_slot(0, 0, 9.85, -17, 17, 1.7))
    for angle in (90, 180, 270):
        drawing.fill(rect(*polar(0, 0, 11, angle), 2.4, 1.6, angle=angle))
    for angle in (300, 51, 180):
        drawing.fill(arc_slot(0, 0, 5.1, angle - 15, angle + 15, 1.1))
    return drawing


def powercon_true1_outlet():
    """NAC3FPX (also TRUE1 TOP)."""
    drawing = Drawing(35.4, 35.4).outline(rect(0, 0, 35.4, 35.4, 5.5)).detail(
        Circle(0, 0, 14.2), Circle(0, 0, 2.65),
        *(Circle(x, y, 1.72) for x in (-12.2, 12.2) for y in (-12.2, 12.2)),
    )
    for angle in (284, 164, 44):
        drawing.fill(arc_slot(0, 0, 5.125, angle - 49, angle + 49, 1.35))
    return drawing


def saf_d_grid():
    """Saf-D-Grid 400 receptacle (used on both equipment and PDUs)."""
    opening = rounded_polygon(
        [(-8.9, -8.85), (8.9, -8.85), (11.9, -0.8), (11.9, 8.85), (-11.9, 8.85), (-11.9, -0.8)], [1, 1, 1, 2, 2, 1],
    )
    return Drawing(33.4, 24.1).outline(rect(0, 0, 33.4, 24.1, 2)).detail(opening).fill(
        rect(0, -1.8, 4.4, 1.4), rect(-6.9, 3, 4.4, 1.4), rect(6.9, 3, 4.4, 1.4),
    )


def hdot_cx():
    """Accepts both C14 and C20 plugs: a C13 profile with slots combining the C13 and C19 patterns."""
    drawing = iec_c13_family()
    drawing.elements = [e for e in drawing.elements if e[0] == 'outline']
    return drawing.fill(
        rect(0, -4, 7, 2.5), rect(0, -2, 2.5, 5),
        rect(-6.5, 4, 6, 2.5), rect(-7, 2, 2.5, 5),
        rect(6.5, 4, 6, 2.5), rect(7, 2, 2.5, 5),
    )


def eaton_c39():
    """Accepts both C14 and C20 plugs: a C20-sized cavity around a stepped block with T-shaped slots."""
    block = polygon([
        (-5.75, -7), (5.75, -7), (5.75, -2), (11, -2), (11, 7), (2.4, 7), (2.4, 3), (-2.4, 3), (-2.4, 7),
        (-11, 7), (-11, -2), (-5.75, -2),
    ])
    return Drawing(35, 27.5).outline(rect(0, 0, 35, 27.5, 3.5)).detail(block).fill(
        rect(0, -4, 7, 2.5), rect(0, -2, 2.5, 5),
        rect(-6.5, 4, 6, 2.5), rect(-7, 2, 2.5, 5),
        rect(6.5, 4, 6, 2.5), rect(7, 2, 2.5, 5),
    )


#
# Registry
#

IEC_60309_TYPES = {
    # Value prefix: number of contacts
    'iec-60309-p-n-e': 3,
    'iec-60309-2p-e': 3,
    'iec-60309-3p-e': 4,
    'iec-60309-3p-n-e': 5,
}


def iec_60309_types(male=False):
    """Return a drawing function for each IEC 60309 type."""
    def factory(contacts, hour):
        def func():
            drawing = iec_60309(contacts, hour, male=male)
            return (drawing, True) if male else drawing
        return func
    return {
        f'{prefix}-{hour}h': factory(contacts, hour)
        for prefix, contacts in IEC_60309_TYPES.items()
        for hour in (4, 6, 9)
    }


def nema_types(male=False):
    """Return a drawing function for each NEMA (straight-blade and locking) and California Style type."""
    suffix = 'p' if male else 'r'
    types = {f'nema-{name}{suffix}': func for name, func in {**NEMA_STRAIGHT, **NEMA_LOCKING}.items()}
    if male:
        types = {value: mirrored(func) for value, func in types.items()}
    for (female_value, male_value), (slots, lugs, recess) in CALIFORNIA_STYLE.items():
        value = male_value if male else female_value
        types[value] = (lambda s=slots, lu=lugs, r=recess: (california(s, male, lu, r), male))
    return types


# Outlet type: drawing function
POWER_OUTLETS = {
    'iec-60320-c5': iec_c5_family,
    'iec-60320-c7': iec_c7_family,
    'iec-60320-c13': iec_c13_family,
    'iec-60320-c15': lambda: iec_c13_family(notch=True),
    'iec-60320-c17': lambda: iec_c13_family(earth=False),
    'iec-60320-c19': iec_c19_family,
    'iec-60320-c21': lambda: iec_c19_family(chamfer=True),
    **iec_60309_types(),
    'iec-60906-1': lambda: iec_60906(2.4),
    'nbr-14136-10a': lambda: iec_60906(2.2),
    'nbr-14136-20a': lambda: iec_60906(2.6),
    **nema_types(),
    'ita-e': ita_e_socket,
    'ita-f': ita_f_socket,
    'ita-g': ita_g,
    'ita-h': ita_h,
    'ita-i': ita_i,
    'ita-j': ita_j,
    'ita-k': ita_k,
    'ita-l': ita_l_socket,
    'ita-m': ita_m,
    'ita-n': lambda: iec_60906(2.4),
    'ita-o': ita_o,
    'usb-a': usb_a,
    'usb-micro-b': usb_micro_b,
    'usb-c': usb_c,
    'molex-micro-fit-1x2': lambda: molex_micro_fit(1, 2),
    'molex-micro-fit-2x2': lambda: molex_micro_fit(2, 2),
    'molex-micro-fit-2x3': lambda: molex_micro_fit(2, 3),
    'molex-micro-fit-2x4': lambda: molex_micro_fit(2, 4),
    'eaton-c39': eaton_c39,
    'hdot-cx': hdot_cx,
    'saf-d-grid': saf_d_grid,
    # Power out chassis connectors are the mirror image of power in
    'neutrik-powercon-20a': mirrored(powercon_20a),
    'neutrik-powercon-32a': powercon_32a,
    'neutrik-powercon-true1': powercon_true1_outlet,
    'neutrik-powercon-true1-top': powercon_true1_outlet,
}

# Port type: drawing function. Faces wrapped with mirrored() are drawn as the mirror image of the mating face.
POWER_PORTS = {
    # IEC 60320 inlets share the orientation of their mating connector
    'iec-60320-c6': lambda: iec_c5_family(male=True),
    'iec-60320-c8': lambda: iec_c7_family(male=True),
    'iec-60320-c14': lambda: iec_c13_family(male=True),
    'iec-60320-c16': lambda: iec_c13_family(male=True, notch=True),
    'iec-60320-c18': lambda: iec_c13_family(male=True, earth=False),
    'iec-60320-c20': lambda: iec_c19_family(male=True),
    'iec-60320-c22': lambda: iec_c19_family(male=True, chamfer=True),
    **iec_60309_types(male=True),
    'iec-60906-1': mirrored(lambda: iec_60906(2.25)),
    'nbr-14136-10a': mirrored(lambda: iec_60906(2.0)),
    'nbr-14136-20a': mirrored(lambda: iec_60906(2.4)),
    **nema_types(male=True),
    'ita-c': ita_c_plug,
    'ita-e': lambda: schuko_plug(strips=False, earth_hole=True),
    'ita-f': schuko_plug,
    'ita-ef': lambda: schuko_plug(earth_hole=True),
    'ita-g': mirrored(lambda: ita_g(socket=False)),
    'ita-h': mirrored(lambda: ita_h(socket=False)),
    'ita-i': mirrored(lambda: ita_i(socket=False)),
    'ita-j': mirrored(lambda: ita_j(socket=False)),
    'ita-k': mirrored(lambda: ita_k(socket=False)),
    'ita-l': ita_l_plug,
    'ita-m': mirrored(lambda: ita_m(socket=False)),
    'ita-n': mirrored(lambda: iec_60906(2.25)),
    'ita-o': mirrored(lambda: ita_o(socket=False)),
    # USB power ports are receptacles on the device
    'usb-a': usb_a,
    'usb-b': usb_b,
    'usb-c': usb_c,
    'usb-mini-a': usb_mini_a,
    'usb-mini-b': usb_mini_b,
    'usb-micro-a': usb_micro_a,
    'usb-micro-b': usb_micro_b,
    'usb-micro-ab': usb_micro_a,
    'usb-3-b': usb_3_b,
    'usb-3-micro-b': usb_3_micro_b,
    'molex-micro-fit-1x2': mirrored(lambda: molex_micro_fit(1, 2)),
    'molex-micro-fit-2x2': mirrored(lambda: molex_micro_fit(2, 2)),
    'molex-micro-fit-2x3': mirrored(lambda: molex_micro_fit(2, 3)),
    'molex-micro-fit-2x4': mirrored(lambda: molex_micro_fit(2, 4)),
    'saf-d-grid': saf_d_grid,
    'neutrik-powercon-20': powercon_20a,
    'neutrik-powercon-32': powercon_32a,
    'neutrik-powercon-true1': powercon_true1_inlet,
    'neutrik-powercon-true1-top': powercon_true1_inlet,
}


def write(directory, drawings):
    directory.mkdir(parents=True, exist_ok=True)
    expected = set()
    for value, func in drawings.items():
        result = func()
        drawing, mirror = result if isinstance(result, tuple) else (result, False)
        path = directory / f'{value}.svg'
        expected.add(path.name)
        content = drawing.svg(mirror=mirror)
        if not path.exists() or path.read_text() != content:
            path.write_text(content)
            print(f'Wrote {path}')
    # Remove drawings for types no longer defined
    for path in directory.glob('*.svg'):
        if path.name not in expected:
            path.unlink()
            print(f'Removed {path}')


def main():
    write(OUTPUT_DIR / 'power-outlet', POWER_OUTLETS)
    write(OUTPUT_DIR / 'power-port', POWER_PORTS)


if __name__ == '__main__':
    main()
