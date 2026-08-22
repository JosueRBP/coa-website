import bpy, math, os, sys, time
import numpy as np
from mathutils import Vector

ROOT=r"C:\Users\josue\Documents\Codex\coa-website"
BLEND=os.path.join(ROOT,'blender','puerto-nuevo-workshop.blend')
RDIR=os.path.join(ROOT,'blender','renders')
TEXDIR=os.path.join(ROOT,'blender','textures');os.makedirs(TEXDIR,exist_ok=True)
ANGREF=os.path.join(ROOT,'art-direction','eyewear-angular-acetate-reference.png')
TILEREF=os.path.join(ROOT,'art-direction','criollo-tile-reference.png')
sys.path.insert(0,os.path.join(ROOT,'blender','scripts'))
import build_hero_tile_machinery_refinement as util

BASEPNG=os.path.join(TEXDIR,'pn-criollo-tile-fidelity-basecolor-1024.png')
ROUGHPNG=os.path.join(TEXDIR,'pn-criollo-tile-fidelity-roughness-1024.png')
HEIGHTPNG=os.path.join(TEXDIR,'pn-criollo-tile-fidelity-height-1024.png')

def hero_material():
    m,bs=util.material('MAT_Hero09_Fidelity_BlackTortoise',(.0005,.00025,.00012),.27)
    n=m.node_tree.nodes;l=m.node_tree.links;tc=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.noise_dimensions='3D';noise.inputs['Scale'].default_value=4.1;noise.inputs['Detail'].default_value=9;noise.inputs['Roughness'].default_value=.7;noise.inputs['Distortion'].default_value=2.2
    ramp=n.new('ShaderNodeValToRGB');cr=ramp.color_ramp;cr.elements.remove(cr.elements[1]);e0=cr.elements[0];e0.position=.20;e0.color=(.0002,.0001,.00006,1)
    for pos,col in [(.58,(.0007,.00020,.00008,1)),(.73,(.0025,.00055,.00012,1)),(.84,(.0065,.0014,.00028,1)),(.94,(.0018,.00028,.00010,1))]:e=cr.elements.new(pos);e.color=col
    l.new(tc.outputs['Generated'],noise.inputs[0]);l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],bs.inputs['Base Color']);bs.inputs['Coat Weight'].default_value=.055;bs.inputs['Coat Roughness'].default_value=.24;bs.inputs['IOR'].default_value=1.49;bs.inputs['Specular IOR Level'].default_value=.18;bs.inputs['Roughness'].default_value=.34
    return m

def prism(name,outline,depth,mat,col,parent):
    n=len(outline);verts=[(x,-depth/2,z) for x,z in outline]+[(x,depth/2,z) for x,z in outline];faces=[tuple(range(n)),tuple(range(n,2*n))]
    for i in range(n):j=(i+1)%n;faces.append((i,j,n+j,n+i))
    me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);col.objects.link(o);o.parent=parent;me.materials.append(mat);b=o.modifiers.new('PN_SculptedPolish','BEVEL');b.width=.006;b.segments=4
    for p in me.polygons:p.use_smooth=True
    return o

