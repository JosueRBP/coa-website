import bpy, os
root=r"C:\Users\josue\Documents\Codex\coa-website\blender\renders"
spots=[o for o in bpy.data.objects if o.name.startswith('PN_DisplaySpot_') and o.type=='LIGHT']
states={o:o.hide_render for o in spots}
for o in spots:o.hide_render=True
scene=bpy.context.scene
for filename,camname in [
    ('eyewear-master-front.png','PN_Cam_MasterFront'),
    ('eyewear-master-three-quarter.png','PN_Cam_Master3Q'),
    ('eyewear-master-side.png','PN_Cam_MasterSide'),
    ('eyewear-master-top.png','PN_Cam_MasterTop')]:
    scene.camera=bpy.data.objects[camname];scene.render.resolution_x=1536;scene.render.resolution_y=1024;scene.render.resolution_percentage=100;scene.render.filepath=os.path.join(root,filename);scene.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True)
for o,v in states.items():o.hide_render=v
scene.camera=bpy.data.objects['PN_Camera_Desktop']
