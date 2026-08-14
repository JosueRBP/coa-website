import * as THREE from 'three'

export class DustController {
  readonly object: THREE.Points
  private readonly positions: Float32Array
  private readonly reducedMotion: boolean

  constructor(reducedMotion: boolean) {
    this.reducedMotion = reducedMotion
    const count = 72
    this.positions = new Float32Array(count * 3)
    for (let index = 0; index < count; index += 1) {
      const offset = index * 3
      this.positions[offset] = ((index * 2.37) % 7) - 3.5
      this.positions[offset + 1] = ((index * 1.61) % 6) - 2.2
      this.positions[offset + 2] = ((index * 3.11) % 5) - 3.1
    }
    const geometry = new THREE.BufferGeometry()
    geometry.setAttribute('position', new THREE.BufferAttribute(this.positions, 3))
    const material = new THREE.PointsMaterial({ color: 0xf3eee0, size: 0.035, transparent: true, opacity: 0.16, depthWrite: false, sizeAttenuation: true })
    this.object = new THREE.Points(geometry, material)
    this.object.name = 'window-dust'
    this.object.raycast = () => undefined
  }

  setViewport(width: number): void {
    this.object.geometry.setDrawRange(0, width < 680 ? 34 : width < 1100 ? 52 : 72)
  }

  update(delta: number, elapsed: number): void {
    if (this.reducedMotion) return
    for (let index = 0; index < this.positions.length; index += 3) {
      this.positions[index + 1] += delta * (0.018 + ((index / 3) % 5) * 0.003)
      this.positions[index] += Math.sin(elapsed * 0.12 + index) * delta * 0.002
      if (this.positions[index + 1] > 4) this.positions[index + 1] = -2.3
    }
    const attribute = this.object.geometry.getAttribute('position')
    attribute.needsUpdate = true
  }
}