def rebuild_hero():
    root=bpy.data.objects['PN_Eyewear_09'];col=bpy.data.collections['PN_Eyewear_Products'];selected=root.select_get();active=bpy.context.view_layer.objects.active==root;origin=root.location.copy();contracts={k:root[k] for k in root.keys()}
    for o in list(bpy.data.objects):
        p=o.parent
        while p:
            if p==root:bpy.data.objects.remove(o,do_unlink=True);break
            p=p.parent
    ac=hero_material();lensmat=util.lensmat();brass,_=util.material('MAT_Hero09_Fidelity_Hardware',(.15,.045,.009),.38,.92)
    # Derived directly from the angular reference: lifted outer brow, marked endpiece,
    # narrowed organic lower edge and deliberately non-identical left/right openings.
    centers=.143
    left_outer=[(-.190,.018),(-.178,.095),(-.118,.133),(-.020,.142),(.090,.118),(.167,.073),(.180,-.010),(.142,-.092),(.055,-.132),(-.055,-.139),(-.150,-.104),(-.190,-.035)]
    right_outer=[(-.175,.060),(-.110,.116),(-.012,.130),(.095,.151),(.174,.112),(.198,.030),(.185,-.058),(.125,-.118),(.020,-.143),(-.095,-.128),(-.163,-.078),(-.184,-.010)]
    left_inner=[(-.142,.012),(-.132,.071),(-.084,.099),(-.005,.105),(.074,.086),(.123,.052),(.132,-.012),(.102,-.067),(.038,-.094),(-.047,-.098),(-.111,-.071),(-.140,-.025)]
    right_inner=[(-.132,.043),(-.079,.083),(-.004,.092),(.074,.106),(.128,.078),(.145,.022),(.136,-.044),(.091,-.082),(.012,-.102),(-.070,-.090),(-.120,-.057),(-.138,-.005)]
    shapes={'L':(left_outer,left_inner,-centers),'R':(right_outer,right_inner,centers)}
    for side,(outer0,inner0,cx) in shapes.items():
        outer=util.catmull([(cx+x,z) for x,z in outer0],5);inner=util.catmull([(cx+x,z) for x,z in inner0],5)
        util.ring(f'PN_Eyewear_09_Front_{side}',outer,inner,.037,ac,col,root);util.lens(f'PN_Eyewear_09_Lens_{side}',inner,lensmat,col,root)
        sgn=-1 if side=='L' else 1;ex=min(x for x,z in outer) if side=='L' else max(x for x,z in outer)
        end=[(ex-sgn*.012,.086),(ex+sgn*.055,.067),(ex+sgn*.073,.020),(ex+sgn*.050,-.030),(ex-sgn*.010,-.045)]
        prism(f'PN_Eyewear_09_Endpiece_{side}',end,.040,ac,col,root)
        hx=ex+sgn*.050;util.tube(f'PN_Eyewear_09_HingePin_{side}',[(hx,-.024,.023),(hx,.025,.023)],.0058,brass,col,root)
        for iz,z in enumerate((.012,.033),1):util.tube(f'PN_Eyewear_09_Rivet_{side}_{iz}',[(hx-sgn*.010,-.026,z),(hx-sgn*.010,-.032,z)],.0024,brass,col,root)
        # Broad tortoise temples immediately recede, avoiding frontal symmetry.
        util.tube(f'PN_Eyewear_09_Temple_{side}',[(hx+sgn*.010,.018,.025),(hx+sgn*.065,.10,.012),(hx+sgn*.10,.27,-.040),(hx+sgn*.075,.35,-.087)],.0175,ac,col,root)
    # Integrated sculpted bridge plate, not a sphere/tube.
    bridge=[(-.055,.074),(-.020,.090),(.018,.084),(.057,.062),(.054,.023),(.022,.040),(-.015,.045),(-.052,.030)]
    prism('PN_Eyewear_09_Bridge_Sculpted',bridge,.037,ac,col,root)
    root.location=origin
    for k,v in contracts.items():root[k]=v
    root['hero_refinement_pass']='reference-fidelity-2.1';root['reference_source']='eyewear-angular-acetate-reference.png'
    root.select_set(selected)
    if active:bpy.context.view_layer.objects.active=root

def save_image(name,path,array,colorspace='sRGB'):
    h,w=array.shape[:2];rgba=np.ones((h,w,4),np.float32)
    if array.ndim==2:rgba[:,:,:3]=array[:,:,None]
    else:rgba[:,:,:3]=array[:,:,:3]
    im=bpy.data.images.get(name)
    if im:bpy.data.images.remove(im)
    im=bpy.data.images.new(name,w,h,alpha=True,float_buffer=False);im.colorspace_settings.name=colorspace
    im.pixels.foreach_set(np.ascontiguousarray(rgba,dtype=np.float32).ravel());im.update();im.filepath_raw=path;im.file_format='PNG';im.save()
    # Reload from disk so render nodes use the exact persisted pixels.
    bpy.data.images.remove(im);im=bpy.data.images.load(path,check_existing=False);im.name=name;im.colorspace_settings.name=colorspace;return im

