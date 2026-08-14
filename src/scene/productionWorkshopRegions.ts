import * as THREE from 'three'
import { workshopMaterials as materials } from './workshopMaterials'
import { createProductionGrille } from './productionGrille'

function box(size: readonly [number, number, number], material: THREE.Material, shadows = true): THREE.Mesh {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(...size), material)
  mesh.castShadow = shadows; mesh.receiveShadow = shadows
  return mesh
}

function contact(size: readonly [number, number], x: number, y: number, z: number, rotationX = -Math.PI / 2): THREE.Mesh {
  const shadow = new THREE.Mesh(new THREE.PlaneGeometry(...size), materials.contactShadow)
  shadow.position.set(x, y, z); shadow.rotation.x = rotationX; shadow.renderOrder = 1
  shadow.raycast = () => undefined
  return shadow
}

function latheHandle(x: number, y: number, z: number): THREE.Group {
  const handle = new THREE.Group()
  const mount = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.16, 8), materials.agedMetal)
  mount.rotation.x = Math.PI / 2
  const grip = box([0.32, 0.055, 0.06], materials.agedMetal)
  grip.position.z = 0.1
  handle.position.set(x, y, z)
  handle.add(mount, grip)
  return handle
}

export function createProductionWorkbench(): { root: THREE.Group; top: THREE.Mesh } {
  const root = new THREE.Group(); root.name = 'PN_Main_Workbench_ProceduralProduction'
  const top = box([5.8, 0.32, 1.82], materials.woodWorkbench); top.position.y = 0.72; root.add(top)
  const apron = box([5.45, 0.28, 0.18], materials.woodAgedDetail); apron.position.set(0, 0.43, 0.75); root.add(apron)
  ;[-2.34, 2.34].forEach((x, cabinetIndex) => {
    const cabinet = box([1.08, 1.5, 1.46], cabinetIndex ? materials.woodAgedDetail : materials.woodCabinet); cabinet.position.set(x, -0.08, 0); root.add(cabinet)
    ;[0.36, -0.02, -0.4].forEach((y, drawerIndex) => {
      const face = box([0.88, 0.29, 0.09], drawerIndex === 1 ? materials.woodWorkbench : materials.woodCabinet); face.position.set(x, y, 0.78); root.add(face, latheHandle(x, y, 0.87))
    })
  })
  ;[-2.72, -1.92, 1.92, 2.72].forEach((x) => { const leg = box([0.22, 1.72, 0.3], materials.woodAgedDetail); leg.position.set(x, -0.18, -0.42); root.add(leg) })
  const stretcher = box([3.65, 0.18, 0.24], materials.woodAgedDetail); stretcher.position.set(0, -0.68, -0.48); root.add(stretcher)
  const centralMat = box([2.45, 0.025, 0.9], materials.displaySurface, false); centralMat.position.set(0, 0.9, 0); root.add(centralMat)
  const ruler = box([1.35, .018, .075], materials.hardwareMetal, false); ruler.position.set(-1.72, .905, .42); ruler.rotation.y = -.12; root.add(ruler)
  const fileGeometry = new THREE.BoxGeometry(.045, .035, .72)
  ;[-.48, -.22, .18].forEach((x, index) => { const file = new THREE.Mesh(fileGeometry, index === 1 ? materials.agedSteel : materials.hardwareMetal); file.position.set(x, .93, .08 + index * .11); file.rotation.y = -.18 + index * .15; file.castShadow = true; root.add(file) })
  const cup = new THREE.Mesh(new THREE.CylinderGeometry(.12,.1,.3,12,1,true), materials.machineryPaint); cup.position.set(1.82,1.03,-.2); cup.castShadow = true; root.add(cup)
  const blankGeometry = new THREE.TorusGeometry(.18,.026,6,18)
  ;[-.22,.22].forEach((x) => { const blank = new THREE.Mesh(blankGeometry, materials.woodAgedDetail); blank.scale.y = .68; blank.position.set(1.35 + x,.93,.22); blank.rotation.x = Math.PI / 2; blank.castShadow = true; root.add(blank) })
  const lensGeometry = new THREE.CylinderGeometry(.16,.16,.018,20)
  ;[-.18,.18].forEach((x) => { const lens = new THREE.Mesh(lensGeometry, materials.glass); lens.position.set(-1.15 + x,.93,-.12); lens.castShadow = true; root.add(lens) })
  const hardwareGeometry = new THREE.CylinderGeometry(.018,.018,.045,6)
  const hardware = new THREE.InstancedMesh(hardwareGeometry, materials.hardwareMetal, 12); const hardwareMatrix = new THREE.Matrix4()
  for (let index = 0; index < 12; index += 1) { hardwareMatrix.makeTranslation(.58 + (index % 4) * .09, .93, -.3 + Math.floor(index / 4) * .08); hardware.setMatrixAt(index, hardwareMatrix) }
  hardware.castShadow = true; hardware.raycast = () => undefined; root.add(hardware)
  const wornEdge = box([3.2,.012,.035], materials.woodAgedDetail, false); wornEdge.position.set(0,.89,.91); root.add(wornEdge)
  root.add(contact([5.9, 1.65], 0, -0.285, 0))
  return { root, top }
}

