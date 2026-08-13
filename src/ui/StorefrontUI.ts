import gsap from 'gsap'
import { AudioController } from '../audio/AudioController'

export class StorefrontUI {
  private readonly panel = document.querySelector<HTMLElement>('[data-focus-panel]'); private readonly productId = document.querySelector<HTMLElement>('[data-focus-id]')
  constructor() { const audioButton = document.querySelector<HTMLButtonElement>('[data-audio-toggle]'); if (audioButton) new AudioController(audioButton) }
  hideLoader(): void { const loader = document.querySelector<HTMLElement>('[data-loading-screen]'); if (loader) gsap.to(loader, { autoAlpha: 0, duration: 0.8, delay: 0.15, ease: 'power2.inOut', onComplete: () => loader.remove() }) }
  setFocusedProduct(id: string | null): void {
    if (!this.panel || !this.productId) return
    if (id) { this.productId.textContent = id; this.panel.setAttribute('aria-hidden', 'false'); document.body.classList.add('is-focused') }
    else { this.panel.setAttribute('aria-hidden', 'true'); document.body.classList.remove('is-focused') }
  }
}
