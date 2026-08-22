import bpy, math, os, sys, time, json
from mathutils import Vector

ROOT=r"C:\Users\josue\Documents\Codex\coa-website"
BLEND=os.path.join(ROOT,'blender','puerto-nuevo-workshop.blend');RDIR=os.path.join(ROOT,'blender','renders');REPORTDIR=os.path.join(ROOT,'blender','reports');os.makedirs(REPORTDIR,exist_ok=True)
REF=os.path.join(ROOT,'art-direction','puerto-nuevo-eyewear-master-orthographic-v1.png')
sys.path.insert(0,os.path.join(ROOT,'blender','scripts'));import build_hero_tile_machinery_refinement as util

def collection(name,parent=None):
    c=bpy.data.collections.get(name)
    if c:
        for o in list(c.objects):bpy.data.objects.remove(o,do_unlink=True)
        return c
    c=bpy.data.collections.new(name);(parent or bpy.context.scene.collection).children.link(c);return c

def descendants(root):
    out=[]
    for o in bpy.data.objects:
        p=o.parent
        while p:
            if p==root:out.append(o);break
            p=p.parent
    return out

def clean_previous():
    removed=[]
    for i in range(1,10):
        root=bpy.data.objects[f'PN_Eyewear_{i:02d}'];removed+=descendants(root);root.scale=(1,1,1);root.rotation_euler=(0,0,0);root['raycast_root']=True
    for o in set(removed):bpy.data.objects.remove(o,do_unlink=True)
    for cname in ('PN_Eyewear_Master_Approved','PN_Eyewear_Reference_Planes'):
        c=bpy.data.collections.get(cname)
        if c:
            for o in list(c.objects):bpy.data.objects.remove(o,do_unlink=True)
    return len(set(removed))

def material_acetate():
    m,bs=util.material('MAT_Eyewear_Approved_BlackTortoise',(.00025,.00010,.00005),.30);n=m.node_tree.nodes;l=m.node_tree.links;tc=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.noise_dimensions='3D';noise.inputs['Scale'].default_value=5.8;noise.inputs['Detail'].default_value=9;noise.inputs['Roughness'].default_value=.72;noise.inputs['Distortion'].default_value=2.0
    ramp=n.new('ShaderNodeValToRGB');r=ramp.color_ramp;r.elements[0].position=.18;r.elements[0].color=(.00015,.00006,.00003,1);r.elements[1].position=.92;r.elements[1].color=(.012,.0024,.00045,1)
    for pos,col in [(.57,(.0008,.0002,.00007,1)),(.72,(.003,.00065,.00014,1)),(.82,(.009,.002,.00035,1))]:e=r.elements.new(pos);e.color=col
    l.new(tc.outputs['Generated'],noise.inputs[0]);l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],bs.inputs['Base Color']);bs.inputs['Transmission Weight'].default_value=.035;bs.inputs['IOR'].default_value=1.49;bs.inputs['Coat Weight'].default_value=.13;bs.inputs['Coat Roughness'].default_value=.17;bs.inputs['Specular IOR Level'].default_value=.22
    return m

def catmull(points,sub=6):return util.catmull(points,sub)

def ring_mesh(name,outer,inner,depth=.007):
    n=len(outer);verts=[]
    for y in (-depth/2,depth/2):
        for seq in (outer,inner):
            for x,z in seq:
                # 4 mm total frontal wrap from center to endpiece.
                yy=y-.0020*(abs(x)/.0775)**2;verts.append((x,yy,z))
    faces=[]
    for i in range(n):
        j=(i+1)%n;faces.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();return me

def prism_mesh(name,outline,depth=.007):
    n=len(outline);verts=[(x,-depth/2,z) for x,z in outline]+[(x,depth/2,z) for x,z in outline];faces=[tuple(range(n)),tuple(range(n,2*n))]+[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)]
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();return me

def temple_mesh(name,side):
    s=-1 if side=='L' else 1
    # Local to hinge: broad 10 mm root, tapered shaft and down-curved terminal.
    pts=[(0,0,.009,.010),(s*.003,.040,.009,.009),(s*.005,.090,.007,.0075),(s*.010,.125,.003,.0065),(s*.018,.143,-.010,.007)]
    verts=[]
    for i,(x,y,z,w) in enumerate(pts):
        if i<len(pts)-1:dx=pts[i+1][0]-x;dy=pts[i+1][1]-y
        else:dx=x-pts[i-1][0];dy=y-pts[i-1][1]
        L=max(.0001,math.hypot(dx,dy));px=-dy/L*w/2;py=dx/L*w/2
        for zz in (-.0025,.0025):verts.extend([(x+px,y+py,z+zz),(x-px,y-py,z+zz)])
    faces=[]
    for i in range(len(pts)-1):
        a=i*4;b=(i+1)*4;faces.extend([(a,b,b+1,a+1),(a+2,a+3,b+3,b+2),(a,a+2,b+2,b),(a+1,b+1,b+3,a+3)])
    faces.extend([(0,1,3,2),(len(verts)-4,len(verts)-2,len(verts)-1,len(verts)-3)])
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();return me

