import { AssetLoader } from './AssetLoader'
import { AssetRegistry } from './AssetRegistry'
import { allAssets, assetManifest } from './assetManifest'
import { tagProductHierarchy } from './modelUtils'
import type { AssetLoadProgress } from './types'
import type { WorkshopContent } from '../scene/createWorkshop'
import type { Product } from '../products/catalog'

export class AssetPipeline {
  readonly loader = new AssetLoader()
  readonly registry = new AssetRegistry(this.loader)

  onProgress(listener: (progress: AssetLoadProgress) => void): void { this.loader.onProgress(listener) }

  async loadEssential(workshop: WorkshopContent, products: Product[]): Promise<void> {
    const definitions = allAssets.filter((asset) => asset.priority === 'essential' && asset.enabled)
    await this.registry.loadAll(definitions)
    this.integrateWorkshop(workshop)
    this.integrateProducts(workshop, products)
  }

  async loadOptional(workshop: WorkshopContent): Promise<void> {
    await this.registry.loadAll(allAssets.filter((asset) => asset.priority === 'optional' && asset.enabled))
    this.integrateWorkshop(workshop)
  }

  private integrateWorkshop(workshop: WorkshopContent): void {
    const regionAssets = [
      [workshop.regions.architecture, assetManifest.workshop.architecture],
      [workshop.regions.window, assetManifest.workshop.window],
      [workshop.regions.grille, assetManifest.workshop.grille],
      [workshop.regions.mainWorkbench, assetManifest.workshop.workbench],
      [workshop.regions.leftDisplays, assetManifest.workshop.leftDisplays],
      [workshop.regions.rightDisplays, assetManifest.workshop.rightDisplays],
      [workshop.regions.floor, assetManifest.workshop.floor],
      [workshop.regions.exterior, assetManifest.workshop.exterior],
      [workshop.regions.machinery, assetManifest.workshop.machinery],
      [workshop.regions.foregroundProps, assetManifest.workshop.foreground],
    ] as const
    regionAssets.forEach(([region, definition]) => {
      const asset = this.registry.get(definition.id)
      if (!asset) return
      region.clear()
      region.add(asset.root)
    })
  }

  private integrateProducts(workshop: WorkshopContent, products: Product[]): void {
    products.forEach((product, index) => {
      const definition = assetManifest.products[product.id]
      if (!definition) return
      const asset = this.registry.get(definition.id)
      const display = workshop.eyewear[index]
      if (!asset || !display) return
      display.clear()
      asset.root.rotation.set(...product.model.rotation)
      asset.root.scale.setScalar(product.model.scale)
      display.add(asset.root)
      tagProductHierarchy(display, product.id)
    })
  }
}
