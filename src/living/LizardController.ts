import * as THREE from 'three'
import type { AnimationMixerRegistry } from '../assets/AnimationMixerRegistry'
import { grilleRouteAnchors } from '../scene/productionGrille'

const route = [grilleRouteAnchors['lower-left'], grilleRouteAnchors['center-left'], grilleRouteAnchors['upper-left'], grilleRouteAnchors['upper-center'], grilleRouteAnchors['upper-right'], grilleRouteAnchors['center-right'], grilleRouteAnchors['lower-right']]
type LizardState = 'idle' | 'alert' | 'moving' | 'pause'

export class LizardController {
  readonly object = new THREE.Group()
  private readonly head = new THREE.Group()
  private readonly tail = new THREE.Group()
  private readonly legs: THREE.Mesh[] = []
  private readonly direction = new THREE.Vector3()
  private readonly raycaster = new THREE.Raycaster()
  private readonly pointer = new THREE.Vector2()
  private readonly hitTarget = new THREE.Mesh(new THREE.SphereGeometry(0.42, 8, 6), new THREE.MeshBasicMaterial({ transparent: true, opacity: 0, depthWrite: false }))
  private state: LizardState = 'idle'
  private segment = 0
  private progress = 0
  private routeDirection = 1
  private stepsRemaining = 0
  private stateTime = 0
  private clickCount = 0
  private pointerDown = new THREE.Vector2()
  private readonly reducedMotion: boolean
  private mixer: THREE.AnimationMixer | null = null
  private actions = new Map<string, THREE.AnimationAction>()

