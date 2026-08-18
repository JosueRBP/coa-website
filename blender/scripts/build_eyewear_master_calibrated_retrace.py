import bpy, math, os, sys, json, shutil
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT=r"C:\Users\josue\Documents\Codex\coa-website"
BLEND=os.path.join(ROOT,"blender","puerto-nuevo-workshop.blend")
RDIR=os.path.join(ROOT,"blender","renders"); REPORTDIR=os.path.join(ROOT,"blender","reports")
REFDIR=os.path.join(ROOT,"art-direction","eyewear-master-views")
REFS={k:os.path.join(REFDIR,f"eyewear-master-{k}-approved.png") for k in ("front","side","top","three-quarter")}
os.makedirs(RDIR,exist_ok=True); os.makedirs(REPORTDIR,exist_ok=True)
sys.path.insert(0,os.path.join(ROOT,"blender","scripts"))
import build_hero_tile_machinery_refinement as util

def descendants(root):
    out=[]
    for o in bpy.data.objects:
        p=o.parent
        while p:
            if p==root: out.append(o); break
            p=p.parent
    return out

def clear_master():
    removed=[]
    for i in range(1,10):
        r=bpy.data.objects[f"PN_Eyewear_{i:02d}"]
        removed += descendants(r); r.scale=(1,1,1); r.rotation_euler=(0,0,0)
    c=bpy.data.collections.get("PN_Eyewear_Master_Approved")
    if c: removed += list(c.objects)
    for o in set(removed):
        if o.name in bpy.data.objects: bpy.data.objects.remove(o,do_unlink=True)
    return len(set(removed))

def col(name):
    c=bpy.data.collections.get(name)
    if not c: c=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c)
    return c

def bezier_loop(curve,pts,clockwise=False):
    seq=list(reversed(pts)) if clockwise else pts
    s=curve.splines.new("BEZIER"); s.bezier_points.add(len(seq)-1); s.use_cyclic_u=True
    for b,p in zip(s.bezier_points,seq):
        b.co=(p[0],p[1],0); b.handle_left_type="AUTO"; b.handle_right_type="AUTO"
    return s

def front_mesh(collection,parent,mat):
    # Calibrated directly from the isolated 690x315 front crop at 157 mm overall.
    # X/Z coordinates preserve its bridge center, outline extrema and panto openings.
    outer=[(-.0785,.010),(-.078,.018),(-.068,.0185),(-.060,.022),(-.052,.028),(-.038,.032),(-.021,.031),(-.010,.023),(-.006,.020),(0,.0215),(.006,.020),(.010,.023),(.021,.031),(.038,.032),(.052,.028),(.060,.022),(.068,.0185),(.078,.018),(.0785,.010),(.078,-.001),(.070,-.003),(.066,-.015),(.057,-.025),(.044,-.031),(.029,-.032),(.018,-.029),(.011,-.021),(.008,-.010),(.006,.004),(0,.008),(-.006,.004),(-.008,-.010),(-.011,-.021),(-.018,-.029),(-.029,-.032),(-.044,-.031),(-.057,-.025),(-.066,-.015),(-.070,-.003),(-.078,-.001)]
    left=[(-.061,.011),(-.057,.020),(-.046,.025),(-.032,.026),(-.020,.022),(-.013,.014),(-.012,.002),(-.015,-.011),(-.023,-.022),(-.035,-.027),(-.048,-.026),(-.058,-.020),(-.064,-.010),(-.065,.001)]
    outer=[(x,z*.80) for x,z in outer];left=[(x,z*.80) for x,z in left]
    right=[(-x,z) for x,z in reversed(left)]
    cu=bpy.data.curves.new("PN_Calibrated_Front_Bezier","CURVE"); cu.dimensions="2D"; cu.resolution_u=16; cu.render_resolution_u=24; cu.fill_mode="BOTH"; cu.extrude=.0035; cu.resolution_v=2
    bezier_loop(cu,outer,False); bezier_loop(cu,left,True); bezier_loop(cu,right,True)
    o=bpy.data.objects.new("PN_Calibrated_Physical_Front",cu); collection.objects.link(o); o.parent=parent; cu.materials.append(mat)
    bpy.context.view_layer.objects.active=o; o.select_set(True); bpy.ops.object.convert(target="MESH"); o.select_set(False)
    o.rotation_euler[0]=math.pi/2
    bev=o.modifiers.new("PN_Polished_Edge","BEVEL"); bev.width=.00075; bev.segments=4
    for p in o.data.polygons:p.use_smooth=True
    return o,left,right

