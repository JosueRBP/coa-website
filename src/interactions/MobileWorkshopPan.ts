import * as THREE from 'three'
import type { ParallaxController } from './ParallaxController'

const PAN_MIN = -3.35
const PAN_CENTER = 0
const PAN_MAX = 3.35
const DRAG_THRESHOLD = 7

export class MobileWorkshopPan {
  private readonly raycaster = new THREE.Raycaster()
  private readonly pointer = new THREE.Vector2()
  private readonly start = new THREE.Vector2()
  private currentPan = PAN_CENTER
  private startPan = PAN_CENTER
  private active = false
  private enabled = true
  private isMobile = false
  private meaningfulDrag = false
  private readonly reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  private readonly element: HTMLElement
  private readonly camera: THREE.PerspectiveCamera
  private readonly products: THREE.Group[]
  private readonly parallax: ParallaxController

  constructor(
    element: HTMLElement,
    camera: THREE.PerspectiveCamera,
    products: THREE.Group[],
    parallax: ParallaxController,
  ) {
    this.element = element; this.camera = camera; this.products = products; this.parallax = parallax
    element.addEventListener('pointerdown', this.onPointerDown)
    window.addEventListener('pointermove', this.onPointerMove, { passive: false })
    window.addEventListener('pointerup', this.onPointerUp)
  }

  setViewport(width: number): void {
    this.isMobile = width < 680
    this.parallax.setHorizontalPan(this.isMobile ? this.currentPan : PAN_CENTER)
  }

  setEnabled(enabled: boolean): void { this.enabled = enabled; if (!enabled) this.active = false }

  private isProductAt(event: PointerEvent): boolean {
    const rect = this.element.getBoundingClientRect()
    this.pointer.set(((event.clientX - rect.left) / rect.width) * 2 - 1, -((event.clientY - rect.top) / rect.height) * 2 + 1)
    this.raycaster.setFromCamera(this.pointer, this.camera)
    return this.raycaster.intersectObjects(this.products, true).length > 0
  }

  private onPointerDown = (event: PointerEvent): void => {
    if (!this.enabled || !this.isMobile || this.isProductAt(event)) return
    this.active = true; this.meaningfulDrag = false; this.start.set(event.clientX, event.clientY); this.startPan = this.currentPan
    this.element.setPointerCapture(event.pointerId)
  }

  private onPointerMove = (event: PointerEvent): void => {
    if (!this.active) return
    const deltaX = event.clientX - this.start.x
    if (Math.abs(deltaX) > DRAG_THRESHOLD) { this.meaningfulDrag = true; event.preventDefault() }
    const viewportScale = Math.max(300, this.element.clientWidth)
    this.currentPan = THREE.MathUtils.clamp(this.startPan - (deltaX / viewportScale) * 5.5, PAN_MIN, PAN_MAX)
    this.parallax.setHorizontalPan(this.currentPan)
    if (this.meaningfulDrag) document.querySelector('[data-mobile-pan-hint]')?.classList.add('is-dismissed')
  }

  private onPointerUp = (): void => {
    if (!this.active) return
    this.active = false
    if (this.reducedMotion) this.parallax.setHorizontalPan(this.currentPan)
  }
}
