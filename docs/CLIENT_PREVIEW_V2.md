# Client Preview V2

## Integración

`public/models/puerto-nuevo-client-preview-v2.glb` es la escena visual principal. La aplicación carga el GLB mediante el pipeline existente y solo oculta el taller procedural después de verificar las nueve raíces `PN_Eyewear_01–09`. Si la descarga falla o falta alguna raíz, mantiene el taller procedural como fallback.

Se preservan raycasting, Focus Mode, cierre, navegación entre productos, mobile pan, resize responsive, orientación, UI editorial y el bolero activado después de una interacción permitida. El DPR queda limitado a 1.25 en mobile y 1.75 en pantallas mayores.

## Composición provisional

La distribución 4–1–4 de las monturas es exclusiva para Client Preview V2. Las ocho laterales son instancias temporales del master congelado con variaciones compactas de negro, carey, ámbar y humo. No representa la distribución ni los productos definitivos.

## Estrategia PBR para producción

| Grupo | Resolución propuesta | Estrategia |
| --- | ---: | --- |
| Arquitectura | 2048² | Atlas Base Color + Normal + ORM |
| Banco y tablillas | 2048² | Atlas compartido |
| Piso criollo | 1024² | Set repetible con margen seguro |
| Reja | 512² | Material paramétrico ligero |
| Exterior | 1024² | Atlas compartido |
| Maquinaria y herramientas | 1024² | Atlas compartido |
| Eyewear | 512²–1024² | Materiales compactos por variante |
| Metales y vidrio | 512² o paramétrico | Parámetros GLTF cuando sea viable |

Base Color, Normal y ORM se comprimirán con KTX2/Basis en la optimización final. Client Preview V2 exporta valores materiales provisionales sin añadir dependencias de decodificación.

## Límites conocidos

- Bake PBR/KTX2 de producción pendiente.
- Monturas laterales provisionales y geométricamente compartidas.
- Lagartijo realista no incluido.
- Revisión final de loza pendiente.
- Optimización final de producción pendiente.

## Reanudación

> Retomar desde Eyewear Master Final Silhouette & Material Polish antes de la distribución definitiva y antes del lagartijo.
