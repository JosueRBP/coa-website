import * as THREE from 'three'
import type { Product } from './catalog'
import { tagProductHierarchy } from '../assets/modelUtils'

function lensShape(width: number, height: number, lift: number): THREE.Shape {
  const shape = new THREE.Shape()
  shape.moveTo(-width * .5, height * .25)
  shape.bezierCurveTo(-width * .5, height * .48, -width * .38, height * .55, -width * .18, height * .54)
  shape.bezierCurveTo(width * .12, height * (.53 + lift), width * .42, height * .52, width * .49, height * .32)
  shape.bezierCurveTo(width * .53, height * .08, width * .5, -height * .3, width * .39, -height * .44)
  shape.bezierCurveTo(width * .2, -height * .56, -width * .22, -height * .56, -width * .4, -height * .43)
  shape.bezierCurveTo(-width * .5, -height * .29, -width * .52, height * .04, -width * .5, height * .25)
  return shape
}

function rimGeometry(width: number, height: number, lift: number): THREE.ExtrudeGeometry {
  const outer = lensShape(width, height, lift)
  const inner = lensShape(width - .15, height - .145, lift * .35)
  outer.holes.push(new THREE.Path(inner.getPoints(18)))
  const geometry = new THREE.ExtrudeGeometry(outer, { depth: .065, bevelEnabled: true, bevelSize: .018, bevelThickness: .018, bevelSegments: 2, curveSegments: 24 })
  geometry.center()
  return geometry
}

export function createEyewearDisplay(product: Product, importedModel?: THREE.Object3D): THREE.Group {
  const display = new THREE.Group(); display.name = `eyewear-${product.id}`; display.userData.productId = product.id
  if (importedModel) { importedModel.rotation.set(...product.model.rotation); importedModel.scale.setScalar(product.model.scale); display.add(importedModel); tagProductHierarchy(display, product.id); return display }

  const variant = Number(product.id) % 3
  const frameMaterial = new THREE.MeshPhysicalMaterial({
    color: new THREE.Color().setHSL(.045 + variant * .035, .25, .16 + variant * .045),
    metalness: .04, roughness: .24 + variant * .04,
    clearcoat: .72, clearcoatRoughness: .24,
  })
  const lensMaterial = new THREE.MeshPhysicalMaterial({ color: 0xb9cfcc, transparent: true, opacity: .18, roughness: .06, transmission: .68, thickness: .018, metalness: 0, depthWrite: false, side: THREE.DoubleSide })
  const width = .78 + variant * .02; const height = .61 - variant * .015; const lift = variant * .018
  const frameGeometry = rimGeometry(width, height, lift); const glassGeometry = new THREE.ShapeGeometry(lensShape(width - .12, height - .11, lift), 18)
  ;[-.43, .43].forEach((x) => { const lens = new THREE.Mesh(glassGeometry, lensMaterial); lens.position.set(x, 0, .003); const rim = new THREE.Mesh(frameGeometry, frameMaterial); rim.position.x = x; display.add(lens, rim) })

  const bridgeCurve = new THREE.QuadraticBezierCurve3(new THREE.Vector3(-.12,.025,0), new THREE.Vector3(0,.12,.015), new THREE.Vector3(.12,.025,0))
  display.add(new THREE.Mesh(new THREE.TubeGeometry(bridgeCurve, 12, .042, 8, false), frameMaterial))
  const templeGeometry = new THREE.BoxGeometry(.06, .065, .96)
  ;[-.82,.82].forEach((x) => { const hinge = new THREE.Mesh(new THREE.CylinderGeometry(.035,.035,.075,8), frameMaterial); hinge.rotation.z = Math.PI / 2; hinge.position.set(x,0,-.015); const temple = new THREE.Mesh(templeGeometry, frameMaterial); temple.position.set(x,-.015,-.43); temple.rotation.x = -.055; temple.rotation.y = x < 0 ? -.035 : .035; display.add(hinge, temple) })
  const padMaterial = new THREE.MeshPhysicalMaterial({ color: 0xd8d0bb, transparent: true, opacity: .58, roughness: .35 })
  ;[-.1,.1].forEach((x) => { const pad = new THREE.Mesh(new THREE.SphereGeometry(.035,7,5), padMaterial); pad.scale.set(.65,1,.4); pad.position.set(x,-.09,.06); display.add(pad) })
  display.traverse((child) => { if (child instanceof THREE.Mesh) { child.castShadow = true; child.receiveShadow = true } })
  tagProductHierarchy(display, product.id)
  return display
}
