import * as THREE from 'three'
import type { ParallaxController } from '../interactions/ParallaxController'
import type { WorkshopContent } from './createWorkshop'

type Breakpoint = 'desktop' | 'tablet' | 'mobile'
type Position = readonly [x: number, y: number, z: number]

interface ResponsiveLayout {
  cameraPosition: Position
  cameraTarget: Position
  productPositions: readonly Position[]
  shelfPositions: readonly Position[]
  productScale: number
  parallaxStrength: number
  shelfWidth: number
  floorY: number
  workbenchY: number
}

const layouts: Record<Breakpoint, ResponsiveLayout> = {
  desktop: {
    cameraPosition: [0, 0.15, 11.2],
    cameraTarget: [0, 0, -2.5],
    productPositions: [
      [-4.3, 2.05, -2.8], [-4.3, 0.5, -2.8], [-4.3, -1.05, -2.8],
      [0, -1.72, -1.95],
      [4.3, 2.55, -2.8], [4.3, 1.3, -2.8], [4.3, 0.05, -2.8],
      [4.3, -1.2, -2.8], [4.3, -2.45, -2.8],
    ],
    shelfPositions: [
      [-4.3, 1.78, -2.95], [-4.3, 0.23, -2.95], [-4.3, -1.32, -2.95],
      [0, -1.98, -1.92],
      [4.3, 2.28, -2.95], [4.3, 1.03, -2.95], [4.3, -0.22, -2.95],
      [4.3, -1.47, -2.95], [4.3, -2.72, -2.95],
    ],
    productScale: 0.5,
    parallaxStrength: 1,
    shelfWidth: 1.45,
    floorY: -3.25,
    workbenchY: -2.95,
  },
  tablet: {
    cameraPosition: [0, 0.1, 14.5],
    cameraTarget: [0, 0, -2.5],
    productPositions: [
      [-4.05, 2.05, -2.8], [-4.05, 0.5, -2.8], [-4.05, -1.05, -2.8],
      [0, -1.62, -1.92], [-1.3, -1.94, -1.82], [1.3, -1.94, -1.82],
      [4.05, 2.05, -2.8], [4.05, 0.5, -2.8], [4.05, -1.05, -2.8],
    ],
    shelfPositions: [
      [-4.05, 1.81, -2.95], [-4.05, 0.26, -2.95], [-4.05, -1.29, -2.95],
      [0, -1.86, -1.9], [-1.3, -2.18, -1.8], [1.3, -2.18, -1.8],
      [4.05, 1.81, -2.95], [4.05, 0.26, -2.95], [4.05, -1.29, -2.95],
    ],
    productScale: 0.44,
    parallaxStrength: 0.72,
    shelfWidth: 1.3,
    floorY: -3.2,
    workbenchY: -2.9,
  },
  mobile: {
    cameraPosition: [0, 0.15, 15.8],
    cameraTarget: [0, -0.05, -3.1],
    productPositions: [
      [-4.2, 2.05, -2.8], [-4.2, 0.5, -2.8], [-4.2, -1.05, -2.8],
      [0, -1.62, -1.92], [-1.25, -1.94, -1.82], [1.25, -1.94, -1.82],
      [4.2, 2.05, -2.8], [4.2, 0.5, -2.8], [4.2, -1.05, -2.8],
    ],
    shelfPositions: [
      [-4.2, 1.84, -2.95], [-4.2, 0.29, -2.95], [-4.2, -1.26, -2.95],
      [0, -1.83, -1.9], [-1.25, -2.18, -1.8], [1.25, -2.18, -1.8],
      [4.2, 1.84, -2.95], [4.2, 0.29, -2.95], [4.2, -1.26, -2.95],
    ],
    productScale: 0.38,
    parallaxStrength: 0.5,
    shelfWidth: 1.12,
    floorY: -3.25,
    workbenchY: -2.95,
  },
}

export class ResponsiveSceneController {
  private readonly cameraPosition = new THREE.Vector3()
  private readonly cameraTarget = new THREE.Vector3()
  private readonly camera: THREE.PerspectiveCamera
  private readonly workshop: WorkshopContent
  private readonly parallax: ParallaxController

  constructor(
    camera: THREE.PerspectiveCamera,
    workshop: WorkshopContent,
    parallax: ParallaxController,
  ) {
    this.camera = camera
    this.workshop = workshop
    this.parallax = parallax
  }

  apply(width: number): void {
    const breakpoint: Breakpoint = width >= 1100 ? 'desktop' : width >= 680 ? 'tablet' : 'mobile'
    const layout = layouts[breakpoint]
    const scale = layout.productScale

    this.cameraPosition.set(...layout.cameraPosition)
    this.cameraTarget.set(...layout.cameraTarget)
    this.camera.position.copy(this.cameraPosition)
    this.camera.lookAt(this.cameraTarget)
    this.parallax.setBasePose(this.cameraPosition, this.cameraTarget, layout.parallaxStrength)
    this.workshop.floor.position.y = layout.floorY
    this.workshop.workbench.position.y = layout.workbenchY
    this.workshop.foreground.visible = breakpoint === 'desktop'

    this.workshop.eyewear.forEach((product, index) => {
      const position = layout.productPositions[index]
      if (!position) throw new Error(`Missing responsive position for product ${index + 1}`)
      const shelfPosition = layout.shelfPositions[index]
      if (!shelfPosition) throw new Error(`Missing responsive shelf position for product ${index + 1}`)

      product.position.set(...position)
      product.rotation.set(-0.1, breakpoint === 'desktop' ? ((index % 3) - 1) * -0.08 : 0, 0)
      product.scale.set(scale, scale, scale)
      product.userData.baseScale = scale

      const shelf = this.workshop.shelves[index]
      if (shelf) {
        shelf.position.set(...shelfPosition)
        shelf.scale.set(layout.shelfWidth / 2.3, 1, breakpoint === 'mobile' ? 0.95 / 1.15 : breakpoint === 'tablet' ? 1.05 / 1.15 : 1)
      }
    })
  }
}
