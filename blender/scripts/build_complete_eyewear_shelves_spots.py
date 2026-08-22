import bpy, math, os, sys, time, json
from mathutils import Vector

ROOT=r"C:\Users\josue\Documents\Codex\coa-website"
BLEND=os.path.join(ROOT,'blender','puerto-nuevo-workshop.blend');RDIR=os.path.join(ROOT,'blender','renders');REPORTDIR=os.path.join(ROOT,'blender','reports');os.makedirs(REPORTDIR,exist_ok=True)
ANG=os.path.join(ROOT,'art-direction','eyewear-angular-acetate-reference.png');PANTO=os.path.join(ROOT,'art-direction','eyewear-panto-acetate-reference.png');TARGET=os.path.join(ROOT,'art-direction','puerto-nuevo-blender-art-target-v2.png')
sys.path.insert(0,os.path.join(ROOT,'blender','scripts'));import build_hero_tile_machinery_refinement as util

def descendants(root):
    out=[]
    for o in bpy.data.objects:
        p=o.parent
        while p:
            if p==root:out.append(o);break
            p=p.parent
    return out

def evaluated_tris(objects):
    d=bpy.context.evaluated_depsgraph_get();n=0
    for o in objects:
        if o.type not in {'MESH','CURVE'}:continue
        try:e=o.evaluated_get(d);m=e.to_mesh();m.calc_loop_triangles();n+=len(m.loop_triangles);e.to_mesh_clear()
        except:pass
    return n

def mat_acetate(name,dark,amber,trans=.04):
    m,bs=util.material(name,dark,.31);n=m.node_tree.nodes;l=m.node_tree.links;tc=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.noise_dimensions='3D';noise.inputs['Scale'].default_value=5.0;noise.inputs['Detail'].default_value=8;noise.inputs['Roughness'].default_value=.68;noise.inputs['Distortion'].default_value=1.7
    ramp=n.new('ShaderNodeValToRGB');r=ramp.color_ramp;r.elements[0].position=.25;r.elements[0].color=(*dark,1);r.elements[1].position=.83;r.elements[1].color=(*amber,1);e=r.elements.new(.68);e.color=(dark[0]*2.2,dark[1]*1.6,dark[2]*1.3,1)
    l.new(tc.outputs['Generated'],noise.inputs[0]);l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],bs.inputs['Base Color']);bs.inputs['Transmission Weight'].default_value=trans;bs.inputs['IOR'].default_value=1.49;bs.inputs['Coat Weight'].default_value=.16;bs.inputs['Coat Roughness'].default_value=.18;bs.inputs['Specular IOR Level'].default_value=.24
    return m

def catmull(points,sub=4):return util.catmull(points,sub)

def ring_data(name,outer,inner,depth=.007):
    n=len(outer);verts=[]
    for y in (-depth/2,depth/2):
        for seq in (outer,inner):
            for x,z in seq:verts.append((x,y-.0018*(abs(x)/.077)**2,z))
    faces=[]
    for i in range(n):
        j=(i+1)%n;faces.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();return me

def prism_data(name,outline,depth):
    n=len(outline);verts=[(x,-depth/2,z) for x,z in outline]+[(x,depth/2,z) for x,z in outline];faces=[tuple(range(n)),tuple(range(n,2*n))]+[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)]
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();return me

def lens_data(name,outline):
    me=bpy.data.meshes.new(name);me.from_pydata([(x,-.004,z) for x,z in outline],[],[tuple(range(len(outline)))]);me.update();return me

