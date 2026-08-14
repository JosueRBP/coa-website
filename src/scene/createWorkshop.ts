import * as THREE from 'three'
import { products } from '../products/catalog'
import { createEyewearDisplay } from '../products/createEyewearDisplay'
import { workshopMaterials as materials } from './workshopMaterials'

export interface WorkshopContent {
  root: THREE.Group
  eyewear: THREE.Group[]
  shelves: THREE.Mesh[]
  floor: THREE.Mesh
  backWall: THREE.Mesh
  workbench: THREE.Group
  foreground: THREE.Group
}

function box(size: readonly [number, number, number], material: THREE.Material): THREE.Mesh {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(...size), material)
  mesh.castShadow = true
  mesh.receiveShadow = true
  return mesh
}

function createArchedWindow(): THREE.Group {
  const window = new THREE.Group()
  window.name = 'arched-window'

  const openingShape = new THREE.Shape()
  openingShape.moveTo(-2.25, -2.3)
  openingShape.lineTo(2.25, -2.3)
  openingShape.lineTo(2.25, 1.35)
  openingShape.absarc(0, 1.35, 2.25, 0, Math.PI, false)
  openingShape.lineTo(-2.25, -2.3)
  const opening = new THREE.Mesh(new THREE.ShapeGeometry(openingShape, 28), materials.sky)
  opening.position.z = -0.08
  window.add(opening)

  const exterior = new THREE.Group()
  exterior.name = 'temporary-exterior'
  const facades = [
    { x: -1.55, y: -1.55, width: 1.45, height: 1.5, material: materials.facadeCoral },
    { x: 0, y: -1.72, width: 1.55, height: 1.16, material: materials.facadeCream },
    { x: 1.55, y: -1.48, width: 1.5, height: 1.65, material: materials.facadeAqua },
  ]
  facades.forEach(({ x, y, width, height, material }, index) => {
    const facade = new THREE.Mesh(new THREE.PlaneGeometry(width, height), material)
    facade.position.set(x, y, -0.065)
    exterior.add(facade)
    ;[-0.28, 0.28].forEach((offset) => {
      const exteriorWindow = new THREE.Mesh(new THREE.PlaneGeometry(0.22, 0.35), materials.exteriorShadow)
      exteriorWindow.position.set(x + offset, y + 0.12 + (index % 2) * 0.08, -0.055)
      exterior.add(exteriorWindow)
      const trim = new THREE.Mesh(new THREE.PlaneGeometry(0.29, 0.43), materials.exteriorTrim)
      trim.position.set(x + offset, y + 0.12 + (index % 2) * 0.08, -0.06)
      exterior.add(trim)
    })
  })
  window.add(exterior)

  const jambGeometry = new THREE.BoxGeometry(0.24, 3.7, 0.28)
  ;[-2.38, 2.38].forEach((x) => {
    const jamb = new THREE.Mesh(jambGeometry, materials.plasterTrim)
    jamb.position.set(x, -0.45, 0.12)
    jamb.castShadow = true
    window.add(jamb)
  })
  const sill = box([5.05, 0.25, 0.5], materials.plasterTrim)
  sill.position.set(0, -2.38, 0.16)
  window.add(sill)

  const archCurve = new THREE.CatmullRomCurve3(
    Array.from({ length: 17 }, (_, index) => {
      const angle = Math.PI - (Math.PI * index) / 16
      return new THREE.Vector3(Math.cos(angle) * 2.38, 1.35 + Math.sin(angle) * 2.38, 0.14)
    }),
  )
  const arch = new THREE.Mesh(new THREE.TubeGeometry(archCurve, 32, 0.12, 6, false), materials.plasterTrim)
  arch.castShadow = true
  window.add(arch)

  const grille = new THREE.Group()
  grille.name = 'decorative-iron-grille'
  const barGeometry = new THREE.BoxGeometry(0.038, 3.55, 0.055)
  ;[-1.65, -0.82, 0, 0.82, 1.65].forEach((x) => {
    const bar = new THREE.Mesh(barGeometry, materials.paintedIron)
    bar.position.set(x, -0.42, 0.34)
    bar.castShadow = true
    grille.add(bar)
  })
  ;[-1.55, -0.42, 0.72].forEach((y) => {
    const rail = box([4.35, 0.038, 0.055], materials.paintedIron)
    rail.position.set(0, y, 0.34)
    grille.add(rail)
  })
  const diamondGeometry = new THREE.BoxGeometry(0.032, 1.05, 0.055)
  ;[-1.23, -0.41, 0.41, 1.23].forEach((x) => {
    ;[-0.98, 0.16].forEach((y) => {
      const forward = new THREE.Mesh(diamondGeometry, materials.paintedIron)
      forward.position.set(x, y, 0.35)
      forward.rotation.z = Math.PI / 4
      const backward = forward.clone()
      backward.rotation.z = -Math.PI / 4
      grille.add(forward, backward)
    })
  })
  const fanGeometry = new THREE.BoxGeometry(0.032, 2.1, 0.055)
  ;[-0.82, -0.41, 0, 0.41, 0.82].forEach((rotation) => {
    const fan = new THREE.Mesh(fanGeometry, materials.paintedIron)
    fan.position.set(Math.sin(rotation) * 0.9, 2.15, 0.34)
    fan.rotation.z = rotation
    grille.add(fan)
  })
  const glazing = new THREE.Mesh(new THREE.ShapeGeometry(openingShape, 28), materials.glass)
  glazing.position.z = 0.22
  window.add(glazing, grille)
  return window
}