export function createProductionArchitecture(): { shell: THREE.Group; floor: THREE.Group; window: THREE.Group; grille: THREE.Group; exterior: THREE.Group; backWall: THREE.Mesh; floorBase: THREE.Mesh } {
  const shell = new THREE.Group(); shell.name = 'PN_Workshop_Architecture_ProceduralProduction'
  const leftWall = box([6.55, 10.5, 0.42], materials.plaster); leftWall.position.set(-5.72, 1.7, -4.5)
  const rightWall = leftWall.clone(); rightWall.position.x = 5.72
  const upperWall = box([4.9, 2.4, 0.42], materials.plasterVariation); upperWall.position.set(0, 5.75, -4.5)
  const lowerWall = box([4.9, 0.75, 0.42], materials.plaster); lowerWall.position.set(0, -2.88, -4.5)
  const leftReturn = box([0.38, 10.5, 5.2], materials.plasterVariation); leftReturn.position.set(-9, 1.7, -2.1)
  const rightReturn = leftReturn.clone(); rightReturn.position.x = 9
  const baseboard = box([17.7, 0.22, 0.15], materials.plasterTrim); baseboard.position.set(0, -3.08, -4.18)
  shell.add(leftWall, rightWall, upperWall, lowerWall, leftReturn, rightReturn, baseboard)

  const floor = new THREE.Group(); floor.name = 'PN_Tiled_Floor_ProceduralProduction'
  const floorBase = new THREE.Mesh(new THREE.PlaneGeometry(24, 18), materials.grout); floorBase.rotation.x = -Math.PI / 2; floorBase.position.y = -3.25; floorBase.receiveShadow = true; floor.add(floorBase)
  const tileGeometry = new THREE.BoxGeometry(0.955, 0.045, 0.955)
  for (let row = 0; row < 10; row += 1) for (let column = 0; column < 18; column += 1) {
    const pattern = (row * 7 + column * 3) % 23
    const tileMaterial = pattern === 0 || pattern === 11 ? materials.ceramicBlue : pattern === 7 ? materials.ceramicRose : pattern === 15 ? materials.ceramicNeutral : materials.ceramicCream
    const tile = new THREE.Mesh(tileGeometry, tileMaterial); tile.position.set(column - 8.5, -3.21, row - 2.5); tile.receiveShadow = true; floor.add(tile)
  }

  const window = new THREE.Group(); window.name = 'PN_Arched_Window_ProceduralProduction'; window.position.set(0, 1.35, -4.34)
  const exterior = createProductionExterior(); window.add(exterior)
  const openingShape = new THREE.Shape(); openingShape.moveTo(-2.25, -2.3); openingShape.lineTo(2.25, -2.3); openingShape.lineTo(2.25, 1.35); openingShape.absarc(0, 1.35, 2.25, 0, Math.PI, false); openingShape.lineTo(-2.25, -2.3)
  const sky = new THREE.Mesh(new THREE.ShapeGeometry(openingShape, 32), materials.sky); sky.position.z = -1.7; window.add(sky)
  const recess = materials.plasterTrim
  ;[-2.42, 2.42].forEach((x) => { const jamb = box([0.28, 3.8, 0.72], recess); jamb.position.set(x, -0.43, 0.02); window.add(jamb) })
  const sill = box([5.12, 0.3, 0.82], recess); sill.position.set(0, -2.42, 0.16); window.add(sill)
  const sillContact = contact([4.72, 0.24], 0, -2.255, 0.48, 0); sillContact.material = materials.contactShadow; window.add(sillContact)
  const archPoints = Array.from({ length: 21 }, (_, index) => { const angle = Math.PI - Math.PI * index / 20; return new THREE.Vector3(Math.cos(angle) * 2.42, 1.35 + Math.sin(angle) * 2.42, 0.06) })
  const arch = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(archPoints), 40, 0.14, 7, false), recess); arch.castShadow = true; window.add(arch)
  const grille = createProductionGrille().root; window.add(grille)
  const glass = new THREE.Mesh(new THREE.ShapeGeometry(openingShape, 32), materials.glass); glass.position.z = 0.18; window.add(glass)
  return { shell, floor, window, grille, exterior, backWall: leftWall, floorBase }
}

