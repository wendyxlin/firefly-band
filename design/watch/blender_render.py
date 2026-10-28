"""Path-traced 'product photo' renders of the Firefly watch in Blender Cycles.
Usage: bvenv/bin/python render.py <shot> [width height samples]"""
import bpy, math, sys, os
from mathutils import Vector

D = os.path.dirname(os.path.abspath(__file__))
shot = sys.argv[1] if len(sys.argv) > 1 else 'hero'
W = int(sys.argv[2]) if len(sys.argv) > 2 else 1500
H = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
SAMPLES = int(sys.argv[4]) if len(sys.argv) > 4 else 128

# shot: three.js view (theta, phi, radius mm, target mm, fov deg), finish, strap, dial state, stone tone, f-stop
SHOTS = {
    'hero':  dict(view=(0.95, 1.10, 200, (0, -8, 0), 16), finish='yellow', strap='black', state='idle', stone='warm', fstop=11.0),
    'find':  dict(view=(1.5708 + 0.25, 0.55, 120, (0, 8, 0), 19), finish='yellow', strap='black', state='find', stone='warm', fstop=8.0),
    'crown': dict(view=(2.75, 1.20, 88, (0, 5, -14), 19), finish='yellow', strap='black', state='idle', stone='warm', fstop=8.0, focus=(0, 5, -17)),
    'rose':  dict(view=(0.70, 1.12, 195, (0, -8, 0), 16), finish='rose', strap='blush', state='idle', stone='light', fstop=11.0),
    'sos':   dict(view=(1.5708 - 0.3, 0.6, 120, (0, 8, 0), 19), finish='steel', strap='black', state='sos', stone='dark', fstop=8.0),
}
cfg = SHOTS[shot]

# ---------------- scene ----------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
cy = scene.cycles
cy.device = 'CPU'; cy.samples = SAMPLES; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.02
cy.use_denoising = True
try: cy.denoiser = 'OPENIMAGEDENOISE'
except Exception: pass
cy.max_bounces = 10; cy.glossy_bounces = 6; cy.transmission_bounces = 10; cy.diffuse_bounces = 3
cy.caustics_reflective = False; cy.caustics_refractive = False; cy.blur_glossy = 0.6
scene.render.resolution_x = W; scene.render.resolution_y = H; scene.render.resolution_percentage = 100
scene.render.film_transparent = False
try:
    scene.view_settings.view_transform = 'AgX'
    for look in ('AgX - Medium High Contrast', 'Medium High Contrast'):
        try: scene.view_settings.look = look; break
        except Exception: pass
except Exception: pass
scene.render.image_settings.file_format = 'PNG'

bpy.ops.wm.obj_import(filepath=os.path.join(D, 'watch.obj'), forward_axis='NEGATIVE_Z', up_axis='Y')
objs = [o for o in scene.objects if o.type == 'MESH']
for o in objs:
    o.scale = (0.001, 0.001, 0.001)
bpy.context.view_layer.update()


def t2b(x, y, z):  # three.js mm (Y up) -> Blender metres (Z up)
    return Vector((x / 1000, -z / 1000, y / 1000))


# ---------------- materials ----------------
def principled(name):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial'); b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    nt.links.new(b.outputs['BSDF'], out.inputs['Surface'])
    return m, nt, b, out


def setin(b, key, val):
    if key in b.inputs: b.inputs[key].default_value = val


FIN = {'yellow': (1.0, 0.74, 0.38), 'rose': (0.98, 0.64, 0.52), 'steel': (0.80, 0.80, 0.81)}
fc = FIN[cfg['finish']]
for nm, rough in (('gold', 0.09), ('gold_satin', 0.28), ('gold_hands', 0.05)):
    m, nt, b, out = principled(nm)
    setin(b, 'Base Color', (*fc, 1)); setin(b, 'Metallic', 1.0); setin(b, 'Roughness', rough)
    if nm == 'gold_satin': setin(b, 'Anisotropic', 0.4)

