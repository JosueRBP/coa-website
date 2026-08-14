import * as THREE from 'three'
import { ParallaxController } from '../interactions/ParallaxController'
import { ProductInteraction } from '../interactions/ProductInteraction'
import { StorefrontUI } from '../ui/StorefrontUI'
import { createWorkshop } from './createWorkshop'
import { ResponsiveSceneController } from './ResponsiveSceneController'
import { LivingWorkshop } from '../living/LivingWorkshop'
import { ProductFocusController } from '../interactions/ProductFocusController'
import { MobileWorkshopPan } from '../interactions/MobileWorkshopPan'

export class StorefrontScene {
  private readonly scene = new THREE.Scene(); private readonly camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100)
  private readonly renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' }); private readonly parallax: ParallaxController; private readonly ui = new StorefrontUI()
  private readonly responsiveLayout: ResponsiveSceneController
  private readonly productInteraction: ProductInteraction
  private readonly focusController: ProductFocusController
  private readonly mobilePan: MobileWorkshopPan
  private readonly livingWorkshop: LivingWorkshop
  private readonly clock = new THREE.Clock()
  private readonly container: HTMLElement
  private resizeFrame: number | null = null
  constructor(container: HTMLElement) {
    this.container = container
    this.scene.background = new THREE.Color(0xc3cfcb); this.scene.fog = new THREE.Fog(0xc3cfcb, 20, 38); this.camera.position.set(0, 0.25, 10.6)
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75)); this.renderer.shadowMap.enabled = true; this.renderer.shadowMap.type = THREE.PCFSoftShadowMap
    this.renderer.outputColorSpace = THREE.SRGBColorSpace; this.renderer.toneMapping = THREE.ACESFilmicToneMapping; this.renderer.toneMappingExposure = 1.05; this.container.appendChild(this.renderer.domElement)
    const workshop = createWorkshop(); this.scene.add(workshop.root); const daylight = this.addLighting(); this.parallax = new ParallaxController(this.container); this.responsiveLayout = new ResponsiveSceneController(this.camera, workshop, this.parallax)
    this.livingWorkshop = new LivingWorkshop(daylight); this.scene.add(this.livingWorkshop.root)
    this.productInteraction = new ProductInteraction(this.container, this.camera, workshop.eyewear, (product) => this.focusController.open(product))
    this.mobilePan = new MobileWorkshopPan(this.container, this.camera, workshop.eyewear, this.parallax)
    this.focusController = new ProductFocusController(this.camera, this.container, workshop.eyewear, this.parallax, this.productInteraction, this.mobilePan, this.ui, this.applyWorkshopLayout)
    window.addEventListener('resize', this.scheduleResize, { passive: true })
    this.applyResize()
  }
  private addLighting(): THREE.DirectionalLight {
    this.scene.add(new THREE.HemisphereLight(0xe9eee7, 0x77756d, 2.3))
    const daylight = new THREE.DirectionalLight(0xe3ece7, 3.05)
    daylight.position.set(-1.5, 7.5, -0.5)
    daylight.target.position.set(0, -1.25, 1.8)
    daylight.castShadow = true
    daylight.shadow.mapSize.set(1024, 1024)
    daylight.shadow.bias = -0.00025
    daylight.shadow.normalBias = 0.035
    daylight.shadow.radius = 3
    daylight.shadow.camera.left = -8; daylight.shadow.camera.right = 8; daylight.shadow.camera.top = 7; daylight.shadow.camera.bottom = -5
    this.scene.add(daylight, daylight.target)
    const roomFill = new THREE.PointLight(0xfff7e6, 7, 18, 1.8)
    roomFill.position.set(-4.5, 4.2, 3.5)
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
  start(): void { this.animate(); requestAnimationFrame(() => this.ui.hideLoader()) }
}
