import type { AssetLoader } from './AssetLoader'
import type { AssetDefinition, LoadedAsset } from './types'

export class AssetRegistry {
  private readonly loaded = new Map<string, LoadedAsset>()
  private readonly loader: AssetLoader
  constructor(loader: AssetLoader) { this.loader = loader }

  get(id: string): LoadedAsset | undefined { return this.loaded.get(id) }

  async load(definition: AssetDefinition): Promise<LoadedAsset | null> {
    if (!definition.enabled) return null
    const existing = this.loaded.get(definition.id)
    if (existing) return existing
    try {
      const asset = await this.loader.load(definition)
      this.loaded.set(definition.id, asset)
      return asset
    } catch {
      return null
    }
  }

  async loadAll(definitions: AssetDefinition[]): Promise<Map<string, LoadedAsset>> {
    await Promise.all(definitions.map((definition) => this.load(definition)))
    return this.loaded
  }
}