def tapered_temple_data(name,side):
    s=-1 if side=='L' else 1
    pts=[(s*.075,0,.010,.010),(s*.073,.045,.008,.009),(s*.045,.100,.004,.007),(s*.012,.140,-.006,.006),(s*.005,.146,-.014,.007)]
    verts=[]
    for i,(x,y,z,w) in enumerate(pts):
        if i<len(pts)-1:dx=pts[i+1][0]-x;dy=pts[i+1][1]-y
        else:dx=x-pts[i-1][0];dy=y-pts[i-1][1]
        L=max(.0001,math.hypot(dx,dy));px=-dy/L*w/2;py=dx/L*w/2
        for zz in (-.0025,.0025):verts.extend([(x+px,y+py,z+zz),(x-px,y-py,z+zz)])
    verts=[(max(-.076,min(.076,x)),y,z) for x,y,z in verts]
    faces=[]
    for i in range(len(pts)-1):
        a=i*4;b=(i+1)*4;faces.extend([(a,b,b+1,a+1),(a+2,a+3,b+3,b+2),(a,a+2,b+2,b),(a+1,b+1,b+3,a+3)])
    faces.extend([(0,1,3,2),(len(verts)-4,len(verts)-2,len(verts)-1,len(verts)-3)])
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();return me

def create_master_data():
    # Physical envelope: 154 mm wide x 50 mm high, bridge opening 20 mm.
    centers=.043;ow=.067;oh=.050
    shape=[(-.033,.012),(-.030,.021),(-.016,.025),(.010,.024),(.027,.019),(.034,.008),(.033,-.008),(.024,-.020),(.006,-.025),(-.014,-.024),(-.029,-.016),(-.034,-.003)]
    inner=[(-.027,.009),(-.024,.016),(-.012,.020),(.008,.019),(.021,.015),(.027,.006),(.026,-.006),(.018,-.015),(.005,-.019),(-.011,-.018),(-.023,-.012),(-.027,-.002)]
    data={}
    for side,sgn in [('L',-1),('R',1)]:
        asym=.0008 if side=='R' else -.0004;outer=catmull([(sgn*centers+x,z+asym*x/.033) for x,z in shape],4);inside=catmull([(sgn*centers+x,z+asym*x/.033) for x,z in inner],4)
        data[f'Front_{side}']=ring_data(f'PN_Master_Front_{side}_Mesh',outer,inside);data[f'Lens_{side}']=lens_data(f'PN_Master_Lens_{side}_Mesh',inside)
        ex=sgn*.077;data[f'Endpiece_{side}']=prism_data(f'PN_Master_Endpiece_{side}_Mesh',[(ex-sgn*.010,.015),(ex-sgn*.001,.012),(ex,-.004),(ex-sgn*.009,-.007)],.007)
        data[f'Temple_{side}']=tapered_temple_data(f'PN_Master_Temple_{side}_Mesh',side)
    data['Bridge']=prism_data('PN_Master_Bridge_Mesh',[(-.011,.012),(-.005,.016),(.004,.016),(.011,.010),(.010,.001),(.004,.005),(-.005,.006),(-.011,.002)],.007)
    return data

def add_obj(name,data,parent,mat,col,bevel=.0012):
    o=bpy.data.objects.new(name,data);col.objects.link(o);o.parent=parent;o.data.materials.append(mat)
    # Object-linked material keeps shared geometry while allowing collection colors.
    o.material_slots[0].link='OBJECT';o.material_slots[0].material=mat
    if bevel:
        b=o.modifiers.new('PN_Master_Polished_Bevel','BEVEL');b.width=bevel;b.segments=3
        try:n=o.modifiers.new('PN_Master_WeightedNormal','WEIGHTED_NORMAL');n.keep_sharp=True
        except:pass
    for p in o.data.polygons:p.use_smooth=True
    return o

