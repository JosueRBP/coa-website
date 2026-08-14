import * as THREE from 'three'

export class ParallaxController {
  private target = new THREE.Vector2(); private current = new THREE.Vector2()
  private readonly basePosition = new THREE.Vector3(0, 0.25, 10.6)
  private readonly baseTarget = new THREE.Vector3(0, -0.1, -2.5)
  private strength = 1
  private enabled = true
  private horizontalPan = 0
  private readonly element: HTMLElement
  constructor(element: HTMLElement) {
    this.element = element
    element.addEventListener('pointermove', this.onPointerMove, { passive: true })
    element.addEventListener('pointerleave', this.onPointerLeave, { passive: true })
  }
  private onPointerMove = (event: PointerEvent): void => {
    const rect = this.element.getBoundingClientRect()
    this.target.set(((event.clientX - rect.left) / rect.width - 0.5) * 2, -((event.clientY - rect.top) / rect.height - 0.5) * 2)
  }
  private onPointerLeave = (): void => { this.target.set(0, 0) }
  setBasePose(position: THREE.Vector3, target: THREE.Vector3, strength: number): void {
    this.basePosition.copy(position)
    this.baseTarget.copy(target)
    this.strength = strength
  }
  setEnabled(enabled: boolean): void { this.enabled = enabled; if (!enabled) { this.target.set(0, 0); this.current.set(0, 0) } }
  setHorizontalPan(pan: number): void { this.horizontalPan = pan }
  update(camera: THREE.PerspectiveCamera): void {
    if (!this.enabled) return
    this.current.lerp(this.target, 0.035)
    camera.position.set(
      this.basePosition.x + this.horizontalPan * 0.32 + this.current.x * 0.22 * this.strength,
      this.basePosition.y + this.current.y * 0.14 * this.strength,
      this.basePosition.z,
    )
    camera.lookAt(
      this.baseTarget.x + this.horizontalPan + this.current.x * 0.06 * this.strength,
      this.baseTarget.y + this.current.y * 0.035 * this.strength,
      this.baseTarget.z,
    )
  }
}
