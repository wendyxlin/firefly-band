"""Path-traced 'product photo' renders of the Firefly v2 bracelet in Blender Cycles.
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
    'hero':    dict(view=(0.55, 1.02, 205, (0, -15, 0), 16), finish='gold', state='idle', stone='light', fstop=11.0, focus=(0, 5, 0)),
    'buttons': dict(view=(0.30, 0.66, 82, (0, 3.5, 0), 19), finish='gold', state='idle', stone='light', fstop=9.0, focus=(0, 6, 0)),
    'find':    dict(view=(-0.25, 0.78, 118, (0, -1, 0), 19), finish='gold', state='find', stone='warm', fstop=8.0, focus=(0, 6, 0)),
    'home':    dict(view=(0.45, 0.80, 118, (0, -1, 0), 19), finish='silver', state='home', stone='light', fstop=8.0, focus=(0, 6, 0)),
    'sos':     dict(view=(-0.40, 0.85, 118, (0, -1, 0), 19), finish='black', state='sos', stone='dark', fstop=8.0, focus=(0, 6, 0)),
    'rose':    dict(view=(0.85, 1.08, 205, (0, -15, 0), 16), finish='rose', state='idle', stone='light', fstop=11.0, focus=(0, 5, 0)),
    'silver':  dict(view=(-0.6, 1.05, 205, (0, -15, 0), 16), finish='silver', state='idle', stone='light', fstop=11.0, focus=(0, 5, 0)),
    'black':   dict(view=(0.55, 1.05, 205, (0, -15, 0), 16), finish='black', state='idle', stone='light', fstop=11.0, focus=(0, 5, 0)),
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

bpy.ops.wm.obj_import(filepath=os.path.join(D, 'bracelet.obj'), forward_axis='NEGATIVE_Z', up_axis='Y')
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


FIN = {'gold': ((1.0, 0.74, 0.38), 1.0, 0.08), 'rose': ((0.98, 0.64, 0.52), 1.0, 0.08),
       'silver': ((0.86, 0.86, 0.87), 1.0, 0.07), 'black': ((0.035, 0.035, 0.04), 0.9, 0.16)}
fc, met, rough0 = FIN[cfg['finish']]
for nm, rough in (('gold', rough0), ('gold_satin', rough0 + 0.22)):
    m, nt, b, out = principled(nm)
    setin(b, 'Base Color', (*fc, 1)); setin(b, 'Metallic', met); setin(b, 'Roughness', rough)
    if cfg['finish'] == 'black': setin(b, 'Coat Weight', 0.6); setin(b, 'Coat Roughness', 0.05)
    if nm == 'gold_satin': setin(b, 'Anisotropic', 0.5)
m, nt, b, out = principled('engrave')
setin(b, 'Base Color', (*[c * 0.45 for c in fc], 1) if cfg['finish'] != 'black' else (0.35, 0.35, 0.37, 1)); setin(b, 'Metallic', 1.0); setin(b, 'Roughness', 0.5)
m, nt, b, out = principled('ceramic')
setin(b, 'Base Color', (0.86, 0.82, 0.78, 1)); setin(b, 'Roughness', 0.3); setin(b, 'Coat Weight', 0.5)

LED = {'find': ((1.0, 0.45, 0.60), 60.0), 'home': ((0.12, 1.0, 0.42), 45.0), 'sos': ((1.0, 0.03, 0.05), 55.0), 'idle': ((1, 1, 1), 0.0)}
lc, ls = LED[cfg['state']]
m, nt, b, out = principled('led_window')     # the sapphire pinhole over the LED
setin(b, 'Base Color', (0.95, 0.93, 0.9, 1)); setin(b, 'Roughness', 0.05); setin(b, 'Coat Weight', 1.0)
if ls > 0: setin(b, 'Emission Color', (*lc, 1)); setin(b, 'Emission Strength', ls * 0.6)
m, nt, b, out = principled('glow')           # soft halo of light around the pinhole
for n in list(nt.nodes):
    if n.type == 'BSDF_PRINCIPLED': nt.nodes.remove(n)
uv = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Location'].default_value = (-1.0, -1.0, 0); mp.inputs['Scale'].default_value = (2.0, 2.0, 1.0)
gr = nt.nodes.new('ShaderNodeTexGradient'); gr.gradient_type = 'SPHERICAL'
pw = nt.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 3.0
em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*lc, 1); em.inputs['Strength'].default_value = ls * 0.35
trn = nt.nodes.new('ShaderNodeBsdfTransparent'); mx = nt.nodes.new('ShaderNodeMixShader')
nt.links.new(uv.outputs['UV'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], gr.inputs['Vector'])
nt.links.new(gr.outputs['Fac'], pw.inputs[0]); nt.links.new(pw.outputs['Value'], mx.inputs['Fac'])
nt.links.new(trn.outputs['BSDF'], mx.inputs[1]); nt.links.new(em.outputs['Emission'], mx.inputs[2]); nt.links.new(mx.outputs['Shader'], out.inputs['Surface'])
if ls == 0:
    for o in objs:
        if o.active_material and o.active_material.name == 'glow': o.hide_render = True

# ---------------- set: stone surface, studio lights, backdrop ----------------
bpy.ops.mesh.primitive_plane_add(size=3.0, location=(0, 0, -0.04935))
surf = bpy.context.active_object
m, nt, b, out = principled('stone'); surf.data.materials.append(m)
TONES = {'warm': ((0.56, 0.42, 0.38), (0.72, 0.58, 0.54)), 'light': ((0.80, 0.70, 0.66), (0.90, 0.83, 0.79)), 'dark': ((0.06, 0.06, 0.065), (0.13, 0.13, 0.14))}
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
