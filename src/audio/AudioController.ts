export interface AmbientTrack {
  id: string
  src: string
  volume: number
  loop?: boolean
}

interface LoadedTrack {
  audio: HTMLAudioElement
  targetVolume: number
}

export class AudioController {
  private enabled = false
  private masterVolume = 0.55
  private readonly button: HTMLButtonElement
  private readonly tracks: LoadedTrack[] = []

  constructor(button: HTMLButtonElement, tracks: AmbientTrack[] = []) {
    this.button = button
    tracks.forEach((track) => this.addTrack(track))
    button.addEventListener('click', this.toggle)
  }

  addTrack(track: AmbientTrack): void {
    const audio = new Audio()
    audio.preload = 'none'
    audio.loop = track.loop ?? true
    audio.volume = 0
    audio.addEventListener('error', () => { audio.pause() }, { once: true })
    audio.src = track.src
    this.tracks.push({ audio, targetVolume: THREEClamp(track.volume) })
  }

  setVolume(volume: number): void {
    this.masterVolume = THREEClamp(volume)
    if (this.enabled) this.fadeTo(this.masterVolume, 650)
  }

  mute(): void { if (this.enabled) this.toggle() }

  private toggle = (): void => {
    this.enabled = !this.enabled
    this.button.setAttribute('aria-pressed', String(this.enabled))
    this.button.setAttribute('aria-label', this.enabled ? 'Desactivar sonido ambiental' : 'Activar sonido ambiental')
    const label = this.button.querySelector<HTMLElement>('[data-audio-label]')
    if (label) label.textContent = this.enabled ? 'Sonido on' : 'Sonido off'
    if (this.enabled) {
      this.tracks.forEach(({ audio }) => { void audio.play().catch(() => undefined) })
      this.fadeTo(this.masterVolume, 900)
    } else {
      this.fadeTo(0, 650, true)
    }
  }

  private fadeTo(masterTarget: number, duration: number, pauseAfter = false): void {
    const startedAt = performance.now()
    const starts = this.tracks.map(({ audio }) => audio.volume)
    const step = (now: number): void => {
      const progress = Math.min(1, (now - startedAt) / duration)
      this.tracks.forEach((track, index) => {
        const destination = track.targetVolume * masterTarget
        track.audio.volume = starts[index]! + (destination - starts[index]!) * progress
      })
      if (progress < 1) requestAnimationFrame(step)
      else if (pauseAfter) this.tracks.forEach(({ audio }) => audio.pause())
    }
    requestAnimationFrame(step)
  }
}

function THREEClamp(value: number): number {
  return Math.min(1, Math.max(0, value))
}