m, nt, b, out = principled('steel_brushed')
setin(b, 'Base Color', (0.78, 0.78, 0.79, 1)); setin(b, 'Metallic', 1.0); setin(b, 'Roughness', 0.32); setin(b, 'Anisotropic', 0.6)

m, nt, b, out = principled('enamel_red')
setin(b, 'Base Color', (0.42, 0.015, 0.03, 1)); setin(b, 'Roughness', 0.2); setin(b, 'Coat Weight', 1.0); setin(b, 'Coat Roughness', 0.03)

m, nt, b, out = principled('opal')    # opal cabochon on the crown: milky, glowing from within
setin(b, 'Base Color', (0.86, 0.88, 0.92, 1)); setin(b, 'Roughness', 0.15); setin(b, 'Subsurface Weight', 0.6)
setin(b, 'Subsurface Scale', 0.002); setin(b, 'Coat Weight', 1.0); setin(b, 'Coat Roughness', 0.02)
setin(b, 'Thin Film Thickness', 380.0); setin(b, 'Thin Film IOR', 1.45)

# mother-of-pearl dial: the dial artwork as base colour, lacquer coat, thin-film iridescence
m, nt, b, out = principled('dial')
tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = bpy.data.images.load(os.path.join(D, 'dial.png'))
nt.links.new(tex.outputs['Color'], b.inputs['Base Color'])
setin(b, 'Roughness', 0.22); setin(b, 'Coat Weight', 1.0); setin(b, 'Coat Roughness', 0.04)
setin(b, 'Thin Film Thickness', 520.0); setin(b, 'Thin Film IOR', 1.33); setin(b, 'Sheen Weight', 0.25)
setin(b, 'Subsurface Weight', 0.15); setin(b, 'Subsurface Scale', 0.001)

# sapphire crystal: clear glass that does not black out the shadow it casts on the dial
m, nt, b, out = principled('sapphire')
setin(b, 'Base Color', (1, 1, 1, 1)); setin(b, 'Roughness', 0.0); setin(b, 'IOR', 1.77); setin(b, 'Transmission Weight', 1.0)
lp = nt.nodes.new('ShaderNodeLightPath'); tr = nt.nodes.new('ShaderNodeBsdfTransparent'); mix = nt.nodes.new('ShaderNodeMixShader')
nt.links.new(lp.outputs['Is Shadow Ray'], mix.inputs['Fac']); nt.links.new(b.outputs['BSDF'], mix.inputs[1]); nt.links.new(tr.outputs['BSDF'], mix.inputs[2])
nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])

# leather: fine pebbled grain from Voronoi + noise bump, soft sheen
STRAP = {'black': (0.012, 0.011, 0.012), 'cognac': (0.20, 0.07, 0.025), 'blush': (0.62, 0.36, 0.30)}
m, nt, b, out = principled('leather')
setin(b, 'Base Color', (*STRAP[cfg['strap']], 1)); setin(b, 'Roughness', 0.62); setin(b, 'Sheen Weight', 0.06); setin(b, 'Coat Weight', 0.05); setin(b, 'Coat Roughness', 0.5)
tc = nt.nodes.new('ShaderNodeTexCoord'); vor = nt.nodes.new('ShaderNodeTexVoronoi'); vor.inputs['Scale'].default_value = 1.6
noi = nt.nodes.new('ShaderNodeTexNoise'); noi.inputs['Scale'].default_value = 0.6; noi.inputs['Detail'].default_value = 4
bm = nt.nodes.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = 0.18; bm.inputs['Distance'].default_value = 0.05
add_ = nt.nodes.new('ShaderNodeMath'); add_.operation = 'ADD'
nt.links.new(tc.outputs['Object'], vor.inputs['Vector']); nt.links.new(tc.outputs['Object'], noi.inputs['Vector'])
nt.links.new(vor.outputs['Distance'], add_.inputs[0]); nt.links.new(noi.outputs['Fac'], add_.inputs[1]); nt.links.new(add_.outputs['Value'], bm.inputs['Height'])
nt.links.new(bm.outputs['Normal'], b.inputs['Normal'])