def create_data():
    # Traced from approved frontal orthographic: panto opening with angular brow.
    centers=.0435
    outer=[(-.034,.007),(-.032,.016),(-.023,.022),(-.010,.025),(.010,.025),(.023,.021),(.032,.014),(.034,.004),(.032,-.009),(.025,-.019),(.013,-.024),(-.002,-.025),(-.017,-.022),(-.028,-.014),(-.034,-.003)]
    inner=[(-.027,.006),(-.025,.013),(-.017,.0175),(-.007,.019),(.008,.019),(.018,.016),(.025,.010),(.027,.002),(.025,-.008),(.019,-.015),(.009,-.019),(-.003,-.0195),(-.014,-.017),(-.022,-.011),(-.027,-.002)]
    data={}
    for side,sgn in [('L',-1),('R',1)]:
        asym=.00035 if side=='R' else -.0002;out=catmull([(sgn*centers+x,z+asym*x/.034) for x,z in outer]);inside=catmull([(sgn*centers+x,z+asym*x/.027) for x,z in inner])
        data[f'Front_{side}']=ring_mesh(f'PN_Approved_Front_{side}_Mesh',out,inside);data[f'Lens_{side}']=prism_mesh(f'PN_Approved_Lens_{side}_Mesh',inside,.003)
        ex=sgn*.0775;data[f'Endpiece_{side}']=prism_mesh(f'PN_Approved_Endpiece_{side}_Mesh',[(ex-sgn*.009,.015),(ex,.012),(ex,-.004),(ex-sgn*.008,-.007)],.007)
        data[f'Temple_{side}']=temple_mesh(f'PN_Approved_Temple_{side}_Mesh',side)
    # Sculpted saddle bridge with subtle upper depressions.
    data['Bridge']=prism_mesh('PN_Approved_Bridge_Mesh',[(-.012,.012),(-.008,.016),(-.003,.013),(.003,.013),(.008,.016),(.012,.011),(.011,.002),(.006,.006),(-.006,.006),(-.011,.002)],.007)
    return data

def add(name,data,parent,mat,col,bevel=.001):
    o=bpy.data.objects.new(name,data);col.objects.link(o);o.parent=parent;data.materials.append(mat);o.material_slots[0].link='OBJECT';o.material_slots[0].material=mat
    b=o.modifiers.new('PN_Approved_PolishedBevel','BEVEL');b.width=bevel;b.segments=4
    try:w=o.modifiers.new('PN_Approved_WeightedNormal','WEIGHTED_NORMAL');w.keep_sharp=True
    except:pass
    for p in data.polygons:p.use_smooth=True
    return o

def build_master():
    col=collection('PN_Eyewear_Master_Approved');physical=bpy.data.objects.new('PN_Eyewear_Master_Physical',None);physical.empty_display_type='CUBE';physical.empty_display_size=.02;physical['scale_mode']='physical_1_to_1';physical['dimensions_mm']={'width':155,'height':50,'bridge':20,'temple':146,'front_thickness':7,'temple_thickness':5};col.objects.link(physical)
    data=create_data();ac=material_acetate();lens,bs=util.material('MAT_Eyewear_Approved_Lens',(.39,.41,.39),.09);bs.inputs['Transmission Weight'].default_value=.40;bs.inputs['Alpha'].default_value=.24;bs.inputs['IOR'].default_value=1.52
    try:lens.surface_render_method='DITHERED'
    except:pass
    metal,_=util.material('MAT_Eyewear_Approved_Hardware',(.18,.055,.009),.34,.92)
    physical_parts=[]
    for key,me in data.items():physical_parts.append(add('PN_Approved_Physical_'+key,me,physical,lens if key.startswith('Lens') else ac,col,.00055 if key.startswith('Lens') else .0010))
    # Temples are local to their inserted hinge positions.
    for side,sgn in [('L',-1),('R',1)]:
        t=next(o for o in physical_parts if o.name.endswith('Temple_'+side));t.location=(sgn*.075,0,0)
        bpy.ops.mesh.primitive_cylinder_add(vertices=14,radius=.0022,depth=.006,location=(sgn*.074,-.001,.009),rotation=(math.pi/2,0,0));h=bpy.context.object;h.name='PN_Approved_Physical_Hinge_'+side;h.parent=physical;h.data.materials.append(metal)
        for j,z in enumerate((.007,.012),1):
            bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.00075,depth=.0008,location=(sgn*.071,-.004,z),rotation=(math.pi/2,0,0));r=bpy.context.object;r.name=f'PN_Approved_Physical_Rivet_{side}_{j}';r.parent=physical;r.data.materials.append(metal)
    # Source stays in the collection but never renders in the workshop.
    for o in descendants(physical):o.hide_render=True
    physical.hide_render=True
    root=bpy.data.objects['PN_Eyewear_09'];root.location=(0,.40,1.31);display=bpy.data.objects.new('PN_Eyewear_Master_Display',None);display.parent=root;display.scale=(2.25,2.25,2.25);display['scale_mode']='editorial_instance_2.25x';display['source']='PN_Eyewear_Master_Physical';col.objects.link(display)
    display_parts=[]
    for src in descendants(physical):
        if src.type!='MESH':continue
        srcmat=src.active_material
        o=bpy.data.objects.new(src.name.replace('Physical','Display'),src.data);col.objects.link(o);o.parent=display;o.matrix_local=src.matrix_local.copy();o.hide_render=False
        if srcmat and o.material_slots:o.material_slots[0].link='OBJECT';o.material_slots[0].material=srcmat
        for mod in src.modifiers:
            nm=o.modifiers.new(mod.name,mod.type)
            if mod.type=='BEVEL':nm.width=mod.width;nm.segments=mod.segments
            elif mod.type=='WEIGHTED_NORMAL':nm.keep_sharp=True
        display_parts.append(o)
    # Fold display temples naturally without touching source mesh.
    for side,angle in [('L',math.radians(-72)),('R',math.radians(72))]:
        o=next(x for x in display_parts if x.name.endswith('Temple_'+side));o.rotation_euler[2]=angle
    root['approved_master_instance']='PN_Eyewear_Master_Display';root['raycast_root']=True
    return physical,display,physical_parts,display_parts

