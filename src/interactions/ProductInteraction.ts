import gsap from 'gsap'
import * as THREE from 'three'

export class ProductInteraction {
  private readonly raycaster = new THREE.Raycaster(); private readonly pointer = new THREE.Vector2(2, 2)
  private hovered: THREE.Group | null = null; private focused: THREE.Group | null = null
  private readonly element: HTMLElement
  private readonly camera: THREE.PerspectiveCamera
  private readonly products: THREE.Group[]
  private readonly onFocusChange: (productId: string | null) => void
  constructor(element: HTMLElement, camera: THREE.PerspectiveCamera, products: THREE.Group[], onFocusChange: (productId: string | null) => void) {
    this.element = element; this.camera = camera; this.products = products; this.onFocusChange = onFocusChange
    element.addEventListener('pointermove', this.onPointerMove, { passive: true }); element.addEventListener('pointerdown', this.onPointerDown); window.addEventListener('keydown', this.onKeyDown)
  }
  private setPointer(event: PointerEvent): void { const rect = this.element.getBoundingClientRect(); this.pointer.set(((event.clientX - rect.left) / rect.width) * 2 - 1, -((event.clientY - rect.top) / rect.height) * 2 + 1) }
  private intersect(): THREE.Group | null {
    this.raycaster.setFromCamera(this.pointer, this.camera); const hit = this.raycaster.intersectObjects(this.products, true)[0]
    return hit ? this.products.find((product) => product.userData.productId === hit.object.userData.productId) ?? null : null
  }
  private baseScale(product: THREE.Group): number { return (product.userData.baseScale as number | undefined) ?? 0.9 }
  cancelTransformAnimations(): void {
    this.products.forEach((product) => gsap.killTweensOf([product.position, product.rotation, product.scale]))
  }
  private onPointerMove = (event: PointerEvent): void => {
    this.setPointer(event); const next = this.intersect(); if (next === this.hovered || this.focused) return
    if (this.hovered) { const scale = this.baseScale(this.hovered); gsap.to(this.hovered.scale, { x: scale, y: scale, z: scale, duration: 0.35, ease: 'power2.out' }) }
    this.hovered = next; this.element.style.cursor = next ? 'pointer' : 'default'
    if (next) { const scale = this.baseScale(next) * 1.067; gsap.to(next.scale, { x: scale, y: scale, z: scale, duration: 0.35, ease: 'power2.out' }) }
  }
  private onPointerDown = (event: PointerEvent): void => { this.setPointer(event); const selected = this.intersect(); if (selected) this.enterFocus(selected); else if (this.focused) this.exitFocus() }
  private onKeyDown = (event: KeyboardEvent): void => { if (event.key === 'Escape') this.exitFocus() }
  private enterFocus(product: THREE.Group): void {
    if (this.focused && this.focused !== product) { const scale = this.baseScale(this.focused); gsap.to(this.focused.scale, { x: scale, y: scale, z: scale, duration: 0.4 }) }
    this.focused = product; const scale = this.baseScale(product) * 1.2; gsap.to(product.scale, { x: scale, y: scale, z: scale, duration: 0.55, ease: 'power3.out' }); this.onFocusChange(product.userData.productId as string)
  }
  private exitFocus(): void { if (!this.focused) return; const scale = this.baseScale(this.focused); gsap.to(this.focused.scale, { x: scale, y: scale, z: scale, duration: 0.45, ease: 'power2.out' }); this.focused = null; this.onFocusChange(null) }
}
