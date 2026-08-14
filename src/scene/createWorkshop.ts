import * as THREE from 'three'
import { products } from '../products/catalog'
import { createEyewearDisplay } from '../products/createEyewearDisplay'
import { workshopMaterials as materials } from './workshopMaterials'
import {
  createProductionArchitecture,
  createProductionForeground,
  createProductionTools,
  createProductionWorkbench,
} from './productionWorkshopRegions'

export interface WorkshopContent {
  root: THREE.Group
  eyewear: THREE.Group[]
  shelves: THREE.Mesh[]
  floor: THREE.Mesh
  backWall: THREE.Mesh
  workbench: THREE.Group
  foreground: THREE.Group
  regions: {
    architecture: THREE.Group
    window: THREE.Group
    grille: THREE.Group
    mainWorkbench: THREE.Group
    leftDisplays: THREE.Group
    rightDisplays: THREE.Group
    machinery: THREE.Group
    foregroundProps: THREE.Group
    floor: THREE.Group
    exterior: THREE.Group
  }
}

function box(size: readonly [number, number, number], material: THREE.Material): THREE.Mesh {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(...size), material)
  mesh.castShadow = true; mesh.receiveShadow = true
  return mesh
}

function createDisplayBay(name: string, left: number, right: number): THREE.Group {
  const bay = new THREE.Group(); bay.name = name
  ;[left, right].forEach((x) => { const upright = box([0.18, 6.35, 0.92], materials.woodAgedDetail); upright.position.set(x, 0, -3.32); bay.add(upright) })
  const back = box([Math.abs(right - left), 6.15, 0.08], materials.plasterVariation); back.position.set((left + right) / 2, 0, -3.78); bay.add(back)
  return bay
}

function createProductNumberLabel(id: string): THREE.Sprite {
  const canvas = document.createElement('canvas'); canvas.width = 128; canvas.height = 64
  const context = canvas.getContext('2d')!; context.clearRect(0, 0, 128, 64)
  context.fillStyle = 'rgba(18, 20, 17, .78)'; context.fillRect(0, 0, 128, 64)
  context.strokeStyle = 'rgba(220, 196, 140, .72)'; context.lineWidth = 2; context.strokeRect(2, 2, 124, 60)
  context.fillStyle = '#efe8d8'; context.font = '32px Georgia'; context.textAlign = 'center'; context.textBaseline = 'middle'; context.fillText(id, 64, 33)
  const texture = new THREE.CanvasTexture(canvas); texture.colorSpace = THREE.SRGBColorSpace
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: texture, transparent: true, depthWrite: false }))
  sprite.name = `product-number-${id}`; sprite.position.set(-.82, .31, .44); sprite.scale.set(.42, .21, 1); sprite.raycast = () => undefined
  return sprite
}

export function createWorkshop(): WorkshopContent {
  const root = new THREE.Group(); root.name = 'puerto-nuevo-workshop'
  const architecture = createProductionArchitecture()
  const furniture = new THREE.Group(); furniture.name = 'furniture'
  const productDisplays = new THREE.Group(); productDisplays.name = 'product-displays'
  const machinery = createProductionTools()
  const foreground = createProductionForeground()
  const bench = createProductionWorkbench(); bench.root.position.set(0, -2.95, -1.65)
  const leftDisplays = createDisplayBay('PN_Left_Displays_ProceduralProduction', -5.78, -3.02)
  const rightDisplays = createDisplayBay('PN_Right_Displays_ProceduralProduction', 3.02, 5.78)
  furniture.add(bench.root, leftDisplays, rightDisplays)

  const eyewear: THREE.Group[] = []
  const shelves: THREE.Mesh[] = []
  products.forEach((product) => {
    const shelf = box([2.3, 0.12, 0.8], materials.woodShelf)
    shelf.name = `product-shelf-${product.id}`
    const lip = box([2.3, 0.055, 0.08], materials.woodWorkbench)
    lip.position.set(0, 0.065, 0.36)
    const productContact = new THREE.Mesh(new THREE.PlaneGeometry(1.25, .38), materials.contactShadow)
    productContact.rotation.x = -Math.PI / 2; productContact.position.set(0, .068, 0); productContact.raycast = () => undefined
    shelf.add(lip, productContact, createProductNumberLabel(product.id))
    const display = createEyewearDisplay(product)
    productDisplays.add(shelf, display)
    shelves.push(shelf); eyewear.push(display)
  })

  root.add(architecture.shell, architecture.floor, architecture.window, furniture, productDisplays, machinery, foreground)
  return {
    root, eyewear, shelves, floor: architecture.floorBase, backWall: architecture.backWall,
    workbench: bench.root, foreground,
    regions: {
      architecture: architecture.shell, window: architecture.window, grille: architecture.grille,
      mainWorkbench: bench.root, leftDisplays, rightDisplays, machinery,
      foregroundProps: foreground, floor: architecture.floor, exterior: architecture.exterior,
    },
  }
}
