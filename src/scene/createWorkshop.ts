import * as THREE from 'three'
import { products } from '../products/catalog'
import { createEyewearDisplay } from '../products/createEyewearDisplay'

export interface WorkshopContent {
  root: THREE.Group
  eyewear: THREE.Group[]
  shelves: THREE.Mesh[]
  floor: THREE.Mesh
  backWall: THREE.Mesh
  workbench: THREE.Group
}

const plaster = new THREE.MeshStandardMaterial({ color: 0xd8d2c4, roughness: 0.96 })
const plasterShade = new THREE.MeshStandardMaterial({ color: 0xc4bdad, roughness: 0.94 })
const wood = new THREE.MeshStandardMaterial({ color: 0x76543a, roughness: 0.72 })
const darkWood = new THREE.MeshStandardMaterial({ color: 0x4b382b, roughness: 0.78 })
const iron = new THREE.MeshStandardMaterial({ color: 0x343a39, metalness: 0.68, roughness: 0.42 })
const steel = new THREE.MeshStandardMaterial({ color: 0x78807d, metalness: 0.72, roughness: 0.34 })
const tile = new THREE.MeshStandardMaterial({ color: 0xb9b3a7, roughness: 0.88 })
const grout = new THREE.MeshStandardMaterial({ color: 0x716f69, roughness: 1 })
const daylight = new THREE.MeshBasicMaterial({ color: 0xbdd7d8 })

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
  const opening = new THREE.Mesh(new THREE.ShapeGeometry(openingShape, 28), daylight)
  opening.position.z = -0.08
  window.add(opening)

  const jambGeometry = new THREE.BoxGeometry(0.24, 3.7, 0.28)
  ;[-2.38, 2.38].forEach((x) => {
    const jamb = new THREE.Mesh(jambGeometry, plasterShade)
    jamb.position.set(x, -0.45, 0.12)
    jamb.castShadow = true
    window.add(jamb)
  })
  const sill = box([5.05, 0.25, 0.5], plasterShade)
  sill.position.set(0, -2.38, 0.16)
  window.add(sill)

  const archCurve = new THREE.CatmullRomCurve3(
    Array.from({ length: 17 }, (_, index) => {
      const angle = Math.PI - (Math.PI * index) / 16
      return new THREE.Vector3(Math.cos(angle) * 2.38, 1.35 + Math.sin(angle) * 2.38, 0.14)
    }),
  )
  const arch = new THREE.Mesh(new THREE.TubeGeometry(archCurve, 32, 0.12, 6, false), plasterShade)
  arch.castShadow = true
  window.add(arch)

  const grille = new THREE.Group()
  grille.name = 'decorative-iron-grille'
  const barGeometry = new THREE.BoxGeometry(0.055, 3.55, 0.08)
  ;[-1.65, -0.82, 0, 0.82, 1.65].forEach((x) => {
    const bar = new THREE.Mesh(barGeometry, iron)
    bar.position.set(x, -0.42, 0.34)
    bar.castShadow = true
    grille.add(bar)
  })
  ;[-1.55, -0.42, 0.72].forEach((y) => {
    const rail = box([4.35, 0.055, 0.08], iron)
    rail.position.set(0, y, 0.34)
    grille.add(rail)
  })
  const diamondGeometry = new THREE.BoxGeometry(0.045, 1.05, 0.08)
  ;[-1.23, -0.41, 0.41, 1.23].forEach((x) => {
    ;[-0.98, 0.16].forEach((y) => {
      const forward = new THREE.Mesh(diamondGeometry, iron)
      forward.position.set(x, y, 0.35)
      forward.rotation.z = Math.PI / 4
      const backward = forward.clone()
      backward.rotation.z = -Math.PI / 4
      grille.add(forward, backward)
    })
  })
  const fanGeometry = new THREE.BoxGeometry(0.045, 2.1, 0.08)
  ;[-0.82, -0.41, 0, 0.41, 0.82].forEach((rotation) => {
    const fan = new THREE.Mesh(fanGeometry, iron)
    fan.position.set(Math.sin(rotation) * 0.9, 2.15, 0.34)
    fan.rotation.z = rotation
    grille.add(fan)
  })
  window.add(grille)
  return window
}

function createWorkbench(): { group: THREE.Group; top: THREE.Mesh } {
  const group = new THREE.Group()
  group.name = 'central-workbench'
  const top = box([5.7, 0.28, 1.75], wood)
  top.position.set(0, 0.7, 0)
  group.add(top)

  ;[-2.35, 2.35].forEach((x) => {
    const cabinet = box([0.95, 1.45, 1.4], darkWood)
    cabinet.position.set(x, -0.12, 0)
    group.add(cabinet)
    ;[0.3, -0.08, -0.46].forEach((y) => {
      const drawer = box([0.77, 0.27, 0.08], wood)
      drawer.position.set(x, y, 0.75)
      const handle = box([0.28, 0.045, 0.07], iron)
      handle.position.set(x, y, 0.82)
      group.add(drawer, handle)
    })
  })
  const stretcher = box([3.8, 0.16, 0.22], darkWood)
  stretcher.position.set(0, -0.55, -0.35)
  group.add(stretcher)
  return { group, top }
}

