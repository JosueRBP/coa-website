import gsap from 'gsap'
import * as THREE from 'three'

export class ProductInteraction {
  private readonly raycaster = new THREE.Raycaster()
  private readonly pointer = new THREE.Vector2(2, 2)
  private hovered: THREE.Group | null = null
  private pressedProduct: THREE.Group | null = null
  private readonly pressPosition = new THREE.Vector2()
  private enabled = true
  private readonly element: HTMLElement
  private readonly camera: THREE.PerspectiveCamera
  private readonly products: THREE.Group[]
  private readonly onSelect: (product: THREE.Group) => void

  constructor(element: HTMLElement, camera: THREE.PerspectiveCamera, products: THREE.Group[], onSelect: (product: THREE.Group) => void) {
    this.element = element; this.camera = camera; this.products = products; this.onSelect = onSelect
    element.addEventListener('pointermove', this.onPointerMove, { passive: true })
    element.addEventListener('pointerdown', this.onPointerDown)
    window.addEventListener('pointerup', this.onPointerUp)
  }
  setEnabled(enabled: boolean): void { this.enabled = enabled; if (!enabled) this.element.style.cursor = 'default' }
  private setPointer(event: PointerEvent): void { const rect = this.element.getBoundingClientRect(); this.pointer.set(((event.clientX - rect.left) / rect.width) * 2 - 1, -((event.clientY - rect.top) / rect.height) * 2 + 1) }
  private intersect(): THREE.Group | null { this.raycaster.setFromCamera(this.pointer, this.camera); const hit = this.raycaster.intersectObjects(this.products, true)[0]; return hit ? this.products.find((product) => product.userData.productId === hit.object.userData.productId) ?? null : null }
  private baseScale(product: THREE.Group): number { return (product.userData.baseScale as number | undefined) ?? 0.9 }
  cancelTransformAnimations(): void { this.products.forEach((product) => gsap.killTweensOf([product.position, product.rotation, product.scale])) }
  private onPointerMove = (event: PointerEvent): void => {
    if (!this.enabled) return
    this.setPointer(event); const next = this.intersect(); if (next === this.hovered) return
    if (this.hovered) { const scale = this.baseScale(this.hovered); gsap.to(this.hovered.scale, { x: scale, y: scale, z: scale, duration: 0.35, overwrite: true }) }
    this.hovered = next; this.element.style.cursor = next ? 'pointer' : 'default'
    if (next) { const scale = this.baseScale(next) * 1.067; gsap.to(next.scale, { x: scale, y: scale, z: scale, duration: 0.35, overwrite: true }) }
  }
  private onPointerDown = (event: PointerEvent): void => {
    if (!this.enabled) return
    this.setPointer(event); this.pressedProduct = this.intersect(); this.pressPosition.set(event.clientX, event.clientY)
  }
  private onPointerUp = (event: PointerEvent): void => {
    if (!this.enabled || !this.pressedProduct) { this.pressedProduct = null; return }
    const distance = this.pressPosition.distanceTo(new THREE.Vector2(event.clientX, event.clientY))
    this.setPointer(event); const releasedProduct = this.intersect(); const selected = this.pressedProduct
    this.pressedProduct = null
    if (distance <= 7 && releasedProduct === selected) this.onSelect(selected)
  }
}
