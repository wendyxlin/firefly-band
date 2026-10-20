"""Generate printable STL shells for the Firefly pod from the page's dimensions (mm)."""
import numpy as np, trimesh
from trimesh.creation import extrude_polygon, cylinder, box
from shapely.geometry import Polygon, box as sbox

L, W, H = 44.0, 24.0, 11.0      # outer pod
R = 9.0                          # corner radius
WALL, FLOOR = 1.2, 1.2           # wall / floor thickness
HALF = H / 2                     # each shell is 5.5 tall

def rrect(l, w, r):
    return sbox(-l/2, -w/2, l/2, w/2).buffer(r, join_style=1).buffer(-r, join_style=1) if False else \
        sbox(-l/2 + r, -w/2 + r, l/2 - r, w/2 - r).buffer(r, resolution=24)

def shell_half(lid: bool):
    outer = extrude_polygon(rrect(L, W, R), HALF)
    inner = extrude_polygon(rrect(L - 2*WALL, W - 2*WALL, R - WALL), HALF - FLOOR)
    inner.apply_translation([0, 0, FLOOR])            # cavity opens at the parting face (z = HALF)
    m = outer.difference(inner)
    if lid:
        # LED diffuser slot 30 x 5 through the floor (which is the top of the pod once flipped)
        slot = box([30, 5, FLOOR + 1]); slot.apply_translation([0, 0, FLOOR/2])
        m = m.difference(slot)
        # button openings 7 x 3 on the +Y long wall at x = +/-9, centred on the parting line
        for x in (-9, 9):
            cut = box([7, WALL + 1, 3]); cut.apply_translation([x, W/2 - WALL/2, HALF - 1.5])
            m = m.difference(cut)
    else:
        # pogo pin holes, 2 mm, 5 mm apart in the floor
        for x in (-2.5, 2.5):
            hole = cylinder(radius=1.0, height=FLOOR + 1, sections=32); hole.apply_translation([x, 0, FLOOR/2])
            m = m.difference(hole)
        # cord channel 5.5 wide x 2.5 deep across the underside, along Y (across the pod width)
        ch = box([5.5, W + 2, 2.5]); ch.apply_translation([0, 0, -1.25 + 1.25])  # from z=0 to z=2.5? keep it in the floor only
        ch = box([5.5, W + 2, 1.0]); ch.apply_translation([0, 0, 0.5])
        for x in (-16, 16):
            c2 = ch.copy(); c2.apply_translation([x, 0, 0]); m = m.difference(c2)
        # button openings' lower halves on the same wall
        for x in (-9, 9):
            cut = box([7, WALL + 1, 3]); cut.apply_translation([x, W/2 - WALL/2, HALF - 1.5])
            m = m.difference(cut)
    # O-ring groove: 1.0 wide x 0.6 deep ring in the parting face, mid-wall
    groove_outer = extrude_polygon(rrect(L - WALL + 0.9, W - WALL + 0.9, R - WALL/2 + 0.45), 0.6)
    groove_inner = extrude_polygon(rrect(L - WALL - 0.9, W - WALL - 0.9, R - WALL/2 - 0.45), 0.6)
    groove = groove_outer.difference(groove_inner); groove.apply_translation([0, 0, HALF - 0.6])
    if lid:
        m = m.difference(groove)
    else:  # the lower half gets a matching 0.4 mm lip instead
        lip = groove.copy(); lip.apply_translation([0, 0, 0.6 - 0.4])
        m = m.union(lip)
    return m

bottom = shell_half(lid=False)
lid = shell_half(lid=True)
for name, m in (("firefly_shell_bottom.stl", bottom), ("firefly_shell_lid.stl", lid)):
    assert m.is_watertight, name
    m.export(name)
    print(name, "extents", np.round(m.extents, 2), "volume mm3", round(m.volume, 1), "watertight", m.is_watertight)

# an assembled preview: lid flipped onto the bottom, plus parts as simple blocks, for a quick look
lid2 = lid.copy(); lid2.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0])); lid2.apply_translation([0, 0, H])
parts = []
def block(sz, pos, color):
    b = box(sz); b.apply_translation(pos); b.visual.face_colors = color; return b
parts.append(block([21, 17.8, 3], [-11, 0, 1.2 + 1.5], [46, 125, 91, 255]))        # SX1262
parts.append(block([21, 17.8, 3.5], [-11, 0, 1.2 + 1.5 + 3 + 1.5 + 1.75], [29, 77, 143, 255]))  # XIAO
parts.append(block([25, 20, 4], [10, 0, 1.2 + 2], [138, 143, 168, 255]))              # battery
mo = cylinder(radius=5, height=2.7); mo.apply_translation([10, 0, 1.2 + 4 + 1.35]); mo.visual.face_colors = [184, 178, 196, 255]; parts.append(mo)
scene = trimesh.Scene([bottom, lid2] + parts)
scene.export("firefly_pod_assembly.glb")
print("assembly exported")
