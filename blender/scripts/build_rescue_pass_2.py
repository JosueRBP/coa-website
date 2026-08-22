import bpy, math, os, time, shutil
from mathutils import Vector

ROOT=r"C:\Users\josue\Documents\Codex\coa-website"
BLEND=os.path.join(ROOT,'blender','puerto-nuevo-workshop.blend')
RDIR=os.path.join(ROOT,'blender','renders')
TARGET=os.path.join(ROOT,'art-direction','puerto-nuevo-blender-art-target-v2.png')
BEFORE=os.path.join(RDIR,'wood-before-rescue.png')
if not os.path.exists(BEFORE) and os.path.exists(os.path.join(RDIR,'wood-material-closeup.png')):
    shutil.copy2(os.path.join(RDIR,'wood-material-closeup.png'),BEFORE)

def mat_nodes(name):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes=True
    n=m.node_tree.nodes; n.clear(); l=m.node_tree.links
    out=n.new('ShaderNodeOutputMaterial'); out.location=(700,0)
    bs=n.new('ShaderNodeBsdfPrincipled'); bs.location=(420,0); l.new(bs.outputs[0],out.inputs[0])
    return m,n,l,bs

def walnut(name,base=(.095,.034,.012),variant=0):
    m,n,l,bs=mat_nodes(name); tc=n.new('ShaderNodeTexCoord'); mp=n.new('ShaderNodeMapping')
    # Each object receives its own Generated coordinates; no continuous cabinet projection.
    mp.inputs['Scale'].default_value=(1.5+variant*.13,.22,.18)
    grain=n.new('ShaderNodeTexNoise'); grain.noise_dimensions='3D'; grain.inputs['Scale'].default_value=3.2; grain.inputs['Detail'].default_value=5.2; grain.inputs['Roughness'].default_value=.62; grain.inputs['Distortion'].default_value=.18
    pores=n.new('ShaderNodeTexNoise'); pores.inputs['Scale'].default_value=78; pores.inputs['Detail'].default_value=2.2; pores.inputs['Roughness'].default_value=.48
    ramp=n.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=.18; ramp.color_ramp.elements[1].position=.84
    factor=1+variant*.035
    ramp.color_ramp.elements[0].color=(base[0]*.70*factor,base[1]*.63*factor,base[2]*.55*factor,1)
    ramp.color_ramp.elements[1].color=(base[0]*1.75*factor,base[1]*1.60*factor,base[2]*1.35*factor,1)
    rough=n.new('ShaderNodeMapRange'); rough.inputs['To Min'].default_value=.48; rough.inputs['To Max'].default_value=.66
    bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.055; bump.inputs['Distance'].default_value=.009
    l.new(tc.outputs['Generated'],mp.inputs[0]); l.new(mp.outputs[0],grain.inputs[0]); l.new(mp.outputs[0],pores.inputs[0]); l.new(grain.outputs['Fac'],ramp.inputs[0]); l.new(ramp.outputs[0],bs.inputs['Base Color']); l.new(pores.outputs['Fac'],rough.inputs['Value']); l.new(rough.outputs[0],bs.inputs['Roughness']); l.new(pores.outputs['Fac'],bump.inputs['Height']); l.new(bump.outputs[0],bs.inputs['Normal'])
    bs.inputs['Coat Weight'].default_value=.045; bs.inputs['Coat Roughness'].default_value=.48
    return m

def simple(name,color,rough=.6,metal=0):
    m,n,l,bs=mat_nodes(name); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    noise=n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=55; noise.inputs['Detail'].default_value=2
    tc=n.new('ShaderNodeTexCoord'); bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.045; bump.inputs['Distance'].default_value=.006
    l.new(tc.outputs['Generated'],noise.inputs[0]); l.new(noise.outputs['Fac'],bump.inputs['Height']); l.new(bump.outputs[0],bs.inputs['Normal'])
    return m

def acetate(name,dark,amber):
    m,n,l,bs=mat_nodes(name); tc=n.new('ShaderNodeTexCoord'); noise=n.new('ShaderNodeTexNoise'); noise.noise_dimensions='3D'; noise.inputs['Scale'].default_value=4.4; noise.inputs['Detail'].default_value=9; noise.inputs['Roughness'].default_value=.72; noise.inputs['Distortion'].default_value=1.25
    ramp=n.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=.26; ramp.color_ramp.elements[0].color=(*dark,1); ramp.color_ramp.elements[1].position=.77; ramp.color_ramp.elements[1].color=(*amber,1)
    l.new(tc.outputs['Generated'],noise.inputs[0]); l.new(noise.outputs['Fac'],ramp.inputs[0]); l.new(ramp.outputs[0],bs.inputs['Base Color'])
    bs.inputs['Roughness'].default_value=.24; bs.inputs['Transmission Weight'].default_value=.055; bs.inputs['IOR'].default_value=1.49; bs.inputs['Coat Weight'].default_value=.42; bs.inputs['Coat Roughness'].default_value=.12
    return m

