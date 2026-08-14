import * as THREE from 'three'
import { DustController } from './DustController'
import { LizardController } from './LizardController'
import { workshopMaterials } from '../scene/workshopMaterials'

export class LivingWorkshop {
  readonly root = new THREE.Group()
  private readonly lizard: LizardController
  private readonly dust: DustController
  private readonly hangingTools: THREE.Group[] = []
  private readonly reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  private readonly baseDaylight: number
  private readonly daylight: THREE.DirectionalLight

  constructor(daylight: THREE.DirectionalLight) {
    this.daylight = daylight
    this.root.name = 'living-workshop'
    this.baseDaylight = daylight.intensity
    this.lizard = new LizardController(this.reducedMotion)
    this.dust = new DustController(this.reducedMotion)
    this.root.add(this.lizard.object, this.dust.object)

    ;[-5.1, 4.85].forEach((x, index) => {
      const hanging = new THREE.Group()
      const cord = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.7, 5), workshopMaterials.agedMetal)
      cord.position.y = -0.35
      const tool = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.58, 0.055), workshopMaterials.machineMetal)
      tool.position.y = -0.92
      hanging.position.set(x, 3.45 - index * 0.35, -3.92)
      hanging.add(cord, tool)
      hanging.traverse((child) => { child.raycast = () => undefined })
      this.hangingTools.push(hanging)
      this.root.add(hanging)
    })
  }

  setViewport(width: number): void {
    this.dust.setViewport(width)
  }

  update(delta: number, elapsed: number): void {
    this.lizard.update(delta, elapsed)
    this.dust.update(delta, elapsed)
    if (this.reducedMotion) return
    this.daylight.intensity = this.baseDaylight * (1 + Math.sin(elapsed * 0.075) * 0.018 + Math.sin(elapsed * 0.031) * 0.008)
    this.daylight.position.x = -1.5 + Math.sin(elapsed * 0.045) * 0.12
    this.hangingTools[0]!.rotation.z = Math.sin(elapsed * 0.31) * 0.012
    this.hangingTools[1]!.rotation.z = Math.sin(elapsed * 0.24 + 1.7) * 0.009
  }
}
