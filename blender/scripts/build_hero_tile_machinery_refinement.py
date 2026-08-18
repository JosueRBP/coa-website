import bpy, math, os, time
import numpy as np
from mathutils import Vector

ROOT=r"C:\Users\josue\Documents\Codex\coa-website"
BLEND=os.path.join(ROOT,'blender','puerto-nuevo-workshop.blend')
RDIR=os.path.join(ROOT,'blender','renders')
TEXDIR=os.path.join(ROOT,'blender','textures'); os.makedirs(TEXDIR,exist_ok=True)
TARGET=os.path.join(ROOT,'art-direction','puerto-nuevo-blender-art-target-v2.png')
TILEREF=os.path.join(ROOT,'art-direction','criollo-tile-reference.png')
TILEPNG=os.path.join(TEXDIR,'pn-criollo-tile-original-1024.png')

def material(name,color,rough=.5,metal=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes=True; n=m.node_tree.nodes; n.clear(); l=m.node_tree.links
    out=n.new('ShaderNodeOutputMaterial'); bs=n.new('ShaderNodeBsdfPrincipled'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal; l.new(bs.outputs[0],out.inputs[0]); return m,bs

def acetate():
    m,bs=material('MAT_Hero09_BlackTortoise',(.002,.0013,.0008),.22); n=m.node_tree.nodes; l=m.node_tree.links
    tc=n.new('ShaderNodeTexCoord'); noise=n.new('ShaderNodeTexNoise'); noise.noise_dimensions='3D'; noise.inputs['Scale'].default_value=5.2; noise.inputs['Detail'].default_value=8; noise.inputs['Roughness'].default_value=.68; noise.inputs['Distortion'].default_value=1.8
    ramp=n.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=.34; ramp.color_ramp.elements[0].color=(.001,.0007,.0004,1); ramp.color_ramp.elements[1].position=.78; ramp.color_ramp.elements[1].color=(.055,.010,.0018,1)
    l.new(tc.outputs['Generated'],noise.inputs[0]); l.new(noise.outputs['Fac'],ramp.inputs[0]); l.new(ramp.outputs[0],bs.inputs['Base Color']); bs.inputs['Coat Weight'].default_value=.5; bs.inputs['Coat Roughness'].default_value=.10; bs.inputs['IOR'].default_value=1.49
    return m

def lensmat():
    m,bs=material('MAT_Hero09_Lens',(.48,.49,.45),.08); bs.inputs['Transmission Weight'].default_value=.38; bs.inputs['Alpha'].default_value=.30; bs.inputs['IOR'].default_value=1.52; bs.inputs['Coat Weight'].default_value=.18
    try:m.surface_render_method='DITHERED'
    except:pass
    return m

def catmull(points,sub=4):
    out=[]; n=len(points)
    for i in range(n):
        p0=Vector(points[(i-1)%n]);p1=Vector(points[i]);p2=Vector(points[(i+1)%n]);p3=Vector(points[(i+2)%n])
        for j in range(sub):
            t=j/sub;t2=t*t;t3=t2*t
            p=.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t2+(-p0+3*p1-3*p2+p3)*t3);out.append(tuple(p))
    return out

def ring(name,outer,inner,depth,mat,col,parent):
    count=len(outer); verts=[]
    for front in (-depth/2,depth/2):
        for seq in (outer,inner):
            for x,z in seq:
                curve=-.010*(abs(x)/.38)**2
                verts.append((x,front+curve,z))
    faces=[]
    for i in range(count):
        j=(i+1)%count; faces.extend([(i,j,count+j,count+i),(2*count+i,3*count+i,3*count+j,2*count+j),(i,2*count+i,2*count+j,j),(count+i,count+j,3*count+j,3*count+i)])
    me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(name,me);col.objects.link(ob);ob.parent=parent;me.materials.append(mat)
    be=ob.modifiers.new('PN_HandPolishedEdge','BEVEL');be.width=.007;be.segments=4
    for p in me.polygons:p.use_smooth=True
    return ob

def lens(name,pts,mat,col,parent):
    me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata([(x,-.026-.008*(abs(x)/.38)**2,z) for x,z in pts],[],[tuple(range(len(pts)))]);me.update();ob=bpy.data.objects.new(name,me);col.objects.link(ob);ob.parent=parent;me.materials.append(mat)
    so=ob.modifiers.new('PN_OpticalThickness','SOLIDIFY');so.thickness=.0035;be=ob.modifiers.new('PN_LensEdge','BEVEL');be.width=.002;be.segments=3;return ob

def tube(name,pts,radius,mat,col,parent=None):
    cu=bpy.data.curves.new(name+'_Curve','CURVE');cu.dimensions='3D';cu.resolution_u=8;cu.bevel_depth=radius;cu.bevel_resolution=3
    sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
    for b,p in zip(sp.bezier_points,pts):b.co=p;b.handle_left_type='AUTO';b.handle_right_type='AUTO'
    ob=bpy.data.objects.new(name,cu);col.objects.link(ob);ob.parent=parent;cu.materials.append(mat);return ob

def rebuild_hero():
    root=bpy.data.objects['PN_Eyewear_09'];col=bpy.data.collections['PN_Eyewear_Products']
    for o in list(bpy.data.objects):
        p=o.parent
        while p:
            if p==root:bpy.data.objects.remove(o,do_unlink=True);break
            p=p.parent
    ac=acetate();lm=lensmat();brass,_=material('MAT_Hero09_HingeMetal',(.22,.085,.018),.35,.92)
    scale=.88; centers=.155*scale
    base=[(-.165,.105),(-.070,.138),(.035,.130),(.145,.105),(.178,.030),(.165,-.072),(.095,-.124),(-.025,-.137),(-.125,-.112),(-.178,-.045)]
    for side,sgn in [('L',-1),('R',1)]:
        asym=.006 if side=='R' else -.004
        local=[(x*scale,(z+asym*(x/.18))*scale) for x,z in base]
        outer=catmull([(sgn*centers+x,z) for x,z in local],5)
        inner=catmull([(sgn*centers+x*.73,z*.70-.002) for x,z in local],5)
        ring(f'PN_Eyewear_09_Front_{side}',outer,inner,.040*scale,ac,col,root);lens(f'PN_Eyewear_09_Lens_{side}',inner,lm,col,root)
        hx=sgn*centers+sgn*.178*scale
        tube(f'PN_Eyewear_09_Endpiece_{side}',[(hx-sgn*.020,-.002,.030),(hx+sgn*.040,.012,.020)],.021,ac,col,root)
        tube(f'PN_Eyewear_09_HingePin_{side}',[(hx+sgn*.025,-.026,.020),(hx+sgn*.025,.026,.020)],.0065,brass,col,root)
        # Recede immediately; only a short asymmetrical glimpse is visible head-on.
        terminal_x=hx+sgn*.105
        tube(f'PN_Eyewear_09_Temple_{side}',[(hx+sgn*.030,.018,.020),(hx+sgn*.060,.105,.008),(terminal_x,.285,-.040),(terminal_x-sgn*.020,.355,-.082)],.018,ac,col,root)
        for pinz in (.011,.030):tube(f'PN_Eyewear_09_HingeRivet_{side}_{pinz}',[(hx+sgn*.010,-.031,pinz),(hx+sgn*.010,-.035,pinz)],.0027,brass,col,root)
    tube('PN_Eyewear_09_Bridge',[(-centers+.144*scale,-.012,.038),(0,-.025,.057),(centers-.144*scale,-.012,.038)],.0145,ac,col,root)
    root['hero_refinement_pass']='surgical-angular-v1';root['hero_scale_factor']=scale

def refine_laterals():
    lm=bpy.data.materials.get('MAT_Rescue_NeutralLens')
    if lm and lm.use_nodes:
        bs=next((n for n in lm.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
        if bs:bs.inputs['Transmission Weight'].default_value=.40;bs.inputs['Alpha'].default_value=.34;bs.inputs['Roughness'].default_value=.10
    for idx in range(1,9):
        root=bpy.data.objects[f'PN_Eyewear_{idx:02d}'];root.scale=(.94,.94,.94)
        for o in bpy.data.objects:
            if o.parent==root or (o.parent and o.parent.parent==root):
                if o.type=='MESH':
                    for m in o.modifiers:
                        if m.type=='BEVEL':m.segments=max(m.segments,3);m.width=min(m.width,.006)
                if 'Bridge' in o.name and o.type=='CURVE':o.data.bevel_depth=min(o.data.bevel_depth,.014)
                if 'Temple' in o.name and o.type=='CURVE':o.data.bevel_depth=min(o.data.bevel_depth,.012)

def tile_texture():
    size=1024;y,x=np.mgrid[0:size,0:size];u=(x+.5)/size;v=(y+.5)/size
    base=np.zeros((size,size,4),dtype=np.float32);base[:,:,:3]=(.58,.34,.105);base[:,:,3]=1
    # Subtle handmade variation and aged border.
    variation=.018*np.sin(x*.037)*np.sin(y*.029)+.012*np.sin((x+y)*.011);base[:,:,:3]+=variation[:,:,None]
    def paint(mask,c):base[mask,:3]=c
    green=np.array((.105,.235,.125));dark=np.array((.035,.105,.055));white=np.array((.78,.72,.57));wine=np.array((.30,.055,.043))
    # Central 12-point star.
    ang=np.arctan2(v-.5,u-.5);rad=np.hypot(u-.5,v-.5);limit=.115+.030*np.cos(6*ang);paint(rad<limit,dark)
    for q in range(4):
        a=q*math.pi/2; ca,sa=math.cos(a),math.sin(a)
        # White inward-curving floral lobes.
        cx=.5+.17*ca;cy=.5+.17*sa;xr=(u-cx)*ca+(v-cy)*sa;yr=-(u-cx)*sa+(v-cy)*ca
        petal=(xr/.115)**2+(yr/.070)**2<1; notch=(xr<-.020)&(((xr+.035)/.055)**2+(yr/.040)**2<1);paint(petal&~notch,white)
        # Burgundy joint.
        cx=.5+.285*ca;cy=.5+.285*sa;xr=(u-cx)*ca+(v-cy)*sa;yr=-(u-cx)*sa+(v-cy)*ca;paint((xr/.045)**2+(yr/.020)**2<1,wine)
        # Large corner botanical arm: sampled curved stem plus three terminal leaves.
        mask=np.zeros((size,size),bool)
        for t in np.linspace(0,1,18):
            px=.5+(.30+.20*t)*ca + .13*math.sin(t*math.pi)*(-sa);py=.5+(.30+.20*t)*sa + .13*math.sin(t*math.pi)*ca
            mask|=((u-px)**2+(v-py)**2)<(.022+(.008*t))**2
        tx=.5+.49*ca;ty=.5+.49*sa
        for off in (-.055,0,.055):
            px=tx+off*(-sa);py=ty+off*ca;mask|=(((u-px)*ca+(v-py)*sa)/.060)**2+((-(u-px)*sa+(v-py)*ca)/.025)**2<1
        paint(mask,green)
    border=np.minimum.reduce([u,v,1-u,1-v]);base[:,:,:3]-=(np.clip((.035-border)/.035,0,1)*.075)[:,:,None]
    img=bpy.data.images.get('PN_CriolloTile_Original') or bpy.data.images.new('PN_CriolloTile_Original',size,size,alpha=True,float_buffer=False)
    img.pixels.foreach_set(base.ravel());img.filepath_raw=TILEPNG;img.file_format='PNG';img.save()
    m,bs=material('MAT_Criollo_Tile_Fidelity',(.6,.35,.10),.67);n=m.node_tree.nodes;l=m.node_tree.links;tex=n.new('ShaderNodeTexImage');tex.image=img;tex.interpolation='Linear';tex.extension='REPEAT';tc=n.new('ShaderNodeTexCoord');l.new(tc.outputs['Generated'],tex.inputs['Vector']);l.new(tex.outputs['Color'],bs.inputs['Base Color'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.055;bump.inputs['Distance'].default_value=.003;l.new(tex.outputs['Color'],bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])
    for o in list(bpy.data.objects):
        if o.name.startswith('PN_RescueTileMotif_'):bpy.data.objects.remove(o,do_unlink=True)
    for o in bpy.data.objects:
        if o.name.startswith('PN_FloorTile_'):
            if o.data.materials:o.data.materials[0]=m
            else:o.data.materials.append(m)

def primitive(kind,name,loc,scale,mat,col,rotation=(0,0,0),segments=24):
    if kind=='cube':bpy.ops.mesh.primitive_cube_add(location=loc,rotation=rotation)
    elif kind=='cyl':bpy.ops.mesh.primitive_cylinder_add(vertices=segments,radius=1,depth=2,location=loc,rotation=rotation)
    elif kind=='torus':bpy.ops.mesh.primitive_torus_add(major_radius=1,minor_radius=.15,major_segments=segments,minor_segments=8,location=loc,rotation=rotation)
    o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(mat);bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for p in o.data.polygons:p.use_smooth=True
    be=o.modifiers.new('PN_MachineEdge','BEVEL');be.width=.005;be.segments=3
    for c in list(o.users_collection):c.objects.unlink(o)
    col.objects.link(o);return o

def refine_machinery():
    col=bpy.data.collections['PN_Workshop_Machinery'];green=bpy.data.materials.get('MAT_Rescue_MachineGreen');steel=bpy.data.materials.get('MAT_Rescue_MachineSteel');rubber=bpy.data.materials.get('MAT_Rescue_Rubber');brass=bpy.data.materials.get('MAT_Hero09_HingeMetal')
    for o in list(bpy.data.objects):
        if o.name.startswith('PN_SurgicalMachine_'):bpy.data.objects.remove(o,do_unlink=True)
    primitive('cyl','PN_SurgicalMachine_DrillRearMotor',(1.50,.78,2.20),(.17,.25,.17),green,col,(math.pi/2,0,0),28)
    primitive('cyl','PN_SurgicalMachine_DrillQuill',(1.47,.47,2.00),(.052,.052,.16),steel,col,segments=24)
    primitive('torus','PN_SurgicalMachine_DrillTableCollar',(1.52,.73,1.48),(.075,.075,.075),steel,col,(math.pi/2,0,0),24)
    primitive('cyl','PN_SurgicalMachine_DrillDepthStop',(1.37,.48,1.94),(.014,.014,.10),brass,col,segments=16)
    tube('PN_SurgicalMachine_DrillCable',[(1.61,.84,2.24),(1.76,.90,1.75),(1.82,.85,1.12)],.008,rubber,col)
    primitive('cyl','PN_SurgicalMachine_BufferMotorBody',(2.65,.66,1.39),(.19,.19,.25),green,col,(math.pi/2,0,0),32)
    for side,sgn in [('L',-1),('R',1)]:
        primitive('cyl',f'PN_SurgicalMachine_BufferShaft_{side}',(2.65+sgn*.21,.66,1.39),(.035,.035,.18),steel,col,(0,math.pi/2,0),20)
        for layer in (-.035,0,.035):primitive('torus',f'PN_SurgicalMachine_BufferCloth_{side}_{layer}',(2.65+sgn*(.35+layer),.66,1.39),(.17,.17,.055),rubber,col,(0,math.pi/2,0),28)
        primitive('cube',f'PN_SurgicalMachine_BufferGuard_{side}',(2.65+sgn*.34,.70,1.48),(.20,.12,.055),green,col,(0,0,sgn*.05))

def cam(name,loc,target,lens=75):
    d=bpy.data.cameras.get(name+'_Data') or bpy.data.cameras.new(name+'_Data');o=bpy.data.objects.get(name) or bpy.data.objects.new(name,d)
    if not o.users_collection:bpy.context.scene.collection.objects.link(o)
    o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;return o

def render(name,camera,samples=72):
    s=bpy.context.scene;s.camera=camera;s.render.resolution_x=1536;s.render.resolution_y=1024;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=os.path.join(RDIR,name)
    t=time.time();bpy.ops.render.render(write_still=True);return round(time.time()-t,2)

def montage(paths,out):
    ims=[]
    for p in paths:
        im=bpy.data.images.load(p,check_existing=False)
        if tuple(im.size)!=(1536,1024):im.scale(1536,1024)
        ims.append(im)
    w=1536;h=1024;dst=bpy.data.images.new('PN_SurgicalMontage',width=w*len(ims),height=h,alpha=True);pix=[0.0]*(w*len(ims)*h*4);rr=w*len(ims)*4;r=w*4
    arrays=[list(i.pixels) for i in ims]
    for y in range(h):
        for j,a in enumerate(arrays):pix[y*rr+j*r:y*rr+(j+1)*r]=a[y*r:(y+1)*r]
    dst.pixels=pix;dst.filepath_raw=out;dst.file_format='PNG';dst.save()
    for i in ims:bpy.data.images.remove(i)
    bpy.data.images.remove(dst)

def metrics():
    d=bpy.context.evaluated_depsgraph_get();t=p=v=0
    for o in bpy.context.scene.objects:
        if o.hide_render or o.type not in {'MESH','CURVE'}:continue
        try:e=o.evaluated_get(d);m=e.to_mesh();m.calc_loop_triangles();t+=len(m.loop_triangles);p+=len(m.polygons);v+=len(m.vertices);e.to_mesh_clear()
        except:pass
    return v,p,t

def main():
    s=bpy.context.scene;approved=bpy.data.objects['PN_Camera_Desktop'];assert tuple(round(x,2) for x in approved.location)==(0,-11.15,2.52) and approved.data.lens==52
    rebuild_hero();refine_laterals();tile_texture();refine_machinery();s.camera=approved;bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    times={};mainp=os.path.join(RDIR,'surgical-main.png');times['main']=render('surgical-main.png',approved,96)
    cameras={
      'surgical-hero-front.png':cam('PN_Cam_SurgicalHeroFront',(0,-3.0,1.44),(0,.26,1.38),88),
      'surgical-hero-three-quarter.png':cam('PN_Cam_SurgicalHero3Q',(.68,-2.62,1.62),(0,.27,1.38),82),
      'surgical-hero-side.png':cam('PN_Cam_SurgicalHeroSide',(.92,-.72,1.56),(0,.29,1.38),76),
      'surgical-tile-closeup.png':cam('PN_Cam_SurgicalTile',(1.25,-3.05,1.42),(1.0,-.16,.08),64),
      'surgical-drill-press.png':cam('PN_Cam_SurgicalDrill',(1.42,-2.30,1.82),(1.48,.60,1.80),80),
      'surgical-buffer.png':cam('PN_Cam_SurgicalBuffer',(2.30,-2.25,1.56),(2.65,.62,1.40),82),
      'surgical-nine-eyewear-diagnostic.png':cam('PN_Cam_SurgicalNine',(0,-7.0,2.65),(0,.65,2.13),56)}
    for f,c in cameras.items():times[f]=render(f,c,72)
    montage([TARGET,mainp],os.path.join(RDIR,'surgical-camera-comparison.png'))
    montage([os.path.join(RDIR,'hero-before-surgical.png'),os.path.join(RDIR,'surgical-hero-front.png')],os.path.join(RDIR,'surgical-hero-before-after.png'))
    montage([os.path.join(RDIR,'tile-before-surgical.png'),TILEREF,os.path.join(RDIR,'surgical-tile-closeup.png')],os.path.join(RDIR,'surgical-tile-before-reference-after.png'))
    s.camera=approved;v,p,t=metrics();s['PN_SurgicalMetrics']=f'vertices={v}, polygons={p}, triangles={t}';s['PN_SurgicalRenderTimes']=str(times);s['PN_CriolloTexture']='1024x1024 original authored texture; reference used only for composition/palette.';bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print('PN_SURGICAL',v,p,t,times);print('PN_CAMERA',tuple(approved.location),approved.data.lens)

if __name__=='__main__':main()