def setmat(obj,m):
    if obj.data.materials: obj.data.materials[0]=m
    else: obj.data.materials.append(m)

def rescue_wood():
    mats=[walnut('MAT_Walnut_Top_Rescue',(.092,.031,.010),0),walnut('MAT_Walnut_Drawer_Rescue',(.078,.025,.008),1),walnut('MAT_Walnut_Frame_Rescue',(.062,.019,.006),2),walnut('MAT_Walnut_Shelf_Rescue',(.072,.023,.007),3),walnut('MAT_Walnut_Stool_Rescue',(.10,.036,.012),4)]
    for o in bpy.data.objects:
        if o.type!='MESH': continue
        n=o.name
        if 'CounterTop' in n or 'WorkbenchTop' in n: setmat(o,mats[0])
        elif 'Drawer' in n or 'CabinetDoor' in n or 'HeroDisplay' in n: setmat(o,mats[1])
        elif any(k in n for k in ('Cabinet','CounterFrame','Kick','Plinth')): setmat(o,mats[2])
        elif 'Shelf_' in n: setmat(o,mats[3])
        elif 'Stool_Seat' in n: setmat(o,mats[4])
    return mats

def remove_children(root):
    for o in list(bpy.data.objects):
        p=o.parent
        while p:
            if p==root: bpy.data.objects.remove(o,do_unlink=True); break
            p=p.parent

def shape_points(style,cx,rx,rz,count=40):
    pts=[]
    for i in range(count):
        a=math.tau*i/count; x=rx*math.cos(a); z=rz*math.sin(a)
        if style=='angular':
            # Rounded-square superellipse with a lifted brow and softened lower corners.
            c,s=math.cos(a),math.sin(a); exponent=.62
            x=rx*math.copysign(abs(c)**exponent,c); z=rz*math.copysign(abs(s)**exponent,s)
            if z>0: z += .020*(abs(x)/rx)**1.45
            else: z += .010*(1-(abs(x)/rx))
        else:
            z += -.018 + .022*math.cos(a)
            x *= .98+.05*max(0,-math.sin(a))
        pts.append((cx+x,0,z))
    return pts

def ring_mesh(name,outer,inner,depth,material,col,parent):
    n=len(outer); verts=[]
    for y in (-depth/2,depth/2): verts += [(x,y,z) for x,_,z in outer]+[(x,y,z) for x,_,z in inner]
    faces=[]
    for i in range(n):
        j=(i+1)%n; faces.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata(verts,[],faces); me.update(); ob=bpy.data.objects.new(name,me); col.objects.link(ob); ob.parent=parent; me.materials.append(material)
    b=ob.modifiers.new('PN_Polished_Acetate_Edge','BEVEL'); b.width=.008; b.segments=4
    return ob

def lens_mesh(name,pts,material,col,parent):
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata([(x,.004,z) for x,_,z in pts],[],[tuple(range(len(pts)))]); me.update(); ob=bpy.data.objects.new(name,me); col.objects.link(ob); ob.parent=parent; me.materials.append(material)
    so=ob.modifiers.new('PN_Lens_Thickness','SOLIDIFY'); so.thickness=.004
    be=ob.modifiers.new('PN_Lens_Polish','BEVEL'); be.width=.0025; be.segments=3
    return ob

def tube(name,pts,radius,material,col,parent,cyclic=False):
    cu=bpy.data.curves.new(name+'_Curve','CURVE'); cu.dimensions='3D'; cu.resolution_u=3; cu.bevel_depth=radius; cu.bevel_resolution=3; cu.resolution_u=6
    sp=cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts)-1)
    for bp,co in zip(sp.bezier_points,pts): bp.co=co; bp.handle_left_type='AUTO'; bp.handle_right_type='AUTO'
    sp.use_cyclic_u=cyclic; ob=bpy.data.objects.new(name,cu); col.objects.link(ob); ob.parent=parent; cu.materials.append(material); return ob

def lens_material():
    m,n,l,bs=mat_nodes('MAT_Rescue_NeutralLens'); bs.inputs['Base Color'].default_value=(.42,.44,.40,1); bs.inputs['Roughness'].default_value=.10; bs.inputs['Transmission Weight'].default_value=.32; bs.inputs['Alpha'].default_value=.40; bs.inputs['IOR'].default_value=1.52; bs.inputs['Coat Weight'].default_value=.22
    try:m.surface_render_method='DITHERED'
    except:pass
    return m

