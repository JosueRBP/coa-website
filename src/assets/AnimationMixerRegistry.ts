import * as THREE from 'three'

export class AnimationMixerRegistry {
  private readonly mixers: THREE.AnimationMixer[] = []
  register(root: THREE.Object3D): THREE.AnimationMixer { const mixer = new THREE.AnimationMixer(root); this.mixers.push(mixer); return mixer }
  unregister(mixer: THREE.AnimationMixer): void { const index = this.mixers.indexOf(mixer); if (index >= 0) this.mixers.splice(index, 1) }
  update(delta: number): void { this.mixers.forEach((mixer) => mixer.update(delta)) }
}
