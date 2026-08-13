import * as THREE from 'three'
import type { Product } from './catalog'

export function createEyewearDisplay(product: Product): THREE.Group {
  const display = new THREE.Group()
  display.name = `eyewear-${product.id}`
  display.userData.productId = product.id
  const frameMaterial = new THREE.MeshStandardMaterial({ color: new THREE.Color().setHSL(0.07 + Number(product.id) * 0.012, 0.18, 0.22), metalness: 0.68, roughness: 0.28 })
  const lensMaterial = new THREE.MeshPhysicalMaterial({ color: 0x8b9692, transparent: true, opacity: 0.32, roughness: 0.12, metalness: 0.05 })
  const lensGeometry = new THREE.BoxGeometry(0.72, 0.34, 0.06)
  const rimGeometry = new THREE.TorusGeometry(0.39, 0.035, 8, 24)
  ;[-0.46, 0.46].forEach((x) => {
    const lens = new THREE.Mesh(lensGeometry, lensMaterial); lens.position.x = x; display.add(lens)
    const rim = new THREE.Mesh(rimGeometry, frameMaterial); rim.position.x = x; rim.scale.y = 0.62; display.add(rim)
  })
  display.add(new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.055, 0.06), frameMaterial))
  const templeGeometry = new THREE.BoxGeometry(0.05, 0.05, 0.82)
  ;[-0.86, 0.86].forEach((x) => { const temple = new THREE.Mesh(templeGeometry, frameMaterial); temple.position.set(x, 0, -0.38); temple.rotation.x = -0.08; display.add(temple) })
  display.traverse((child) => { if (child instanceof THREE.Mesh) { child.castShadow = true; child.userData.productId = product.id } })
  return display
}
