import { LoadingManager, type Group } from 'three'
import { GLTFLoader, type GLTF } from 'three/addons/loaders/GLTFLoader.js'
import { clone } from 'three/addons/utils/SkeletonUtils.js'
import { prepareModel } from './modelUtils'
import type { AssetDefinition, AssetLoadProgress, LoadedAsset } from './types'

export class AssetLoader {
  private readonly manager = new LoadingManager()
  private readonly loader = new GLTFLoader(this.manager)
  private readonly cache = new Map<string, Promise<GLTF>>()
  private progressListener: ((progress: AssetLoadProgress) => void) | null = null

  constructor() {
    this.manager.onProgress = (url, loaded, total) => this.progressListener?.({ loaded, total, percent: total ? Math.round((loaded / total) * 100) : 0, currentUrl: url })
  }

  onProgress(listener: (progress: AssetLoadProgress) => void): void { this.progressListener = listener }

  configure(configureLoader: (loader: GLTFLoader) => void): void {
    // Future DRACO/Meshopt decoders can be attached here without changing call sites.
    configureLoader(this.loader)
  }

  async load(definition: AssetDefinition): Promise<LoadedAsset> {
    let pending = this.cache.get(definition.path)
    if (!pending) {
      pending = this.loader.loadAsync(definition.path)
      this.cache.set(definition.path, pending)
    }
    try {
      const gltf = await pending
      const root = clone(gltf.scene) as Group
      prepareModel(root, definition)
      return { root, animations: gltf.animations, definition }
    } catch (error) {
      this.cache.delete(definition.path)
      throw error
    }
  }

  async loadOrFallback(definition: AssetDefinition, fallback: () => LoadedAsset): Promise<LoadedAsset> {
    if (!definition.enabled) return fallback()
    try { return await this.load(definition) } catch { return fallback() }
  }
}