def rebuild_eyewear():
    col=bpy.data.collections.get('PN_Eyewear_Products'); lens=lens_material(); brass=simple('MAT_Rescue_HingeBrass',(.24,.105,.025),.38,.9)
    black=acetate('MAT_Rescue_Acetate_BlackTortoise',(.0015,.001,.0007),(.042,.008,.0015)); tort=acetate('MAT_Rescue_Acetate_Tortoise',(.010,.003,.001),(.16,.035,.005)); honey=acetate('MAT_Rescue_Acetate_Honey',(.025,.007,.002),(.30,.105,.018)); smoke=acetate('MAT_Rescue_Acetate_Smoke',(.008,.007,.006),(.065,.050,.036))
    palette=[black,tort,smoke,tort,black,honey,tort,honey,black]
    angular={1,3,5,7,9}
    for idx in range(1,10):
        root=bpy.data.objects[f'PN_Eyewear_{idx:02d}']; remove_children(root); style='angular' if idx in angular else 'panto'; scale=1.14 if idx==9 else .96
        rx=(.158 if style=='angular' else .148)*scale; rz=(.112 if style=='angular' else .122)*scale; centers=.177*scale; rim=.030*scale; depth=.042*scale
        for side,sgn in [('L',-1),('R',1)]:
            cx=sgn*centers; outer=shape_points(style,cx,rx,rz); inner=shape_points(style,cx,rx-rim,rz-rim*.80)
            ring_mesh(f'{root.name}_Front_{side}',outer,inner,depth,palette[idx-1],col,root); lens_mesh(f'{root.name}_Lens_{side}',inner,lens,col,root)
            hx=cx+sgn*(rx+.008); tube(f'{root.name}_HingePin_{side}',[(hx,-.026,.015),(hx,.026,.015)],.008,brass,col,root)
            tube(f'{root.name}_Temple_{side}',[(hx,0,.015),(hx+sgn*.075,.075,.005),(hx+sgn*.12,.25,-.035),(hx+sgn*.105,.34,-.070)],.015*scale,palette[idx-1],col,root)
        bridge_z=.030 if style=='angular' else .045
        tube(f'{root.name}_Bridge',[(-centers+rx*.89,0,bridge_z),(0,-.006,bridge_z+.025),(centers-rx*.89,0,bridge_z)],.020*scale,palette[idx-1],col,root)
        root['eyewear_style']=style; root['reference_family']='angular-primary' if style=='angular' else 'panto-secondary'; root['hero_product']=(idx==9)

def flat_shape(name,verts,z,mat,col):
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata([(x,y,z) for x,y in verts],[],[tuple(range(len(verts)))]); me.update(); ob=bpy.data.objects.new(name,me); col.objects.link(ob); me.materials.append(mat); return ob

def motif_component_data(name,kind,mat):
    verts=[]
    if kind=='center':
        for i in range(16):
            a=math.tau*i/16; r=.095 if i%2==0 else .060; verts.append((r*math.cos(a),r*math.sin(a)))
    elif kind=='white':
        for q in range(4):
            a=math.pi/2*q; cx=.13*math.cos(a); cy=.13*math.sin(a)
            for i in range(10):
                t=math.tau*i/10; verts.append((cx+.082*math.cos(t)*(.65+abs(math.cos(a))*.35),cy+.082*math.sin(t)*(.65+abs(math.sin(a))*.35)))
    return verts

