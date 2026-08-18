import gsap from 'gsap'
import { AudioController } from '../audio/AudioController'
import type { Product } from '../products/catalog'
import type { CommerceAction, PurchaseUIState } from '../commerce/types'
import type { AssetLoadProgress } from '../assets/types'

export interface FocusUIHandlers { close: () => void; previous: () => void; next: () => void; reserve: () => void; acquire: () => void }
const information = {
  concept: ['Concepto', 'Una tienda que se recorre como un lugar: entra al taller, descubre nueve monturas y conoce el oficio detrás de cada pieza.'],
  workshop: ['El taller', 'Un espacio inspirado en las casas de Puerto Nuevo de los años sesenta, donde arquitectura, herramientas y luz tropical enmarcan la colección.'],
  process: ['Proceso artesanal', 'Cada montura se corta, ensambla, pule y ajusta a mano en pequeñas ediciones. El ritmo del taller está presente en cada detalle.'],
  visit: ['Visita nuestro taller', 'Las citas privadas y el recorrido completo del proceso formarán parte de la experiencia final. Para este demo, la solicitud de visita es informativa.'],
} as const

export class StorefrontUI {
  private readonly panel = document.querySelector<HTMLElement>('[data-focus-panel]')
  private readonly closeButton = document.querySelector<HTMLButtonElement>('[data-focus-close]')
  private readonly infoOverlay = document.querySelector<HTMLElement>('[data-info-overlay]')
  constructor() {
    const audioButton = document.querySelector<HTMLButtonElement>('[data-audio-toggle]')
    if (audioButton) new AudioController(audioButton, [{ id: 'quizas-bolero', src: `${import.meta.env.BASE_URL}audio/quizas-quizas-quizas-los-panchos.mp3`, volume: 0.34, loop: true }])
    document.querySelectorAll<HTMLElement>('[data-info-open]').forEach((button) => button.addEventListener('click', () => this.openInformation(button.dataset.infoOpen ?? 'concept')))
    document.querySelectorAll<HTMLElement>('[data-info-close]').forEach((button) => button.addEventListener('click', this.closeInformation))
    document.querySelector('[data-collection-view]')?.addEventListener('click', this.closeInformation)
    window.addEventListener('keydown', (event) => { if (event.key === 'Escape' && this.infoOverlay?.getAttribute('aria-hidden') === 'false') this.closeInformation() })
  }
  bindFocusControls(handlers: FocusUIHandlers): void { this.closeButton?.addEventListener('click', handlers.close); document.querySelector('[data-focus-previous]')?.addEventListener('click', handlers.previous); document.querySelector('[data-focus-next]')?.addEventListener('click', handlers.next); document.querySelector('[data-focus-reserve]')?.addEventListener('click', handlers.reserve); document.querySelector('[data-focus-acquire]')?.addEventListener('click', handlers.acquire) }
  private openInformation(key: string): void { const entry = information[key as keyof typeof information] ?? information.concept; const title = document.querySelector<HTMLElement>('[data-info-title]'); const copy = document.querySelector<HTMLElement>('[data-info-copy]'); if (title) title.textContent = entry[0]; if (copy) copy.textContent = entry[1]; this.infoOverlay?.setAttribute('aria-hidden', 'false'); document.body.classList.add('is-info-open') }
  private closeInformation = (): void => { this.infoOverlay?.setAttribute('aria-hidden', 'true'); document.body.classList.remove('is-info-open') }
  hideLoader(): void { const loader = document.querySelector<HTMLElement>('[data-loading-screen]'); if (loader) gsap.to(loader, { autoAlpha: 0, duration: 0.8, delay: 0.15, ease: 'power2.inOut', onComplete: () => loader.remove() }) }
  updateLoadingProgress(progress: AssetLoadProgress): void { const bar = document.querySelector<HTMLElement>('[data-loading-progress]'); const percent = document.querySelector<HTMLElement>('[data-loading-percent]'); if (bar) bar.style.width = `${progress.percent}%`; if (percent) percent.textContent = `${progress.percent}%` }
  showPreviewFallback(): void { const message = document.querySelector<HTMLElement>('[data-loading-message]'); if (message) message.textContent = 'Usando taller interactivo alterno…' }
  renderProduct(product: Product): void {
    const values: Record<string, string> = { '[data-focus-count]': `${product.id} / 09`, '[data-focus-name]': product.name, '[data-focus-subtitle]': product.subtitle, '[data-focus-price]': `$${product.price.toLocaleString()} USD`, '[data-focus-short]': product.shortDescription, '[data-focus-edition]': `Edición ${product.edition}`, '[data-focus-material]': product.material, '[data-focus-hinge]': product.hinge, '[data-focus-dimensions]': product.dimensions, '[data-focus-made-in]': product.madeIn, '[data-focus-lead]': product.leadTime }
    Object.entries(values).forEach(([selector, value]) => { const node = document.querySelector<HTMLElement>(selector); if (node) node.textContent = value })
    const acquire = document.querySelector<HTMLButtonElement>('[data-focus-acquire]'); if (acquire) acquire.textContent = `Adquirir — $${product.price.toLocaleString()}`
    const reserve = document.querySelector<HTMLButtonElement>('[data-focus-reserve]'); if (reserve) reserve.textContent = `Reserva — $${product.reservationPrice.toLocaleString()}`
    const status = document.querySelector<HTMLElement>('[data-focus-status]'); if (status) status.textContent = ''
  }
  showFocus(): void { if (!this.panel) return; this.closeInformation(); this.panel.setAttribute('aria-hidden', 'false'); document.body.classList.add('is-focused'); this.closeButton?.focus({ preventScroll: true }) }
  hideFocus(): void { this.panel?.setAttribute('aria-hidden', 'true'); document.body.classList.remove('is-focused') }
  showPurchaseMessage(action: CommerceAction): void { const status = document.querySelector<HTMLElement>('[data-focus-status]'); if (status) status.textContent = action === 'acquire' ? 'Demo: la compra segura estará disponible en la próxima fase.' : 'Demo: hemos registrado tu interés en reservar esta pieza.' }
  setPurchaseState(_action: CommerceAction, _state: PurchaseUIState, message = ''): void { const status = document.querySelector<HTMLElement>('[data-focus-status]'); if (status) status.textContent = message }
}
