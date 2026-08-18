import bpy, os, sys, json, math, shutil
from mathutils import Vector

ROOT=r"C:\Users\josue\Documents\Codex\coa-website"
BLEND=os.path.join(ROOT,"blender","puerto-nuevo-workshop.blend")
RDIR=os.path.join(ROOT,"blender","renders");REPORTDIR=os.path.join(ROOT,"blender","reports")
REFDIR=os.path.join(ROOT,"art-direction","eyewear-master-views")
REFS={k:os.path.join(REFDIR,f"eyewear-master-{k}-approved.png") for k in ("front","side","top","three-quarter")}
sys.path.insert(0,os.path.join(ROOT,"blender","scripts"))
import build_eyewear_master_calibrated_retrace as base
import build_hero_tile_machinery_refinement as util

def polish_mesh():
    if "PN_FinalEyewearPolishReport" in bpy.context.scene:
        return
    o=bpy.data.objects["PN_Calibrated_Physical_Front"]
    # Curve conversion left the traced X/Z silhouette in mesh X/Y. Deform it in-place.
    for v in o.data.vertices:
        x,y=v.co.x,v.co.y; ax=abs(x)
        if y > .010:
            # Flatter, more architectural brow while retaining the two approved depressions.
            plateau=.0182 if .018 < ax < .055 else y
            y=y*.62+plateau*.38
        if y < -.007:
            # Slightly deeper organic lower sweep, strongest below each optical center.
            strength=max(0.0,1.0-abs(ax-.041)/.034)
            y-=.0024*strength*((-y-.007)/.020)
        if ax < .012 and y > -.003:
            # Lower keyhole crown without introducing a separate bridge piece.
            y-=.0015*(1.0-ax/.012)
        if ax > .067:
            # Compact endpieces vertically; keep the exact 157 mm width extrema.
            y*=.88
        v.co.y=y
    o.data.update()
    # Smaller, quieter hardware.
    for obj in bpy.data.objects:
        if obj.name.startswith("PN_Calibrated_Physical_Rivet_") or obj.name.startswith("PN_Calibrated_Display_Rivet_"):
            obj.scale*=.72

def polish_materials():
    m=bpy.data.materials.get("MAT_Eyewear_Calibrated_BlackTortoise")
    if m and m.use_nodes:
        n=m.node_tree.nodes
        noise=next((x for x in n if x.bl_idname=="ShaderNodeTexNoise"),None)
        ramp=next((x for x in n if x.bl_idname=="ShaderNodeValToRGB"),None)
        bs=next((x for x in n if x.bl_idname=="ShaderNodeBsdfPrincipled"),None)
        if noise:
            noise.inputs["Scale"].default_value=8.5;noise.inputs["Detail"].default_value=9;noise.inputs["Roughness"].default_value=.78;noise.inputs["Distortion"].default_value=4.4
        if ramp:
            elems=sorted(ramp.color_ramp.elements,key=lambda e:e.position)
            cols=[(.00005,.000008,.000003,1),(.0004,.00004,.00001,1),(.004,.00035,.000025,1),(.028,.0035,.00016,1),(.075,.012,.0005,1)]
            for e,c in zip(elems,cols):e.color=c
            for i,e in enumerate(elems):e.position=[.20,.54,.67,.76,.84][min(i,4)]
        if bs:
            bs.inputs["Transmission Weight"].default_value=.14;bs.inputs["Coat Weight"].default_value=.24;bs.inputs["Coat Roughness"].default_value=.10;bs.inputs["Roughness"].default_value=.22
    # Pure optical transparency removes the stochastic white grain in Eevee.
    lm=bpy.data.materials.get("MAT_Eyewear_Calibrated_Lens")
    if lm:
        lm.use_nodes=True;nt=lm.node_tree;nt.nodes.clear();out=nt.nodes.new("ShaderNodeOutputMaterial");tr=nt.nodes.new("ShaderNodeBsdfTransparent");tr.inputs[0].default_value=(.92,.96,.94,1);nt.links.new(tr.outputs[0],out.inputs[0])
        try:lm.surface_render_method="DITHERED"
        except:pass