def build_tile_maps():
    S=1024;y,x=np.mgrid[0:S,0:S];u=(x+.5)/S;v=(y+.5)/S
    base=np.zeros((S,S,3),np.float32);base[:]=(.39,.225,.060)
    handmade=.012*np.sin(x*.027)*np.sin(y*.031)+.007*np.sin((x+y)*.013);base+=handmade[:,:,None]
    height=np.full((S,S),.48,np.float32);rough=np.full((S,S),.68,np.float32)
    def paint(mask,color,h=.51,r=.66):base[mask]=color;height[mask]=h;rough[mask]=r
    dark=(.045,.115,.060);green=(.12,.255,.135);white=(.76,.70,.54);wine=(.29,.052,.040)
    # Central eight-point star, safely inside the tile.
    dx=u-.5;dy=v-.5;ang=np.arctan2(dy,dx);rad=np.hypot(dx,dy);paint(rad<(.105+.030*np.cos(4*ang)),dark,.515,.70)
    # White floral quartet and wine connectors at cardinal positions.
    for q in range(4):
        a=q*math.pi/2;ca,sa=math.cos(a),math.sin(a)
        cx=.5+.175*ca;cy=.5+.175*sa;xr=(u-cx)*ca+(v-cy)*sa;yr=-(u-cx)*sa+(v-cy)*ca
        petal=(xr/.105)**2+(yr/.070)**2<1;notch=((xr+.055)/.052)**2+(yr/.040)**2<1;paint(petal&~notch,white,.505,.72)
        cx=.5+.300*ca;cy=.5+.300*sa;xr=(u-cx)*ca+(v-cy)*sa;yr=-(u-cx)*sa+(v-cy)*ca;paint((xr/.038)**2+(yr/.021)**2<1,wine,.508,.69)
    # Four independent corner arms, curving inward; all terminate before 8% safe margin.
    corners=[(.12,.12,1,1),(.88,.12,-1,1),(.88,.88,-1,-1),(.12,.88,1,-1)]
    for cx,cy,sx,sy in corners:
        mask=np.zeros((S,S),bool)
        controls=[(cx,cy),(cx+.10*sx,cy+.015*sy),(cx+.15*sx,cy+.105*sy),(cx+.205*sx,cy+.17*sy)]
        for seg in range(3):
            a0=np.array(controls[seg]);a1=np.array(controls[seg+1])
            for t in np.linspace(0,1,18):
                p=a0*(1-t)+a1*t;mask|=(u-p[0])**2+(v-p[1])**2<.020**2
        # Three-leaf terminal kept inside margins.
        tx,ty=controls[0]
        for ox,oy in [(0,0),(.035*sx,.012*sy),(.012*sx,.040*sy)]:mask|=((u-(tx+ox))/(.045))**2+((v-(ty+oy))/(.022))**2<1
        paint(mask,green,.512,.70)
    # Visible safe margin and restrained edge aging.
    edge=np.minimum.reduce([u,v,1-u,1-v]);fade=np.clip((.055-edge)/.055,0,1);base-=fade[:,:,None]*.045;rough+=fade*.055
    base=np.clip(base,0,1);rough=np.clip(rough,0,1);height=np.clip(height,0,1)
    ib=save_image('PN_Criollo_Fidelity_BaseColor',BASEPNG,base,'sRGB');ir=save_image('PN_Criollo_Fidelity_Roughness',ROUGHPNG,rough,'Non-Color');ih=save_image('PN_Criollo_Fidelity_Height',HEIGHTPNG,height,'Non-Color')
    m,bs=util.material('MAT_Criollo_Tile_ReferenceFidelity',(.39,.225,.060),.68);n=m.node_tree.nodes;l=m.node_tree.links;tc=n.new('ShaderNodeTexCoord')
    tb=n.new('ShaderNodeTexImage');tb.image=ib;tb.interpolation='Linear';tb.extension='CLIP';tr=n.new('ShaderNodeTexImage');tr.image=ir;tr.interpolation='Linear';tr.extension='CLIP';th=n.new('ShaderNodeTexImage');th.image=ih;th.interpolation='Linear';th.extension='CLIP'
    l.new(tc.outputs['Generated'],tb.inputs[0]);l.new(tc.outputs['Generated'],tr.inputs[0]);l.new(tc.outputs['Generated'],th.inputs[0]);l.new(tb.outputs['Color'],bs.inputs['Base Color']);l.new(tr.outputs['Color'],bs.inputs['Roughness']);b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.11;b.inputs['Distance'].default_value=.0015;l.new(th.outputs['Color'],b.inputs['Height']);l.new(b.outputs[0],bs.inputs['Normal'])
    for o in bpy.data.objects:
        if o.name.startswith('PN_FloorTile_'):
            if o.data.materials:o.data.materials[0]=m
            else:o.data.materials.append(m)

