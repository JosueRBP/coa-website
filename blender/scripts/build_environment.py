"""Build the Puerto Nuevo workshop architecture pass in Blender 5.2 LTS.

Run with:
  blender --background --python blender/scripts/build_environment.py

All dimensions are metres. Object names are stable and export-oriented.
"""

from pathlib import Path
import math

import bpy
import bmesh
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
BLEND_PATH = ROOT / "blender" / "puerto-nuevo-workshop.blend"
RENDER_DIR = ROOT / "blender" / "renders"
TARGET_PATH = ROOT / "art-direction" / "puerto-nuevo-blender-art-target-v2.png"
PREVIEW_PATH = RENDER_DIR / "architecture-preview-v2.png"
COMPARISON_PATH = RENDER_DIR / "camera-comparison-v2.png"
OVERLAY_PATH = RENDER_DIR / "camera-overlay-50.png"


def reset_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials,
                       bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def collection(name, parent=None):
    col = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(col)
    return col


def move_to_collection(obj, col):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    col.objects.link(obj)


def material(name, color, roughness=0.5, metallic=0.0, transmission=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if transmission:
        bsdf.inputs["Transmission Weight"].default_value = transmission
        bsdf.inputs["IOR"].default_value = 1.45
    return mat


def box(name, location, dimensions, mat, col, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new("EdgeSoftening", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    obj.data.materials.append(mat)
    move_to_collection(obj, col)
    return obj


def cylinder(name, location, radius, depth, mat, col, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth,
                                       location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    move_to_collection(obj, col)
    return obj


def arched_prism(name, center_x, sill_z, width, spring_z, top_z, depth, mat, col):
    """Extruded facade/window shape with vertical jambs and a shallow elliptical arch."""
    half = width / 2
    points = [(-half, 0, sill_z), (half, 0, sill_z), (half, 0, spring_z)]
    steps = 48
    for i in range(1, steps + 1):
        theta = i * math.pi / steps
        x = half * math.cos(theta)
        z = spring_z + (top_z - spring_z) * math.sin(theta)
        points.append((x, 0, z))
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm = bmesh.new()
    verts = [bm.verts.new((x + center_x, y, z)) for x, y, z in points]
    face = bm.faces.new(verts)
    geom = bmesh.ops.extrude_face_region(bm, geom=[face])
    extruded = [e for e in geom["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=Vector((0, depth, 0)), verts=extruded)
    bmesh.ops.translate(bm, vec=Vector((0, -depth / 2, 0)), verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def curve_tube(name, points, bevel_depth, mat, col):
    curve = bpy.data.curves.new(name + "_Curve", "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = bevel_depth
    curve.bevel_resolution = 3
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for p, co in zip(spline.points, points):
        p.co = (*co, 1.0)
    obj = bpy.data.objects.new(name, curve)
    col.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def drawer_bank(prefix, x, width, y, z0, height, drawers, mats, col, variant=0):
    wood, dark, brass = mats
    box(prefix + "_Plinth", (x, y + 0.01, z0 + 0.055),
        (width - 0.07, 0.65, 0.11), dark, col, 0.012)
    box(prefix + "_Carcass", (x, y, z0 + height / 2 + 0.05),
        (width, 0.72, height - 0.10), wood, col, 0.022)
    # Face frame makes each bank read as traditional built cabinetry, not stacked modules.
    rail = 0.055
    box(prefix + "_Frame_Left", (x-width/2+rail/2, y-0.39, z0+height/2),
        (rail, 0.055, height-0.10), wood, col, 0.008)
    box(prefix + "_Frame_Right", (x+width/2-rail/2, y-0.39, z0+height/2),
        (rail, 0.055, height-0.10), wood, col, 0.008)
    gap = 0.040 + 0.006 * variant
    drawer_h = (height - gap * (drawers + 1)) / drawers
    for i in range(drawers):
        z = z0 + gap + drawer_h / 2 + i * (drawer_h + gap)
        box(f"{prefix}_Drawer_{i+1:02d}", (x, y - 0.376, z),
            (width - 0.12, 0.042, drawer_h - 0.012), dark, col, 0.010)
        handle = box(f"{prefix}_Handle_{i+1:02d}", (x, y - 0.405, z),
                     (0.17 + 0.025 * (variant % 2), 0.025, 0.032), brass, col, 0.010)
    return


def build_scene():
    reset_scene()
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0

    root = collection("PN_Workshop_Environment")
    shell = collection("PN_Workshop_Shell", root)
    window_col = collection("PN_Arched_Window", root)
    bench_col = collection("PN_Main_Workbench", root)
    shelf_col = collection("PN_Product_Shelves", root)
    lighting = collection("PN_Lighting", root)
    cameras = collection("PN_Cameras", root)

    plaster = material("MAT_Plaster_Warm", (0.43, 0.39, 0.34), 0.88)
    plaster_inner = material("MAT_Window_Reveal", (0.72, 0.68, 0.60), 0.82)
    wood = material("MAT_Walnut_Provisional", (0.20, 0.075, 0.025), 0.42)
    wood_dark = material("MAT_Walnut_Dark", (0.095, 0.030, 0.012), 0.48)
    floor_mat = material("MAT_Terrazzo_Provisional", (0.34, 0.30, 0.25), 0.72)
    tile_a = material("MAT_Criollo_Tile_Cream", (0.43, 0.39, 0.31), 0.76)
    tile_b = material("MAT_Criollo_Tile_Aged", (0.32, 0.35, 0.31), 0.78)
    tile_motif = material("MAT_Criollo_Motif", (0.22, 0.30, 0.26), 0.73)
    tile_flower = material("MAT_Criollo_Flower", (0.43, 0.20, 0.13), 0.76)
    metal = material("MAT_Aged_Brass", (0.33, 0.19, 0.07), 0.34, 0.72)
    black = material("MAT_Blackened_Steel", (0.025, 0.022, 0.018), 0.31, 0.78)
    glass = material("MAT_Window_Glass", (0.50, 0.70, 0.72), 0.08, 0.0, 0.32)

    # Room: back wall is assembled around the arched void, preserving a real opening.
    room_w, room_d, room_h = 8.4, 3.9, 4.8
    back_y = 1.55
    box("PN_Floor", (0, -0.40, -0.075), (room_w, room_d, 0.15), floor_mat, shell)
    # Provisional encaustic-style grid to judge scale and perspective only.
    tile_size = 0.56
    for ix in range(-7, 8):
        for iy in range(-3, 4):
            x, y = ix * tile_size, -0.40 + iy * tile_size
            tile = box(f"PN_FloorTile_{ix+8:02d}_{iy+4:02d}", (x, y, 0.006),
                       (tile_size-0.018, tile_size-0.018, 0.012),
                       tile_a if (ix+iy) % 2 == 0 else tile_b, shell, 0.006)
            motif = box(f"PN_FloorMotif_{ix+8:02d}_{iy+4:02d}", (x, y, 0.014),
                        (0.18, 0.18, 0.008), tile_motif, shell, 0.012)
            motif.rotation_euler[2] = math.radians(45)
            if (ix + 2*iy) % 3 == 0:
                cylinder(f"PN_FloorFlower_{ix+8:02d}_{iy+4:02d}",
                         (x, y, 0.020), 0.052, 0.008, tile_flower, shell, 12)
    box("PN_Ceiling", (0, -0.40, room_h + 0.08), (room_w, room_d, 0.16), plaster, shell)
    box("PN_Wall_Left", (-room_w/2 + 0.09, -0.40, room_h/2),
        (0.18, room_d, room_h), plaster, shell)
    box("PN_Wall_Right", (room_w/2 - 0.09, -0.40, room_h/2),
        (0.18, room_d, room_h), plaster, shell)

    # Segmental arch: wide span and low 0.58 m rise, matching the official silhouette.
    win_w, sill, spring, top = 3.65, 1.42, 3.98, 4.38
    jamb_x = win_w / 2
    box("PN_BackWall_Left", (-(room_w + win_w)/4, back_y, room_h/2),
        ((room_w-win_w)/2, 0.18, room_h), plaster, shell)
    box("PN_BackWall_Right", ((room_w + win_w)/4, back_y, room_h/2),
        ((room_w-win_w)/2, 0.18, room_h), plaster, shell)
    box("PN_BackWall_BelowWindow", (0, back_y, sill/2), (win_w, 0.18, sill), plaster, shell)
    box("PN_BackWall_AboveWindow", (0, back_y, (room_h+top)/2),
        (win_w, 0.18, room_h-top), plaster, shell)
    # Corner infill above the curved crown makes the wall read as a proper arch opening.
    for side in (-1, 1):
        for i in range(12):
            x0 = i * (jamb_x / 12)
            x1 = (i + 1) * (jamb_x / 12)
            xmid = (x0 + x1) / 2
            arch_z = spring + (top-spring) * math.sqrt(max(0.0, 1-(xmid/jamb_x)**2))
            width = x1-x0+0.008
            box(f"PN_ArchSpandrel_{'L' if side < 0 else 'R'}_{i+1:02d}",
                (side*xmid, back_y, (arch_z+top)/2), (width, 0.18, top-arch_z), plaster, shell)

    glass_obj = arched_prism("PN_Window_Glass", 0, sill+0.07, win_w-0.30, spring-0.03,
                             top-0.15, 0.018, glass, window_col)
    glass_obj.location.y = back_y + 0.025
    # Thick arch and jamb reveal, kept modular for future grille insertion.
    arch_pts = []
    for i in range(49):
        t = i * math.pi / 48
        arch_pts.append((jamb_x * math.cos(t), back_y-0.13,
                         spring + (top-spring)*math.sin(t)))
    curve_tube("PN_Window_Arch_Frame", arch_pts, 0.135, plaster_inner, window_col)
    inner_half = jamb_x - 0.16
    inner_pts = []
    for i in range(49):
        t = i * math.pi / 48
        inner_pts.append((inner_half * math.cos(t), back_y-0.245,
                          (spring-0.02) + (top-spring-0.12)*math.sin(t)))
    curve_tube("PN_Window_Inner_Reveal", inner_pts, 0.050, plaster_inner, window_col)
    box("PN_Window_Jamb_Left", (-jamb_x, back_y-0.13, (sill+spring)/2),
        (0.27, 0.38, spring-sill), plaster_inner, window_col, 0.025)
    box("PN_Window_Jamb_Right", (jamb_x, back_y-0.13, (sill+spring)/2),
        (0.27, 0.38, spring-sill), plaster_inner, window_col, 0.025)
    box("PN_Window_Sill", (0, back_y-0.20, sill-0.045),
        (win_w+0.28, 0.50, 0.17), plaster_inner, window_col, 0.025)
    # Provisional mullions only; ornamental grille is intentionally deferred.
    for i, x in enumerate((-1.32, -0.66, 0, 0.66, 1.32), 1):
        box(f"PN_Window_Mullion_V_{i:02d}", (x, back_y-0.22, 2.61),
            (0.018, 0.028, 2.02), black, window_col)
    for i, z in enumerate((2.12, 2.70, 3.27), 1):
        box(f"PN_Window_Mullion_H_{i:02d}", (0, back_y-0.22, z),
            (win_w-0.38, 0.028, 0.018), black, window_col)

    # Main workbench and cabinetry; the central knee opening is 1.72 m wide.
    bench_y, counter_z = 0.92, 1.02
    box("PN_Workbench_Countertop", (0, bench_y-0.18, counter_z),
        (7.85, 0.88, 0.14), wood, bench_col, 0.035)
    box("PN_Workbench_BackRail", (0, bench_y+0.22, counter_z+0.16),
        (7.85, 0.12, 0.25), wood_dark, bench_col, 0.018)
    box("PN_Workbench_ToeKick_Left", (-2.63, bench_y+0.06, 0.075),
        (3.50, 0.58, 0.15), wood_dark, bench_col, 0.012)
    box("PN_Workbench_ToeKick_Right", (2.63, bench_y+0.06, 0.075),
        (3.50, 0.58, 0.15), wood_dark, bench_col, 0.012)
    bank_specs = [(-3.46, 0.88, 2), (-2.48, 0.90, 4), (-1.48, 0.88, 3),
                  (1.48, 0.88, 4), (2.48, 0.90, 3), (3.46, 0.88, 2)]
    for i, (x, w, drawers) in enumerate(bank_specs, 1):
        drawer_bank(f"PN_Cabinet_{i:02d}", x, w, bench_y, 0.00, 0.92,
                    drawers, (wood, wood_dark, metal), bench_col, variant=i % 3)
        if i < 6 and i != 3:
            box(f"PN_Cabinet_Divider_{i:02d}", (x+w/2+0.05, bench_y-0.38, 0.52),
                (0.075, 0.06, 0.80), wood, bench_col, 0.008)
    box("PN_Central_Opening_Header", (0, bench_y, 0.89), (1.72, 0.72, 0.13), wood, bench_col)
    box("PN_Central_Opening_Apron", (0, bench_y-0.39, 0.84),
        (1.72, 0.07, 0.18), wood_dark, bench_col, 0.012)

    # Stool: simple production-scale placeholder, no small detailing.
    cylinder("PN_Stool_Seat", (0, -0.20, 0.68), 0.35, 0.105, wood, bench_col, 48)
    for i, (x, y) in enumerate(((-.25,-.22),(.25,-.22),(-.21,.06),(.21,.06)), 1):
        leg = cylinder(f"PN_Stool_Leg_{i:02d}", (x, y, 0.32), 0.025, 0.62, black, bench_col, 16)
        leg.rotation_euler[1] = math.radians(5 if x < 0 else -5)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.285, minor_radius=0.018,
                                    major_segments=40, minor_segments=10,
                                    location=(0, -0.08, 0.31))
    stool_ring = bpy.context.object
    stool_ring.name = "PN_Stool_FootRing"
    stool_ring.data.materials.append(black)
    move_to_collection(stool_ring, bench_col)

    # Exactly eight product shelves: four left, four right.
    shelf_zs = (1.48, 2.02, 2.56, 3.10)
    for side, sx, label in ((-1, -2.65, "L"), (1, 2.65, "R")):
        for level, z in enumerate(shelf_zs, 1):
            box(f"PN_Shelf_{label}_{level:02d}", (sx, back_y-0.30, z),
                (0.99 + 0.025*((level+side) % 2), 0.33, 0.125), wood, shelf_col, 0.025)
            box(f"PN_ShelfBracket_{label}_{level:02d}", (sx, back_y-0.13, z-0.08),
                (0.18, 0.045, 0.09), metal, shelf_col, 0.010)

    # Camera tuned to retain floor, counter, shelves and the complete arch at 3:2.
    bpy.ops.object.camera_add(location=(0, -11.15, 2.52))
    camera = bpy.context.object
    camera.name = "PN_Camera_Desktop"
    camera.data.name = "PN_Camera_Desktop_Data"
    camera.data.lens = 52
    camera.data.sensor_width = 36
    camera.data.dof.use_dof = False
    move_to_collection(camera, cameras)
    aim_camera(camera, Vector((0, 0.72, 1.69)))
    scene.camera = camera

    # Warm room ambience and a large daylight source immediately outside the window.
    scene.world.color = (0.025, 0.021, 0.017)
    world_nodes = scene.world.node_tree if scene.world and scene.world.use_nodes else None
    if not world_nodes:
        scene.world.use_nodes = True
        world_nodes = scene.world.node_tree
    bg = world_nodes.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.055, 0.045, 0.035, 1)
    bg.inputs["Strength"].default_value = 0.22

    add_area_light("PN_Light_Window_Key", (0, 1.14, 2.95), (0, 0.10, 1.45),
                   860, (1.0, 0.94, 0.84), 4.25, lighting)
    add_area_light("PN_Light_Ceiling_Fill", (0, -0.25, 4.35), (0, 0.45, 1.45),
                   250, (0.88, 0.91, 1.0), 4.6, lighting)
    add_area_light("PN_Light_Bench_Bounce", (0, -0.85, 1.45), (0, 0.75, 0.82),
                   310, (1.0, 0.88, 0.72), 3.6, lighting)

    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1536
    scene.render.resolution_y = 1024
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.image_settings.color_depth = "8"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.render.filepath = str(PREVIEW_PATH)
    scene.render.resolution_percentage = 100
    return scene


def aim_camera(obj, target):
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def add_area_light(name, location, target, energy, color, size, col):
    data = bpy.data.lights.new(name + "_Data", "AREA")
    data.energy = energy
    data.color = color
    data.shape = "RECTANGLE"
    data.size = size
    data.size_y = size
    obj = bpy.data.objects.new(name, data)
    col.objects.link(obj)
    obj.location = location
    aim_camera(obj, Vector(target))
    return obj


def create_comparison():
    """Create full-resolution side-by-side and 50% overlay diagnostic images."""
    import numpy as np

    target = bpy.data.images.load(str(TARGET_PATH), check_existing=False)
    render = bpy.data.images.load(str(PREVIEW_PATH), check_existing=False)
    target.scale(1536, 1024)
    render.scale(1536, 1024)
    a = np.empty(1536 * 1024 * 4, dtype=np.float32)
    b = np.empty_like(a)
    target.pixels.foreach_get(a)
    render.pixels.foreach_get(b)
    a = a.reshape((1024, 1536, 4))
    b = b.reshape((1024, 1536, 4))
    canvas = np.concatenate((a, b), axis=1)
    image = bpy.data.images.new("PN_Camera_Comparison_V2", width=3072, height=1024, alpha=True)
    image.pixels.foreach_set(canvas.ravel())
    image.filepath_raw = str(COMPARISON_PATH)
    image.file_format = "PNG"
    image.save()
    overlay_pixels = a * 0.5 + b * 0.5
    overlay_pixels[:, :, 3] = 1.0
    overlay = bpy.data.images.new("PN_Camera_Overlay_50", width=1536, height=1024, alpha=False)
    overlay.pixels.foreach_set(overlay_pixels.ravel())
    overlay.filepath_raw = str(OVERLAY_PATH)
    overlay.file_format = "PNG"
    overlay.save()


def main():
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    BLEND_PATH.parent.mkdir(parents=True, exist_ok=True)
    scene = build_scene()
    bpy.ops.render.render(write_still=True)
    create_comparison()
    # Save after rendering so settings and the comparison datablock are retained.
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    print(f"Created: {BLEND_PATH}")
    print(f"Created: {PREVIEW_PATH}")
    print(f"Created: {COMPARISON_PATH}")
    print(f"Created: {OVERLAY_PATH}")


if __name__ == "__main__":
    main()