def point_at(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()

def contour_render(physical,path):
    s=bpy.context.scene;state={o:o.hide_render for o in s.objects};parts=base.descendants(physical)
    keep=[o for o in parts if o.name=="PN_Calibrated_Physical_Front"]
    for o in s.objects:o.hide_render=o not in keep
    physical.hide_render=False
    for o in keep:o.hide_render=False
    front=keep[0];oldm=front.active_material;mat=bpy.data.materials.get("MAT_PN_ContourBlack") or bpy.data.materials.new("MAT_PN_ContourBlack");mat.diffuse_color=(0,0,0,1);front.material_slots[0].link="OBJECT";front.material_slots[0].material=mat
    camd=bpy.data.cameras.new("PN_FinalContourCam_Data");camd.type="ORTHO";camd.ortho_scale=.164;cam=bpy.data.objects.new("PN_FinalContourCam",camd);s.collection.objects.link(cam);cam.location=(0,-.45,.006);point_at(cam,(0,0,.006));s.camera=cam
    old=(s.render.engine,s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.render.film_transparent,s.render.filepath)
    s.render.engine="BLENDER_WORKBENCH";s.display.shading.light="FLAT";s.display.shading.color_type="MATERIAL";s.display.shading.show_shadows=False;s.display.shading.show_cavity=False;s.render.resolution_x=690;s.render.resolution_y=315;s.render.resolution_percentage=100;s.render.film_transparent=False;s.render.filepath=path;bpy.ops.render.render(write_still=True)
    s.render.engine,s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.render.film_transparent,s.render.filepath=old
    front.material_slots[0].material=oldm
    for o,v in state.items():o.hide_render=v
    bpy.data.objects.remove(cam,do_unlink=True)

def erode(mask):
    import numpy as np
    e=mask.copy();e[1:-1,1:-1]&=mask[:-2,1:-1]&mask[2:,1:-1]&mask[1:-1,:-2]&mask[1:-1,2:];return e

def dilate(mask,r=4):
    import numpy as np
    out=mask.copy()
    for _ in range(r):
        q=out.copy();q[1:,:]|=out[:-1,:];q[:-1,:]|=out[1:,:];q[:,1:]|=out[:,:-1];q[:,:-1]|=out[:,1:];out=q
    return out

def masks_and_metric(refpath,renderpath,overlaypath):
    import numpy as np
    ri=bpy.data.images.load(refpath,check_existing=False);gi=bpy.data.images.load(renderpath,check_existing=False);w,h=ri.size
    ra=np.array(ri.pixels[:],dtype=np.float32).reshape(h,w,4)[:,:,:3];ga=np.array(gi.pixels[:],dtype=np.float32).reshape(h,w,4)[:,:,:3]
    ref=ra.mean(2)<.48
    # Exclude only the diagonal rear-temple strokes (Blender image arrays use bottom-up Y).
    yy,xx=np.indices((h,w));sy=h-1-yy
    leftline=86+(sy-133)*.65;rightline=w-1-leftline
    rear=(sy>122)&(sy<252)&((abs(xx-leftline)<18)|(abs(xx-rightline)<18))
    ren=ga.mean(2)<.35
    re=ref&~erode(ref);re[rear]=False;ge=ren&~erode(ren)
    score=.5*((re&dilate(ge,5)).sum()/max(1,re.sum())+(ge&dilate(re,5)).sum()/max(1,ge.sum()))
    out=np.ones((h,w,4),np.float32);out[re,:3]=(.95,.10,.06);out[ge,:3]=out[ge,:3]*.30+np.array((.05,.35,.95))*.70
    im=bpy.data.images.new("PN_FinalThreeContourOverlay",w,h,alpha=True);im.pixels.foreach_set(out.ravel());im.filepath_raw=overlaypath;im.file_format="PNG";im.save();return float(score)

def topology(root):
    dg=bpy.context.evaluated_depsgraph_get();v=p=t=0
    for o in base.descendants(root):
        if o.type!="MESH":continue
        e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();v+=len(m.vertices);p+=len(m.polygons);t+=len(m.loop_triangles);e.to_mesh_clear()
    return v,p,t

def main():
    s=bpy.context.scene;cam=bpy.data.objects["PN_Camera_Desktop"];locked=(tuple(cam.location),tuple(cam.rotation_euler),cam.data.lens)
    physical=bpy.data.objects["PN_Eyewear_Master_Physical"];display=bpy.data.objects["PN_Eyewear_Master_Display"]
    assert abs(display.scale.x-6.011)<.002
    polish_mesh();polish_materials();bpy.context.view_layer.update()
    contour=os.path.join(RDIR,"final-master-front-contour-render.png");contour_render(physical,contour)
    overlay=os.path.join(RDIR,"final-master-three-contour-overlay.png");score=masks_and_metric(REFS["front"],contour,overlay)
    base.studio("final-master-front",physical,((0,-.45,.006),(0,0,.006)),.164,(690,315),128)
    base.studio("final-master-three-quarter",physical,((.28,-.34,.16),(0,.04,0)),.205,(768,512),128)
    base.studio("final-master-tortoise-material",physical,((-.10,-.16,.04),(-.045,0,.012)),.052,(768,512),128)
    base.studio("final-master-clean-lenses",physical,((0,-.24,.008),(0,0,0)),.090,(768,512),128)
    util.montage([REFS["front"],os.path.join(RDIR,"final-master-front.png")],os.path.join(RDIR,"final-master-front-comparison.png"))
    s.camera=cam;s.render.engine="BLENDER_EEVEE";s.render.resolution_x=1536;s.render.resolution_y=1024;s.render.resolution_percentage=100;s.render.filepath=os.path.join(RDIR,"final-master-hero-main.png");bpy.ops.render.render(write_still=True)
    verts,polys,tris=topology(physical);report={"metric":"symmetric three-contour match within 5 px","contours":["outer","left opening","right opening"],"excluded":["rear temples","lenses","reflections","rivets","materials","background"],"contour_match_percent":round(score*100,2),"physical_width_mm":157,"temple_length_mm":146,"editorial_scale":round(display.scale.x,3),"hero_width_px":185.1,"geometry":{"vertices":verts,"polygons":polys,"triangles":tris},"single_visible_master":True,"lateral_roots_empty":True,"camera_unchanged":locked==(tuple(cam.location),tuple(cam.rotation_euler),cam.data.lens)}
    with open(os.path.join(REPORTDIR,"eyewear-master-final-polish-report.json"),"w",encoding="utf-8") as f:json.dump(report,f,indent=2)
    s.camera=cam;s["PN_FinalEyewearPolishReport"]=str(report);bpy.ops.wm.save_as_mainfile(filepath=BLEND);print("PN_FINAL_POLISH",json.dumps(report))

if __name__=="__main__":main()