function createWorkbench(): { group: THREE.Group; top: THREE.Mesh } {
  const group = new THREE.Group()
  group.name = 'central-workbench'
  const top = box([5.7, 0.28, 1.75], materials.mediumWoodLight)
  top.position.set(0, 0.7, 0)
  group.add(top)

  ;[-2.35, 2.35].forEach((x) => {
    const cabinet = box([0.95, 1.45, 1.4], materials.darkWood)
    cabinet.position.set(x, -0.12, 0)
    group.add(cabinet)
    ;[0.3, -0.08, -0.46].forEach((y) => {
      const drawer = box([0.77, 0.27, 0.08], materials.mediumWood)
      drawer.position.set(x, y, 0.75)
      const handle = box([0.28, 0.045, 0.07], materials.agedMetal)
      handle.position.set(x, y, 0.82)
      group.add(drawer, handle)
    })
  })
  const stretcher = box([3.8, 0.16, 0.22], materials.darkWood)
  stretcher.position.set(0, -0.55, -0.35)
  group.add(stretcher)
  return { group, top }
}

function createWorkshopTools(): THREE.Group {
  const tools = new THREE.Group()
  tools.name = 'workshop-tools'

  const drillBase = box([1.15, 0.18, 0.85], materials.agedMetal)
  drillBase.position.set(-4.6, -2.68, -1.75)
  const drillColumn = box([0.18, 1.65, 0.18], materials.machineMetal)
  drillColumn.position.set(-4.6, -1.78, -1.95)
  const drillHead = box([0.9, 0.48, 0.62], materials.machinePaint)
  drillHead.position.set(-4.38, -1.05, -1.8)
  const drillBit = box([0.07, 0.62, 0.07], materials.machineMetal)
  drillBit.position.set(-4.18, -1.58, -1.65)
  tools.add(drillBase, drillColumn, drillHead, drillBit)

  const drillTable = new THREE.Mesh(new THREE.CylinderGeometry(0.48, 0.48, 0.1, 16), materials.machineMetal)
  drillTable.position.set(-4.35, -1.82, -1.7)
  tools.add(drillTable)

  const grinderBase = box([1.3, 0.22, 0.75], materials.agedMetal)
  grinderBase.position.set(4.45, -2.7, -1.7)
  const motor = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.34, 1.15, 12), materials.machinePaint)
  motor.rotation.z = Math.PI / 2
  motor.position.set(4.45, -2.28, -1.65)
  motor.castShadow = true
  const wheelGeometry = new THREE.CylinderGeometry(0.48, 0.48, 0.1, 16)
  ;[-0.66, 0.66].forEach((offset) => {
    const wheel = new THREE.Mesh(wheelGeometry, materials.agedMetal)
    wheel.rotation.z = Math.PI / 2
    wheel.position.set(4.45 + offset, -2.28, -1.65)
    wheel.castShadow = true
    tools.add(wheel)
  })
  tools.add(grinderBase, motor)

  const pegboard = box([2.1, 2.3, 0.12], materials.darkWood)
  pegboard.position.set(-4.6, 1.8, -3.95)
  tools.add(pegboard)
  ;[-5.25, -4.65, -4.05].forEach((x, index) => {
    const hangingTool = box([0.09, 0.85 + index * 0.12, 0.08], materials.machineMetal)
    hangingTool.position.set(x, 1.8, -3.82)
    hangingTool.rotation.z = index === 1 ? 0.15 : -0.12
    tools.add(hangingTool)
  })
  const clampGeometry = new THREE.TorusGeometry(0.22, 0.045, 6, 12, Math.PI * 1.45)
  ;[-2.1, -1.55].forEach((x) => {
    const clamp = new THREE.Mesh(clampGeometry, materials.agedMetal)
    clamp.position.set(x, -2.08, -0.72)
    clamp.rotation.x = Math.PI / 2
    tools.add(clamp)
  })
  return tools
}

