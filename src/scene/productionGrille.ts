import * as THREE from 'three'
import { workshopMaterials as materials } from './workshopMaterials'

export type GrilleAnchorName = 'upper-left' | 'upper-center' | 'upper-right' | 'center-left' | 'center' | 'center-right' | 'lower-left' | 'lower-center' | 'lower-right'

const windowOrigin = new THREE.Vector3(0, 1.35, -4.34)
const grilleDepth = 0.34
const localAnchorCoordinates: Record<GrilleAnchorName, readonly [number, number]> = {
  'upper-left': [-1.55, 1.18], 'upper-center': [0, 2.7], 'upper-right': [1.55, 1.18],
  'center-left': [-1.55, -0.22], center: [0, -0.22], 'center-right': [1.55, -0.22],
  'lower-left': [-1.55, -1.5], 'lower-center': [0, -1.5], 'lower-right': [1.55, -1.5],
}

export const grilleRouteAnchors = Object.fromEntries(Object.entries(localAnchorCoordinates).map(([name, [x, y]]) => [name, new THREE.Vector3(x + windowOrigin.x, y + windowOrigin.y, grilleDepth + windowOrigin.z)])) as Record<GrilleAnchorName, THREE.Vector3>

function tube(points: THREE.Vector3[], radius = 0.025): THREE.Mesh {
  const curve = new THREE.CatmullRomCurve3(points)
  const mesh = new THREE.Mesh(new THREE.TubeGeometry(curve, Math.max(8, points.length * 5), radius, 6, false), materials.paintedIron)
  mesh.castShadow = true
  return mesh
}

function petal(centerX: number, centerY: number, flip = 1): THREE.Group {
  const motif = new THREE.Group()
  const height = 0.48
  const width = 0.24
  ;[-1, 1].forEach((side) => {
    motif.add(tube([
      new THREE.Vector3(centerX, centerY - height, grilleDepth),
      new THREE.Vector3(centerX + side * width, centerY - height * 0.2, grilleDepth),
      new THREE.Vector3(centerX + side * width * 0.72, centerY + height * 0.46, grilleDepth),
      new THREE.Vector3(centerX, centerY + height, grilleDepth),
    ], 0.021))
  })
  motif.rotation.z = flip < 0 ? Math.PI : 0
  return motif
}

export function createProductionGrille(): { root: THREE.Group; anchors: THREE.Group } {
  const root = new THREE.Group()
  root.name = 'PN_Window_Grille_ProceduralProduction'
  const anchors = new THREE.Group()
  anchors.name = 'PN_Grille_Route_Anchors'

  const verticalGeometry = new THREE.CylinderGeometry(0.026, 0.026, 3.65, 7)
  ;[-2.12, -1.55, 0, 1.55, 2.12].forEach((x) => {
    const bar = new THREE.Mesh(verticalGeometry, materials.paintedIron)
    bar.position.set(x, -0.46, grilleDepth)
    bar.castShadow = true
    root.add(bar)
  })
  ;[-1.72, -0.22, 1.08].forEach((y) => {
    root.add(tube([new THREE.Vector3(-2.12, y, grilleDepth), new THREE.Vector3(2.12, y, grilleDepth)], 0.027))
  })

  ;[-1.17, -0.39, 0.39, 1.17].forEach((x, index) => {
    root.add(petal(x, -0.94, index % 2 ? -1 : 1), petal(x, 0.42, index % 2 ? 1 : -1))
  })

  const archPoints = Array.from({ length: 19 }, (_, index) => {
    const angle = Math.PI - (Math.PI * index) / 18
    return new THREE.Vector3(Math.cos(angle) * 2.12, 1.08 + Math.sin(angle) * 2.12, grilleDepth)
  })
  root.add(tube(archPoints, 0.03))
  ;[-0.86, -0.43, 0, 0.43, 0.86].forEach((angle) => {
    root.add(tube([
      new THREE.Vector3(0, 1.08, grilleDepth),
      new THREE.Vector3(Math.sin(angle) * 0.9, 2.05, grilleDepth),
      new THREE.Vector3(Math.sin(angle) * 1.72, 2.62 - Math.abs(angle) * 0.35, grilleDepth),
    ], 0.022))
  })
  root.add(petal(0, 2.08))

  Object.entries(localAnchorCoordinates).forEach(([name, [x, y]]) => {
    const anchor = new THREE.Object3D()
    anchor.name = `PN_Grille_Anchor_${name}`
    anchor.position.set(x, y, grilleDepth)
    anchors.add(anchor)
  })
  root.add(anchors)
  return { root, anchors }
}

