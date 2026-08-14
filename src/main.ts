import './styles/main.css'
import { StorefrontScene } from './scene/StorefrontScene'

const root = document.querySelector<HTMLDivElement>('#app')
if (!root) throw new Error('Application root was not found.')

root.innerHTML = `
  <main class="storefront" aria-label="Puerto Nuevo 1960 interactive eyewear workshop">
    <div class="scene-root" data-scene-root aria-hidden="true"></div>
    <header class="brand-mark"><span class="brand-mark__name">Puerto Nuevo</span><span class="brand-mark__year">Est. 1960</span></header>
    <div class="scene-instructions"><span>Explore the collection</span><span class="scene-instructions__detail">Select a frame to focus</span></div>
    <div class="mobile-pan-hint" data-mobile-pan-hint aria-hidden="true"><span>←</span> Explore the workshop <span>→</span></div>
    <button class="audio-toggle" type="button" data-audio-toggle aria-pressed="false" aria-label="Enable ambient audio"><span class="audio-toggle__dot" aria-hidden="true"></span><span data-audio-label>Sound off</span></button>
    <section class="focus-experience" data-focus-panel aria-hidden="true" aria-label="Product details">
      <div class="focus-experience__shade" aria-hidden="true"></div>
      <div class="focus-drag-zone" data-focus-drag-zone aria-label="Drag to rotate product"></div>
      <div class="focus-experience__shell" role="dialog" aria-modal="true" aria-labelledby="focus-name">
        <div class="focus-experience__topline"><span data-focus-count>01 / 09</span><button class="focus-icon-button" type="button" data-focus-close aria-label="Close product focus">×</button></div>
        <div class="focus-experience__identity">
          <span class="focus-kicker" data-focus-edition>Edition 03 / 100</span>
          <h1 id="focus-name" data-focus-name>Brisa</h1>
          <p class="focus-subtitle" data-focus-subtitle>Olive acetate</p>
          <p class="focus-price" data-focus-price>$1,200 USD</p>
          <p class="focus-description" data-focus-short></p>
          <span class="focus-drag-hint">Drag the frame to examine</span>
        </div>
        <dl class="focus-specs">
          <div><dt>Material</dt><dd data-focus-material></dd></div>
          <div><dt>Hinge</dt><dd data-focus-hinge></dd></div>
          <div><dt>Dimensions</dt><dd data-focus-dimensions></dd></div>
          <div><dt>Made in</dt><dd data-focus-made-in></dd></div>
          <div><dt>Lead time</dt><dd data-focus-lead></dd></div>
        </dl>
        <div class="focus-actions">
          <p class="focus-action-status" data-focus-status aria-live="polite"></p>
          <button type="button" data-focus-acquire>Acquire — $1,200</button>
          <button type="button" data-focus-reserve>Reserve — $200</button>
        </div>
        <nav class="focus-navigation" aria-label="Browse eyewear"><button type="button" data-focus-previous>← Previous</button><button type="button" data-focus-next>Next →</button></nav>
      </div>
    </section>
    <div class="loading-screen" data-loading-screen aria-label="Loading the workshop"><span class="loading-screen__brand">PN / 1960</span><span class="loading-screen__line"></span></div>
  </main>`

const sceneRoot = document.querySelector<HTMLElement>('[data-scene-root]')
if (!sceneRoot) throw new Error('Scene root was not found.')
new StorefrontScene(sceneRoot).start()
