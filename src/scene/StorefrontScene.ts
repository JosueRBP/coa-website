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

export class StorefrontScene {
  private readonly scene = new THREE.Scene(); private readonly camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100)
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
    this.scene.add(new THREE.HemisphereLight(0xe9f0ec, 0x665f56, 1.35))
    const windowFill = new THREE.RectAreaLight(0xfff8e8, 18, 4.7, 5.7)
    windowFill.position.set(0, 1.25, -3.95)
    windowFill.lookAt(0, -0.7, 2.5)
    this.scene.add(windowFill)
    const daylight = new THREE.DirectionalLight(0xfff6df, 3.75)
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
    const roomFill = new THREE.PointLight(0xfff3dc, 3.4, 16, 2)
    roomFill.position.set(-4.8, 3.8, 3.2)
    this.scene.add(roomFill)
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
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75)); this.renderer.setSize(width, height, false)
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
    await this.assetPipeline.loadEssential(this.workshop, products)
    this.ui.updateLoadingProgress({ loaded: 1, total: 1, percent: 100, currentUrl: '' })
    this.ui.hideLoader()
    void this.loadOptionalAssets()
  }
  private async loadOptionalAssets(): Promise<void> {
    await this.assetPipeline.loadOptional(this.workshop)
    const lizard = this.assetPipeline.registry.get(assetManifest.lizard.model.id)
    if (lizard) this.livingWorkshop.useImportedLizard(lizard.root, lizard.animations)
  }
}
