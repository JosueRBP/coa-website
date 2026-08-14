import * as THREE from 'three'
import type { AssetDefinition } from './types'

export function prepareModel(root: THREE.Group, definition: AssetDefinition): void {
  root.name ||= definition.expectedRootName ?? definition.id
  root.position.set(...definition.transform.position)
  root.rotation.set(...definition.transform.rotation)
  root.scale.set(...definition.transform.scale)
  root.traverse((child) => {
    if (child instanceof THREE.Mesh) {
      child.castShadow = definition.castShadow ?? true
      child.receiveShadow = definition.receiveShadow ?? true
      // Blender-authored PBR materials are intentionally preserved.
    }
  })
  if (definition.normalizeScale) normalizeModelScale(root, definition.normalizeScale)
  if (import.meta.env.DEV) validateModel(root, definition)
}

function normalizeModelScale(root: THREE.Group, targetSize: number): void {
  const size = new THREE.Vector3()
  new THREE.Box3().setFromObject(root).getSize(size)
  const largest = Math.max(size.x, size.y, size.z)
  if (largest > 0) root.scale.multiplyScalar(targetSize / largest)
}

function validateModel(root: THREE.Group, definition: AssetDefinition): void {
  const bounds = new THREE.Box3().setFromObject(root)
  const size = new THREE.Vector3()
  bounds.getSize(size)
  if (definition.expectedRootName && root.name !== definition.expectedRootName) console.info(`[assets] ${definition.id}: expected root "${definition.expectedRootName}", received "${root.name}".`)
  console.info(`[assets] ${definition.id}`, { name: root.name, size: size.toArray(), transform: definition.transform })
}

export function tagProductHierarchy(root: THREE.Object3D, productId: string): void {
  root.userData.productId = productId
  root.traverse((child) => { child.userData.productId = productId })
}

