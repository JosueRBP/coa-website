import './styles/main.css'
import { StorefrontScene } from './scene/StorefrontScene'

const root = document.querySelector<HTMLDivElement>('#app')
if (!root) throw new Error('Application root was not found.')

root.innerHTML = `
  <main class="storefront" aria-label="Puerto Nuevo 1960 interactive eyewear workshop">
    <div class="scene-root" data-scene-root aria-hidden="true"></div>
    <header class="brand-mark"><span class="brand-mark__name">Puerto Nuevo</span><span class="brand-mark__year">Est. 1960</span></header>
    <div class="scene-instructions"><span>Explore the collection</span><span class="scene-instructions__detail">Select a frame to focus</span></div>
    <button class="audio-toggle" type="button" data-audio-toggle aria-pressed="false" aria-label="Enable ambient audio"><span class="audio-toggle__dot" aria-hidden="true"></span><span data-audio-label>Sound off</span></button>
    <section class="focus-panel" data-focus-panel aria-live="polite" aria-hidden="true"><span class="focus-panel__eyebrow">Selected frame</span><strong class="focus-panel__id" data-focus-id>01</strong><span class="focus-panel__hint">Press Esc or tap outside to return</span></section>
    <div class="loading-screen" data-loading-screen aria-label="Loading the workshop"><span class="loading-screen__brand">PN / 1960</span><span class="loading-screen__line"></span></div>
  </main>`

const sceneRoot = document.querySelector<HTMLElement>('[data-scene-root]')
if (!sceneRoot) throw new Error('Scene root was not found.')
new StorefrontScene(sceneRoot).start()
