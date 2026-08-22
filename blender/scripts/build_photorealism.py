import bpy
import math
import os
import time
from mathutils import Vector

ROOT = r"C:\Users\josue\Documents\Codex\coa-website"
BLEND = os.path.join(ROOT, "blender", "puerto-nuevo-workshop.blend")
RENDERS = os.path.join(ROOT, "blender", "renders")
TARGET = os.path.join(ROOT, "art-direction", "puerto-nuevo-blender-art-target-v2.png")
os.makedirs(RENDERS, exist_ok=True)


def clear_nodes(mat):
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    return nt, nt.nodes, nt.links


def output_principled(mat):
    nt, n, l = clear_nodes(mat)
    out = n.new("ShaderNodeOutputMaterial")
    out.location = (760, 20)
    bsdf = n.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (480, 20)
    l.new(bsdf.outputs[0], out.inputs[0])
    return nt, n, l, bsdf


def procedural_surface(name, base, rough=0.7, metallic=0.0, macro=2.2, medium=16.0,
                       micro=85.0, color_strength=0.08, bump=0.12):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    nt, n, l, bsdf = output_principled(mat)
    tex = n.new("ShaderNodeTexCoord")
    sep = n.new("ShaderNodeSeparateXYZ")
    noise1 = n.new("ShaderNodeTexNoise"); noise1.inputs[2].default_value = macro; noise1.inputs[3].default_value = 4.2; noise1.inputs[4].default_value = 0.62
    noise2 = n.new("ShaderNodeTexNoise"); noise2.inputs[2].default_value = medium; noise2.inputs[3].default_value = 5.0; noise2.inputs[4].default_value = 0.56
    noise3 = n.new("ShaderNodeTexNoise"); noise3.inputs[2].default_value = micro; noise3.inputs[3].default_value = 2.5; noise3.inputs[4].default_value = 0.48
    mixc = n.new("ShaderNodeMixRGB"); mixc.blend_type = 'MULTIPLY'; mixc.inputs[0].default_value = color_strength
    mixr = n.new("ShaderNodeMixRGB"); mixr.blend_type = 'MULTIPLY'; mixr.inputs[0].default_value = 0.35
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.18
    ramp.color_ramp.elements[0].color = tuple(max(0.004, c*(1-color_strength*1.7)) for c in base) + (1,)
    ramp.color_ramp.elements[1].position = 0.82
    ramp.color_ramp.elements[1].color = tuple(min(0.92, c*(1+color_strength)) for c in base) + (1,)
    bumpn = n.new("ShaderNodeBump"); bumpn.inputs['Strength'].default_value = bump; bumpn.inputs['Distance'].default_value = 0.035
    l.new(tex.outputs['Generated'], noise1.inputs['Vector']); l.new(tex.outputs['Generated'], noise2.inputs['Vector']); l.new(tex.outputs['Generated'], noise3.inputs['Vector'])
    l.new(noise1.outputs['Fac'], ramp.inputs[0]); l.new(ramp.outputs[0], mixc.inputs[1]); l.new(noise2.outputs['Color'], mixc.inputs[2])
    l.new(noise2.outputs['Fac'], mixr.inputs[1]); l.new(noise3.outputs['Fac'], mixr.inputs[2])
    l.new(mixc.outputs[0], bsdf.inputs['Base Color']); l.new(mixr.outputs[0], bsdf.inputs['Roughness']); l.new(noise3.outputs['Fac'], bumpn.inputs['Height']); l.new(bumpn.outputs[0], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metallic
    return mat


def wood(name, lightness=1.0, grain_scale=7.0, rough=0.52):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    nt, n, l, bsdf = output_principled(mat)
    tc = n.new("ShaderNodeTexCoord")
    mapping = n.new("ShaderNodeMapping")
    mapping.inputs['Scale'].default_value = (grain_scale*.18, grain_scale*.055, grain_scale*.07)
    wave = n.new("ShaderNodeTexWave"); wave.wave_type='BANDS'; wave.bands_direction='X'; wave.inputs['Scale'].default_value=2.0; wave.inputs['Distortion'].default_value=4.2; wave.inputs['Detail'].default_value=3.0; wave.inputs['Detail Scale'].default_value=1.7
    macro = n.new("ShaderNodeTexNoise"); macro.inputs[2].default_value=2.5; macro.inputs[3].default_value=5.0; macro.inputs[4].default_value=0.7
    pores = n.new("ShaderNodeTexNoise"); pores.inputs[2].default_value=72; pores.inputs[3].default_value=2.2; pores.inputs[4].default_value=0.55
    mix = n.new("ShaderNodeMixRGB"); mix.blend_type='MULTIPLY'; mix.inputs[0].default_value=.14
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color=(0.105*lightness,0.038*lightness,0.013*lightness,1)
    ramp.color_ramp.elements[0].position=.12
    ramp.color_ramp.elements[1].color=(0.245*lightness,0.092*lightness,0.030*lightness,1)
    ramp.color_ramp.elements[1].position=.88
    roughmix=n.new("ShaderNodeMapRange"); roughmix.inputs['From Min'].default_value=0; roughmix.inputs['From Max'].default_value=1; roughmix.inputs['To Min'].default_value=rough-.11; roughmix.inputs['To Max'].default_value=rough+.14
    bumpn=n.new("ShaderNodeBump"); bumpn.inputs['Strength'].default_value=.17; bumpn.inputs['Distance'].default_value=.018
    l.new(tc.outputs['Generated'],mapping.inputs[0]); l.new(mapping.outputs[0],wave.inputs[0]); l.new(mapping.outputs[0],macro.inputs[0]); l.new(mapping.outputs[0],pores.inputs[0])
    l.new(wave.outputs['Color'],ramp.inputs[0]); l.new(ramp.outputs[0],mix.inputs[1]); l.new(macro.outputs['Color'],mix.inputs[2]); l.new(mix.outputs[0],bsdf.inputs['Base Color'])
    l.new(pores.outputs['Fac'],roughmix.inputs['Value']); l.new(roughmix.outputs[0],bsdf.inputs['Roughness']); l.new(pores.outputs['Fac'],bumpn.inputs['Height']); l.new(bumpn.outputs[0],bsdf.inputs['Normal'])
    bsdf.inputs['Coat Weight'].default_value=.08; bsdf.inputs['Coat Roughness'].default_value=.36
    return mat


def metal(name, base, metallic=.86, rough=.42, painted=False):
    mat=procedural_surface(name,base,rough,metallic,macro=3.4,medium=24,micro=120,color_strength=.10,bump=.09)
    bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    if painted:
        bsdf.inputs['Metallic'].default_value=.58
        bsdf.inputs['Coat Weight'].default_value=.12
        bsdf.inputs['Coat Roughness'].default_value=.32
    return mat


def glass(name, base, rough=.12, transmission=.72, ior=1.48):
    mat=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    nt,n,l,bsdf=output_principled(mat)
    noise=n.new('ShaderNodeTexNoise'); noise.inputs[2].default_value=18; noise.inputs[3].default_value=3; noise.inputs[4].default_value=.45
    tc=n.new('ShaderNodeTexCoord'); bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.025; bump.inputs['Distance'].default_value=.008
    l.new(tc.outputs['Generated'],noise.inputs[0]); l.new(noise.outputs['Fac'],bump.inputs['Height']); l.new(bump.outputs[0],bsdf.inputs['Normal'])
    bsdf.inputs['Base Color'].default_value=(*base,1); bsdf.inputs['Roughness'].default_value=rough; bsdf.inputs['Transmission Weight'].default_value=transmission*.35; bsdf.inputs['IOR'].default_value=ior; bsdf.inputs['Coat Weight'].default_value=.18
    bsdf.inputs['Alpha'].default_value=.16 if name=='MAT_Window_Glass' else .42
    try: mat.surface_render_method='DITHERED'
    except Exception: pass
    return mat


def acetate(name, base, transmission=.10, rough=.28):
    mat=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    nt,n,l,bsdf=output_principled(mat)
    tc=n.new('ShaderNodeTexCoord'); noise=n.new('ShaderNodeTexNoise'); noise.noise_dimensions='3D'; noise.inputs[2].default_value=5.5; noise.inputs[3].default_value=8; noise.inputs[4].default_value=.72; noise.inputs[5].default_value=.35
    ramp=n.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=tuple(max(.003,c*.30) for c in base)+(1,); ramp.color_ramp.elements[0].position=.26; ramp.color_ramp.elements[1].color=tuple(min(.78,c*1.45+.015) for c in base)+(1,); ramp.color_ramp.elements[1].position=.74
    micro=n.new('ShaderNodeTexNoise'); micro.inputs[2].default_value=92; micro.inputs[3].default_value=2.5
    bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.035; bump.inputs['Distance'].default_value=.007
    l.new(tc.outputs['Generated'],noise.inputs[0]); l.new(noise.outputs['Fac'],ramp.inputs[0]); l.new(ramp.outputs[0],bsdf.inputs['Base Color']); l.new(tc.outputs['Generated'],micro.inputs[0]); l.new(micro.outputs['Fac'],bump.inputs['Height']); l.new(bump.outputs[0],bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value=rough; bsdf.inputs['Transmission Weight'].default_value=transmission; bsdf.inputs['IOR'].default_value=1.49; bsdf.inputs['Coat Weight'].default_value=.38; bsdf.inputs['Coat Roughness'].default_value=.14
    return mat


def assign_by_name(fragment, mat):
    for obj in bpy.data.objects:
        if fragment in obj.name and obj.type in {'MESH','CURVE'}:
            if obj.data.materials:
                obj.data.materials[0]=mat
            else:
                obj.data.materials.append(mat)


def refine_materials():
    plaster=procedural_surface('MAT_Plaster_Warm',(0.57,.49,.38),.86,macro=1.8,medium=13,micro=115,color_strength=.075,bump=.085)
    reveal=procedural_surface('MAT_Window_Reveal',(.69,.62,.50),.82,macro=2.3,medium=19,micro=130,color_strength=.07,bump=.13)
    top=wood('MAT_Walnut_Provisional',1.08,8.5,.49)
    dark=wood('MAT_Walnut_Dark',.80,7.0,.57)
    da=wood('MAT_Walnut_Drawer_A',.96,6.2,.55)
    db=wood('MAT_Walnut_Drawer_B',1.06,7.6,.52)
    frame=wood('MAT_Walnut_Frame',.86,8.8,.59)
    metal('MAT_Aged_Brass',(.24,.105,.022),.90,.43)
    steel=metal('MAT_Blackened_Steel',(.018,.015,.012),.88,.39)
    grille=metal('MAT_Grille_White_Aged',(.68,.64,.54),.32,.61,True)
    glass('MAT_Window_Glass',(.75,.78,.72),.16,.68)
    procedural_surface('MAT_Criollo_Tile_Cream',(.64,.56,.44),.54,macro=1.2,medium=8,micro=105,color_strength=.06,bump=.045)
    procedural_surface('MAT_Criollo_Tile_Aged',(.51,.45,.36),.61,macro=1.1,medium=10,micro=120,color_strength=.08,bump=.06)
    procedural_surface('MAT_Criollo_Motif',(.095,.28,.25),.58,macro=1.5,medium=11,micro=100,color_strength=.08,bump=.04)
    procedural_surface('MAT_Criollo_Flower',(.43,.16,.105),.58,macro=1.5,medium=11,micro=100,color_strength=.08,bump=.04)
    for name,base in [('MAT_Exterior_Turquoise',(.075,.30,.31)),('MAT_Exterior_Cream',(.48,.39,.27)),('MAT_Exterior_Coral',(.43,.14,.085)),('MAT_Exterior_Trim',(.67,.60,.47)),('MAT_Exterior_Pavement',(.29,.27,.23))]:
        procedural_surface(name,base,.80,macro=1.6,medium=18,micro=90,color_strength=.11,bump=.10)
    procedural_surface('MAT_Tropical_Foliage',(.045,.19,.055),.73,macro=3,medium=24,micro=85,color_strength=.13,bump=.05)
    procedural_surface('MAT_Tropical_Foliage_Light',(.15,.34,.075),.72,macro=3,medium=24,micro=85,color_strength=.13,bump=.05)
    metal('MAT_Prop_BlackenedSteel',(.019,.016,.013),.9,.38)
    metal('MAT_Prop_MachineGreen',(.035,.12,.075),.60,.54,True)
    metal('MAT_Prop_AgedBrass',(.26,.12,.026),.91,.41)
    wood('MAT_Prop_DarkWood',.73,8,.58)
    procedural_surface('MAT_Prop_Rubber',(.009,.008,.007),.84,macro=4,medium=32,micro=140,color_strength=.07,bump=.14)
    procedural_surface('MAT_Prop_Cloth',(.21,.15,.09),.94,macro=4,medium=28,micro=160,color_strength=.12,bump=.22)
    procedural_surface('MAT_Prop_Ceramic',(.42,.37,.29),.47,macro=2,medium=16,micro=100,color_strength=.04,bump=.025)
    glass('MAT_Prop_ClearGlass',(.70,.68,.58),.14,.60)
    glass('MAT_Prop_NeutralLens',(.45,.47,.43),.105,.66,1.52)
    procedural_surface('MAT_Prop_Vinyl',(.006,.005,.004),.31,macro=3,medium=30,micro=110,color_strength=.05,bump=.05)
    acetate('MAT_Acetate_Amber',(.32,.085,.010),.14,.25)
    acetate('MAT_Acetate_Tortoise',(.105,.018,.004),.08,.31)
    acetate('MAT_Acetate_Smoke',(.070,.055,.043),.17,.26)
    acetate('MAT_Acetate_WarmBlack',(.011,.006,.003),.055,.24)
    acetate('MAT_Acetate_Crystal',(.50,.31,.14),.40,.19)
    acetate('MAT_Prop_AcetateSheet',(.28,.065,.012),.12,.38)
    assign_by_name('PN_CounterTop',top)
    assign_by_name('PN_Shelf_',wood('MAT_Walnut_Shelves',.92,9.2,.61))
    assign_by_name('PN_Window_Mullion_',grille)
    return [plaster,reveal,top,dark,da,db,frame,steel,grille]


def refine_geometry():
    # Non-destructive craftsmanship modifiers; dimensions and transforms remain unchanged.
    for obj in bpy.data.objects:
        if obj.type!='MESH': continue
        n=obj.name
        if any(k in n for k in ('Drawer','Cabinet','Counter','Shelf','Eyewear','Machine','Tool_')):
            if not any(m.type=='WEIGHTED_NORMAL' for m in obj.modifiers):
                try:
                    mod=obj.modifiers.new('PN_Craft_Normal','WEIGHTED_NORMAL'); mod.keep_sharp=True
                except Exception: pass
        if n.startswith('PN_Eyewear_') and any(k in n for k in ('Front','Temple','Bridge')):
            for m in obj.modifiers:
                if m.type=='BEVEL':
                    m.width=min(max(m.width,0.004),0.011); m.segments=max(m.segments,3)


def lighting():
    energies={'PN_Light_Window_Key':520,'PN_Light_Exterior_Daylight':470,'PN_Light_Bench_Bounce':260,'PN_Light_Ceiling_Fill':105}
    colors={'PN_Light_Window_Key':(1.0,.86,.70),'PN_Light_Exterior_Daylight':(.79,.90,1.0),'PN_Light_Bench_Bounce':(1.0,.72,.48),'PN_Light_Ceiling_Fill':(.70,.78,1.0)}
    for name,e in energies.items():
        o=bpy.data.objects.get(name)
        if o:
            o.data.energy=e; o.data.color=colors[name]
            if o.data.type=='AREA': o.data.shape='DISK'; o.data.size=max(o.data.size,3.2)
    for o in bpy.data.objects:
        if o.name.startswith('PN_ShelfLight_'):
            o.data.energy=10.0; o.data.color=(1.0,.69,.42); o.data.shadow_soft_size=.32
        elif o.name=='PN_TaskLamp_Practical':
            o.data.energy=28; o.data.color=(1.0,.58,.30); o.data.shadow_soft_size=.16
    world=bpy.context.scene.world
    if world and world.use_nodes:
        bg=next((n for n in world.node_tree.nodes if n.type=='BACKGROUND'),None)
        if bg: bg.inputs['Color'].default_value=(.075,.09,.12,1); bg.inputs['Strength'].default_value=.22


def point_camera(name,loc,target,lens=64):
    data=bpy.data.cameras.get(name+'_Data') or bpy.data.cameras.new(name+'_Data')
    cam=bpy.data.objects.get(name) or bpy.data.objects.new(name,data)
    if cam.name not in bpy.context.scene.collection.objects: bpy.context.scene.collection.objects.link(cam)
    cam.location=loc; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler(); data.lens=lens
    return cam


def render(path,cam=None,res=(1536,1024),samples=96):
    s=bpy.context.scene
    if cam: s.camera=cam
    s.render.resolution_x=res[0]; s.render.resolution_y=res[1]; s.render.resolution_percentage=100
    s.render.image_settings.file_format='PNG'; s.render.image_settings.color_mode='RGBA'; s.render.filepath=path
    if hasattr(s,'eevee'): s.eevee.taa_render_samples=samples
    t=time.time(); bpy.ops.render.render(write_still=True); return time.time()-t


def composite_side_by_side(left_path,right_path,out_path):
    left=bpy.data.images.load(left_path,check_existing=False); right=bpy.data.images.load(right_path,check_existing=False)
    w,h=1536,1024
    # Both source images are required to be 1536x1024 by the production brief.
    if left.size[:] != (w,h): left.scale(w,h)
    if right.size[:] != (w,h): right.scale(w,h)
    out=bpy.data.images.new('PN_Comparison',width=w*2,height=h,alpha=True)
    lp=list(left.pixels); rp=list(right.pixels); pixels=[0.0]*(w*2*h*4)
    row=w*4; outrow=w*2*4
    for y in range(h):
        pixels[y*outrow:y*outrow+row]=lp[y*row:(y+1)*row]
        pixels[y*outrow+row:(y+1)*outrow]=rp[y*row:(y+1)*row]
    out.pixels=pixels; out.filepath_raw=out_path; out.file_format='PNG'; out.save()
    bpy.data.images.remove(left); bpy.data.images.remove(right); bpy.data.images.remove(out)


def triangle_report():
    deps=bpy.context.evaluated_depsgraph_get(); tris=0; verts=0; by_group={'architecture':0,'grille':0,'exterior':0,'props':0,'eyewear':0}
    for obj in bpy.context.scene.objects:
        if obj.hide_render or obj.type not in {'MESH','CURVE'}: continue
        ev=obj.evaluated_get(deps)
        try: mesh=ev.to_mesh()
        except Exception: continue
        mesh.calc_loop_triangles(); count=len(mesh.loop_triangles); tris+=count; verts+=len(mesh.vertices)
        n=obj.name
        key='props'
        if 'Grille' in n or 'Mullion' in n: key='grille'
        elif n.startswith('PN_Exterior_'): key='exterior'
        elif n.startswith('PN_Eyewear_'): key='eyewear'
        elif any(k in n for k in ('Wall','Ceiling','Floor','Window','Counter','Cabinet','Drawer','Shelf','Stool')): key='architecture'
        by_group[key]+=count
        ev.to_mesh_clear()
    return verts,tris,by_group


def main():
    s=bpy.context.scene; approved=s.camera
    assert tuple(round(v,2) for v in approved.location)==(0.0,-11.15,2.52) and round(approved.data.lens,1)==52.0
    assert sorted(o.name for o in bpy.data.objects if o.name.startswith('PN_Eyewear_') and o.type=='EMPTY')==[f'PN_Eyewear_{i:02d}' for i in range(1,10)]
    assert sorted(o.name for o in bpy.data.objects if o.name.startswith('PN_LizardPath_Anchor_'))==[f'PN_LizardPath_Anchor_{i:02d}' for i in range(1,9)]
    refine_materials(); refine_geometry(); lighting()
    for obj in bpy.data.objects:
        if obj.type=='MESH' and obj.data.materials and obj.data.materials[0] and obj.data.materials[0].name=='MAT_Window_Glass':
            try: obj.visible_shadow=False
            except Exception: pass
    s.view_settings.look='AgX - Medium High Contrast'
    s.render.engine='BLENDER_EEVEE'; s.render.resolution_x=1536; s.render.resolution_y=1024; s.render.resolution_percentage=100
    s.render.image_settings.file_format='PNG'; s.render.film_transparent=False
    approved.hide_render=False; s.camera=approved
    # Persist the approved camera and material pass before the potentially long render batch.
    s.camera=approved
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    times={}
    main_path=os.path.join(RENDERS,'photoreal-main.png'); times['photoreal-main.png']=render(main_path,approved,samples=128)
    cameras={
      'bench-hero-photoreal.png':point_camera('PN_Cam_BenchHero',(0,-5.0,1.72),(0,.34,1.42),66),
      'wood-material-closeup.png':point_camera('PN_Cam_Wood',(-1.55,-3.55,1.58),(-1.35,.05,1.12),72),
      'plaster-wall-closeup.png':point_camera('PN_Cam_Plaster',(-2.55,-4.35,2.82),(-2.35,.82,2.65),78),
      'criollo-floor-closeup.png':point_camera('PN_Cam_Floor',(1.6,-3.65,1.64),(1.15,-.25,.10),58),
      'machinery-tools-closeup.png':point_camera('PN_Cam_Machines',(1.70,-4.45,1.72),(1.48,.18,1.38),70),
      'grille-exterior-closeup.png':point_camera('PN_Cam_Grille',(0,-5.7,2.62),(0,1.0,2.65),67),
      'lighting-diagnostic.png':point_camera('PN_Cam_Lighting',(0,-7.0,2.85),(0,.30,1.75),56),
      'materials-surface-preview.png':point_camera('PN_Cam_Materials',(-.35,-4.25,1.88),(-.25,.10,1.30),64),
    }
    for filename,cam in cameras.items(): times[filename]=render(os.path.join(RENDERS,filename),cam,samples=96)
    composite_side_by_side(TARGET,main_path,os.path.join(RENDERS,'camera-comparison-photoreal.png'))
    s.camera=approved
    verts,tris,groups=triangle_report()
    s['PN_Photoreal_RenderTimes']=str({k:round(v,2) for k,v in times.items()})
    s['PN_Photoreal_Triangles']=tris; s['PN_Photoreal_Vertices']=verts; s['PN_Photoreal_TrianglesByGroup']=str(groups)
    s['PN_ExternalResources']='None; all materials are original procedural Blender node graphs.'
    s['PN_BakeProposal']='Architecture 2048; workbench 2048; eyewear atlas 2048; machinery/tools 2048; grille 1024; exterior 2048; floor 2048. ORM packed; normal BC5; basecolor ETC1S; normals/ORM UASTC.'
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print('PN_RENDER_TIMES',s['PN_Photoreal_RenderTimes']); print('PN_VERTS',verts,'PN_TRIS',tris,'PN_GROUPS',groups)
    print('PN_CAMERA',tuple(approved.location),approved.data.lens)


if __name__=='__main__': main()
