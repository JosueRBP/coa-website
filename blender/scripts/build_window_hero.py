"""Window Hero + Final Materials pass for Puerto Nuevo workshop.

Blender 5.2 LTS:
  blender --background --python blender/scripts/build_window_hero.py

Rebuilds the approved architecture from build_environment.py, preserves the
approved desktop camera, and adds export-oriented grille, exterior and PBR
materials. Procedural surfaces are intentionally bake-ready and use no image
textures.
"""

from pathlib import Path
import importlib.util
import math

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
BASE_SCRIPT = ROOT / "blender" / "scripts" / "build_environment.py"
BLEND_PATH = ROOT / "blender" / "puerto-nuevo-workshop.blend"
RENDER_DIR = ROOT / "blender" / "renders"
TARGET_PATH = ROOT / "art-direction" / "puerto-nuevo-blender-art-target-v2.png"
WINDOW_PREVIEW = RENDER_DIR / "window-hero-refined.png"
GRILLE_PREVIEW = RENDER_DIR / "grille-detail-refined.png"
MATERIALS_PREVIEW = RENDER_DIR / "materials-refined.png"
EXTERIOR_PREVIEW = RENDER_DIR / "exterior-refined.png"
COMPARISON_V3 = RENDER_DIR / "camera-comparison-v4.png"


def load_base_module():
    spec = importlib.util.spec_from_file_location("pn_environment", BASE_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


base = load_base_module()


def new_collection(name, parent=None):
    old = bpy.data.collections.get(name)
    if old:
        bpy.data.collections.remove(old)
    col = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(col)
    return col


def principled(mat):
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    mat.node_tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return nodes, mat.node_tree.links, bsdf


def noise_surface(mat, color_a, color_b, scale, detail, roughness,
                  bump_strength=0.08, bump_distance=0.035):
    nodes, links, bsdf = principled(mat)
    tex = nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = scale
    tex.inputs["Detail"].default_value = detail
    tex.inputs["Roughness"].default_value = 0.72
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.28
    ramp.color_ramp.elements[0].color = (*color_a, 1)
    ramp.color_ramp.elements[1].position = 0.72
    ramp.color_ramp.elements[1].color = (*color_b, 1)
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = bump_strength
    bump.inputs["Distance"].default_value = bump_distance
    bsdf.inputs["Roughness"].default_value = roughness
    links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(tex.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])