function createForeground(): THREE.Group {
  const foreground = new THREE.Group()
  foreground.name = 'desktop-foreground-depth'
  const leftTable = box([3.8, 0.34, 2.7], materials.darkWood)
  leftTable.position.set(-7.25, -2.55, 4.3)
  leftTable.rotation.y = 0.15
  const rightTable = box([3.3, 0.3, 2.35], materials.mediumWood)
  rightTable.position.set(7.35, -2.48, 4.7)
  rightTable.rotation.y = -0.18
  foreground.add(leftTable, rightTable)

  const tray = box([1.65, 0.12, 0.85], materials.machineMetal)
  tray.position.set(6.9, -2.19, 4.35)
  foreground.add(tray)
  ;[-0.48, 0, 0.48].forEach((offset, index) => {
    const file = box([0.08, 0.06, 0.95], index === 1 ? materials.agedMetal : materials.machineMetal)
    file.position.set(6.9 + offset, -2.08, 4.32)
    file.rotation.y = 0.18 * (index - 1)
    foreground.add(file)
  })
  return foreground
}

export function createWorkshop(): WorkshopContent {
  const root = new THREE.Group()
  root.name = 'puerto-nuevo-workshop'
  const eyewear: THREE.Group[] = []
  const shelves: THREE.Mesh[] = []
  const architecture = new THREE.Group()
  architecture.name = 'architecture'
  const furniture = new THREE.Group()
  furniture.name = 'furniture'
  const productDisplays = new THREE.Group()
  productDisplays.name = 'product-displays'
  const toolsAndMachines = new THREE.Group()
  toolsAndMachines.name = 'tools-and-machines'
  const foreground = createForeground()
  root.add(architecture, furniture, productDisplays, toolsAndMachines, foreground)

  const floor = new THREE.Mesh(new THREE.PlaneGeometry(24, 18), materials.grout)
  floor.rotation.x = -Math.PI / 2
  floor.position.y = -3.25
  floor.receiveShadow = true
  architecture.add(floor)
  const tileGeometry = new THREE.BoxGeometry(0.92, 0.045, 0.92)
  for (let row = 0; row < 10; row += 1) {
    for (let column = 0; column < 18; column += 1) {
      const pattern = (row + column) % 7
      const tileMaterial = pattern === 0 ? materials.ceramicBlue : pattern === 3 ? materials.ceramicRose : materials.ceramicCream
      const floorTile = new THREE.Mesh(tileGeometry, tileMaterial)
      floorTile.position.set(column - 8.5, -3.21, row - 2.5)
      floorTile.receiveShadow = true
      architecture.add(floorTile)
    }
  }

  const backWall = new THREE.Mesh(new THREE.PlaneGeometry(18, 10.5), materials.plaster)
  backWall.position.set(0, 1.7, -4.5)
  backWall.receiveShadow = true
  architecture.add(backWall)
  const wallVariation = box([5.2, 4.6, 0.035], materials.plasterVariation)
  wallVariation.position.set(-5.9, 1.1, -4.47)
  architecture.add(wallVariation)
  const leftReturn = box([0.3, 10.5, 5], materials.plasterVariation)
  leftReturn.position.set(-9, 1.7, -2.1)
  const rightReturn = leftReturn.clone()
  rightReturn.position.x = 9
  architecture.add(leftReturn, rightReturn)

  const window = createArchedWindow()
  window.position.set(0, 1.35, -4.34)
  architecture.add(window)

  const bench = createWorkbench()
  bench.group.position.set(0, -2.95, -1.65)
  furniture.add(bench.group)

  const shelfMaterial = materials.displaySurface
  products.forEach((product) => {
    const shelf = box([2.3, 0.12, 0.8], shelfMaterial)
    shelf.name = `product-shelf-${product.id}`
    productDisplays.add(shelf)
    shelves.push(shelf)

    const display = createEyewearDisplay(product)
    productDisplays.add(display)
    eyewear.push(display)
  })

  const leftUnit = new THREE.Group()
  leftUnit.name = 'left-shelving'
  ;[-5.75, -3.05].forEach((x) => {
    const upright = box([0.16, 6.4, 0.85], materials.darkWood)
    upright.position.set(x, 0, -3.35)
    leftUnit.add(upright)
  })
  const rightUnit = leftUnit.clone()
  rightUnit.name = 'right-shelving'
  rightUnit.position.x = 8.6
  furniture.add(leftUnit, rightUnit)
  toolsAndMachines.add(createWorkshopTools())

  return { root, eyewear, shelves, floor, backWall, workbench: bench.group, foreground }
}