export function createProductionTools(): THREE.Group {
  const tools = new THREE.Group(); tools.name = 'PN_Machinery_ProceduralProduction'
  const drillBase = box([1.2, 0.2, 0.9], materials.agedMetal); drillBase.position.set(-4.6, -2.68, -1.75)
  const column = new THREE.Mesh(new THREE.CylinderGeometry(0.11, 0.13, 1.8, 10), materials.machineMetal); column.position.set(-4.6, -1.7, -1.95); column.castShadow = true
  const head = box([0.95, 0.52, 0.68], materials.machinePaint); head.position.set(-4.38, -0.93, -1.83)
  const pulley = new THREE.Mesh(new THREE.CylinderGeometry(0.26, 0.26, 0.12, 12), materials.agedMetal); pulley.rotation.z = Math.PI / 2; pulley.position.set(-4.82, -0.9, -1.82)
  const table = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 0.11, 16), materials.machineMetal); table.position.set(-4.35, -1.72, -1.7)
  const bit = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.012, 0.64, 7), materials.machineMetal); bit.position.set(-4.15, -1.46, -1.62)
  tools.add(drillBase, column, head, pulley, table, bit)

  const grinderBase = box([1.5, 0.22, 0.82], materials.agedMetal); grinderBase.position.set(4.45, -2.7, -1.7)
  const motor = new THREE.Mesh(new THREE.CylinderGeometry(0.36, 0.36, 1.2, 16), materials.machinePaint); motor.rotation.z = Math.PI / 2; motor.position.set(4.45, -2.25, -1.65); motor.castShadow = true; tools.add(grinderBase, motor)
  ;[-0.7, 0.7].forEach((offset) => { const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 0.12, 18), materials.agedMetal); wheel.rotation.z = Math.PI / 2; wheel.position.set(4.45 + offset, -2.25, -1.65); wheel.castShadow = true; tools.add(wheel) })

  const board = box([2.2, 2.35, 0.13], materials.woodAgedDetail); board.position.set(-4.65, 1.8, -3.93); tools.add(board)
  const handleMaterial = materials.mediumWoodLight
  ;[-5.3, -4.85, -4.4, -3.95].forEach((x, index) => {
    const steel = box([0.055, 0.72 + index * 0.09, 0.045], materials.machineMetal); steel.position.set(x, 1.95, -3.82)
    const handle = box([0.12, 0.34, 0.08], handleMaterial); handle.position.set(x, 1.35, -3.79); tools.add(steel, handle)
  })
  ;[-1.9, -1.45, 1.55].forEach((x) => { const clamp = new THREE.Mesh(new THREE.TorusGeometry(0.22, 0.04, 6, 14, Math.PI * 1.45), materials.agedMetal); clamp.position.set(x, -2.03, -0.7); clamp.rotation.x = Math.PI / 2; tools.add(clamp) })
  tools.add(contact([1.45, 1.05], -4.55, -3.19, -1.78), contact([1.75, 1], 4.45, -3.19, -1.72))
  return tools
}

