import * as THREE from 'three'

type TextureKind = 'plaster' | 'wood' | 'metal' | 'ceramic'

function seededNoise(x: number, y: number, seed: number): number {
  const value = Math.sin(x * 12.9898 + y * 78.233 + seed * 37.719) * 43758.5453
  return value - Math.floor(value)
}

function proceduralTexture(kind: TextureKind, base: THREE.Color, seed: number): THREE.CanvasTexture {
  const size = 128
  const canvas = document.createElement('canvas')
  canvas.width = size; canvas.height = size
  const context = canvas.getContext('2d')!
  const image = context.createImageData(size, size)
  for (let y = 0; y < size; y += 1) for (let x = 0; x < size; x += 1) {
    const index = (y * size + x) * 4
    const noise = seededNoise(x, y, seed) - 0.5
    const broad = Math.sin((kind === 'wood' ? y : x + y) * 0.075 + seed) * 0.5
    const grain = kind === 'wood' ? Math.sin(y * 0.7 + noise * 5) * 0.5 : 0
    const strength = kind === 'plaster' ? noise * 0.045 + broad * 0.018
      : kind === 'wood' ? noise * 0.05 + broad * 0.07 + grain * 0.025
        : kind === 'metal' ? noise * 0.035 : noise * 0.025 + broad * 0.012
    image.data[index] = THREE.MathUtils.clamp((base.r + strength) * 255, 0, 255)
    image.data[index + 1] = THREE.MathUtils.clamp((base.g + strength) * 255, 0, 255)
    image.data[index + 2] = THREE.MathUtils.clamp((base.b + strength) * 255, 0, 255)
    image.data[index + 3] = 255
  }
  context.putImageData(image, 0, 0)
  const texture = new THREE.CanvasTexture(canvas)
  texture.colorSpace = THREE.SRGBColorSpace
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping
  texture.anisotropy = 4
  texture.repeat.set(kind === 'wood' ? 1.2 : 3, kind === 'wood' ? 3.8 : 3)
  return texture
}

function standard(name: string, color: number, roughness: number, metalness = 0, kind?: TextureKind, seed = 1): THREE.MeshStandardMaterial {
  const material = new THREE.MeshStandardMaterial({ color, roughness, metalness })
  material.name = name
  if (kind) {
    material.map = proceduralTexture(kind, new THREE.Color(color), seed)
    material.color.set(0xffffff)
    material.userData.textureSlots = { map: null, normalMap: null, roughnessMap: null }
  }
  return material
}

const contactShadow = new THREE.MeshBasicMaterial({ color: 0x211c18, transparent: true, opacity: 0.14, depthWrite: false })
contactShadow.name = 'contactShadow'

export const workshopMaterials = {
  plaster: standard('plasterWarmLimestone', 0xd9d4c8, 0.94, 0, 'plaster', 2),
  plasterVariation: standard('plasterAgedVariation', 0xcac4b8, 0.96, 0, 'plaster', 8),
  plasterTrim: standard('plasterWindowTrim', 0xe8e2d5, 0.87, 0, 'plaster', 13),
  woodWorkbench: standard('woodWorkbench', 0x805638, 0.62, 0, 'wood', 3),
  woodShelf: standard('woodShelf', 0x68452f, 0.7, 0, 'wood', 7),
  woodCabinet: standard('woodCabinet', 0x54392c, 0.76, 0, 'wood', 11),
  woodAgedDetail: standard('woodAgedDetail', 0x3f3028, 0.82, 0, 'wood', 17),
  mediumWood: standard('woodCabinetSecondary', 0x765139, 0.72, 0, 'wood', 5),
  mediumWoodLight: standard('woodWorkbenchLight', 0x8b6345, 0.65, 0, 'wood', 3),
  darkWood: standard('woodAgedDark', 0x493329, 0.79, 0, 'wood', 17),
  paintedIron: standard('paintedIron', 0x343a38, 0.56, 0.5, 'metal', 4),
  darkSteel: standard('darkSteel', 0x292e2d, 0.42, 0.75, 'metal', 9),
  agedSteel: standard('agedSteel', 0x505552, 0.58, 0.62, 'metal', 14),
  machineryPaint: standard('machineryPaint', 0x53645f, 0.57, 0.32, 'metal', 20),
  hardwareMetal: standard('hardwareMetal', 0x777b76, 0.34, 0.82, 'metal', 25),
  agedMetal: standard('agedSteelLegacy', 0x414643, 0.58, 0.62, 'metal', 14),
  machineMetal: standard('hardwareMetalLegacy', 0x6c7775, 0.36, 0.76, 'metal', 25),
  machinePaint: standard('machineryPaintLegacy', 0x53605c, 0.57, 0.35, 'metal', 20),
  ceramicCream: standard('tileCream', 0xbdb7aa, 0.78, 0, 'ceramic', 2),
  ceramicBlue: standard('tileMutedAqua', 0x718b87, 0.8, 0, 'ceramic', 4),
  ceramicRose: standard('tileMutedCoral', 0x98736a, 0.82, 0, 'ceramic', 6),
  ceramicNeutral: standard('tileNeutral', 0xa7a096, 0.84, 0, 'ceramic', 8),
  grout: standard('tileGrout', 0x77746d, 1),
  displaySurface: standard('woodShelfLegacy', 0x5e422f, 0.7, 0, 'wood', 7),
  contactShadow,
  glass: new THREE.MeshPhysicalMaterial({
    name: 'windowGlass', color: 0xd8e6e2, transparent: true, opacity: 0.12,
    roughness: 0.18, transmission: 0.82, thickness: 0.025, metalness: 0,
    depthWrite: false, side: THREE.DoubleSide,
  }),
  sky: new THREE.MeshBasicMaterial({ color: 0xd8e8e8, toneMapped: false }),
  facadeCoral: standard('facadeCoral', 0xc58172, 0.9, 0, 'plaster', 21),
  facadeAqua: standard('facadeAqua', 0x79a49e, 0.88, 0, 'plaster', 22),
  facadeCream: standard('facadeCream', 0xdacdb5, 0.92, 0, 'plaster', 23),
  exteriorTrim: standard('exteriorTrim', 0xeee8da, 0.84, 0, 'plaster', 24),
  exteriorShadow: standard('exteriorOpening', 0x3e5b5d, 0.82),
  exteriorStreet: standard('exteriorStreet', 0x7f817b, 0.96, 0, 'ceramic', 28),
  exteriorFoliage: standard('exteriorFoliage', 0x536d55, 0.88, 0, 'plaster', 29),
}