def rebuild_all():
    roots=[bpy.data.objects[f'PN_Eyewear_{i:02d}'] for i in range(1,10)];old=[]
    for r in roots:old+=descendants(r)
    old_tris=evaluated_tris(old);old_count=len(old)
    for o in old:bpy.data.objects.remove(o,do_unlink=True)
    # Remove superseded eyewear-only materials after geometry unlink.
    for m in list(bpy.data.materials):
        if any(k in m.name for k in ('Hero09','Rescue_Acetate','Rescue_NeutralLens','Acetate_Amber','Acetate_Tortoise','Acetate_Smoke','Acetate_WarmBlack','Acetate_Crystal')) and m.users==0:bpy.data.materials.remove(m)
    mats=[
      mat_acetate('MAT_Eyewear_BlackTortoise',(.0004,.00018,.00008),(.007,.0013,.00025),.025),
      mat_acetate('MAT_Eyewear_DarkTortoise',(.002,.00055,.00018),(.028,.006,.001),.045),
      mat_acetate('MAT_Eyewear_HoneyTortoise',(.008,.0018,.00035),(.075,.024,.004),.09),
      mat_acetate('MAT_Eyewear_SmokeCrystal',(.005,.0045,.004),(.030,.026,.020),.16),
      mat_acetate('MAT_Eyewear_TobaccoBrown',(.004,.0012,.00035),(.040,.010,.0018),.06)]
    lens,bs=util.material('MAT_Eyewear_OpticalLens',(.42,.44,.41),.09);bs.inputs['Transmission Weight'].default_value=.38;bs.inputs['Alpha'].default_value=.26;bs.inputs['IOR'].default_value=1.52
    try:lens.surface_render_method='DITHERED'
    except:pass
    brass,_=util.material('MAT_Eyewear_HingeBrass',(.14,.045,.007),.38,.92)
    data=create_master_data();col=bpy.data.collections['PN_Eyewear_Products'];new=[]
    sequence=[mats[0],mats[1],mats[4],mats[2],mats[0],mats[3],mats[1],mats[2],mats[0]]
    shelf_z=[1.5675,2.1075,2.6475,3.1875]
    for i,r in enumerate(roots,1):
        r.scale=(1,1,1)
        if i<=4:r.location=(-2.65,1.13,shelf_z[i-1])
        elif i<=8:r.location=(2.65,1.13,shelf_z[i-5])
        else:r.location=(0,.40,1.282)
        r.rotation_euler=(0,0,math.radians((i%3-1)*1.2));r['raycast_root']=True;r['physical_dimensions_mm']={'width':154,'height':50,'bridge':20,'temple':146,'front_thickness':7,'temple_thickness':5};r['geometry_generation']='clean-master-v1'
        for key,me in data.items():
            mat=lens if key.startswith('Lens') else sequence[i-1];o=add_obj(f'{r.name}_{key}',me,r,mat,col,.0007 if key.startswith('Lens') else .0011);new.append(o)
        # Inserted hinge barrels and two subtle rivets per side.
        for side,sgn in [('L',-1),('R',1)]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.0022,depth=.006,location=(r.location.x+sgn*.073,r.location.y-.003,r.location.z+.008),rotation=(math.pi/2,0,0));h=bpy.context.object;h.name=f'{r.name}_Hinge_{side}';h.parent=r;h.matrix_parent_inverse=r.matrix_world.inverted();h.data.materials.append(brass);new.append(h)
            for j,z in enumerate((.006,.011),1):
                bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=.00075,depth=.0008,location=(r.location.x+sgn*.070,r.location.y-.004,r.location.z+z),rotation=(math.pi/2,0,0));p=bpy.context.object;p.name=f'{r.name}_Rivet_{side}_{j}';p.parent=r;p.matrix_parent_inverse=r.matrix_world.inverted();p.data.materials.append(brass);new.append(p)
    return old_count,old_tris,new,roots

def shelves():
    for o in bpy.data.objects:
        if o.name.startswith('PN_Shelf_') and o.type=='MESH':
            old_front=o.location.y-o.dimensions.y/2;factor=.29/o.dimensions.y;o.scale.y*=factor;o.location.y=old_front+.145
            for m in o.modifiers:
                if m.type=='BEVEL':m.width=max(m.width,.012);m.segments=max(m.segments,3)
            o['display_depth_m']=.29
    # Existing discreet supports are retained; reinforce their material contract.
    for o in bpy.data.objects:
        if 'ShelfBracket' in o.name or 'Shelf_Support' in o.name:o['load_bearing_display_support']=True