def plaster_material(mat):
    nodes, links, bsdf = principled(mat)
    fine = nodes.new("ShaderNodeTexNoise")
    fine.inputs["Scale"].default_value = 115.0
    fine.inputs["Detail"].default_value = 4.0
    fine.inputs["Roughness"].default_value = 0.78
    micro = nodes.new("ShaderNodeTexNoise")
    micro.inputs["Scale"].default_value = 340.0
    micro.inputs["Detail"].default_value = 2.0
    lime = nodes.new("ShaderNodeTexNoise")
    lime.inputs["Scale"].default_value = 2.8
    lime.inputs["Detail"].default_value = 3.0
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.20
    ramp.color_ramp.elements[0].color = (0.31, 0.285, 0.25, 1)
    ramp.color_ramp.elements[1].position = 0.82
    ramp.color_ramp.elements[1].color = (0.46, 0.425, 0.37, 1)
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.18
    bump.inputs["Distance"].default_value = 0.018
    bump2 = nodes.new("ShaderNodeBump")
    bump2.inputs["Strength"].default_value = 0.06
    bump2.inputs["Distance"].default_value = 0.004
    rough = nodes.new("ShaderNodeMapRange")
    rough.inputs["To Min"].default_value = 0.78
    rough.inputs["To Max"].default_value = 0.94
    links.new(lime.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(fine.outputs["Fac"], bump.inputs["Height"])
    links.new(micro.outputs["Fac"], bump2.inputs["Height"])
    links.new(bump.outputs["Normal"], bump2.inputs["Normal"])
    links.new(bump2.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(lime.outputs["Fac"], rough.inputs["Value"])
    links.new(rough.outputs["Result"], bsdf.inputs["Roughness"])


def wood_material(mat, light=False):
    nodes, links, bsdf = principled(mat)
    texcoord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (0.55, 7.0, 7.0)
    wave = nodes.new("ShaderNodeTexWave")
    wave.wave_type = "BANDS"
    wave.bands_direction = "X"
    wave.inputs["Scale"].default_value = 2.4
    wave.inputs["Distortion"].default_value = 3.2
    wave.inputs["Detail"].default_value = 3.0
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 5.0
    noise.inputs["Detail"].default_value = 4.0
    mix = nodes.new("ShaderNodeMixRGB")
    mix.blend_type = "MULTIPLY"
    mix.inputs[0].default_value = 0.36
    ramp = nodes.new("ShaderNodeValToRGB")
    if light:
        colors = ((0.050, 0.016, 0.006, 1), (0.145, 0.052, 0.016, 1))
    else:
        colors = ((0.030, 0.008, 0.003, 1), (0.092, 0.026, 0.008, 1))
    ramp.color_ramp.elements[0].color = colors[0]
    ramp.color_ramp.elements[1].color = colors[1]
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.16
    bump.inputs["Distance"].default_value = 0.012
    rough = nodes.new("ShaderNodeMapRange")
    rough.inputs["To Min"].default_value = 0.34
    rough.inputs["To Max"].default_value = 0.57
    links.new(texcoord.outputs["Generated"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], wave.inputs["Vector"])
    links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    links.new(wave.outputs["Color"], mix.inputs[1])
    links.new(noise.outputs["Fac"], mix.inputs[2])
    links.new(mix.outputs["Color"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(mix.outputs["Color"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(noise.outputs["Fac"], rough.inputs["Value"])
    links.new(rough.outputs["Result"], bsdf.inputs["Roughness"])


def metal_material(mat, painted=False):
    nodes, links, bsdf = principled(mat)
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 42.0
    noise.inputs["Detail"].default_value = 3.0
    ramp = nodes.new("ShaderNodeValToRGB")
    if painted:
        ramp.color_ramp.elements[0].color = (0.38, 0.36, 0.32, 1)
        ramp.color_ramp.elements[1].color = (0.72, 0.69, 0.62, 1)
        bsdf.inputs["Metallic"].default_value = 0.28
        bsdf.inputs["Roughness"].default_value = 0.48
    else:
        ramp.color_ramp.elements[0].color = (0.12, 0.060, 0.018, 1)
        ramp.color_ramp.elements[1].color = (0.33, 0.20, 0.055, 1)
        bsdf.inputs["Metallic"].default_value = 0.82
        bsdf.inputs["Roughness"].default_value = 0.40
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])


def glass_material(mat):
    nodes, links, bsdf = principled(mat)
    out = nodes.get("Material Output")
    links.remove(bsdf.outputs["BSDF"].links[0])
    transparent = nodes.new("ShaderNodeBsdfTransparent")
    mix = nodes.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = 0.13
    links.new(transparent.outputs["BSDF"], mix.inputs[1])
    links.new(bsdf.outputs["BSDF"], mix.inputs[2])
    links.new(mix.outputs["Shader"], out.inputs["Surface"])
    bsdf.inputs["Base Color"].default_value = (0.82, 0.84, 0.80, 1)
    bsdf.inputs["Roughness"].default_value = 0.16
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["IOR"].default_value = 1.45
    bsdf.inputs["Transmission Weight"].default_value = 0.18
    bsdf.inputs["Coat Weight"].default_value = 0.08


def prepare_materials():
    plaster_material(bpy.data.materials["MAT_Plaster_Warm"])
    noise_surface(bpy.data.materials["MAT_Window_Reveal"],
                  (0.67, 0.63, 0.55), (0.88, 0.85, 0.77), 65, 3, 0.82, 0.10, 0.012)
    wood_material(bpy.data.materials["MAT_Walnut_Provisional"], light=True)
    wood_material(bpy.data.materials["MAT_Walnut_Dark"], light=False)
    drawer_a = bpy.data.materials.new("MAT_Walnut_Drawer_A")
    drawer_b = bpy.data.materials.new("MAT_Walnut_Drawer_B")
    frame_wood = bpy.data.materials.new("MAT_Walnut_Frame")
    wood_material(drawer_a, light=True)
    wood_material(drawer_b, light=False)
    wood_material(frame_wood, light=False)
    for obj in bpy.data.objects:
        if obj.name.startswith("PN_Cabinet_") and "_Drawer_" in obj.name:
            idx = int(obj.name.rsplit("_", 1)[-1])
            obj.data.materials.clear()
            obj.data.materials.append(drawer_a if idx % 2 else drawer_b)
        elif obj.name.startswith("PN_Cabinet_") and "_Frame_" in obj.name:
            obj.data.materials.clear()
            obj.data.materials.append(frame_wood)
    metal_material(bpy.data.materials["MAT_Aged_Brass"], painted=False)
    glass_material(bpy.data.materials["MAT_Window_Glass"])
    for obj in list(bpy.data.objects):
        if obj.name.startswith("PN_Window_Mullion_"):
            bpy.data.objects.remove(obj, do_unlink=True)

    # Original criollo palette with slight per-material variation; geometry provides real joints.
    noise_surface(bpy.data.materials["MAT_Criollo_Tile_Cream"],
                  (0.45, 0.42, 0.35), (0.62, 0.59, 0.50), 24, 3, 0.68, 0.05, 0.008)
    noise_surface(bpy.data.materials["MAT_Criollo_Tile_Aged"],
                  (0.25, 0.31, 0.29), (0.39, 0.43, 0.38), 20, 3, 0.71, 0.06, 0.008)
    noise_surface(bpy.data.materials["MAT_Criollo_Motif"],
                  (0.16, 0.25, 0.23), (0.30, 0.40, 0.36), 30, 2, 0.70, 0.04, 0.006)
    noise_surface(bpy.data.materials["MAT_Criollo_Flower"],
                  (0.35, 0.15, 0.10), (0.55, 0.29, 0.20), 28, 2, 0.70, 0.04, 0.006)

    grille = bpy.data.materials.new("MAT_Grille_White_Aged")
    metal_material(grille, painted=True)
    bsdf = grille.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = 0.62
    return grille


def cyclic_tube(name, points, radius, mat, col):
    curve = bpy.data.curves.new(name + "_Curve", "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 1
    curve.bevel_depth = radius
    curve.bevel_resolution = 2
    spline = curve.splines.new("POLY")
    spline.points.add(len(points)-1)
    for p, co in zip(spline.points, points):
        p.co = (*co, 1)
    spline.use_cyclic_u = True
    obj = bpy.data.objects.new(name, curve)
    col.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def line_tube(name, points, radius, mat, col):
    return base.curve_tube(name, points, radius, mat, col)


def ellipse_loop(name, center, rx, rz, radius, mat, col, samples=24, angle=0.0):
    cx, cy, cz = center
    ca, sa = math.cos(angle), math.sin(angle)
    points = []
    for i in range(samples):
        px, pz = rx*math.cos(i*math.tau/samples), rz*math.sin(i*math.tau/samples)
        points.append((cx + px*ca-pz*sa, cy, cz + px*sa+pz*ca))
    return cyclic_tube(name, points, radius, mat, col)


def flower(name, center, scale, mat, col, style=0, top_variant=False):
    x, y, z = center
    petal_rx = (0.13 + 0.015*(style%2)) * scale
    petal_rz = (0.25 if not top_variant else 0.17) * scale
    offset = (0.20 + 0.018*(style%3)) * scale
    tilt = math.radians((-5, 0, 7)[style%3])
    r = 0.0075
    ellipse_loop(name+"_Petal_T", (x, y, z+offset), petal_rx, petal_rz, r, mat, col, angle=tilt)
    ellipse_loop(name+"_Petal_B", (x, y, z-offset), petal_rx, petal_rz, r, mat, col, angle=-tilt)
    ellipse_loop(name+"_Petal_L", (x-offset, y, z), petal_rz, petal_rx, r, mat, col, angle=tilt)
    ellipse_loop(name+"_Petal_R", (x+offset, y, z), petal_rz, petal_rx, r, mat, col, angle=-tilt)
    ellipse_loop(name+"_Center", center, 0.052*scale, 0.052*scale, 0.008, mat, col, 18)


def arch_height(x, half=1.825, spring=3.98, top=4.38):
    return spring + (top-spring) * math.sqrt(max(0.0, 1.0-(x/half)**2))


def build_grille(mat):
    root = bpy.data.collections.get("PN_Workshop_Environment")
    col = new_collection("PN_Window_Grille", root)
    y = 1.285
    half, spring, top, sill = 1.825, 3.98, 4.38, 1.42
    # Outer structural perimeter follows the approved segmental aperture.
    arch = []
    for i in range(49):
        x = -half + 2*half*i/48
        arch.append((x, y, arch_height(x)))
    line_tube("PN_Grille_Outer_Arch", arch, 0.015, mat, col)
    line_tube("PN_Grille_Jamb_L", [(-half,y,sill),(-half,y,spring)], 0.015, mat, col)
    line_tube("PN_Grille_Jamb_R", [(half,y,sill),(half,y,spring)], 0.015, mat, col)
    line_tube("PN_Grille_Sill_Rail", [(-half,y,sill),(half,y,sill)], 0.015, mat, col)

    for i, x in enumerate((-1.58,-1.32,-1.05,-0.79,-0.52,-0.26,0,0.26,0.52,0.79,1.05,1.32,1.58), 1):
        line_tube(f"PN_Grille_VRail_{i:02d}", [(x,y,sill),(x,y,arch_height(x)-0.03)],
                  0.0068, mat, col)
    for i, z in enumerate((1.64,1.88,2.12,2.36,2.60,2.84,3.08,3.32,3.56,3.80), 1):
        # Clip horizontal extent to the arch at upper levels.
        extent = half if z <= spring else half*math.sqrt(max(0, 1-((z-spring)/(top-spring))**2))
        line_tube(f"PN_Grille_HRail_{i:02d}", [(-extent,y,z),(extent,y,z)], 0.0068, mat, col)

    # Caribbean floral modules: six field flowers, a hero center and five crown adaptations.
    for row, z in enumerate((2.02, 2.78, 3.46), 1):
        xs = (-1.10, 0, 1.10) if row != 2 else (-0.92, 0, 0.92)
        for idx, x in enumerate(xs, 1):
            scale = (0.58 + 0.04*((row+idx)%3)) if x else (0.78 if row == 2 else 0.64)
            flower(f"PN_Grille_Flower_R{row}_{idx}", (x,y-0.012,z), scale, mat, col,
                   style=row+idx)
    for idx, x in enumerate((-1.36,-0.68,0,0.68,1.36), 1):
        z = min(4.02, arch_height(x)-0.18)
        flower(f"PN_Grille_CrownFlower_{idx:02d}", (x,y-0.012,z),
               0.42 + 0.035*(idx%2), mat, col, style=idx, top_variant=True)

    # Stable anchor empties for a future lizard spline/path; no character is created.
    anchor_positions = [(-1.72,sill+0.08),(-1.35,2.15),(-0.72,2.88),(0,3.45),
                        (0.70,3.82),(1.34,3.30),(1.72,2.45),(0.35,1.55)]
    for i, (x,z) in enumerate(anchor_positions, 1):
        obj = bpy.data.objects.new(f"PN_LizardPath_Anchor_{i:02d}", None)
        obj.empty_display_type = "SPHERE"
        obj.empty_display_size = 0.045
        obj.location = (x, y-0.06, z)
        obj["path_order"] = i
        obj["purpose"] = "future_lizard_route"
        col.objects.link(obj)
    return col


def exterior_material(name, color, roughness=0.82):
    mat = bpy.data.materials.new(name)
    noise_surface(mat, tuple(c*0.82 for c in color), color, 18, 3, roughness, 0.10, 0.02)
    return mat


def facade_window(prefix, x, y, z, width, height, wall_mat, trim_mat, dark_mat, col, balcony=False):
    base.box(prefix+"_Recess", (x,y,z), (width,0.10,height), dark_mat,col,0.025)
    t = 0.075
    base.box(prefix+"_TrimTop", (x,y-0.07,z+height/2), (width+0.18,0.10,t),trim_mat,col,0.02)
    base.box(prefix+"_TrimBottom", (x,y-0.07,z-height/2), (width+0.18,0.13,t),trim_mat,col,0.02)
    base.box(prefix+"_TrimL", (x-width/2,y-0.07,z), (t,0.10,height),trim_mat,col,0.02)
    base.box(prefix+"_TrimR", (x+width/2,y-0.07,z), (t,0.10,height),trim_mat,col,0.02)
    for gx in (-0.22,0,0.22):
        base.box(prefix+f"_GrilleV_{gx:+.2f}",(x+gx*width,y-0.14,z),(0.018,0.025,height-0.08),trim_mat,col)
    for gz in (-0.23,0.23):
        base.box(prefix+f"_GrilleH_{gz:+.2f}",(x,y-0.14,z+gz*height),(width-0.08,0.025,0.018),trim_mat,col)
    if balcony:
        base.box(prefix+"_BalconySlab",(x,y-0.34,z-height/2-0.02),(width+0.46,0.48,0.10),trim_mat,col,0.02)
        for bi, bx in enumerate((-0.42,-0.21,0,0.21,0.42),1):
            base.box(prefix+f"_Baluster_{bi}",(x+bx*width,y-0.57,z-height/2+0.25),(0.025,0.025,0.48),trim_mat,col)
        base.box(prefix+"_BalconyRail",(x,y-0.57,z-height/2+0.48),(width+0.40,0.035,0.035),trim_mat,col)


def build_exterior():
    root = bpy.data.collections.get("PN_Workshop_Environment")
    col = new_collection("PN_Exterior_PR", root)
    turquoise = exterior_material("MAT_Exterior_Turquoise", (0.11,0.37,0.38))
    cream = exterior_material("MAT_Exterior_Cream", (0.50,0.43,0.31))
    coral = exterior_material("MAT_Exterior_Coral", (0.49,0.20,0.13))
    trim = exterior_material("MAT_Exterior_Trim", (0.78,0.74,0.63),0.76)
    dark = bpy.data.materials.new("MAT_Exterior_Window_Dark")
    noise_surface(dark,(0.025,0.035,0.032),(0.07,0.09,0.08),12,2,0.58,0.03,0.01)
    pavement = exterior_material("MAT_Exterior_Pavement", (0.35,0.32,0.27),0.88)
    foliage = exterior_material("MAT_Tropical_Foliage", (0.12,0.28,0.10),0.78)
    foliage2 = exterior_material("MAT_Tropical_Foliage_Light", (0.28,0.42,0.15),0.78)

    # Three facades on staggered planes provide parallax rather than a photographic card.
    facade_specs = [(-1.34,3.48,2.55,1.58,4.9,turquoise,"Turquoise"),
                    (0,4.62,2.85,1.48,5.4,cream,"Cream"),
                    (1.34,3.92,2.60,1.58,5.0,coral,"Coral")]
    for x,y,z,w,h,mat,label in facade_specs:
        base.box(f"PN_Exterior_{label}_Facade",(x,y,z),(w,0.22,h),mat,col,0.035)
        base.box(f"PN_Exterior_{label}_Cornice",(x,y-0.16,z+h/2-0.12),(w+0.12,0.18,0.18),trim,col,0.03)
        facade_window(f"PN_Exterior_{label}_Window_L",x-w*0.23,y-0.18,z+0.78,w*0.34,1.18,mat,trim,dark,col,balcony=label!="Cream")
        facade_window(f"PN_Exterior_{label}_Window_R",x+w*0.23,y-0.18,z+0.78,w*0.34,1.18,mat,trim,dark,col,balcony=label=="Cream")
        facade_window(f"PN_Exterior_{label}_Door",x,y-0.18,z-1.05,w*0.42,1.65,mat,trim,dark,col,False)
    base.box("PN_Exterior_Sidewalk",(0,2.92,0.16),(8.5,1.25,0.18),pavement,col,0.025)
    base.box("PN_Exterior_Street",(0,2.05,-0.02),(8.5,0.55,0.08),dark,col)

    # Sparse tropical layers: low-poly leaves and two thin vines near the crown.
    for plant, (px,py,pz) in enumerate(((-1.72,3.10,3.72),(1.56,3.30,4.00)),1):
        trunk = base.cylinder(f"PN_Exterior_Plant_{plant}_Stem",(px,py,pz-0.35),0.018,0.85,trim,col,10)
        for li in range(9):
            angle = li*2.4
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=0.17*(0.82+0.05*(li%4)),
                location=(px+0.28*math.cos(angle),py-0.08*li/9,pz+0.18*math.sin(angle)+0.05*li))
            leaf = bpy.context.object
            leaf.name = f"PN_Exterior_Plant_{plant}_Leaf_{li+1:02d}"
            leaf.scale = (1.18+0.10*(li%3),0.30+0.04*(li%2),0.48+0.05*((li+1)%3))
            leaf.rotation_euler = (0.18*math.sin(angle),angle,0.35*math.cos(angle))
            leaf.data.materials.append(foliage if li%2 else foliage2)
            base.move_to_collection(leaf,col)
    return col


def refine_criollo_floor():
    """Replace sticker-like diamonds with a full-tile, flush encaustic pattern."""
    shell = bpy.data.collections["PN_Workshop_Shell"]
    for obj in list(bpy.data.objects):
        if obj.name.startswith("PN_FloorMotif_") or obj.name.startswith("PN_FloorFlower_"):
            bpy.data.objects.remove(obj, do_unlink=True)
    green = bpy.data.materials["MAT_Criollo_Motif"]
    coral = bpy.data.materials["MAT_Criollo_Flower"]
    for tile in [o for o in bpy.data.objects if o.name.startswith("PN_FloorTile_")]:
        suffix = tile.name.replace("PN_FloorTile_", "")
        parts = suffix.split("_")
        variant = (int(parts[0]) + 2*int(parts[1])) % 4
        x,y = tile.location.x,tile.location.y
        motif_mat = green if variant in (0,1,3) else coral
        for band, angle in enumerate((45,135),1):
            stripe = base.box(f"PN_CriolloPattern_{suffix}_{band}",(x,y,0.0125),
                              (0.49,0.048,0.001),motif_mat,shell,0.0)
            stripe.rotation_euler[2] = math.radians(angle + (90 if variant == 3 else 0))
        center_mat = coral if variant % 2 == 0 else green
        base.cylinder(f"PN_CriolloCenter_{suffix}",(x,y,0.0125),0.052,0.001,
                      center_mat,shell,16)


def smart_uv_all():
    # UV layer for future bakes. Cubic/procedural mapping remains visible in this pass.
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or len(obj.data.polygons) == 0:
            continue
        if not obj.data.uv_layers:
            obj.data.uv_layers.new(name="UVMap")


def create_grille_measurement_copy():
    """Evaluated mesh copies preserve editable curves while exposing true export cost."""
    source = bpy.data.collections["PN_Window_Grille"]
    root = bpy.data.collections.get("PN_Workshop_Environment")
    measure = new_collection("PN_Window_Grille_Measurement", root)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    tri_count = 0
    for obj in list(source.objects):
        if obj.type != "CURVE":
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = bpy.data.meshes.new_from_object(evaluated)
        copy = bpy.data.objects.new(obj.name+"_MeshEval",mesh)
        measure.objects.link(copy)
        copy.hide_render = True
        copy.hide_viewport = True
        tri_count += sum(max(1,len(p.vertices)-2) for p in mesh.polygons)
    measure["evaluated_triangle_count"] = tri_count
    measure["purpose"] = "export_cost_measurement_keep_editable_curves"
    print(f"PN_GRILLE_REAL_TRIANGLES {tri_count}")
    return tri_count


def add_camera(name, location, target, lens):
    bpy.ops.object.camera_add(location=location)
    cam = bpy.context.object
    cam.name = name
    cam.data.name = name+"_Data"
    cam.data.lens = lens
    base.aim_camera(cam, Vector(target))
    cam_col = bpy.data.collections.get("PN_Cameras")
    base.move_to_collection(cam, cam_col)
    return cam


def render_with_camera(scene, camera, path):
    scene.camera = camera
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def create_comparison(render_path):
    import numpy as np
    target = bpy.data.images.load(str(TARGET_PATH), check_existing=False)
    render = bpy.data.images.load(str(render_path), check_existing=False)
    target.scale(1536,1024)
    render.scale(1536,1024)
    a = np.empty(1536*1024*4,dtype=np.float32)
    b = np.empty_like(a)
    target.pixels.foreach_get(a)
    render.pixels.foreach_get(b)
    canvas = np.concatenate((a.reshape(1024,1536,4),b.reshape(1024,1536,4)),axis=1)
    img = bpy.data.images.new("PN_Camera_Comparison_V3",3072,1024,alpha=True)
    img.pixels.foreach_set(canvas.ravel())
    img.filepath_raw = str(COMPARISON_V3)
    img.file_format = "PNG"
    img.save()


def report_stats():
    objects = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    verts = sum(len(o.data.vertices) for o in objects)
    polys = sum(len(o.data.polygons) for o in objects)
    tris = 0
    for obj in objects:
        for poly in obj.data.polygons:
            tris += max(1,len(poly.vertices)-2)
    print(f"PN_STATS mesh_objects={len(objects)} vertices={verts} polygons={polys} estimated_triangles={tris}")
    print("PN_TEXTURE_MEMORY image_textures=0 estimated_runtime_MB=0 procedural_materials_require_future_bake")
    for cname in ("PN_Workshop_Shell","PN_Window_Grille_Measurement","PN_Exterior_PR"):
        col = bpy.data.collections[cname]
        col_tris = sum(max(1,len(p.vertices)-2) for o in col.all_objects if o.type=="MESH" for p in o.data.polygons)
        # Conservative uncompressed vertex/index/material overhead; GLB meshopt/Draco is usually far smaller.
        raw_mb = col_tris * 3 * 40 / (1024*1024)
        glb_mb = raw_mb * 0.28
        print(f"PN_GLB_ESTIMATE {cname} triangles={col_tris} estimated_compressed_MB={glb_mb:.3f}")


def main():
    RENDER_DIR.mkdir(parents=True,exist_ok=True)
    scene = base.build_scene()
    desktop = bpy.data.objects["PN_Camera_Desktop"]
    approved_transform = (desktop.location.copy(),desktop.rotation_euler.copy(),desktop.data.lens)
    grille_mat = prepare_materials()
    build_grille(grille_mat)
    build_exterior()
    refine_criollo_floor()
    create_grille_measurement_copy()
    smart_uv_all()

    # Natural exterior/world balance: readable shadows without a theatrical source.
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.32
    bpy.data.lights["PN_Light_Window_Key_Data"].energy = 540
    bpy.data.lights["PN_Light_Window_Key_Data"].color = (1.0,0.97,0.91)
    bpy.data.lights["PN_Light_Bench_Bounce_Data"].energy = 300
    bpy.data.lights["PN_Light_Bench_Bounce_Data"].color = (1.0,0.88,0.75)
    bpy.data.lights["PN_Light_Ceiling_Fill_Data"].energy = 170
    lighting_col = bpy.data.collections["PN_Lighting"]
    base.add_area_light("PN_Light_Exterior_Daylight", (0,2.55,3.15), (0,4.10,2.75),
                        720, (0.78,0.88,1.0), 5.8, lighting_col)

    scene.render.resolution_x = 1536
    scene.render.resolution_y = 1024
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.look = "AgX - Medium High Contrast"

    render_with_camera(scene,desktop,WINDOW_PREVIEW)
    create_comparison(WINDOW_PREVIEW)
    grille_cam = add_camera("PN_Camera_GrilleDetail",(0,-6.65,2.82),(0,1.28,2.84),72)
    render_with_camera(scene,grille_cam,GRILLE_PREVIEW)
    materials_cam = add_camera("PN_Camera_Materials",(0,-6.6,1.52),(0,0.72,0.76),58)
    render_with_camera(scene,materials_cam,MATERIALS_PREVIEW)
    exterior_cam = add_camera("PN_Camera_Exterior",(0,-7.0,2.70),(0,2.25,2.75),68)
    render_with_camera(scene,exterior_cam,EXTERIOR_PREVIEW)

    # Restore and assert the approved camera before saving.
    desktop.location = approved_transform[0]
    desktop.rotation_euler = approved_transform[1]
    desktop.data.lens = approved_transform[2]
    scene.camera = desktop
    assert tuple(round(v,6) for v in desktop.location) == (0.0,-11.15,2.52)
    assert round(desktop.data.lens,3) == 52.0
    report_stats()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    print(f"Created: {BLEND_PATH}")
    for path in (WINDOW_PREVIEW,GRILLE_PREVIEW,MATERIALS_PREVIEW,EXTERIOR_PREVIEW,COMPARISON_V3):
        print(f"Created: {path}")


if __name__ == "__main__":
    main()
