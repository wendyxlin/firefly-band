"""Printable parts for the Firefly bangle (stepped-cushion version), from the same numbers as the 3D model (mm).
Outputs: firefly_centerpiece_base.stl, firefly_centerpiece_dome.stl, firefly_wing.stl (print two), firefly_clasp_box.stl
Requires: pip install trimesh manifold3d shapely numpy"""
import numpy as np, trimesh
from shapely.geometry import Polygon
from trimesh.creation import cylinder, box, torus, extrude_polygon

M = dict(engine="manifold")
L, W, H = 28.0, 24.0, 11.0          # centerpiece envelope
N_SE = 4.0                           # superellipse exponent ("cushion" outline)
PILLOW = [(-5.5, .78), (-5.42, .86), (-5.22, .92), (-4.92, .955), (-4.6, .97), (-4.0, .985), (-3.0, .995),
          (-1.5, 1.0), (1.2, 1.0), (2.0, .99), (2.6, .97), (3.0, .94), (3.2, .9)]


def se_pts(hx, hz, n=N_SE, N=160):
    t = np.linspace(0, 2 * np.pi, N, endpoint=False); c, s = np.cos(t), np.sin(t)
    return np.stack([hx * np.sign(c) * np.abs(c) ** (2 / n), hz * np.sign(s) * np.abs(s) ** (2 / n)], 1)


def loft(rings):
    """rings: list of (y, hx, hz) -> closed watertight mesh (Y up)."""
    N = 160; V = []; F = []
    for y, hx, hz in rings:
        for x, z in se_pts(hx, hz, N=N): V.append([x, y, z])
    R = len(rings)
    for r in range(R - 1):
        for i in range(N):
            a, b, c, d = r * N + i, r * N + (i + 1) % N, (r + 1) * N + i, (r + 1) * N + (i + 1) % N
            F += [[a, b, c], [b, d, c]]
    bc = len(V); V.append([0, rings[0][0], 0]); tc = len(V); V.append([0, rings[-1][0], 0]); top = (R - 1) * N
    for i in range(N):
        F.append([bc, (i + 1) % N, i]); F.append([tc, top + i, top + (i + 1) % N])
    m = trimesh.Trimesh(np.array(V), np.array(F), process=True); m.fix_normals(); return m


def tier(w, d, h, y0):
    """flat superellipse slab, outer size w x d, from y0 to y0+h."""
    poly = Polygon(se_pts(w / 2, d / 2))
    m = extrude_polygon(poly, h)                      # extrudes along +Z
    m.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]))  # Z -> Y
    m.apply_translation([0, y0, 0]); return m


def ellipse_ring(ao, bo, ai, bi, h, y0):
    t = np.linspace(0, 2 * np.pi, 120, endpoint=False)
    poly = Polygon(np.stack([ao * np.cos(t), bo * np.sin(t)], 1), [np.stack([ai * np.cos(t), bi * np.sin(t)], 1)])
    m = extrude_polygon(poly, h); m.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0])); m.apply_translation([0, y0, 0]); return m


def ellipse_prism(a, b, h, y0):
    t = np.linspace(0, 2 * np.pi, 120, endpoint=False)
    m = extrude_polygon(Polygon(np.stack([a * np.cos(t), b * np.sin(t)], 1)), h)
    m.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0])); m.apply_translation([0, y0, 0]); return m


def rod(p, d, r, length):
    """cylinder of radius r centred at p, axis along direction d."""
    c = cylinder(radius=r, height=length, sections=32)
    c.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], d / np.linalg.norm(d))); c.apply_translation(p); return c


# ---------- centerpiece ----------
outer = loft([(y, L / 2 * k, W / 2 * k) for y, k in PILLOW])
inner = loft([(max(-4.5, min(2.2, y)), L / 2 * k - 1.0, W / 2 * k - 1.0) for y, k in PILLOW[2:-2]])
body = outer.union(tier(L - 3.0, W - 3.0, 1.4, 2.7), **M).union(tier(L - 5.4, W - 5.4, 1.6, 3.9), **M)
body = body.union(ellipse_ring(9.6, 7.6, 7.9, 5.9, 0.7, 5.5), **M)            # halo plate
body = body.union(ellipse_ring(7.75, 5.75, 7.5, 5.5, 1.5, 6.0), **M)          # bezel collar for the 15 x 11 stone
shell = body.difference(inner, **M)
shell = shell.difference(ellipse_prism(6.8, 4.8, 4.0, 3.0), **M)               # light window under the stone (0.7 mm ledge)
for i in range(26):                                                            # seats for 26 x 1.2 mm halo stones
    t = (i + .5) / 26 * 2 * np.pi
    shell = shell.difference(rod(np.array([np.cos(t) * 8.75, 6.1, np.sin(t) * 6.75]), np.array([0, 1, 0]), 0.62, 0.9), **M)
