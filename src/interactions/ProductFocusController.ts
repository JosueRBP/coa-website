import gsap from 'gsap'
import * as THREE from 'three'
import { getProduct, products, type Product } from '../products/catalog'
import type { StorefrontUI } from '../ui/StorefrontUI'
import type { ParallaxController } from './ParallaxController'
import type { ProductInteraction } from './ProductInteraction'
import type { MobileWorkshopPan } from './MobileWorkshopPan'
import type { CommerceAction } from '../commerce/types'

type FocusState = 'explore' | 'entering-focus' | 'focus' | 'switching-product' | 'exiting-focus'

interface FocusPose {
  camera: readonly [number, number, number]
  target: readonly [number, number, number]
  product: readonly [number, number, number]
  scale: number
}

const focusPoses: Record<string, FocusPose> = Object.fromEntries(products.map((product, index) => [product.id, {
  camera: [0, 0.15, 8.4], target: [-1.35, 0.05, 2.1], product: [-1.35, 0.05, 2.1], scale: 1.45 + (index % 2) * 0.04,
}]))

export class ProductFocusController {
  private state: FocusState = 'explore'
  private selected: THREE.Group | null = null
  private selectedProduct: Product | null = null
  private lastPointerDown = new THREE.Vector2()
  private dragging = false
  private rotationX = -0.08
  private rotationY = 0
  private commercePending = false
  private readonly reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  private readonly target = new THREE.Vector3()
  private readonly camera: THREE.PerspectiveCamera
  private readonly element: HTMLElement
  private readonly productGroups: THREE.Group[]
  private readonly parallax: ParallaxController
  private readonly interaction: ProductInteraction
  private readonly ui: StorefrontUI
  private readonly restoreResponsiveLayout: () => void
  private readonly dragZone: HTMLElement | null
  private readonly mobilePan: MobileWorkshopPan

  constructor(camera: THREE.PerspectiveCamera, element: HTMLElement, productGroups: THREE.Group[], parallax: ParallaxController, interaction: ProductInteraction, mobilePan: MobileWorkshopPan, ui: StorefrontUI, restoreResponsiveLayout: () => void) {
    this.camera = camera; this.element = element; this.productGroups = productGroups; this.parallax = parallax; this.interaction = interaction; this.mobilePan = mobilePan; this.ui = ui; this.restoreResponsiveLayout = restoreResponsiveLayout
    this.dragZone = document.querySelector<HTMLElement>('[data-focus-drag-zone]')
    this.element.tabIndex = -1
    ui.bindFocusControls({ close: this.close, previous: () => this.navigate(-1), next: () => this.navigate(1), reserve: () => this.purchase('reserve'), acquire: () => this.purchase('acquire') })
    window.addEventListener('keydown', this.onKeyDown)
    this.dragZone?.addEventListener('pointerdown', this.onDragStart)
    window.addEventListener('pointermove', this.onDragMove, { passive: false })
    window.addEventListener('pointerup', this.onDragEnd)
  }

  get isFocused(): boolean { return this.state !== 'explore' }

  open = (group: THREE.Group): void => {
    if (this.state !== 'explore') return
    const product = getProduct(group.userData.productId as string)
    if (!product) return
    this.state = 'entering-focus'; this.selected = group; this.selectedProduct = product
    this.interaction.setEnabled(false); this.mobilePan.setEnabled(false); this.interaction.cancelTransformAnimations(); this.parallax.setEnabled(false)
    this.ui.renderProduct(product); this.ui.showFocus(); this.applyFocusPose(group, product, true)
  }

  reapplyAfterResize(): void {
    if (!this.selected || !this.selectedProduct) return
    gsap.killTweensOf([this.camera.position, this.selected.position, this.selected.rotation, this.selected.scale, this.target])
    this.applyFocusPose(this.selected, this.selectedProduct, false)
  }