def reference_planes():
    col=collection('PN_Eyewear_Reference_Planes');img=bpy.data.images.load(REF,check_existing=True)
    specs=[('Front',(0,.25,0),(.0,0,0)),('Side',(.32,0,0),(math.pi/2,0,math.pi/2)),('Top',(0,0,.32),(0,0,0))]
    for label,loc,rot in specs:
        o=bpy.data.objects.new('PN_Approved_Reference_'+label,None);o.empty_display_type='IMAGE';o.data=img;o.location=loc;o.rotation_euler=rot;o.empty_display_size=.31;o.color[3]=.45;o.hide_render=True;col.objects.link(o)

def point_at(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

def hero_spot(display):
    spot=bpy.data.objects.get('PN_DisplaySpot_09')
    if spot:spot.data.energy=22;spot.data.spot_size=math.radians(28);spot.data.spot_blend=.82;spot.data.shadow_soft_size=.36;point_at(spot,bpy.data.objects['PN_Eyewear_09'].location)

def bounds(root):
    pts=[]
    for o in descendants(root):
        if o.type=='MESH':pts += [root.matrix_world.inverted()@(o.matrix_world@Vector(c)) for c in o.bound_box]
    return tuple(round((max(getattr(p,a) for p in pts)-min(getattr(p,a) for p in pts))*1000,2) for a in ('x','y','z'))

def studio_render(name,physical,camloc,target,lens=72,wire=False):
    s=bpy.context.scene;hidden={o:o.hide_render for o in s.objects};phys=descendants(physical)
    for o in s.objects:o.hide_render=o not in phys
    physical.hide_render=False
    for o in phys:o.hide_render=False;o.show_wire=wire;o.show_all_edges=wire
    cam=util.cam('PN_Cam_'+name,camloc,target,lens);old=s.render.engine
    # Dedicated neutral studio lights prevent the isolated product from rendering black.
    temp=[]
    for j,(loc,energy,size) in enumerate([((-.22,-.28,.28),260,0.32),((.25,-.05,.18),150,0.22)]):
        d=bpy.data.lights.new('PN_TempStudio_Data','AREA');d.energy=energy;d.shape='DISK';d.size=size;o=bpy.data.objects.new('PN_TempStudio',d);s.collection.objects.link(o);o.location=loc;point_at(o,(0,.04,0));temp.append(o)
    if wire:s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='OBJECT';s.display.shading.show_shadows=True
    util.render(name+'.png',cam,64)
    s.render.engine=old
    for o,v in hidden.items():o.hide_render=v
    for o in phys:o.show_wire=False;o.show_all_edges=False
    for o in temp:bpy.data.objects.remove(o,do_unlink=True)

def main():
    s=bpy.context.scene;approved=bpy.data.objects['PN_Camera_Desktop'];assert tuple(round(v,2) for v in approved.location)==(0,-11.15,2.52) and approved.data.lens==52
    removed=clean_previous();reference_planes();physical,display,pparts,dparts=build_master();hero_spot(display)
    for o in bpy.data.objects:
        if o.name.startswith('PN_Spot_Beam_'):o.hide_render=True
    s.camera=approved;bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    # Orthographic-style studio views of the 1:1 physical source.
    studio_render('approved-master-front',physical,(0,-.48,0),(0,0,0),76)
    studio_render('approved-master-side',physical,(.48,0,.005),(0,.06,0),76)
    studio_render('approved-master-top',physical,(0,.06,.48),(0,.06,0),76)
    studio_render('approved-master-three-quarter',physical,(.30,-.38,.18),(0,.04,0),72)
    studio_render('approved-master-hinge-closeup',physical,(.15,-.18,.055),(.073,0,.009),95)
    studio_render('approved-master-tortoise-closeup',physical,(.06,-.18,.035),(.02,0,.008),105)
    studio_render('approved-master-wireframe',physical,(0,-.45,.03),(0,0,0),76,True)
    # Workshop hero and physical/editorial scale diagnostic.
    s.camera=approved;util.render('approved-master-hero-main.png',approved,96)
    diag=util.cam('PN_Cam_ApprovedScale',(.25,-1.25,1.42),(0,.4,1.31),72);util.render('approved-master-scale-comparison.png',diag,72)
    util.montage([REF,os.path.join(RDIR,'approved-master-front.png')],os.path.join(RDIR,'approved-master-front-comparison.png'))
    util.montage([REF,os.path.join(RDIR,'approved-master-side.png')],os.path.join(RDIR,'approved-master-side-comparison.png'))
    util.montage([REF,os.path.join(RDIR,'approved-master-top.png')],os.path.join(RDIR,'approved-master-top-comparison.png'))
    util.montage([REF,os.path.join(RDIR,'approved-master-three-quarter.png')],os.path.join(RDIR,'approved-master-three-quarter-comparison.png'))
    util.montage([os.path.join(RDIR,'approved-master-front.png'),os.path.join(RDIR,'approved-master-scale-comparison.png')],os.path.join(RDIR,'approved-master-physical-editorial-comparison.png'))
    # Silhouette overlay uses the frontal studio render against the approved sheet.
    ref=bpy.data.images.load(REF,check_existing=False);ren=bpy.data.images.load(os.path.join(RDIR,'approved-master-front.png'),check_existing=False);ref.scale(1536,1024);ren.scale(1536,1024)
    import numpy as np
    ra=np.array(ref.pixels[:],np.float32).reshape(1024,1536,4);ga=np.array(ren.pixels[:],np.float32).reshape(1024,1536,4);rm=ra[:,:,:3].mean(2)<.72;gm=ga[:,:,:3].mean(2)<.35;out=np.ones((1024,1536,3),np.float32);out[rm]=(.95,.25,.16);out[gm]=out[gm]*.38+np.array((.10,.38,.95))*.62
    im=bpy.data.images.new('PN_ApprovedOverlay',1536,1024,alpha=True);rgba=np.ones((1024,1536,4),np.float32);rgba[:,:,:3]=out;im.pixels.foreach_set(rgba.ravel());im.update();im.filepath_raw=os.path.join(RDIR,'approved-master-front-overlay.png');im.file_format='PNG';im.save()
    dims=bounds(physical);front_pts=[]
    for o in descendants(physical):
        if o.type=='MESH' and any(k in o.name for k in ('Front_','Endpiece_','Bridge')):front_pts += [physical.matrix_world.inverted()@(o.matrix_world@Vector(c)) for c in o.bound_box]
    front_width=round((max(p.x for p in front_pts)-min(p.x for p in front_pts))*1000,2)
    deps=bpy.context.evaluated_depsgraph_get();polys=tris=verts=0
    for o in descendants(physical):
        if o.type!='MESH':continue
        e=o.evaluated_get(deps);m=e.to_mesh();m.calc_loop_triangles();verts+=len(m.vertices);polys+=len(m.polygons);tris+=len(m.loop_triangles);e.to_mesh_clear()
    report={'previous_eyewear_objects_removed':removed,'visible_new_eyewear_instances':1,'physical_bounds_mm':{'front_width':front_width,'open_total_width':dims[0],'open_depth':dims[1],'height':dims[2]},'design_dimensions_mm':{'front_width':155,'height':50,'bridge':20,'temple':146,'front_thickness':7,'temple_thickness':5},'editorial_scale':2.25,'physical_objects':len([o for o in descendants(physical) if o.type=='MESH']),'vertices':verts,'polygons':polys,'triangles':tris,'lateral_roots_visible_geometry':0}
    with open(os.path.join(REPORTDIR,'approved-eyewear-master-report.json'),'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
    s.camera=approved;s['PN_ApprovedMasterReport']=str(report);bpy.ops.wm.save_as_mainfile(filepath=BLEND);print('PN_APPROVED_MASTER',report);print('PN_CAMERA',tuple(approved.location),approved.data.lens)

if __name__=='__main__':main()