def render_silhouette(cam):
    root=bpy.data.objects['PN_Eyewear_09'];desc=[]
    for o in bpy.data.objects:
        p=o.parent
        while p:
            if p==root:desc.append(o);break
            p=p.parent
    hidden={o:o.hide_render for o in bpy.context.scene.objects};mats={o:list(o.data.materials) for o in desc if o.type in {'MESH','CURVE'}};black,_=util.material('MAT_Silhouette_Black',(0,0,0),1)
    for o in bpy.context.scene.objects:o.hide_render=o not in desc
    for o in mats:o.data.materials.clear();o.data.materials.append(black)
    s=bpy.context.scene;oldfilm=s.render.film_transparent;s.render.film_transparent=True;util.render('fidelity-hero-silhouette.png',cam,32);s.render.film_transparent=oldfilm
    for o,val in hidden.items():o.hide_render=val
    for o,arr in mats.items():o.data.materials.clear();[o.data.materials.append(m) for m in arr]

def silhouette_overlay():
    ref=bpy.data.images.load(ANGREF,check_existing=False);hero=bpy.data.images.load(os.path.join(RDIR,'fidelity-hero-silhouette.png'),check_existing=False);W,H=1536,1024
    ref.scale(W,H);hero.scale(W,H);ra=np.array(ref.pixels[:],np.float32).reshape(H,W,4);ha=np.array(hero.pixels[:],np.float32).reshape(H,W,4);rm=ra[:,:,:3].mean(2)<.86;hm=ha[:,:,3]>.08
    out=np.ones((H,W,4),np.float32);out[rm,:3]=(.95,.28,.20);out[hm,:3]=out[hm,:3]*.38+np.array((.10,.35,.95))*.62;out[:,:,3]=1
    save_image('PN_Hero_Silhouette_Overlay',os.path.join(RDIR,'fidelity-hero-silhouette-overlay.png'),out[:,:,:3]);bpy.data.images.remove(ref);bpy.data.images.remove(hero)

def main():
    s=bpy.context.scene;approved=bpy.data.objects['PN_Camera_Desktop'];assert tuple(round(v,2) for v in approved.location)==(0,-11.15,2.52) and approved.data.lens==52
    before=s.get('PN_SurgicalMetrics','triangles=138552');rebuild_hero();build_tile_maps();s.camera=approved;bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    mainp=os.path.join(RDIR,'fidelity-main.png');times={'main':util.render('fidelity-main.png',approved,96)}
    front=util.cam('PN_Cam_FidelityHeroFront',(0,-2.85,1.44),(0,.26,1.38),92);q3=util.cam('PN_Cam_FidelityHero3Q',(.63,-2.48,1.61),(0,.27,1.38),84)
    tile=bpy.data.objects.get('PN_FloorTile_04_04') or next(o for o in bpy.data.objects if o.name.startswith('PN_FloorTile_'));tx,ty=tile.location.x,tile.location.y
    top1=util.cam('PN_Cam_FidelityTileTop',(tx,ty,2.15),(tx,ty,0),76);top9=util.cam('PN_Cam_FidelityTileGrid',(tx,ty,3.35),(tx,ty,0),70)
    for f,c in [('fidelity-hero-front.png',front),('fidelity-hero-three-quarter.png',q3),('fidelity-tile-single-top.png',top1),('fidelity-tile-grid-3x3.png',top9)]:times[f]=util.render(f,c,72)
    render_silhouette(q3);silhouette_overlay()
    util.montage([ANGREF,os.path.join(RDIR,'fidelity-hero-three-quarter.png')],os.path.join(RDIR,'fidelity-hero-reference-comparison.png'))
    util.montage([TILEREF,os.path.join(RDIR,'fidelity-tile-single-top.png')],os.path.join(RDIR,'fidelity-tile-reference-comparison.png'))
    s.camera=approved;v,p,t=util.metrics();s['PN_Fidelity21_TrianglesBefore']=138552;s['PN_Fidelity21_TrianglesAfter']=t;s['PN_Fidelity21_Metrics']=f'vertices={v}, polygons={p}, triangles={t}';s['PN_Fidelity21_Note']='99,776 was Photorealism pass; 138,552 was subsequent surgical pass. They are different scene revisions, not a reduction claim.';bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print('PN_FIDELITY_BEFORE',138552,'AFTER',t,'VERTS',v,'POLYS',p);print('PN_CAMERA',tuple(approved.location),approved.data.lens);print('PN_TIMES',times)

if __name__=='__main__':main()