export function createProductionForeground(): THREE.Group {
  const root = new THREE.Group(); root.name = 'PN_Foreground_Props_ProceduralProduction'
  const left = box([4.2, 0.36, 2.9], materials.woodAgedDetail); left.position.set(-7.35, -2.52, 4.15); left.rotation.y = 0.14
  const right = box([3.7, 0.34, 2.6], materials.woodCabinet); right.position.set(7.45, -2.48, 4.45); right.rotation.y = -0.16; root.add(left, right)
  const mat = box([1.65, 0.035, 1.1], materials.machinePaint, false); mat.position.set(-6.65, -2.3, 3.8); root.add(mat)
  const tray = box([1.75, 0.1, 0.92], materials.machineMetal); tray.position.set(6.95, -2.22, 4.12); root.add(tray)
  ;[-0.52, 0, 0.52].forEach((offset, index) => { const tool = box([0.07, 0.055, 1.02], index === 1 ? materials.agedMetal : materials.machineMetal); tool.position.set(6.95 + offset, -2.12, 4.1); tool.rotation.y = (index - 1) * 0.16; root.add(tool) })
  ;[-6.9, -6.45].forEach((x) => { const blank = new THREE.Mesh(new THREE.TorusGeometry(0.24, 0.035, 6, 18), materials.displaySurface); blank.scale.y = 0.65; blank.position.set(x, -2.24, 3.65); blank.rotation.x = Math.PI / 2; root.add(blank) })
  return root
}

export function createProductionExterior(): THREE.Group {
  const root = new THREE.Group(); root.name = 'PN_Window_Exterior_ProceduralProduction'
  const facadeData = [
    { x: -1.55, y: -1.25, z: -0.42, w: 1.75, h: 2.2, material: materials.facadeCoral },
    { x: 0.05, y: -1.55, z: -0.58, w: 1.7, h: 1.65, material: materials.facadeCream },
    { x: 1.65, y: -1.05, z: -0.76, w: 1.9, h: 2.55, material: materials.facadeAqua },
  ]
  facadeData.forEach(({ x, y, z, w, h, material }, index) => {
    const facade = box([w, h, 0.12], material, false); facade.position.set(x, y, z); root.add(facade)
    ;[-0.32, 0.32].forEach((offset) => {
      const recess = box([0.4, 0.58, 0.07], materials.exteriorShadow, false); recess.position.set(x + offset, y + 0.2, z + 0.075)
      const trim = box([0.34, 0.52, 0.045], materials.exteriorTrim, false); trim.position.set(x + offset, y + 0.2, z + 0.12)
      const opening = box([0.24, 0.42, 0.05], materials.exteriorShadow, false); opening.position.set(x + offset, y + 0.2, z + 0.15); root.add(recess, trim, opening)
    })
    if (index !== 1) {
      const balcony = box([w * .76,.08,.34], materials.paintedIron, false); balcony.position.set(x,y-.18,z+.28); root.add(balcony)
      const railGeometry = new THREE.BoxGeometry(.025,.42,.025)
      for (let rail = -2; rail <= 2; rail += 1) { const bar = new THREE.Mesh(railGeometry, materials.paintedIron); bar.position.set(x + rail * w * .075, y + .05, z + .47); root.add(bar) }
      const topRail = box([w * .46,.025,.025], materials.paintedIron, false); topRail.position.set(x,y+.25,z+.47); root.add(topRail)
    }
  })
  const middle = box([2.25,2.1,.09], materials.facadeAqua, false); middle.position.set(-2.15,.05,-1.05); root.add(middle)
  const middleRoof = box([2.5,.12,.2], materials.exteriorTrim, false); middleRoof.position.set(-2.15,1.13,-.99); root.add(middleRoof)
  const distant = box([5.2,3.5,.08], materials.facadeCream, false); distant.position.set(-.2,.15,-1.45); distant.scale.set(1.15,1,1); root.add(distant)
  ;[-2.25,-.85,.75,2.05].forEach((x,index) => { const silhouette = box([.72 + (index % 2) * .2,1.1 + (index % 3) * .35,.05], index % 2 ? materials.facadeAqua : materials.facadeCream, false); silhouette.position.set(x,1.55 + (index % 3) * .1,-1.25 - index * .08); root.add(silhouette) })
  return root
}