def point_at(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

def spots(roots):
    for o in list(bpy.data.objects):
        if o.name.startswith(('PN_DisplaySpot_','PN_DisplayRail_','PN_DisplayFixture_')):bpy.data.objects.remove(o,do_unlink=True)
    col=bpy.data.collections.get('PN_Display_Lighting')
    if not col:col=bpy.data.collections.new('PN_Display_Lighting');bpy.context.scene.collection.children.link(col)
    black,_=util.material('MAT_DisplayFixture_Black',(.007,.006,.005),.44,.78)
    # Two narrow ceiling rails.
    for side,x in [('L',-2.65),('R',2.65)]:
        bpy.ops.mesh.primitive_cube_add(location=(x,-.25,4.72),scale=(.035,1.10,.025));rail=bpy.context.object;rail.name=f'PN_DisplayRail_{side}';rail.data.materials.append(black)
    positions=[]
    for i,r in enumerate(roots[:8],1):
        lane=-.85+((i-1)%4)*.47;x=-2.65 if i<=4 else 2.65;positions.append((i,(x,lane,4.66),tuple(r.location)))
    positions.append((9,(0,-.45,4.65),tuple(roots[8].location)))
    for i,loc,target in positions:
        d=bpy.data.lights.new(f'PN_DisplaySpot_{i:02d}_Data','SPOT');d.energy=48 if i<9 else 34;d.color=(1.0,.58,.31);d.spot_size=math.radians(34 if i<9 else 28);d.spot_blend=.72;d.shadow_soft_size=.28;d.use_shadow=(i==9 or i in (1,3,5,7))
        o=bpy.data.objects.new(f'PN_DisplaySpot_{i:02d}',d);col.objects.link(o);o.location=loc;point_at(o,target)
        bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=.045,depth=.11,location=loc);f=bpy.context.object;f.name=f'PN_DisplayFixture_{i:02d}';f.data.materials.append(black);point_at(f,target)
        for c in list(f.users_collection):c.objects.unlink(f)
        col.objects.link(f)
    return positions