for sx in (-1, 1):
    shell = shell.difference(rod(np.array([sx * 12.2, 3.6, 0]), np.array([0, 1, 0]), 0.8, 4.0), **M)   # wing actuator holes
    # sockets for the band's twin wires (dia 2.4 mm), angled along the wire where it meets the body
    BA, BB, BY, POD_Y = 33.0, 25.5, 22.5, 51.95
    th = np.arccos(13.2 / BA); tang = np.array([-BA * np.sin(th) * sx, BB * np.cos(th), 0.0]); tang /= np.linalg.norm(tang)
    for z in (-2.0, 2.0):
        p = np.array([sx * 13.2, BY + BB * np.sin(th) - POD_Y, z])
        shell = shell.difference(rod(p + tang * 1.5, tang, 1.2, 6.0), **M)   # runs 4.5 mm into the body


def half(mesh, top):
    k = box([L + 20, 30, W + 20]); k.apply_translation([0, 15 if top else -15, 0]); return mesh.intersection(k, **M)


dome_part, base_part = half(shell, True), half(shell, False)

# ---------- wing button (leaf with a vein and a post for the switch) ----------
u = np.linspace(0, 1, 60)
upper = np.stack([-0.7 + 6.9 * u, 2.15 * np.sin(np.pi * u) ** 0.8], 1)
leaf = Polygon(np.vstack([upper, upper[::-1][1:-1] * [1, -1]]))
wing = extrude_polygon(leaf.buffer(0), 1.1)
vein = rod(np.array([2.9, 0, 1.15]), np.array([1, 0, 0]), 0.16, 4.9)
post = cylinder(radius=0.7, height=1.6, sections=24); post.apply_translation([0, 0, -0.8])
wing = wing.union(vein, **M).union(post, **M)

# ---------- capsule clasp: 35 x 8 x 14, hollow, wire sockets in both ends ----------
def rounded_block(l, h, w, r, b):
    pts = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            for sy in (-1, 1):
                t = torus(major_radius=max(r - b, 0.01), minor_radius=b, major_sections=24, minor_sections=12)
                t.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
                t.apply_translation([sx * (l / 2 - r), sy * (h / 2 - b), sz * (w / 2 - r)]); pts.append(t.vertices)
    return trimesh.convex.convex_hull(np.vstack(pts))


cL, cH, cW = 35.0, 8.0, 14.0
cb = rounded_block(cL, cH, cW, 6.8, 2.6).difference(rounded_block(cL - 2, cH - 2, cW - 2, 5.8, 1.6), **M)
for sx in (-1, 1):
    th = np.arccos(16.6 / 33.0); tang = np.array([-33 * np.sin(-th) * sx, 25.5 * np.cos(-th), 0.0]); tang /= np.linalg.norm(tang)
    for z in (-2.0, 2.0):
        cb = cb.difference(rod(np.array([sx * 16.6, 3.6, z]) - tang * 1.5, tang, 1.2, 6.0), **M)
for dx in (-2.5, 2.5):
    hole = cylinder(radius=1.0, height=4, sections=24); hole.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])); hole.apply_translation([dx, -cH / 2, 0]); cb = cb.difference(hole, **M)


def export(mesh, name, flip=False, yup=True):
    m = mesh.copy()
    if yup: m.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]))   # Y-up -> Z-up for slicers
    if flip: m.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
    m.apply_translation([0, 0, -m.bounds[0][2]])
    m.export(name)
    print(name, "extents", np.round(m.extents, 2), "watertight", m.is_watertight, "· resin ~", round(m.volume / 1000 * 1.15, 2), "g")


export(base_part, "firefly_centerpiece_base.stl")
export(dome_part, "firefly_centerpiece_dome.stl", flip=True)
export(wing, "firefly_wing.stl", yup=False)
export(cb, "firefly_clasp_box.stl")
