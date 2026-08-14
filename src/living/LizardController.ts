import * as THREE from 'three'

const route = [
  new THREE.Vector3(-1.62, 1.18, -3.94),
  new THREE.Vector3(-0.82, 1.18, -3.94),
  new THREE.Vector3(-0.82, 2.2, -3.94),
  new THREE.Vector3(0, 2.78, -3.94),
  new THREE.Vector3(0.82, 2.2, -3.94),
  new THREE.Vector3(0.82, 1.18, -3.94),
  new THREE.Vector3(1.62, 1.18, -3.94),
]

export class LizardController {
  readonly object = new THREE.Group()
  private readonly head: THREE.Mesh
  private readonly direction = new THREE.Vector3()
  private segment = 0
  private progress = 0
  private routeDirection = 1
  private pauseRemaining = 1.8
  private readonly reducedMotion: boolean

  constructor(reducedMotion: boolean) {
    this.reducedMotion = reducedMotion
    this.object.name = 'grille-lagartijo'
    const skin = new THREE.MeshStandardMaterial({ color: 0x69765a, roughness: 0.82 })
    const underside = new THREE.MeshStandardMaterial({ color: 0x939172, roughness: 0.88 })
    const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.075, 0.32, 4, 8), skin)
    body.rotation.z = Math.PI / 2
    this.head = new THREE.Mesh(new THREE.ConeGeometry(0.105, 0.2, 7), skin)
    this.head.rotation.z = -Math.PI / 2
    this.head.position.x = 0.27
    const tailCurve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(-0.22, 0, 0), new THREE.Vector3(-0.48, 0.025, 0),
      new THREE.Vector3(-0.75, -0.035, 0), new THREE.Vector3(-0.98, 0.04, 0),
    ])
    const tail = new THREE.Mesh(new THREE.TubeGeometry(tailCurve, 12, 0.035, 5, false), skin)
    this.object.add(body, this.head, tail)
    const legGeometry = new THREE.CylinderGeometry(0.018, 0.012, 0.24, 5)
    ;[-0.16, 0.14].forEach((x) => {
      ;[-1, 1].forEach((side) => {
        const leg = new THREE.Mesh(legGeometry, underside)
        leg.position.set(x, side * 0.13, 0)
        leg.rotation.z = side * 0.88
        this.object.add(leg)
      })
    })
    this.object.scale.setScalar(0.72)
    this.object.position.copy(route[0])
    this.object.traverse((child) => { child.raycast = () => undefined })
  }

  update(delta: number, elapsed: number): void {
    if (this.reducedMotion) return
    if (this.pauseRemaining > 0) {
      this.pauseRemaining -= delta
      this.head.rotation.y = Math.sin(elapsed * 0.7) * 0.12
      return
    }

    const nextSegment = this.segment + this.routeDirection
    const targetIndex = THREE.MathUtils.clamp(nextSegment, 0, route.length - 1)
    const start = route[this.segment]
    const end = route[targetIndex]
    if (!start || !end) return
    this.progress = Math.min(1, this.progress + delta * 0.095)
    this.object.position.lerpVectors(start, end, THREE.MathUtils.smoothstep(this.progress, 0, 1))
    this.direction.subVectors(end, start)
    this.object.rotation.z = Math.atan2(this.direction.y, this.direction.x)
    this.head.rotation.y = Math.sin(elapsed * 2.1) * 0.035

    if (this.progress >= 1) {
      this.segment = targetIndex
      this.progress = 0
      const endpoint = this.segment === 0 || this.segment === route.length - 1
      if (endpoint) this.routeDirection *= -1
      this.pauseRemaining = 1.2 + ((this.segment * 1.73) % 2.8)
    }
  }
}