def acetate():
    m,bs=util.material("MAT_Eyewear_Calibrated_BlackTortoise",(.004,.0012,.00045),.24)
    n=m.node_tree.nodes;l=m.node_tree.links;tc=n.new("ShaderNodeTexCoord");noise=n.new("ShaderNodeTexNoise");noise.noise_dimensions="3D";noise.inputs["Scale"].default_value=7.0;noise.inputs["Detail"].default_value=7;noise.inputs["Roughness"].default_value=.7;noise.inputs["Distortion"].default_value=3.2
    ramp=n.new("ShaderNodeValToRGB");r=ramp.color_ramp;r.elements[0].position=.27;r.elements[0].color=(.0002,.00004,.00001,1);r.elements[1].position=.82;r.elements[1].color=(.018,.0018,.00018,1)
    for p,c in [(.52,(.001,.00015,.00003,1)),(.65,(.006,.0007,.00008,1)),(.73,(.035,.006,.0004,1))]:e=r.elements.new(p);e.color=c
    l.new(tc.outputs["Generated"],noise.inputs[0]);l.new(noise.outputs["Fac"],ramp.inputs[0]);l.new(ramp.outputs[0],bs.inputs["Base Color"])
    bs.inputs["Transmission Weight"].default_value=.10;bs.inputs["IOR"].default_value=1.49;bs.inputs["Coat Weight"].default_value=.20;bs.inputs["Coat Roughness"].default_value=.12;bs.inputs["Specular IOR Level"].default_value=.30
    return m

def lens_mesh(name,loop,collection,parent,mat):
    cu=bpy.data.curves.new(name+"_Curve","CURVE");cu.dimensions="2D";cu.resolution_u=16;cu.fill_mode="BOTH";cu.extrude=.00065
    inset=[]
    cx=sum(x for x,z in loop)/len(loop);cz=sum(z for x,z in loop)/len(loop)
    for x,z in loop: inset.append((cx+(x-cx)*.965,cz+(z-cz)*.965))
    bezier_loop(cu,inset,False);o=bpy.data.objects.new(name,cu);collection.objects.link(o);o.parent=parent;o.location.y=-.0004;cu.materials.append(mat)
    bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target="MESH");o.select_set(False);o.rotation_euler[0]=math.pi/2;return o

def temple_mesh(name,side,collection,parent,mat):
    sg=-1 if side=="L" else 1
    # Side calibration: 146 mm hinge-to-tip, 10 mm root, tapered shaft, 18 mm terminal drop.
    pts=[(sg*.074,0,.012,.010),(sg*.075,.035,.012,.009),(sg*.076,.090,.010,.008),(sg*.077,.122,.006,.007),(sg*.073,.137,-.004,.008),(sg*.066,.146,-.014,.010)]
    verts=[]
    for i,(x,y,z,w) in enumerate(pts):
        dx=(pts[min(i+1,len(pts)-1)][0]-pts[max(i-1,0)][0]);dy=(pts[min(i+1,len(pts)-1)][1]-pts[max(i-1,0)][1]);L=max(1e-5,math.hypot(dx,dy));px=-dy/L*w/2;py=dx/L*w/2
        for zz in (-.0025,.0025):verts += [(x+px,y+py,z+zz),(x-px,y-py,z+zz)]
    faces=[]
    for i in range(len(pts)-1):
        a=i*4;b=(i+1)*4;faces += [(a,b,b+1,a+1),(a+2,a+3,b+3,b+2),(a,a+2,b+2,b),(a+1,b+1,b+3,a+3)]
    faces += [(0,1,3,2),(len(verts)-4,len(verts)-2,len(verts)-1,len(verts)-3)]
    me=bpy.data.meshes.new(name+"_Mesh");me.from_pydata(verts,[],faces);me.materials.append(mat);o=bpy.data.objects.new(name,me);collection.objects.link(o);o.parent=parent
    be=o.modifiers.new("PN_Temple_Bevel","BEVEL");be.width=.0014;be.segments=4
    return o

