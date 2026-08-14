# Puerto Nuevo 1960 — Blender Asset Guide

## Export format and scene setup

- Export production models as glTF 2.0 binary (`.glb`) unless external texture iteration specifically requires `.gltf`.
- Model in meters where practical. One Blender meter should arrive as one Three.js world unit.
- Export Y-up using Blender's standard glTF exporter.
- Apply location-independent rotation and scale before export (`Ctrl+A`).
- Keep origins intentional: floor-level for architecture and machinery, mounting point for wall objects, hinge/center point for interactive objects.
- Remove hidden prototypes, unused cameras, lights, and materials from exports.
- Use descriptive, stable names. Avoid default names such as `Cube.001`.

Recommended roots include:

- `PN_Workshop_Shell`
- `PN_Arched_Window`
- `PN_Window_Grille`
- `PN_Main_Workbench`
- `PN_DrillPress`
- `PN_Frame_01` through `PN_Frame_09`
- `PN_Lizard`

The workshop is intentionally modular. Export architecture, grille, window, workbench, machinery, foreground props, products, and lizard separately rather than as one monolithic scene.

## Geometry

- Preserve silhouette quality where it matters and remove unseen geometry.
- Prefer clean topology and sensible smoothing over dense subdivision.
- Apply modifiers that are required for the final silhouette.
- Use instancing for repeated workshop pieces when it survives export cleanly.
- Eyewear origins must support rotation during Focus Mode.
- The lizard should use meaningful bone names and a stable root bone.

## Materials and textures

- Use metallic/roughness PBR materials compatible with glTF.
- Pack or correctly reference textures; avoid workstation-absolute paths.
- Keep color space correct: sRGB for base color/emissive, non-color for normal/roughness/metallic.
- Use 1K textures for small props and background objects.
- Use up to 2K for hero workshop pieces, eyewear, and the lizard when the visual gain is clear.
- Avoid 4K textures unless profiling proves they are necessary.
- Combine texture channels and atlases where this reduces requests without harming iteration.

## Animation

- Use meaningful clip names. Planned lizard clips are `idle`, `walk`, `turn`, `lookLeft`, `lookRight`, and `startled`.
- Keep animation actions self-contained and remove unused NLA tracks before export.
- Test loop boundaries for idle and walk clips.
- AnimationMixers are updated by the application's central frame loop; models must not contain runtime scripts or independent timers.

## Preliminary web budgets

These are optimization goals rather than hard limits:

- Workshop core, combined across modular essential GLBs: preferably 5–8 MB compressed or less.
- Each eyewear model: preferably 1–2 MB or less.
- Lizard including animations: preferably 1–2 MB or less.
- Optional machinery and foreground props should be aggressively optimized and must not delay first interaction.

Mobile is a primary target. Review triangle count, draw calls, texture memory, and decoded asset size—not only the `.glb` transfer size.

## Integration checklist

1. Copy the asset into the matching `public/models` or `public/textures` directory.
2. Confirm its path and transform in `src/assets/assetManifest.ts`.
3. Set that manifest entry's `enabled` flag to `true`.
4. Run the site and inspect development-only name, bounds, and transform logging.
5. Tune only the manifest transform; do not bury export corrections in scene code.
6. Verify shadows, materials, responsive framing, raycasting, and Focus Mode.
7. Leave the procedural region available until the production model passes desktop and mobile review.