function createWorkshopTools(): THREE.Group {
  const tools = new THREE.Group()
  tools.name = 'workshop-tools'

  const drillBase = box([1.15, 0.18, 0.85], iron)
  drillBase.position.set(-4.6, -2.68, -1.75)
  const drillColumn = box([0.18, 1.65, 0.18], steel)
  drillColumn.position.set(-4.6, -1.78, -1.95)
  const drillHead = box([0.9, 0.48, 0.62], iron)
  drillHead.position.set(-4.38, -1.05, -1.8)
  const drillBit = box([0.07, 0.62, 0.07], steel)
  drillBit.position.set(-4.18, -1.58, -1.65)
  tools.add(drillBase, drillColumn, drillHead, drillBit)

  const grinderBase = box([1.3, 0.22, 0.75], iron)
  grinderBase.position.set(4.45, -2.7, -1.7)
  const motor = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.34, 1.15, 12), steel)
  motor.rotation.z = Math.PI / 2
  motor.position.set(4.45, -2.28, -1.65)
  motor.castShadow = true
  const wheelGeometry = new THREE.CylinderGeometry(0.48, 0.48, 0.1, 16)
  ;[-0.66, 0.66].forEach((offset) => {
    const wheel = new THREE.Mesh(wheelGeometry, iron)
    wheel.rotation.z = Math.PI / 2
    wheel.position.set(4.45 + offset, -2.28, -1.65)
    wheel.castShadow = true
    tools.add(wheel)
  })
  tools.add(grinderBase, motor)

  const pegboard = box([2.1, 2.3, 0.12], darkWood)
  pegboard.position.set(-4.6, 1.8, -3.95)
  tools.add(pegboard)
  ;[-5.25, -4.65, -4.05].forEach((x, index) => {
    const hangingTool = box([0.09, 0.85 + index * 0.12, 0.08], steel)
    hangingTool.position.set(x, 1.8, -3.82)
    hangingTool.rotation.z = index === 1 ? 0.15 : -0.12
    tools.add(hangingTool)
  })
  return tools
}

export function createWorkshop(): WorkshopContent {
  const root = new THREE.Group()
  root.name = 'puerto-nuevo-workshop'
  const eyewear: THREE.Group[] = []
  const shelves: THREE.Mesh[] = []

  const floor = new THREE.Mesh(new THREE.PlaneGeometry(24, 18), tile)
  floor.rotation.x = -Math.PI / 2
  floor.position.y = -3.25
  floor.receiveShadow = true
  root.add(floor)
  const grid = new THREE.GridHelper(24, 24, grout.color, grout.color)
  grid.position.y = -3.235
  const gridMaterials = Array.isArray(grid.material) ? grid.material : [grid.material]
  gridMaterials.forEach((material) => { material.transparent = true; material.opacity = 0.26 })
  root.add(grid)

  const backWall = new THREE.Mesh(new THREE.PlaneGeometry(18, 10.5), plaster)
  backWall.position.set(0, 1.7, -4.5)
  backWall.receiveShadow = true
  root.add(backWall)
  const leftReturn = box([0.3, 10.5, 5], plasterShade)
  leftReturn.position.set(-9, 1.7, -2.1)
  const rightReturn = leftReturn.clone()
  rightReturn.position.x = 9
  root.add(leftReturn, rightReturn)

  const window = createArchedWindow()
  window.position.set(0, 1.35, -4.34)
  root.add(window)

  const bench = createWorkbench()
  bench.group.position.set(0, -2.95, -1.65)
  root.add(bench.group)

  const shelfMaterial = wood
  products.forEach((product) => {
    const shelf = box([2.3, 0.12, 0.8], shelfMaterial)
    shelf.name = `product-shelf-${product.id}`
    root.add(shelf)
    shelves.push(shelf)

    const display = createEyewearDisplay(product)
    root.add(display)
    eyewear.push(display)
  })

  const leftUnit = new THREE.Group()
  leftUnit.name = 'left-shelving'
  ;[-5.75, -3.05].forEach((x) => {
    const upright = box([0.16, 6.4, 0.85], darkWood)
    upright.position.set(x, 0, -3.35)
    leftUnit.add(upright)
  })
  const rightUnit = leftUnit.clone()
  rightUnit.name = 'right-shelving'
  rightUnit.position.x = 8.6
  root.add(leftUnit, rightUnit, createWorkshopTools())

  return { root, eyewear, shelves, floor, backWall, workbench: bench.group }
}
