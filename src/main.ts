import './styles/main.css'
import { StorefrontScene } from './scene/StorefrontScene'

const root = document.querySelector<HTMLDivElement>('#app')
if (!root) throw new Error('Application root was not found.')

root.innerHTML = `
  <main class="storefront" aria-label="Taller interactivo de eyewear Puerto Nuevo 1960">
    <div class="scene-root" data-scene-root aria-hidden="true"></div>
    <header class="brand-mark" aria-label="Puerto Nuevo 1960"><span class="brand-mark__name">Puerto Nuevo</span><span class="brand-mark__year">1960</span><span class="brand-mark__rule" aria-hidden="true"></span><span class="brand-mark__craft">Handcrafted eyewear<br><em>Hechas a mano en Puerto Rico</em></span></header>
    <nav class="atelier-nav" aria-label="Explorar Puerto Nuevo"><button type="button" data-collection-view><span>01</span> La colección</button><button type="button" data-info-open="workshop"><span>02</span> El taller</button><button type="button" data-info-open="process"><span>03</span> Proceso artesanal</button></nav>
    <div class="audio-control"><button class="audio-toggle" type="button" data-audio-toggle aria-pressed="false" aria-label="Activar sonido ambiental"><span class="audio-toggle__dot" aria-hidden="true"></span><span data-audio-label>Sonido off</span></button><div class="audio-panel" aria-label="Controles de sonido"><span>Música de fondo</span><strong>Bolero de Puerto Rico</strong><label>Volumen <input type="range" min="0" max="100" value="55" data-audio-volume aria-label="Volumen ambiental"></label><small>Pista licenciada pendiente</small></div></div>
    <button class="info-button" type="button" data-info-open="concept" aria-label="Información sobre el concepto">i</button>
    <div class="scene-instructions"><span>Mueve el cursor para explorar</span><span class="scene-instructions__detail">Haz clic en cualquier montura para descubrir más</span></div>
    <div class="mobile-pan-hint" data-mobile-pan-hint aria-hidden="true"><span>←</span><span>Desliza para explorar<br><small>Toca una montura para descubrir más</small></span><span>→</span></div>
    <section class="heritage-strip" aria-label="Valores de Puerto Nuevo"><article><strong>Hecho en Puerto Rico</strong><span>Inspirado en la arquitectura y el alma de nuestra isla.</span></article><article><strong>Hecho a mano</strong><span>Cada montura es única e irrepetible.</span></article><article><strong>Edición limitada</strong><span>Producción limitada por diseño.</span></article><article><strong>Materiales premium</strong><span>Acetatos italianos y bisagras de titanio.</span></article></section>
    <button class="visit-card" type="button" data-info-open="visit"><span>Visita nuestro taller</span><small>Agenda una cita privada para conocer el proceso completo.</small><b>↗</b></button>
    <section class="info-overlay" data-info-overlay aria-hidden="true" aria-labelledby="info-title"><button type="button" class="info-overlay__backdrop" data-info-close aria-label="Cerrar información"></button><article class="info-overlay__panel" role="dialog" aria-modal="true"><span class="info-overlay__eyebrow">Puerto Nuevo 1960</span><h2 id="info-title" data-info-title>El taller</h2><p data-info-copy></p><button type="button" class="info-overlay__close" data-info-close>Cerrar</button></article></section>
    <section class="focus-experience" data-focus-panel aria-hidden="true" aria-label="Detalles de producto">
      <div class="focus-experience__shade" aria-hidden="true"></div><div class="focus-drag-zone" data-focus-drag-zone aria-label="Arrastra para rotar la montura"></div>
      <div class="focus-experience__shell" role="dialog" aria-modal="true" aria-labelledby="focus-name">
        <div class="focus-experience__topline"><span data-focus-count>01 / 09</span><button class="focus-icon-button" type="button" data-focus-close aria-label="Cerrar producto">×</button></div>
        <div class="focus-experience__identity"><span class="focus-kicker" data-focus-edition>Edición 03 / 100</span><h1 id="focus-name" data-focus-name>Brisa</h1><p class="focus-subtitle" data-focus-subtitle>Acetato oliva</p><p class="focus-price" data-focus-price>$1,200 USD</p><p class="focus-description" data-focus-short></p><div class="focus-provenance"><span>Hecho a mano</span><span>Edición limitada</span><span>Acetato italiano premium</span></div><span class="focus-drag-hint">Arrastra la montura para examinar</span></div>
        <dl class="focus-specs"><div><dt>Material</dt><dd data-focus-material></dd></div><div><dt>Bisagra</dt><dd data-focus-hinge></dd></div><div><dt>Medidas</dt><dd data-focus-dimensions></dd></div><div><dt>Origen</dt><dd data-focus-made-in></dd></div><div><dt>Entrega</dt><dd data-focus-lead></dd></div></dl>
        <div class="focus-actions"><p class="focus-action-status" data-focus-status aria-live="polite"></p><button type="button" data-focus-acquire>Adquirir — $1,200</button><button type="button" data-focus-reserve>Reserva — $200</button></div>
        <nav class="focus-navigation" aria-label="Explorar monturas"><button type="button" data-focus-previous>← Anterior</button><button type="button" data-focus-next>Siguiente →</button></nav>
      </div>
    </section>
    <div class="loading-screen" data-loading-screen aria-label="Preparando el taller"><span class="loading-screen__brand">Puerto Nuevo</span><span class="loading-screen__year">1960</span><span class="loading-screen__message" data-loading-message>Preparando el taller…</span><span class="loading-screen__line"><span data-loading-progress></span></span><span class="loading-screen__percent" data-loading-percent>0%</span></div>
  </main>`

const sceneRoot = document.querySelector<HTMLElement>('[data-scene-root]')
if (!sceneRoot) throw new Error('Scene root was not found.')
new StorefrontScene(sceneRoot).start()