  constructor(reducedMotion: boolean) {
    this.reducedMotion = reducedMotion
    this.object.name = 'grille-lagartijo'
    const skin = new THREE.MeshStandardMaterial({ color: 0x596348, roughness: 0.88 })
    const underside = new THREE.MeshStandardMaterial({ color: 0x969273, roughness: 0.92 })
    const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.075, 0.34, 5, 9), skin); body.rotation.z = Math.PI / 2
    const headShape = new THREE.Mesh(new THREE.ConeGeometry(0.1, 0.22, 8), skin); headShape.rotation.z = -Math.PI / 2; headShape.position.x = 0.1; headShape.scale.set(1, .78, .9); this.head.position.x = .22; this.head.add(headShape)
    const eyeMaterial = new THREE.MeshStandardMaterial({ color: 0x10120d, roughness: .35 })
    ;[-1, 1].forEach((side) => { const eye = new THREE.Mesh(new THREE.SphereGeometry(.018, 6, 4), eyeMaterial); eye.position.set(.17, side * .065, .025); this.head.add(eye) })
    const tailCurve = new THREE.CatmullRomCurve3([new THREE.Vector3(0,0,0), new THREE.Vector3(-.27,.02,0), new THREE.Vector3(-.56,-.025,0), new THREE.Vector3(-.83,.035,0), new THREE.Vector3(-1.05,0,0)])
    this.tail.position.x = -.2; this.tail.add(new THREE.Mesh(new THREE.TubeGeometry(tailCurve, 18, .032, 6, false), skin))
    this.object.add(body, this.head, this.tail)
    const legGeometry = new THREE.CylinderGeometry(.016, .011, .23, 6)
    ;[-.15, .14].forEach((x) => [-1, 1].forEach((side) => { const leg = new THREE.Mesh(legGeometry, underside); leg.position.set(x, side * .13, 0); leg.rotation.z = side * .9; this.legs.push(leg); this.object.add(leg) }))
    this.object.scale.setScalar(.72); this.object.position.copy(route[0])
    this.object.traverse((child) => { child.raycast = () => undefined })
    this.hitTarget.name = 'lagartijo-touch-target'; this.hitTarget.position.x = -.18; this.hitTarget.scale.set(1.8, .65, .7); this.object.add(this.hitTarget)
  }

  bindInteraction(element: HTMLElement, camera: THREE.Camera, canInteract: () => boolean): void {
    const setPointer = (event: PointerEvent): void => { const rect = element.getBoundingClientRect(); this.pointer.set(((event.clientX - rect.left) / rect.width) * 2 - 1, -((event.clientY - rect.top) / rect.height) * 2 + 1) }
    element.addEventListener('pointerdown', (event) => { this.pointerDown.set(event.clientX, event.clientY) }, { passive: true })
    element.addEventListener('pointerup', (event) => {
      if (!canInteract() || this.pointerDown.distanceTo(new THREE.Vector2(event.clientX, event.clientY)) > 8) return
      setPointer(event); this.raycaster.setFromCamera(this.pointer, camera)
      if (this.raycaster.intersectObject(this.hitTarget, false).length > 0) this.triggerTraversal()
    })
  }
  private triggerTraversal(): void {
    if (this.state === 'moving' || this.state === 'alert') return
    this.clickCount += 1; this.state = 'alert'; this.stateTime = 0
    this.routeDirection = this.segment >= route.length - 1 ? -1 : this.segment <= 0 ? 1 : this.clickCount % 2 ? 1 : -1
    this.stepsRemaining = 2 + (this.clickCount % 4)
  }
  useImportedModel(root: THREE.Object3D, clips: THREE.AnimationClip[], mixers: AnimationMixerRegistry): void {
    this.object.clear(); root.traverse((child) => { child.raycast = () => undefined }); this.object.add(root, this.hitTarget)
    this.mixer = mixers.register(root); this.actions = new Map(clips.map((clip) => [clip.name.toLowerCase(), this.mixer!.clipAction(clip)]))
    this.actions.get('idle')?.play()
  }
  update(delta: number, elapsed: number): void {
    const motionDelta = this.reducedMotion ? 0 : delta
    this.stateTime += motionDelta
    if (this.state === 'idle') { this.object.scale.y = .72 * (1 + Math.sin(elapsed * 1.2) * .012); this.head.rotation.z = Math.sin(elapsed * .38) * .09; this.tail.rotation.z = Math.sin(elapsed * .45) * .025; return }
    if (this.state === 'alert') { this.head.rotation.z = Math.sin(this.stateTime * 12) * .13; if (this.reducedMotion || this.stateTime > .34) { this.state = 'moving'; this.stateTime = 0; this.actions.get('idle')?.stop(); this.actions.get('walk')?.play() } return }
    if (this.state === 'pause') { if (this.reducedMotion || this.stateTime > .45) { this.state = this.stepsRemaining > 0 ? 'moving' : 'idle'; this.stateTime = 0 } return }
    const targetIndex = THREE.MathUtils.clamp(this.segment + this.routeDirection, 0, route.length - 1)
    const start = route[this.segment]; const end = route[targetIndex]; if (!start || !end) return
    this.progress = this.reducedMotion ? 1 : Math.min(1, this.progress + delta * .62)
    this.object.position.lerpVectors(start, end, THREE.MathUtils.smoothstep(this.progress, 0, 1)); this.direction.subVectors(end, start); this.object.rotation.z = Math.atan2(this.direction.y, this.direction.x)
    this.legs.forEach((leg, index) => { leg.rotation.x = Math.sin(elapsed * 12 + index * Math.PI) * .45; leg.rotation.z = (index % 2 ? 1 : -1) * .9 }); this.object.position.z = start.z + Math.sin(this.progress * Math.PI) * .015
    this.tail.rotation.z = Math.sin(elapsed * 8) * .055
    if (this.progress >= 1) { this.segment = targetIndex; this.progress = 0; this.stepsRemaining -= 1; if (this.segment === 0 || this.segment === route.length - 1) this.routeDirection *= -1; this.state = this.stepsRemaining > 0 ? 'pause' : 'idle'; this.stateTime = 0; if (this.state === 'idle') { this.actions.get('walk')?.stop(); this.actions.get('idle')?.play() } }
  }
}