def rescue_floor():
    shell=bpy.data.collections.get('PN_Workshop_Shell'); ochre=simple('MAT_Criollo_Ochre',(.56,.31,.075),.66); green=simple('MAT_Criollo_Green',(.11,.24,.125),.69); white=simple('MAT_Criollo_WhiteFlower',(.70,.64,.48),.72); wine=simple('MAT_Criollo_Wine',(.25,.045,.035),.68); dark=simple('MAT_Criollo_DarkCenter',(.035,.105,.055),.72)
    for o in list(bpy.data.objects):
        if o.name.startswith(('PN_CriolloPattern_','PN_CriolloCenter_','PN_FloorMotif_','PN_FloorFlower_','PN_RescueTileMotif_')): bpy.data.objects.remove(o,do_unlink=True)
    tiles=[o for o in bpy.data.objects if o.name.startswith('PN_FloorTile_')]
    for i,t in enumerate(tiles):
        setmat(t,ochre if i%5 else simple('MAT_Criollo_Ochre_Variant',(.50,.275,.065),.70)); x,y=t.location.x,t.location.y; z=t.location.z+t.dimensions.z*.56
        # Four botanical arms, white quatrefoil, wine joints, dark star center.
        for q in range(4):
            a=math.pi/2*q
            tube(f'PN_RescueTileMotif_{i:03d}_Stem_{q}',[(x+.07*math.cos(a),y+.07*math.sin(a),z),(x+.18*math.cos(a+.12),y+.18*math.sin(a+.12),z),(x+.23*math.cos(a+.34),y+.23*math.sin(a+.34),z)],.006,green,shell,None)
            bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=.036,location=(x+.145*math.cos(a),y+.145*math.sin(a),z+.002),scale=(1.5,.52,.10)); p=bpy.context.object; p.name=f'PN_RescueTileMotif_{i:03d}_Wine_{q}'; setmat(p,wine)
            bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.072,location=(x+.115*math.cos(a),y+.115*math.sin(a),z+.001),scale=(.65+abs(math.cos(a))*.35,.65+abs(math.sin(a))*.35,.06)); w=bpy.context.object; w.name=f'PN_RescueTileMotif_{i:03d}_White_{q}'; setmat(w,white)
        bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.075,depth=.002,location=(x,y,z+.002)); c=bpy.context.object; c.name=f'PN_RescueTileMotif_{i:03d}_Center'; setmat(c,dark)

def refine_machines():
    steel=simple('MAT_Rescue_MachineSteel',(.025,.026,.023),.37,.88); green=simple('MAT_Rescue_MachineGreen',(.035,.115,.064),.58,.60); rubber=simple('MAT_Rescue_Rubber',(.008,.008,.007),.84)
    for old in [o for o in bpy.data.objects if o.name.startswith(('PN_Machine_FunctionalScrew_','PN_Machine_PowerCable'))]: bpy.data.objects.remove(old,do_unlink=True)
    for o in bpy.data.objects:
        if not o.name.startswith('PN_Machine_') or o.type!='MESH': continue
        setmat(o,green if any(k in o.name for k in ('Base','Head','Motor','Control')) else steel)
        for p in o.data.polygons: p.use_smooth=True
        b=next((m for m in o.modifiers if m.type=='BEVEL'),None) or o.modifiers.new('PN_Functional_Edge','BEVEL'); b.width=min(max(getattr(b,'width',.006),.006),.018); b.segments=max(getattr(b,'segments',2),3)
    col=bpy.data.collections.get('PN_Workshop_Machinery')
    # Functional detail that stays below the eyewear sightline.
    for j,(x,z) in enumerate([(1.43,1.26),(1.60,1.30),(2.05,1.34),(2.38,1.29)]):
        bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=.022,depth=.016,location=(x,.05,z),rotation=(math.pi/2,0,0)); s=bpy.context.object; s.name=f'PN_Machine_FunctionalScrew_{j+1:02d}'; setmat(s,steel)
    tube('PN_Machine_PowerCable',[(2.38,.18,1.18),(2.55,.28,1.10),(2.70,.36,1.10)],.010,rubber,col,None)

def lighting():
    vals={'PN_Light_Window_Key':470,'PN_Light_Exterior_Daylight':410,'PN_Light_Bench_Bounce':170,'PN_Light_Ceiling_Fill':65}
    for n,e in vals.items():
        o=bpy.data.objects.get(n)
        if o:o.data.energy=e
    for o in bpy.data.objects:
        if o.name.startswith('PN_ShelfLight_'): o.data.energy=4.0
        elif o.name=='PN_TaskLamp_Practical': o.data.energy=38; o.data.color=(1,.52,.25)
    bpy.context.scene.view_settings.look='AgX - Medium High Contrast'; bpy.context.scene.view_settings.exposure=-.35

def camera(name,loc,target,lens=70):
    d=bpy.data.cameras.get(name+'_Data') or bpy.data.cameras.new(name+'_Data'); o=bpy.data.objects.get(name) or bpy.data.objects.new(name,d)
    if not o.users_collection:bpy.context.scene.collection.objects.link(o)
    o.location=loc; o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler(); d.lens=lens; return o

def render(name,cam,samples=96):
    s=bpy.context.scene; s.camera=cam; s.render.resolution_x=1536; s.render.resolution_y=1024; s.render.resolution_percentage=100; s.render.filepath=os.path.join(RDIR,name); s.render.image_settings.file_format='PNG'
    t=time.time(); bpy.ops.render.render(write_still=True); return round(time.time()-t,2)

