import bpy, os, json, hashlib, datetime, math

ROOT=r"C:\Users\josue\Documents\Codex\coa-website"
BLEND=os.path.join(ROOT,"blender","web-export","puerto-nuevo-client-preview-v2.blend")
GLB=os.path.join(ROOT,"public","models","puerto-nuevo-client-preview-v2.glb")
MANIFEST=os.path.join(ROOT,"public","models","puerto-nuevo-client-preview-v2.manifest.json")
os.makedirs(os.path.dirname(GLB),exist_ok=True)

def descendants(root):
    out=[]
    for o in bpy.data.objects:
        p=o.parent
        while p:
            if p==root:out.append(o);break
            p=p.parent
    return out

def material_variant(name,base,accent):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
    n=m.node_tree.nodes;l=m.node_tree.links;n.clear();out=n.new("ShaderNodeOutputMaterial");bs=n.new("ShaderNodeBsdfPrincipled");noise=n.new("ShaderNodeTexNoise");ramp=n.new("ShaderNodeValToRGB");tex=n.new("ShaderNodeTexCoord")
    noise.noise_dimensions="3D";noise.inputs["Scale"].default_value=7.5;noise.inputs["Detail"].default_value=5;noise.inputs["Roughness"].default_value=.72
    ramp.color_ramp.elements[0].color=(*base,1);ramp.color_ramp.elements[0].position=.25;ramp.color_ramp.elements[1].color=(*accent,1);ramp.color_ramp.elements[1].position=.78
    l.new(tex.outputs["Generated"],noise.inputs[0]);l.new(noise.outputs["Fac"],ramp.inputs[0]);l.new(ramp.outputs[0],bs.inputs["Base Color"]);l.new(bs.outputs[0],out.inputs[0]);bs.inputs["Roughness"].default_value=.28;bs.inputs["Metallic"].default_value=0;bs.inputs["IOR"].default_value=1.49;bs.inputs["Coat Weight"].default_value=.16
    return m

def distribute():
    source=bpy.data.objects["PN_Eyewear_Master_Display"]
    variants=[
        material_variant("MAT_Web_Eyewear_Black",(.002,.001,.0008),(.030,.006,.001)),
        material_variant("MAT_Web_Eyewear_Tortoise",(.003,.0007,.0002),(.095,.018,.0015)),
        material_variant("MAT_Web_Eyewear_Amber",(.010,.002,.0003),(.16,.045,.004)),
        material_variant("MAT_Web_Eyewear_Smoke",(.003,.004,.0045),(.035,.028,.022)),
    ]
    source_parts=[o for o in descendants(source) if o.type=="MESH"]
    for index in range(1,9):
        root=bpy.data.objects[f"PN_Eyewear_{index:02d}"]
        for old in descendants(root):bpy.data.objects.remove(old,do_unlink=True)
        inst=bpy.data.objects.new(f"PN_Eyewear_{index:02d}_PreviewInstance",None);bpy.context.scene.collection.objects.link(inst);inst.parent=root;inst.scale=(3.65,3.65,3.65);inst["client_preview_provisional"]=True;inst["product_id"]=f"{index:02d}"
        mat=variants[(index-1)%len(variants)]
        for src in source_parts:
            o=bpy.data.objects.new(src.name.replace("Display",f"Preview_{index:02d}"),src.data);bpy.context.scene.collection.objects.link(o);o.parent=inst;o.matrix_local=src.matrix_local.copy();o.hide_render=False
            srcmat=src.active_material
            if o.material_slots:
                o.material_slots[0].link="OBJECT";o.material_slots[0].material=srcmat if ("Lens" in o.name or "Hinge" in o.name or "Rivet" in o.name) else mat
        root["product_id"]=f"{index:02d}";root["raycast_root"]=True;root["distribution"]="Client Preview V2 provisional"
    bpy.data.objects["PN_Eyewear_09"]["product_id"]="09";bpy.data.objects["PN_Eyewear_09"]["distribution"]="Client Preview V2 provisional"