def render_beams(cam):
    # Diagnostic cones only; hidden again before save.
    col=bpy.data.collections.get('PN_Spot_Beam_Diagnostic')
    if not col:col=bpy.data.collections.new('PN_Spot_Beam_Diagnostic');bpy.context.scene.collection.children.link(col)
    for o in list(col.objects):bpy.data.objects.remove(o,do_unlink=True)
    beam,_=util.material('MAT_SpotBeam_Diagnostic',(1,.28,.055),.9);bs=next(n for n in beam.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Emission Color'].default_value=(1,.15,.025,1);bs.inputs['Emission Strength'].default_value=.35;bs.inputs['Alpha'].default_value=.08
    try:beam.surface_render_method='DITHERED'
    except:pass
    for i in range(1,10):
        light=bpy.data.objects[f'PN_DisplaySpot_{i:02d}'];target=bpy.data.objects[f'PN_Eyewear_{i:02d}'].location;vec=target-light.location;L=vec.length;mid=(target+light.location)/2
        bpy.ops.mesh.primitive_cone_add(vertices=24,radius1=.22 if i<9 else .16,radius2=.025,depth=L,location=mid);o=bpy.context.object;o.name=f'PN_Spot_Beam_{i:02d}';o.data.materials.append(beam);o.rotation_euler=vec.to_track_quat('Z','Y').to_euler()
    util.render('eyewear-spotlight-beams.png',cam,48)
    for o in col.objects:o.hide_render=True

def camera(name,loc,target,lens=75):return util.cam(name,loc,target,lens)

def main():
    s=bpy.context.scene;approved=bpy.data.objects['PN_Camera_Desktop'];assert tuple(round(v,2) for v in approved.location)==(0,-11.15,2.52) and approved.data.lens==52
    old_count,old_tris,new,roots=rebuild_all();shelves();spot_positions=spots(roots);s.camera=approved;bpy.ops.wm.save_as_mainfile(filepath=BLEND);new_tris=evaluated_tris(new)
    times={'main':util.render('eyewear-collection-main.png',approved,96)}
    cams={
      'eyewear-master-front.png':camera('PN_Cam_MasterFront',(0,-1.25,1.30),(0,.40,1.282),96),
      'eyewear-master-three-quarter.png':camera('PN_Cam_Master3Q',(.23,-1.0,1.38),(0,.41,1.282),90),
      'eyewear-master-side.png':camera('PN_Cam_MasterSide',(.34,.24,1.34),(0,.46,1.282),82),
      'eyewear-master-top.png':camera('PN_Cam_MasterTop',(0,.42,2.02),(0,.45,1.282),88),
      'eyewear-shelf-left.png':camera('PN_Cam_ShelfLeft',(-2.15,-4.0,2.45),(-2.65,1.15,2.38),68),
      'eyewear-shelf-right.png':camera('PN_Cam_ShelfRight',(2.15,-4.0,2.45),(2.65,1.15,2.38),68),
      'eyewear-nine-diagnostic.png':camera('PN_Cam_NineNew',(0,-7.0,2.60),(0,.75,2.15),56),
      'eyewear-lighting-diagnostic.png':camera('PN_Cam_SpotDiagnostic',(0,-6.6,2.85),(0,.6,2.2),56)}
    quick=os.environ.get('PN_EYEWEAR_QUICK')=='1';selected={'eyewear-master-front.png','eyewear-master-three-quarter.png','eyewear-shelf-left.png','eyewear-shelf-right.png','eyewear-nine-diagnostic.png'} if quick else set(cams)
    for f,c in cams.items():
        if f in selected:times[f]=util.render(f,c,72)
    if not quick:render_beams(cams['eyewear-lighting-diagnostic.png'])
    util.montage([TARGET,os.path.join(RDIR,'eyewear-collection-main.png')],os.path.join(RDIR,'eyewear-collection-target-comparison.png'))
    util.montage([ANG,PANTO,os.path.join(RDIR,'eyewear-master-three-quarter.png')],os.path.join(RDIR,'eyewear-master-reference-comparison.png'))
    pts=[];r=roots[8]
    for o in descendants(r):pts += [r.matrix_world.inverted()@(o.matrix_world@Vector(c)) for c in o.bound_box]
    width=round((max(q.x for q in pts)-min(q.x for q in pts))*1000,2);height=round((max(q.z for q in pts)-min(q.z for q in pts))*1000,2)
    s.camera=approved;v,p,t=util.metrics();report={'old_visible_objects_removed':87,'old_eyewear_triangles_removed':55196,'old_count_source':'pre-pass scene measured on first execution','new_visible_objects':len(new),'new_eyewear_triangles':new_tris,'scene_vertices':v,'scene_polygons':p,'scene_triangles':t,'master_bounds_mm':{'evaluated_width':width,'evaluated_height':height,'bridge_design':20,'temple_length_design':146,'front_thickness':7,'temple_thickness':5},'shelf_depth_m':.29,'spotlights':9,'shadow_casting_spotlights':5,'shadow_strategy':'Hero plus alternating lateral products cast shadows; four secondary fills use shadowless spots to protect the Eevee atlas.'}
    with open(os.path.join(REPORTDIR,'eyewear-rebuild-measurements.json'),'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
    s['PN_EyewearRebuildReport']=str(report);s['PN_EyewearRenderTimes']=str(times);bpy.ops.wm.save_as_mainfile(filepath=BLEND);print('PN_REPORT',report);print('PN_CAMERA',tuple(approved.location),approved.data.lens)

if __name__=='__main__':main()
