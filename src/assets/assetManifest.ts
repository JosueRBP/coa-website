import type { AssetDefinition } from './types'

const identity = { position: [0, 0, 0], rotation: [0, 0, 0], scale: [1, 1, 1] } as const

export const assetManifest = {
  clientPreview: {
    scene: { id: 'client-preview.v2', kind: 'workshop', path: `${import.meta.env.BASE_URL}models/puerto-nuevo-client-preview-v2.glb`, priority: 'essential', enabled: true, transform: identity, expectedRootName: 'Scene' },
  },
  workshop: {
    architecture: { id: 'workshop.architecture', kind: 'workshop', path: '/models/workshop/workshop-shell.glb', priority: 'essential', enabled: false, transform: identity, expectedRootName: 'PN_Workshop_Shell' },
    window: { id: 'workshop.window', kind: 'workshop', path: '/models/workshop/arched-window.glb', priority: 'essential', enabled: false, transform: identity, expectedRootName: 'PN_Arched_Window' },
    grille: { id: 'workshop.grille', kind: 'workshop', path: '/models/workshop/window-grille.glb', priority: 'essential', enabled: false, transform: identity, expectedRootName: 'PN_Window_Grille' },
    workbench: { id: 'workshop.workbench', kind: 'workshop', path: '/models/workshop/main-workbench.glb', priority: 'essential', enabled: false, transform: identity, expectedRootName: 'PN_Main_Workbench' },
    leftDisplays: { id: 'workshop.leftDisplays', kind: 'workshop', path: '/models/workshop/left-displays.glb', priority: 'essential', enabled: false, transform: identity, expectedRootName: 'PN_Left_Displays' },
    rightDisplays: { id: 'workshop.rightDisplays', kind: 'workshop', path: '/models/workshop/right-displays.glb', priority: 'essential', enabled: false, transform: identity, expectedRootName: 'PN_Right_Displays' },
    floor: { id: 'workshop.floor', kind: 'workshop', path: '/models/workshop/tiled-floor.glb', priority: 'essential', enabled: false, transform: identity, expectedRootName: 'PN_Tiled_Floor' },
    exterior: { id: 'workshop.exterior', kind: 'workshop', path: '/models/workshop/window-exterior.glb', priority: 'optional', enabled: false, transform: identity, expectedRootName: 'PN_Window_Exterior' },
    machinery: { id: 'workshop.machinery', kind: 'workshop', path: '/models/workshop/machinery.glb', priority: 'optional', enabled: false, transform: identity },
    foreground: { id: 'workshop.foreground', kind: 'prop', path: '/models/props/foreground-props.glb', priority: 'optional', enabled: false, transform: identity },
  },
  products: Object.fromEntries(Array.from({ length: 9 }, (_, index) => {
    const id = String(index + 1).padStart(2, '0')
    return [id, { id: `product.${id}`, kind: 'product', path: `/models/products/frame-${id}.glb`, priority: 'essential', enabled: false, transform: identity, expectedRootName: `PN_Frame_${id}` } satisfies AssetDefinition]
  })) as Record<string, AssetDefinition>,
  lizard: {
    model: { id: 'lizard.model', kind: 'lizard', path: '/models/lizard/puerto-rico-anole.glb', priority: 'optional', enabled: false, transform: identity, expectedRootName: 'PN_Lizard' },
  },
} satisfies Record<string, Record<string, AssetDefinition>>

export const allAssets: AssetDefinition[] = Object.values(assetManifest).flatMap((category) => Object.values(category))
