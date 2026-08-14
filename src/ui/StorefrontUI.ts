import gsap from 'gsap'
import { AudioController } from '../audio/AudioController'
import type { Product } from '../products/catalog'

export interface FocusUIHandlers {
  close: () => void
  previous: () => void
  next: () => void
  reserve: () => void
  acquire: () => void
}

export class StorefrontUI {
  private readonly panel = document.querySelector<HTMLElement>('[data-focus-panel]')
  private readonly closeButton = document.querySelector<HTMLButtonElement>('[data-focus-close]')

  constructor() {
    const audioButton = document.querySelector<HTMLButtonElement>('[data-audio-toggle]')
    if (audioButton) new AudioController(audioButton)
  }

  bindFocusControls(handlers: FocusUIHandlers): void {
    this.closeButton?.addEventListener('click', handlers.close)
    document.querySelector('[data-focus-previous]')?.addEventListener('click', handlers.previous)
    document.querySelector('[data-focus-next]')?.addEventListener('click', handlers.next)
    document.querySelector('[data-focus-reserve]')?.addEventListener('click', handlers.reserve)
    document.querySelector('[data-focus-acquire]')?.addEventListener('click', handlers.acquire)
  }

  hideLoader(): void {
    const loader = document.querySelector<HTMLElement>('[data-loading-screen]')
    if (loader) gsap.to(loader, { autoAlpha: 0, duration: 0.8, delay: 0.15, ease: 'power2.inOut', onComplete: () => loader.remove() })
  }

  renderProduct(product: Product): void {
    const values: Record<string, string> = {
      '[data-focus-count]': `${product.id} / 09`, '[data-focus-name]': product.name,
      '[data-focus-subtitle]': product.subtitle, '[data-focus-price]': `$${product.price.toLocaleString()} USD`,
      '[data-focus-short]': product.shortDescription, '[data-focus-edition]': `Edition ${product.edition}`,
      '[data-focus-material]': product.material, '[data-focus-hinge]': product.hinge,
      '[data-focus-dimensions]': product.dimensions, '[data-focus-made-in]': product.madeIn,
      '[data-focus-lead]': product.leadTime,
    }
    Object.entries(values).forEach(([selector, value]) => { const node = document.querySelector<HTMLElement>(selector); if (node) node.textContent = value })
    const acquire = document.querySelector<HTMLButtonElement>('[data-focus-acquire]'); if (acquire) acquire.textContent = `Acquire — $${product.price.toLocaleString()}`
    const reserve = document.querySelector<HTMLButtonElement>('[data-focus-reserve]'); if (reserve) reserve.textContent = `Reserve — $${product.reservationPrice.toLocaleString()}`
    const status = document.querySelector<HTMLElement>('[data-focus-status]'); if (status) status.textContent = ''
  }

  showFocus(): void {
    if (!this.panel) return
    this.panel.setAttribute('aria-hidden', 'false')
    document.body.classList.add('is-focused')
    this.closeButton?.focus({ preventScroll: true })
  }

  hideFocus(): void {
    this.panel?.setAttribute('aria-hidden', 'true')
    document.body.classList.remove('is-focused')
  }

  showPurchaseMessage(): void {
    const status = document.querySelector<HTMLElement>('[data-focus-status]')
    if (status) status.textContent = 'Checkout integration coming next.'
  }
}
