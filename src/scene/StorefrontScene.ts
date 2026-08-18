import * as THREE from 'three'
import { ParallaxController } from '../interactions/ParallaxController'
import { ProductInteraction } from '../interactions/ProductInteraction'
import { StorefrontUI } from '../ui/StorefrontUI'
import { createWorkshop } from './createWorkshop'
import { ResponsiveSceneController } from './ResponsiveSceneController'
import { LivingWorkshop } from '../living/LivingWorkshop'
import { ProductFocusController } from '../interactions/ProductFocusController'
import { MobileWorkshopPan } from '../interactions/MobileWorkshopPan'
import { AssetPipeline } from '../assets/AssetPipeline'
import { assetManifest } from '../assets/assetManifest'
import { products } from '../products/catalog'
import type { WorkshopContent } from './createWorkshop'
import { tagProductHierarchy } from '../assets/modelUtils'

export class StorefrontScene {
  private readonly scene = new THREE.Scene(); private readonly camera = new THREE.PerspectiveCamera(26, 1, 0.1, 100)
  private readonly renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' }); private readonly parallax: ParallaxController; private readonly ui = new StorefrontUI()
  private readonly responsiveLayout: ResponsiveSceneController
  private readonly productInteraction: ProductInteraction
  private readonly focusController: ProductFocusController
  private readonly mobilePan: MobileWorkshopPan
  private readonly livingWorkshop: LivingWorkshop
  private readonly clock = new THREE.Clock()
  private readonly assetPipeline = new AssetPipeline()
  private readonly workshop: WorkshopContent
  private readonly container: HTMLElement
  private resizeFrame: number | null = null
  constructor(container: HTMLElement) {
    this.container = container
    this.scene.background = new THREE.Color(0xbccbc8); this.scene.fog = new THREE.Fog(0xbccbc8, 23, 40); this.camera.position.set(0, 0.25, 10.6)
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75)); this.renderer.shadowMap.enabled = true; this.renderer.shadowMap.type = THREE.PCFSoftShadowMap
    this.renderer.outputColorSpace = THREE.SRGBColorSpace; this.renderer.toneMapping = THREE.ACESFilmicToneMapping; this.renderer.toneMappingExposure = 1.12; this.container.appendChild(this.renderer.domElement)
    const workshop = createWorkshop(); this.workshop = workshop; this.scene.add(workshop.root); const daylight = this.addLighting(); this.parallax = new ParallaxController(this.container); this.responsiveLayout = new ResponsiveSceneController(this.camera, workshop, this.parallax)
    this.livingWorkshop = new LivingWorkshop(daylight); this.scene.add(this.livingWorkshop.root)
    this.productInteraction = new ProductInteraction(this.container, this.camera, workshop.eyewear, (product) => this.focusController.open(product))
    this.mobilePan = new MobileWorkshopPan(this.container, this.camera, workshop.eyewear, this.parallax)
    this.focusController = new ProductFocusController(this.camera, this.container, workshop.eyewear, this.parallax, this.productInteraction, this.mobilePan, this.ui, this.applyWorkshopLayout)
    this.livingWorkshop.bindInteraction(this.container, this.camera, () => !this.focusController.isFocused)
    window.addEventListener('resize', this.scheduleResize, { passive: true })
    this.assetPipeline.onProgress((progress) => this.ui.updateLoadingProgress(progress))
    this.applyResize()
  }
  private addLighting(): THREE.DirectionalLight {
    this.scene.add(new THREE.HemisphereLight(0xe9f0ec, 0x5b554e, 1.15))
    const windowFill = new THREE.RectAreaLight(0xfff1d6, 12, 4.6, 5.6)
    windowFill.position.set(0, 1.25, -3.95)
    windowFill.lookAt(0, -0.7, 2.5)
    this.scene.add(windowFill)
    const daylight = new THREE.DirectionalLight(0xffe4bd, 3)
    daylight.position.set(-0.8, 5.8, -3.35)
    daylight.target.position.set(0.4, -2.2, 2.6)
    daylight.castShadow = true
    daylight.shadow.mapSize.set(1536, 1536)
    daylight.shadow.bias = -0.00025
    daylight.shadow.normalBias = 0.035
    daylight.shadow.radius = 4
    daylight.shadow.camera.near = 0.5; daylight.shadow.camera.far = 20
    daylight.shadow.camera.left = -8; daylight.shadow.camera.right = 8; daylight.shadow.camera.top = 7; daylight.shadow.camera.bottom = -5
    this.scene.add(daylight, daylight.target)
    const roomFill = new THREE.PointLight(0xe7eee7, 1.5, 16, 2)
    roomFill.position.set(-4.8, 3.8, 3.2)
    this.scene.add(roomFill)
    const benchBounce = new THREE.RectAreaLight(0xd8a978, 2.5, 7.5, 1.5)
    benchBounce.position.set(0, -1.45, -1.7); benchBounce.lookAt(0, .2, -3.8); this.scene.add(benchBounce)
    return daylight
  }
  private scheduleResize = (): void => {
    if (this.resizeFrame !== null) return
    this.resizeFrame = requestAnimationFrame(() => {
      this.resizeFrame = null
      this.applyResize()
    })
  }
  private applyResize(): void {
    const width = this.container.clientWidth; const height = this.container.clientHeight
    if (width <= 0 || height <= 0 || !Number.isFinite(width / height)) return
    this.camera.aspect = width / height; this.camera.updateProjectionMatrix()
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, width < 680 ? 1.25 : 1.75)); this.renderer.setSize(width, height, false)
    if (this.focusController.isFocused) this.focusController.reapplyAfterResize()
    else this.applyWorkshopLayout()
    this.mobilePan.setViewport(width)
    this.livingWorkshop.setViewport(width)
  }
  private applyWorkshopLayout = (): void => {
    this.productInteraction.cancelTransformAnimations()
    this.responsiveLayout.apply(this.container.clientWidth)
  }
  private animate = (): void => {
    requestAnimationFrame(this.animate)
    const delta = Math.min(this.clock.getDelta(), 0.05)
    this.livingWorkshop.update(delta, this.clock.elapsedTime)
    this.parallax.update(this.camera)
    this.renderer.render(this.scene, this.camera)
  }
  start(): void {
    this.animate()
    void this.prepareAssets()
  }
  private async prepareAssets(): Promise<void> {
    const preview = await this.assetPipeline.registry.load(assetManifest.clientPreview.scene)
    if (preview) this.integrateClientPreview(preview.root)
    else this.ui.showPreviewFallback()
    await this.assetPipeline.loadEssential(this.workshop, products)
    this.ui.updateLoadingProgress({ loaded: 1, total: 1, percent: 100, currentUrl: '' })
    this.ui.hideLoader()
    void this.loadOptionalAssets()
  }
  private integrateClientPreview(imported: THREE.Group): void {
    this.workshop.root.children.forEach((child) => { child.visible = false })
    imported.name = 'PN_Client_Preview_V2'
    imported.traverse((child) => {
      if (!(child instanceof THREE.Mesh)) return
      child.castShadow = true
      child.receiveShadow = true
      const materials = Array.isArray(child.material) ? child.material : [child.material]
      materials.forEach((material) => this.applyPreviewMaterial(material))
    })
    this.workshop.root.add(imported)
    // Blender empties are loaded as Object3D nodes, not necessarily THREE.Group.
    // Their transform/child contract is all the interaction system requires.
    const importedProducts = products
      .map((product) => imported.getObjectByName(`PN_Eyewear_${product.id}`))
      .filter((node): node is THREE.Group => node !== undefined)
    if (importedProducts.length !== products.length) {
      imported.visible = false
      this.workshop.root.children.forEach((child) => { if (child !== imported) child.visible = true })
      console.warn('[client-preview-v2] Missing eyewear roots; procedural fallback remains active.')
      return
    }
    this.workshop.eyewear.splice(0, this.workshop.eyewear.length, ...importedProducts)
    importedProducts.forEach((group, index) => {
      tagProductHierarchy(group, products[index].id)
      group.userData.previewPosition = group.position.toArray(); group.userData.previewQuaternion = group.quaternion.toArray(); group.userData.previewScale = group.scale.toArray(); group.userData.baseScale = group.scale.x
    })
    this.workshop.root.userData.clientPreviewImported = true
    this.renderer.toneMappingExposure = 1.1
    this.scene.background = new THREE.Color(0x17130f); this.scene.fog = null
    this.applyResize()
  }

  private applyPreviewMaterial(material: THREE.Material): void {
    if (!(material instanceof THREE.MeshStandardMaterial)) return
    const name = material.name.toLowerCase()
    const set = (color: number, roughness: number, metalness = 0): void => {
      material.color.setHex(color)
      material.roughness = roughness
      material.metalness = metalness
      material.needsUpdate = true
    }
    if (name.includes('plaster')) set(0x827665, 0.92)
    else if (name.includes('window_reveal')) set(0xb5aa98, 0.86)
    else if (name.includes('walnut') || name.includes('darkwood')) set(name.includes('dark') ? 0x35170d : 0x5a2813, 0.68)
    else if (name.includes('aged_brass') || name.includes('agedbrass') || name.includes('hingemetal')) set(0x8b6127, 0.42, 0.72)
    else if (name.includes('blackened') || name.includes('fixture_black')) set(0x151511, 0.58, 0.55)
    else if (name.includes('machinegreen')) set(0x173b2c, 0.56, 0.18)
    else if (name.includes('machinesteel')) set(0x434842, 0.48, 0.72)
    else if (name.includes('rubber')) set(0x11120f, 0.9)
    else if (name.includes('acetate') || name.includes('tortoise')) set(name.includes('amber') ? 0x6b3214 : 0x17100d, 0.3)
    else if (name.includes('grille')) set(0xc9c1ae, 0.72, 0.18)
    else if (name.includes('exterior_turquoise')) set(0x518f89, 0.88)
    else if (name.includes('exterior_coral')) set(0xa75e4f, 0.88)
    else if (name.includes('exterior_cream') || name.includes('exterior_trim')) set(0xb5a78d, 0.9)
    else if (name.includes('exterior_window_dark')) set(0x26322f, 0.84)
    else if (name.includes('foliage')) set(name.includes('light') ? 0x52774a : 0x2d593b, 0.9)
  }
  private async loadOptionalAssets(): Promise<void> {
    await this.assetPipeline.loadOptional(this.workshop)
    const lizard = this.assetPipeline.registry.get(assetManifest.lizard.model.id)
    if (lizard) this.livingWorkshop.useImportedLizard(lizard.root, lizard.animations)
  }
}