  private applyFocusPose(group: THREE.Group, product: Product, animate: boolean): void {
    const basePose = focusPoses[product.id]
    if (!basePose) return
    const mobile = this.element.clientWidth < 680
    const pose: FocusPose = mobile
      ? { camera: [0, 0.25, 9.3], target: [0, 1.2, 2.1], product: [0, 2.62, 2.1], scale: 1.34 }
      : basePose
    const duration = !animate || this.reducedMotion ? 0 : 0.9
    this.rotationX = -0.08; this.rotationY = 0
    gsap.killTweensOf([this.camera.position, group.position, group.rotation, group.scale, this.target])
    this.target.set(...pose.target)
    gsap.to(this.camera.position, { x: pose.camera[0], y: pose.camera[1], z: pose.camera[2], duration, ease: 'power3.inOut', overwrite: true, onUpdate: () => this.camera.lookAt(this.target) })
    gsap.to(group.position, { x: pose.product[0], y: pose.product[1], z: pose.product[2], duration, ease: 'power3.inOut', overwrite: true })
    gsap.to(group.rotation, { x: this.rotationX, y: 0, z: 0, duration, overwrite: true })
    gsap.to(group.scale, { x: pose.scale, y: pose.scale, z: pose.scale, duration, ease: 'power3.inOut', overwrite: true, onComplete: () => { this.state = 'focus' } })
  }

  private navigate(direction: number): void {
    if (this.state !== 'focus' || !this.selectedProduct || this.commercePending) return
    const currentIndex = products.findIndex((product) => product.id === this.selectedProduct?.id)
    const nextIndex = (currentIndex + direction + products.length) % products.length
    const product = products[nextIndex]
    const group = this.productGroups[nextIndex]
    if (!product || !group) return
    this.state = 'switching-product'
    const focusCamera = this.camera.position.clone()
    this.restoreResponsiveLayout()
    this.camera.position.copy(focusCamera)
    this.selected = group; this.selectedProduct = product; this.ui.renderProduct(product)
    this.applyFocusPose(group, product, true)
  }

  private close = (): void => {
    if (this.state === 'explore' || this.state === 'exiting-focus' || this.commercePending || !this.selected) return
    this.state = 'exiting-focus'; this.dragging = false
    gsap.killTweensOf([this.camera.position, this.target])
    const focusCamera = this.camera.position.clone()
    this.restoreResponsiveLayout()
    const workshopCamera = this.camera.position.clone()
    this.camera.position.copy(focusCamera)
    const duration = this.reducedMotion ? 0 : 0.75
    gsap.to(this.camera.position, { x: workshopCamera.x, y: workshopCamera.y, z: workshopCamera.z, duration, ease: 'power3.inOut', overwrite: true, onComplete: () => {
      this.restoreResponsiveLayout(); this.parallax.setEnabled(true); this.mobilePan.setEnabled(true); this.interaction.setEnabled(true); this.ui.hideFocus(); this.selected = null; this.selectedProduct = null; this.state = 'explore'; this.element.focus({ preventScroll: true })
    } })
  }

  private purchase(action: CommerceAction): void {
    if (this.state !== 'focus' || !this.selectedProduct || this.commercePending) return
    this.ui.showPurchaseMessage(action)
  }
  private onKeyDown = (event: KeyboardEvent): void => { if (event.key === 'Escape') this.close(); else if (event.key === 'ArrowLeft') this.navigate(-1); else if (event.key === 'ArrowRight') this.navigate(1) }
  private onDragStart = (event: PointerEvent): void => { if (this.state !== 'focus' || !this.selected || !this.dragZone) return; this.dragging = true; this.lastPointerDown.set(event.clientX, event.clientY); this.dragZone.setPointerCapture(event.pointerId); this.dragZone.style.cursor = 'grabbing' }
  private onDragMove = (event: PointerEvent): void => {
    if (!this.dragging || !this.selected || this.state !== 'focus') return
    event.preventDefault(); const deltaX = event.clientX - this.lastPointerDown.x; const deltaY = event.clientY - this.lastPointerDown.y; this.lastPointerDown.set(event.clientX, event.clientY)
    this.rotationY = THREE.MathUtils.clamp(this.rotationY + deltaX * 0.006, -0.7, 0.7); this.rotationX = THREE.MathUtils.clamp(this.rotationX + deltaY * 0.003, -0.28, 0.18)
    this.selected.rotation.set(this.rotationX, this.rotationY, 0)
  }
  private onDragEnd = (): void => { if (!this.dragging) return; this.dragging = false; if (this.dragZone) this.dragZone.style.cursor = 'grab' }
}