m, nt, b, out = principled('thread')
setin(b, 'Base Color', (0.78, 0.70, 0.56, 1)); setin(b, 'Roughness', 0.75); setin(b, 'Sheen Weight', 0.5)

# LED glows: soft emissive halos under the hour markers (state-dependent)
def glow_strength(h):
    if cfg['state'] == 'find':
        d = min(abs(h - 2), 12 - abs(h - 2)); return (1.0, 0.30, 0.02), (22.0 if d == 0 else 4.0 if d == 1 else 0.0)
    if cfg['state'] == 'sos':
        return (1.0, 0.03, 0.05), 14.0
    return (1, 1, 1), 0.0
for h in range(12):
    col, s = glow_strength(h)
    m, nt, b, out = principled(f'glow_{h}')
    for n in list(nt.nodes):
        if n.type == 'BSDF_PRINCIPLED': nt.nodes.remove(n)
    uv = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Location'].default_value = (-1.0, -1.0, 0); mp.inputs['Scale'].default_value = (2.0, 2.0, 1.0)
    gr = nt.nodes.new('ShaderNodeTexGradient'); gr.gradient_type = 'SPHERICAL'
    sc = nt.nodes.new('ShaderNodeMath'); sc.operation = 'MULTIPLY'; sc.inputs[1].default_value = 1.0
    pw = nt.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 2.2
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*col, 1); em.inputs['Strength'].default_value = s
    trn = nt.nodes.new('ShaderNodeBsdfTransparent'); mx = nt.nodes.new('ShaderNodeMixShader'); clamp = nt.nodes.new('ShaderNodeMath'); clamp.operation = 'MINIMUM'; clamp.inputs[1].default_value = 1.0
    nt.links.new(uv.outputs['UV'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], gr.inputs['Vector'])
    nt.links.new(gr.outputs['Fac'], sc.inputs[0]); nt.links.new(sc.outputs['Value'], pw.inputs[0]); nt.links.new(pw.outputs['Value'], clamp.inputs[0])
    nt.links.new(clamp.outputs['Value'], mx.inputs['Fac']); nt.links.new(trn.outputs['BSDF'], mx.inputs[1]); nt.links.new(em.outputs['Emission'], mx.inputs[2])
    nt.links.new(mx.outputs['Shader'], out.inputs['Surface'])
    if s == 0:
        for o in objs:
            if o.active_material and o.active_material.name == f'glow_{h}': o.hide_render = True

# ---------------- set: stone surface, studio lights, backdrop ----------------
bpy.ops.mesh.primitive_plane_add(size=3.0, location=(0, 0, -0.0500))
surf = bpy.context.active_object
m, nt, b, out = principled('stone'); surf.data.materials.append(m)
TONES = {'warm': ((0.50, 0.44, 0.36), (0.66, 0.60, 0.51)), 'light': ((0.72, 0.68, 0.62), (0.84, 0.80, 0.75)), 'dark': ((0.06, 0.06, 0.065), (0.13, 0.13, 0.14))}
c1, c2 = TONES[cfg['stone']]
tc = nt.nodes.new('ShaderNodeTexCoord'); noi = nt.nodes.new('ShaderNodeTexNoise'); noi.inputs['Scale'].default_value = 18; noi.inputs['Detail'].default_value = 12; noi.inputs['Roughness'].default_value = 0.62
wav = nt.nodes.new('ShaderNodeTexWave'); wav.inputs['Scale'].default_value = 3.5; wav.inputs['Distortion'].default_value = 9; wav.inputs['Detail'].default_value = 6
ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color = (*c1, 1); ramp.color_ramp.elements[1].color = (*c2, 1)
mixc = nt.nodes.new('ShaderNodeMix'); mixc.data_type = 'RGBA'; mixc.blend_type = 'MULTIPLY'; mixc.inputs['Factor'].default_value = 0.18
nt.links.new(tc.outputs['Object'], noi.inputs['Vector']); nt.links.new(tc.outputs['Object'], wav.inputs['Vector'])
nt.links.new(noi.outputs['Fac'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], mixc.inputs['A']); nt.links.new(wav.outputs['Color'], mixc.inputs['B'])
nt.links.new(mixc.outputs['Result'], b.inputs['Base Color'])
setin(b, 'Roughness', 0.45 if cfg['stone'] != 'dark' else 0.3); setin(b, 'Coat Weight', 0.15 if cfg['stone'] != 'dark' else 0.4)
bmp = nt.nodes.new('ShaderNodeBump'); bmp.inputs['Strength'].default_value = 0.04; nt.links.new(noi.outputs['Fac'], bmp.inputs['Height']); nt.links.new(bmp.outputs['Normal'], b.inputs['Normal'])

