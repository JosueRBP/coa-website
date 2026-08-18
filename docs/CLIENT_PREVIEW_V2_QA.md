# Client Preview V2 — QA

Fecha: 2026-08-18

## Verificaciones completadas

- `npm run build`: aprobado con TypeScript y Vite 8.2.1.
- Reimportación del GLB en Blender 5.2 LTS: aprobada.
- GLB: 618 objetos reimportados, 588 meshes.
- Raíces `PN_Eyewear_01–09`: presentes.
- Anclajes `PN_LizardPath_Anchor_01–08`: presentes.
- HTTP local: `index.html` y GLB responden `200`.
- Content-Type del GLB: `model/gltf-binary`.
- Responsive resize y DPR: inspección estática; límite mobile 1.25, desktop/tablet 1.75.
- Fallback: inspección de flujo; el taller procedural solo se oculta después de validar las nueve raíces.
- Audio: ruta existente preservada, loop y desbloqueo tras interacción preservados.
- Focus Mode, cierre, navegación y mobile pan: controladores existentes preservados y enlazados al mismo arreglo mutable de nueve raíces importadas.
- Scroll horizontal: bloqueado por estilos existentes en `html`, `body` y `#app`.

## Viewports objetivo

- Desktop 1920×1080.
- Laptop 1366×768.
- Mobile 390×844.
- Mobile 430×932.

El código responsive contempla los cuatro tamaños, orientación vertical y cambios de viewport. La comprobación visual/capturas y la inspección de consola en navegador quedaron pendientes porque no había ninguna instancia del navegador integrado disponible en esta sesión. No se declara QA visual aprobado sin esa evidencia.

## Peso

- GLB: 4,016,036 bytes (3.83 MB).
- JS: 782.78 KB minificado; 213.77 KB gzip.
- CSS: 13.01 KB; 3.49 KB gzip.
- Build completo con modelo y audio: 7,195,844 bytes (6.86 MB).
- Texturas externas web: 0 MB; los valores materiales provisionales están incluidos en el GLB.

## Advertencias

- Vite informa que el chunk principal supera 500 KB. No bloquea el build; el code splitting queda como optimización posterior.
- Falta QA visual real en navegador y capturas de los cuatro viewports.
- Falta bake PBR/KTX2 de producción.
