import * as THREE from 'three'
import { ParallaxController } from '../interactions/ParallaxController'
import { ProductInteraction } from '../interactions/ProductInteraction'
import { StorefrontUI } from '../ui/StorefrontUI'
import { createWorkshop } from './createWorkshop'
import { ResponsiveSceneController } from './ResponsiveSceneController'

export class StorefrontScene {
  private readonly scene = new THREE.Scene(); private readonly camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100)
  private readonly renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' }); private readonly parallax: ParallaxController; private readonly ui = new StorefrontUI()
  private readonly responsiveLayout: ResponsiveSceneController
  private readonly productInteraction: ProductInteraction
  private readonly container: HTMLElement
  private resizeFrame: number | null = null
  constructor(container: HTMLElement) {
    this.container = container
    this.scene.background = new THREE.Color(0xb8c4c1); this.scene.fog = new THREE.Fog(0xb8c4c1, 18, 34); this.camera.position.set(0, 0.25, 10.6)
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75)); this.renderer.shadowMap.enabled = true; this.renderer.shadowMap.type = THREE.PCFSoftShadowMap
    this.renderer.outputColorSpace = THREE.SRGBColorSpace; this.renderer.toneMapping = THREE.ACESFilmicToneMapping; this.renderer.toneMappingExposure = 1.1; this.container.appendChild(this.renderer.domElement)
    const workshop = createWorkshop(); this.scene.add(workshop.root); this.addLighting(); this.parallax = new ParallaxController(this.container); this.responsiveLayout = new ResponsiveSceneController(this.camera, workshop, this.parallax)
    this.productInteraction = new ProductInteraction(this.container, this.camera, workshop.eyewear, (id) => this.ui.setFocusedProduct(id))
    window.addEventListener('resize', this.scheduleResize, { passive: true })
    this.applyResize()
  }
  private addLighting(): void {
    this.scene.add(new THREE.HemisphereLight(0xe5ebdf, 0x777267, 2.15))
    const daylight = new THREE.DirectionalLight(0xe1ece8, 3.4)
    daylight.position.set(0, 6.5, -1.5)
    daylight.target.position.set(0, -1, 1.5)
    daylight.castShadow = true
    daylight.shadow.mapSize.set(1024, 1024)
    daylight.shadow.camera.left = -8; daylight.shadow.camera.right = 8; daylight.shadow.camera.top = 7; daylight.shadow.camera.bottom = -5
    this.scene.add(daylight, daylight.target)
    const roomFill = new THREE.PointLight(0xfff4dc, 9, 18, 1.8)
    roomFill.position.set(-4.5, 4.5, 3.5)
    this.scene.add(roomFill)
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
    this.productInteraction.cancelTransformAnimations()
    this.responsiveLayout.apply(width)
  }
  private animate = (): void => { requestAnimationFrame(this.animate); this.parallax.update(this.camera); this.renderer.render(this.scene, this.camera) }
  start(): void { this.animate(); requestAnimationFrame(() => this.ui.hideLoader()) }
}