def optimize():
    # Remove export-only diagnostics and hidden physical/reference sources from this copy only.
    for cname in ("PN_Eyewear_Reference_Planes","PN_Window_Grille_Measurement","PN_Spot_Beam_Diagnostic","PN_Props_Cameras","PN_Props_Lighting","PN_Cameras"):
        c=bpy.data.collections.get(cname)
        if c:
            for o in list(c.all_objects):
                if o.name in bpy.data.objects:bpy.data.objects.remove(o,do_unlink=True)
    physical=bpy.data.objects.get("PN_Eyewear_Master_Physical")
    if physical:
        for o in descendants(physical):bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.objects.remove(physical,do_unlink=True)
    # Diagnostics and labels are not part of the client scene.
    for o in list(bpy.data.objects):
        if o.type in {"CAMERA","FONT"} or o.name.startswith("PN_Spot_Beam_"):
            bpy.data.objects.remove(o,do_unlink=True)
    # Ensure visible mesh normals are valid and transforms are export-safe.
    for o in bpy.data.objects:
        if o.type=="MESH" and not o.hide_render:
            for p in o.data.polygons:p.use_smooth=p.use_smooth

def exportable(o):
    if o.hide_render or o.hide_viewport:return False
    if o.type=="MESH":return True
    if o.type=="EMPTY":
        return o.name.startswith(("PN_Eyewear_","PN_LizardPath_Anchor_","PN_Turntable","PN_Workshop","PN_Window","PN_Main","PN_Product","PN_Exterior","PN_Arched"))
    return False

def evaluated_stats(selected):
    dg=bpy.context.evaluated_depsgraph_get();verts=polys=tris=0;meshes=0
    for o in selected:
        if o.type!="MESH":continue
        e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();verts+=len(m.vertices);polys+=len(m.polygons);tris+=len(m.loop_triangles);meshes+=1;e.to_mesh_clear()
    return {"mesh_objects":meshes,"vertices":verts,"polygons":polys,"triangles":tris}

def main():
    distribute();optimize();bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    bpy.ops.object.select_all(action="DESELECT");selected=[]
    for o in bpy.context.scene.objects:
        if exportable(o):o.select_set(True);selected.append(o)
    stats=evaluated_stats(selected)
    bpy.ops.export_scene.gltf(filepath=GLB,export_format="GLB",use_selection=True,export_cameras=False,export_lights=False,export_apply=True,export_yup=True,export_texcoords=True,export_normals=True,export_materials="EXPORT",export_image_format="AUTO")
    size=os.path.getsize(GLB);sha=hashlib.sha256(open(GLB,"rb").read()).hexdigest().upper();materials=sorted({m.name for o in selected if o.type=="MESH" for m in o.data.materials if m})
    interactive=[f"PN_Eyewear_{i:02d}" for i in range(1,10)]+[f"PN_LizardPath_Anchor_{i:02d}" for i in range(1,9)]
    manifest={"asset":"puerto-nuevo-client-preview-v2.glb","stage":"Client Preview V2","distribution":"Provisional 4-1-4; not final product distribution","generated":"2026-08-18","bytes":size,"megabytes":round(size/1048576,2),"sha256":sha,"geometry":stats,"materials":{"count":len(materials),"names":materials},"textures":{"embedded":True,"strategy":"Procedural values exported provisionally; production bake pending","estimated_compressed_megabytes":0},"interactive_nodes":interactive,"known_limitations":["Provisional eyewear variants share the approved master geometry","Production PBR atlas/KTX2 bake remains pending","Realistic lizard is not included","Final tile and production optimization remain pending"]}
    with open(MANIFEST,"w",encoding="utf-8") as f:json.dump(manifest,f,indent=2,ensure_ascii=False)
    print("PN_CLIENT_PREVIEW_V2",json.dumps(manifest))

if __name__=="__main__":main()