def area(name, loc, size, power, color=(1, 1, 1), shape='RECTANGLE', size_y=None, aim=(0, 0, 0)):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = power; ld.color = color; ld.shape = shape; ld.size = size
    if size_y is not None: ld.size_y = size_y
    ob = bpy.data.objects.new(name, ld); scene.collection.objects.link(ob); ob.location = loc
    ob.rotation_euler = (Vector(aim) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob
area('key', (0.30, -0.25, 0.42), 0.32, 2.6, (1.0, 0.94, 0.86), shape='DISK')
area('top', (0.0, 0.05, 0.55), 0.6, 1.8, (1, 1, 1), shape='ELLIPSE', size_y=0.45)
area('rim', (-0.28, 0.30, 0.16), 0.5, 1.6, (0.86, 0.90, 1.0), size_y=0.06)
area('fill', (-0.30, -0.22, 0.10), 0.3, 0.35, (1.0, 0.97, 0.93))

world = bpy.data.worlds.new('studio'); scene.world = world; world.use_nodes = True
wn = world.node_tree; [wn.nodes.remove(n) for n in list(wn.nodes)]
wo = wn.nodes.new('ShaderNodeOutputWorld'); lpw = wn.nodes.new('ShaderNodeLightPath')
bgc = wn.nodes.new('ShaderNodeBackground'); bgc.inputs['Color'].default_value = (*([c * 0.30 for c in c1]), 1); bgc.inputs['Strength'].default_value = 1.0
bgr = wn.nodes.new('ShaderNodeBackground'); bgr.inputs['Color'].default_value = (0.03, 0.028, 0.026, 1); bgr.inputs['Strength'].default_value = 1.0
mw = wn.nodes.new('ShaderNodeMixShader')
wn.links.new(lpw.outputs['Is Camera Ray'], mw.inputs['Fac']); wn.links.new(bgr.outputs['Background'], mw.inputs[1]); wn.links.new(bgc.outputs['Background'], mw.inputs[2]); wn.links.new(mw.outputs['Shader'], wo.inputs['Surface'])

# ---------------- camera: macro lens with shallow depth of field ----------------
th, ph, r, tg, fov = cfg['view']
tgt = Vector(tg)
pos_t = (tg[0] + r * math.sin(ph) * math.sin(th), tg[1] + r * math.cos(ph), tg[2] + r * math.sin(ph) * math.cos(th))
camd = bpy.data.cameras.new('cam'); camd.sensor_fit = 'VERTICAL'; camd.sensor_height = 24
camd.lens = (24 / 2) / math.tan(math.radians(fov) / 2); camd.clip_start = 0.005; camd.clip_end = 20
camd.dof.use_dof = True; camd.dof.aperture_fstop = cfg['fstop']
cam = bpy.data.objects.new('cam', camd); scene.collection.objects.link(cam); scene.camera = cam
cam.location = t2b(*pos_t); tb = t2b(*tg)
cam.rotation_euler = (tb - cam.location).to_track_quat('-Z', 'Y').to_euler()
fp = t2b(*cfg.get('focus', (0, 9.5, 0))); camd.dof.focus_distance = (fp - cam.location).length

scene.render.filepath = os.path.join(D, f'out_{shot}.png')
bpy.ops.render.render(write_still=True)
print('rendered', scene.render.filepath)