def side_by_side(a,b,out):
    ia=bpy.data.images.load(a,check_existing=False); ib=bpy.data.images.load(b,check_existing=False); w,h=1536,1024
    if tuple(ia.size)!=(w,h):ia.scale(w,h)
    if tuple(ib.size)!=(w,h):ib.scale(w,h)
    im=bpy.data.images.new('PN_RescueCompare',width=3072,height=1024,alpha=True); pa=list(ia.pixels); pb=list(ib.pixels); pix=[0.0]*(3072*1024*4)
    for y in range(h):
        r=w*4; rr=3072*4; pix[y*rr:y*rr+r]=pa[y*r:(y+1)*r]; pix[y*rr+r:(y+1)*rr]=pb[y*r:(y+1)*r]
    im.pixels=pix; im.filepath_raw=out; im.file_format='PNG'; im.save(); bpy.data.images.remove(ia); bpy.data.images.remove(ib); bpy.data.images.remove(im)

def metrics():
    d=bpy.context.evaluated_depsgraph_get(); tri=poly=vert=0
    for o in bpy.context.scene.objects:
        if o.hide_render or o.type not in {'MESH','CURVE'}:continue
        try:e=o.evaluated_get(d);m=e.to_mesh();m.calc_loop_triangles();tri+=len(m.loop_triangles);poly+=len(m.polygons);vert+=len(m.vertices);e.to_mesh_clear()
        except:pass
    return vert,poly,tri

def main():
    s=bpy.context.scene; approved=bpy.data.objects['PN_Camera_Desktop']; assert tuple(round(v,2) for v in approved.location)==(0,-11.15,2.52) and approved.data.lens==52
    rescue_wood(); rescue_floor(); rebuild_eyewear(); refine_machines(); lighting(); s.camera=approved
    s['PN_WebTextureBudget']='Hero eyewear+bench 2048 shared; architecture/floor 2048 shared; machinery+props 1024; exterior 1024; grille 512; ORM packed. KTX2 target 18-27 MB.'
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    quick=os.environ.get('PN_RESCUE_QUICK')=='1'
    times={}; mainp=os.path.join(RDIR,'rescue-pass-main.png'); times['main']=render('rescue-pass-main.png',approved,72 if quick else 128)
    cams={
      'rescue-wood-after.png':camera('PN_Cam_RescueWood',(-1.4,-3.7,1.62),(-1.25,.05,1.15),72),
      'rescue-criollo-tile.png':camera('PN_Cam_RescueTile',(1.3,-3.25,1.52),(1.0,-.2,.08),62),
      'rescue-eyewear-hero-front.png':camera('PN_Cam_RescueHeroFront',(0,-3.15,1.42),(0,.26,1.38),84),
      'rescue-eyewear-hero-three-quarter.png':camera('PN_Cam_RescueHero3Q',(.75,-2.75,1.64),(0,.28,1.38),78),
      'rescue-eyewear-panto.png':camera('PN_Cam_RescuePanto',(-2.05,-2.55,2.22),(-2.65,1.03,2.16),88),
      'rescue-machinery.png':camera('PN_Cam_RescueMachine',(1.75,-4.0,1.70),(1.65,.16,1.42),72),
      'rescue-grille-exterior.png':camera('PN_Cam_RescueExterior',(0,-5.5,2.72),(0,1.2,2.60),66),
      'rescue-lighting-diagnostic.png':camera('PN_Cam_RescueLighting',(0,-6.8,2.78),(0,.25,1.72),56),
      'rescue-material-preview.png':camera('PN_Cam_RescueMaterials',(-.35,-4.0,1.82),(-.2,.10,1.28),66)}
    selected={'rescue-criollo-tile.png','rescue-eyewear-hero-front.png','rescue-eyewear-hero-three-quarter.png','rescue-material-preview.png'} if quick else set(cams)
    for f,c in cams.items():
        if f in selected: times[f]=render(f,c,96)
    side_by_side(TARGET,mainp,os.path.join(RDIR,'rescue-camera-comparison.png')); side_by_side(BEFORE,os.path.join(RDIR,'rescue-wood-after.png'),os.path.join(RDIR,'rescue-wood-before-after.png'))
    s.camera=approved; v,p,t=metrics(); s['PN_RescueMetrics']=f'vertices={v}, polygons={p}, triangles={t}'; s['PN_RescueRenderTimes']=str(times); bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print('PN_RESCUE_METRICS',v,p,t); print('PN_RESCUE_TIMES',times); print('PN_CAMERA',tuple(approved.location),approved.data.lens)

if __name__=='__main__':main()
