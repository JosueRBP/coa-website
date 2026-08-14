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
  private masterVolume = 1
  private readonly button: HTMLButtonElement
  private readonly tracks: LoadedTrack[] = []

  constructor(button: HTMLButtonElement, tracks: AmbientTrack[] = []) {
    this.button = button
    tracks.forEach((track) => this.addTrack(track))
    button.addEventListener('click', this.toggle)
    window.addEventListener('pointerdown', this.startOnFirstInteraction, { capture: true, once: true })
    window.addEventListener('keydown', this.startOnFirstInteraction, { capture: true, once: true })
  }

  addTrack(track: AmbientTrack): void {
    const audio = new Audio()
    audio.preload = 'metadata'
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

  private startOnFirstInteraction = (event: Event): void => {
    if ((event.target as Element | null)?.closest?.('[data-audio-toggle]')) return
    this.enable()
  }

  private toggle = (): void => {
    if (this.enabled) this.disable()
    else this.enable()
  }

  private enable(): void {
    if (this.enabled) return
    this.enabled = true
    this.syncButton()
    this.tracks.forEach(({ audio }) => { void audio.play().catch(() => this.disable()) })
    this.fadeTo(this.masterVolume, 1100)
  }

  private disable(): void {
    if (!this.enabled) return
    this.enabled = false
    this.syncButton()
    this.fadeTo(0, 650, true)
  }

  private syncButton(): void {
    this.button.setAttribute('aria-pressed', String(this.enabled))
    this.button.setAttribute('aria-label', this.enabled ? 'Desactivar sonido ambiental' : 'Activar sonido ambiental')
    const label = this.button.querySelector<HTMLElement>('[data-audio-label]')
    if (label) label.textContent = this.enabled ? 'Sonido on' : 'Sonido off'
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
