import * as THREE from 'three'
import type { Product } from './catalog'
import { tagProductHierarchy } from '../assets/modelUtils'

function lensShape(width: number, height: number, lift: number): THREE.Shape {
  const shape = new THREE.Shape()
  shape.moveTo(-width * .48, height * .08)
  shape.bezierCurveTo(-width * .48, height * .46, -width * .2, height * .54, 0, height * .48)
  shape.bezierCurveTo(width * .25, height * .53, width * .48, height * .37, width * .48, height * .04)
  shape.bezierCurveTo(width * .46, -height * .4, width * .18, -height * (.48 - lift), 0, -height * .43)
  shape.bezierCurveTo(-width * .25, -height * .5, -width * .48, -height * .3, -width * .48, height * .08)
  return shape
}

function rimGeometry(width: number, height: number, lift: number): THREE.ExtrudeGeometry {
  const outer = lensShape(width, height, lift)
  const inner = lensShape(width - .105, height - .095, lift)
  outer.holes.push(new THREE.Path(inner.getPoints(18)))
  const geometry = new THREE.ExtrudeGeometry(outer, { depth: .045, bevelEnabled: true, bevelSize: .012, bevelThickness: .012, bevelSegments: 1, curveSegments: 18 })
  geometry.center()
  return geometry
}

export function createEyewearDisplay(product: Product, importedModel?: THREE.Object3D): THREE.Group {
  const display = new THREE.Group(); display.name = `eyewear-${product.id}`; display.userData.productId = product.id
  if (importedModel) { importedModel.rotation.set(...product.model.rotation); importedModel.scale.setScalar(product.model.scale); display.add(importedModel); tagProductHierarchy(display, product.id); return display }

  const variant = Number(product.id) % 3
  const frameMaterial = new THREE.MeshPhysicalMaterial({
    color: new THREE.Color().setHSL(.045 + variant * .035, .25, .16 + variant * .045),
    metalness: variant === 1 ? .62 : .28, roughness: variant === 2 ? .38 : .26,
    clearcoat: variant === 0 ? .48 : .22, clearcoatRoughness: .3,
  })
  const lensMaterial = new THREE.MeshPhysicalMaterial({ color: 0xb9cfcc, transparent: true, opacity: .18, roughness: .06, transmission: .68, thickness: .018, metalness: 0, depthWrite: false, side: THREE.DoubleSide })
  const width = .76 + variant * .025; const height = .56 - variant * .025; const lift = variant * .025
  const frameGeometry = rimGeometry(width, height, lift); const glassGeometry = new THREE.ShapeGeometry(lensShape(width - .12, height - .11, lift), 18)
  ;[-.43, .43].forEach((x) => { const lens = new THREE.Mesh(glassGeometry, lensMaterial); lens.position.set(x, 0, .003); const rim = new THREE.Mesh(frameGeometry, frameMaterial); rim.position.x = x; display.add(lens, rim) })

  const bridgeCurve = new THREE.QuadraticBezierCurve3(new THREE.Vector3(-.11,.015,0), new THREE.Vector3(0,.11,.015), new THREE.Vector3(.11,.015,0))
  display.add(new THREE.Mesh(new THREE.TubeGeometry(bridgeCurve, 10, .025, 6, false), frameMaterial))
  const templeGeometry = new THREE.BoxGeometry(.035, .035, .92)
  ;[-.82,.82].forEach((x) => { const hinge = new THREE.Mesh(new THREE.CylinderGeometry(.035,.035,.075,8), frameMaterial); hinge.rotation.z = Math.PI / 2; hinge.position.set(x,0,-.015); const temple = new THREE.Mesh(templeGeometry, frameMaterial); temple.position.set(x,-.015,-.43); temple.rotation.x = -.055; temple.rotation.y = x < 0 ? -.035 : .035; display.add(hinge, temple) })
  const padMaterial = new THREE.MeshPhysicalMaterial({ color: 0xd8d0bb, transparent: true, opacity: .58, roughness: .35 })
  ;[-.1,.1].forEach((x) => { const pad = new THREE.Mesh(new THREE.SphereGeometry(.035,7,5), padMaterial); pad.scale.set(.65,1,.4); pad.position.set(x,-.09,.06); display.add(pad) })
  display.traverse((child) => { if (child instanceof THREE.Mesh) { child.castShadow = true; child.receiveShadow = true } })
  tagProductHierarchy(display, product.id)
  return display
}