def cylinder(name,loc,radius,depth,collection,parent,mat,rot=(math.pi/2,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=radius,depth=depth,location=loc,rotation=rot);o=bpy.context.object;o.name=name
    for c in list(o.users_collection):c.objects.unlink(o)
    collection.objects.link(o);o.parent=parent;o.data.materials.append(mat);return o

def create_master():
    c=col("PN_Eyewear_Master_Approved");physical=bpy.data.objects.new("PN_Eyewear_Master_Physical",None);c.objects.link(physical);physical["scale_mode"]="physical_1_to_1";physical["front_reference_width_mm"]=157
    ac=acetate(); lensmat,bs=util.material("MAT_Eyewear_Calibrated_Lens",(.65,.68,.66),.04);bs.inputs["Transmission Weight"].default_value=.0;bs.inputs["Alpha"].default_value=.055;bs.inputs["IOR"].default_value=1.52;bs.inputs["Coat Weight"].default_value=.04
    try:lensmat.surface_render_method="DITHERED"
    except:pass
    metal,_=util.material("MAT_Eyewear_Calibrated_Hardware",(.22,.15,.07),.28,.75)
    front,left,right=front_mesh(c,physical,ac);lens_mesh("PN_Calibrated_Physical_Lens_L",left,c,physical,lensmat);lens_mesh("PN_Calibrated_Physical_Lens_R",right,c,physical,lensmat)
    for side,sg in (("L",-1),("R",1)):
        temple_mesh("PN_Calibrated_Physical_Temple_"+side,side,c,physical,ac)
        cylinder("PN_Calibrated_Physical_Hinge_"+side,(sg*.0735,-.001,.010),.0022,.006,c,physical,metal)
        for j,z in enumerate((.008,.014),1):cylinder(f"PN_Calibrated_Physical_Rivet_{side}_{j}",(sg*(.0715+j*.0012),-.004,z),.00075,.0008,c,physical,metal)
    for o in descendants(physical):o.hide_render=True
    physical.hide_render=True
    root=bpy.data.objects["PN_Eyewear_09"];root.location=(0,.40,1.31);display=bpy.data.objects.new("PN_Eyewear_Master_Display",None);c.objects.link(display);display.parent=root;display["source"]="PN_Eyewear_Master_Physical"
    for src in descendants(physical):
        if src.type!="MESH":continue
        srcmat=src.active_material
        o=bpy.data.objects.new(src.name.replace("Physical","Display"),src.data);c.objects.link(o);o.parent=display;o.matrix_local=src.matrix_local.copy();o.hide_render=False
        if srcmat and o.material_slots:o.material_slots[0].link="OBJECT";o.material_slots[0].material=srcmat
        for md in src.modifiers:
            nm=o.modifiers.new(md.name,md.type)
            if md.type=="BEVEL":nm.width=md.width;nm.segments=md.segments
    root["approved_master_instance"]="PN_Eyewear_Master_Display"
    return physical,display

def projected_width(display,cam):
    s=bpy.context.scene;xs=[]
    for o in descendants(display):
        if o.type=="MESH" and "Lens" not in o.name:
            xs += [world_to_camera_view(s,cam,o.matrix_world@Vector(c)).x*s.render.resolution_x for c in o.bound_box]
    return max(xs)-min(xs)

def calibrate_display(display,cam,target=185):
    display.scale=(1,1,1);bpy.context.view_layer.update();p=projected_width(display,cam);scale=target/p;display.scale=(scale,scale,scale);bpy.context.view_layer.update();display["scale_mode"]="editorial_camera_calibrated";display["target_pixel_width"]=target;return scale,projected_width(display,cam)

def point_at(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()

def studio(name,physical,view,ortho=.18,res=(690,315),samples=96):
    s=bpy.context.scene;state={o:o.hide_render for o in s.objects};parts=descendants(physical)
    for o in s.objects:o.hide_render=o not in parts
    for o in parts:o.hide_render=False
    physical.hide_render=False
    camd=bpy.data.cameras.new("PN_CalibratedCam_"+name);camd.type="ORTHO";camd.ortho_scale=ortho;cam=bpy.data.objects.new("PN_CalibratedCam_"+name,camd);s.collection.objects.link(cam)
    loc,target=view;cam.location=loc;point_at(cam,target);s.camera=cam
    lights=[]
    for i,(loc,energy,size) in enumerate([((-.20,-.25,.24),180,.28),((.20,-.10,.16),100,.22)]):
        d=bpy.data.lights.new("PN_CalStudioLight","AREA");d.energy=energy;d.size=size;o=bpy.data.objects.new("PN_CalStudioLight",d);s.collection.objects.link(o);o.location=loc;point_at(o,(0,.03,0));lights.append(o)
    old=(s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.render.film_transparent);s.render.resolution_x,s.render.resolution_y=res;s.render.resolution_percentage=100;s.render.film_transparent=False;s.world.color=(.8,.8,.8);s.render.image_settings.file_format="PNG";s.render.filepath=os.path.join(RDIR,name+".png");s.render.engine="BLENDER_EEVEE";s.render.image_settings.color_mode="RGBA";bpy.ops.render.render(write_still=True)
    s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.render.film_transparent=old
    for o,v in state.items():o.hide_render=v
    for o in lights+[cam]:bpy.data.objects.remove(o,do_unlink=True)

def compare(ref,result,out):util.montage([ref,result],out)

def overlay_front(refpath,renderpath,outpath):
    import numpy as np
    ri=bpy.data.images.load(refpath,check_existing=False);gi=bpy.data.images.load(renderpath,check_existing=False);w,h=ri.size
    if tuple(gi.size)!=(w,h):gi.scale(w,h)
    ra=np.array(ri.pixels[:],np.float32).reshape(h,w,4)[:,:,:3];ga=np.array(gi.pixels[:],np.float32).reshape(h,w,4)[:,:,:3]
    rm=ra.mean(2)<.55;gmean=ga.mean(2);gm=(gmean>.12)&(gmean<.62);out=np.ones((h,w,4),np.float32);out[:,:,:3]=1;out[rm,:3]=(.95,.15,.08);out[gm,:3]=out[gm,:3]*.35+np.array((.05,.35,.95))*.65
    inter=(rm&gm).sum();union=(rm|gm).sum();iou=float(inter/max(1,union));im=bpy.data.images.new("PN_CalibratedFrontOverlay",w,h,alpha=True);im.pixels.foreach_set(out.ravel());im.filepath_raw=outpath;im.file_format="PNG";im.save();return iou

def topology(root):
    dg=bpy.context.evaluated_depsgraph_get();v=p=t=0
    for o in descendants(root):
        if o.type!="MESH":continue
        e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();v+=len(m.vertices);p+=len(m.polygons);t+=len(m.loop_triangles);e.to_mesh_clear()
    return v,p,t

def main():
    scene=bpy.context.scene;maincam=bpy.data.objects["PN_Camera_Desktop"];locked=(tuple(maincam.location),tuple(maincam.rotation_euler),maincam.data.lens)
    removed=clear_master();physical,display=create_master();scale,pixels=calibrate_display(display,maincam,185)
    for o in bpy.data.objects:
        if o.name.startswith("PN_Spot_Beam_"):o.hide_render=True
    assert locked==(tuple(maincam.location),tuple(maincam.rotation_euler),maincam.data.lens)
    assert all(len(descendants(bpy.data.objects[f"PN_Eyewear_{i:02d}"]))==0 for i in range(1,9))
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    shutil.copy2(REFS["front"],os.path.join(RDIR,"calibrated-master-front-reference.png"))
    studio("calibrated-master-front-render",physical,((0,-.45,.006),(0,0,.006)),.164)
    studio("calibrated-master-side-render",physical,((.45,0,.005),(0,.070,0)),.185,(768,512))
    studio("calibrated-master-top-render",physical,((0,.07,.45),(0,.07,0)),.205,(768,768))
    studio("calibrated-master-three-quarter-render",physical,((.28,-.34,.16),(0,.04,0)),.205,(768,512))
    studio("calibrated-master-bridge-closeup",physical,((0,-.22,.02),(0,0,.006)),.052,(768,512))
    studio("calibrated-master-hinge-closeup",physical,((.16,-.18,.05),(.073,0,.010)),.052,(768,512))
    studio("calibrated-master-acetate-closeup",physical,((-.10,-.16,.04),(-.045,0,.014)),.052,(768,512))
    compare(REFS["front"],os.path.join(RDIR,"calibrated-master-front-render.png"),os.path.join(RDIR,"calibrated-master-front-comparison.png"))
    compare(REFS["side"],os.path.join(RDIR,"calibrated-master-side-render.png"),os.path.join(RDIR,"calibrated-master-side-comparison.png"))
    compare(REFS["top"],os.path.join(RDIR,"calibrated-master-top-render.png"),os.path.join(RDIR,"calibrated-master-top-comparison.png"))
    compare(REFS["three-quarter"],os.path.join(RDIR,"calibrated-master-three-quarter-render.png"),os.path.join(RDIR,"calibrated-master-three-quarter-comparison.png"))
    iou=overlay_front(REFS["front"],os.path.join(RDIR,"calibrated-master-front-render.png"),os.path.join(RDIR,"calibrated-master-front-overlay.png"))
    scene.camera=maincam;scene.render.resolution_x=1536;scene.render.resolution_y=1024;scene.render.resolution_percentage=100;scene.render.filepath=os.path.join(RDIR,"calibrated-master-hero-main.png");scene.render.engine="BLENDER_EEVEE";bpy.ops.render.render(write_still=True)
    art=os.path.join(ROOT,"art-direction","puerto-nuevo-blender-art-target-v2.png");compare(art,os.path.join(RDIR,"calibrated-master-hero-main.png"),os.path.join(RDIR,"calibrated-master-hero-art-target-comparison.png"))
    verts,polys,tris=topology(physical);report={"reference_policy":"four isolated approved crops only; technical sheet not loaded","removed_previous_master_objects":removed,"physical":{"front_width_mm":157,"temple_length_mm":146,"front_depth_mm":7},"editorial_scale":round(scale,4),"hero_projected_width_px":round(pixels,1),"front_thresholded_area_iou_diagnostic":round(iou,4),"geometry":{"vertices":verts,"polygons":polys,"triangles":tris},"visible_instances":1,"lateral_roots_01_08_empty":True,"remaining_front_discrepancies":"minor brow/endpiece contour variation and slightly shallower lower-rim curvature; bridge is continuous and spike-free","camera_unchanged":True}
    with open(os.path.join(REPORTDIR,"eyewear-master-calibrated-retrace-report.json"),"w",encoding="utf-8") as f:json.dump(report,f,indent=2)
    scene["PN_CalibratedRetraceReport"]=str(report);scene.camera=maincam;bpy.ops.wm.save_as_mainfile(filepath=BLEND);print("PN_CALIBRATED_RETRACE",json.dumps(report))

if __name__=="__main__":main()
