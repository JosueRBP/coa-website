export class AudioController {
  private enabled = false
  private readonly button: HTMLButtonElement
  constructor(button: HTMLButtonElement) { this.button = button; button.addEventListener('click', this.toggle) }
  private toggle = (): void => {
    this.enabled = !this.enabled; this.button.setAttribute('aria-pressed', String(this.enabled)); this.button.setAttribute('aria-label', this.enabled ? 'Disable ambient audio' : 'Enable ambient audio')
    const label = this.button.querySelector<HTMLElement>('[data-audio-label]'); if (label) label.textContent = this.enabled ? 'Sound on' : 'Sound off'
  }
}
