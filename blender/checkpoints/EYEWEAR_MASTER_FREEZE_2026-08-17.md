# Eyewear Master Freeze — 2026-08-17

Checkpoint formal del estado visual aprobado para Client Preview V2. El archivo fuente principal y este checkpoint no deben modificarse durante la integración web.

## Estado congelado

- Cámara desktop: `(0, -11.15, 2.52)`, lente `52 mm`.
- Master actual: Eyewear Master Final Silhouette & Material Polish; frontal panto continuo, puente keyhole integrado, patillas completas, acetato negro/carey y lentes transparentes.
- Escala física: `157 mm` de ancho; patillas de `146 mm`.
- Escala editorial: `6.011×`.
- Proyección hero: aproximadamente `185.1 px` en un render de 1536 px.
- `PN_Eyewear_01–08`: vacíos.
- `PN_Eyewear_09`: contiene `PN_Eyewear_Master_Display`.
- Tablillas laterales: `0.29 m`.
- Iluminación de producto: nueve spotlights.
- Piso, madera, maquinaria, reja, exterior y tocadiscos: estado visual actual preservado.
- Ruta interactiva futura: `PN_LizardPath_Anchor_01–08` preservados.
- Geometría evaluada del master: 7,292 vértices, 5,556 polígonos y 8,224 triángulos.
- Métrica diagnóstica final: 46.73% de coincidencia simétrica de tres contornos dentro de 5 px; excluye patillas posteriores, lentes, reflejos, remaches, materiales y fondo.

## Pendientes visuales conocidos

- Polish final adicional del master, si el cliente lo solicita.
- Distribución definitiva de las nueve monturas.
- Revisión final de loza.
- Lagartijo realista.
- Optimización final de producción.

La distribución 4–1–4 creada posteriormente dentro de `blender/web-export/puerto-nuevo-client-preview-v2.blend` es provisional y existe exclusivamente para Client Preview V2.

## Procedencia

- Último script ejecutado antes de congelar: `blender/scripts/polish_eyewear_master_final.py`.
- Referencia frontal: `art-direction/eyewear-master-views/eyewear-master-front-approved.png`.
- Referencia lateral: `art-direction/eyewear-master-views/eyewear-master-side-approved.png`.
- Referencia superior: `art-direction/eyewear-master-views/eyewear-master-top-approved.png`.
- Referencia tres cuartos: `art-direction/eyewear-master-views/eyewear-master-three-quarter-approved.png`.

## SHA-256

- Checkpoint `.blend`: `27A4E58340150BE22057E124BD0A57AA88577BBE0A9EF69B629551F2D8813ABC`
- Frontal: `6CF886D73D97592648A856CCB39C88771FF6DC35184F6F1EB62CA17E6E0D8DE4`
- Lateral: `731452669EA9D8C15DFB31336D712600EBA766E3B91BD0184382A2188B3D88E0`
- Superior: `CE7BE8B523D5F9B6A9ABCE89B2C926A6D417C3F0D69014E141986CD47074DA0D`
- Tres cuartos: `A291C9884DDB402FB0EB7A22154023660ABEC68AB19E6E08380737CE30979DD5`

## Punto de reanudación

> Retomar desde Eyewear Master Final Silhouette & Material Polish antes de la distribución definitiva y antes del lagartijo.
