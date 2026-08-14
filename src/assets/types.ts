import type * as THREE from 'three'

export type AssetPriority = 'essential' | 'optional'
export type AssetKind = 'workshop' | 'product' | 'lizard' | 'prop'

export interface AssetTransform {
  position: readonly [number, number, number]
  rotation: readonly [number, number, number]
  scale: readonly [number, number, number]
}

export interface AssetDefinition {
  id: string
  kind: AssetKind
  path: string
  priority: AssetPriority
  enabled: boolean
  transform: AssetTransform
  normalizeScale?: number
  castShadow?: boolean
  receiveShadow?: boolean
  expectedRootName?: string
}

export interface LoadedAsset {
  root: THREE.Group
  animations: THREE.AnimationClip[]
  definition: AssetDefinition
}

export interface AssetLoadProgress {
  loaded: number
  total: number
  percent: number
  currentUrl: string
}

