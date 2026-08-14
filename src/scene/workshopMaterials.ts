import * as THREE from 'three'

function standard(color: number, roughness: number, metalness = 0): THREE.MeshStandardMaterial {
  return new THREE.MeshStandardMaterial({ color, roughness, metalness })
}

export const workshopMaterials = {
  plaster: standard(0xddd8cc, 0.92),
  plasterVariation: standard(0xcfc8ba, 0.96),
  plasterTrim: standard(0xeee8da, 0.84),
  mediumWood: standard(0x765139, 0.63),
  mediumWoodLight: standard(0x8b6345, 0.68),
  darkWood: standard(0x493329, 0.72),
  agedMetal: standard(0x363b39, 0.48, 0.62),
  paintedIron: standard(0xb7b8ae, 0.54, 0.46),
  machineMetal: standard(0x6c7775, 0.33, 0.72),
  machinePaint: standard(0x53605c, 0.56, 0.38),
  ceramicCream: standard(0xbeb7a8, 0.82),
  ceramicBlue: standard(0x738d8a, 0.78),
  ceramicRose: standard(0x9d7367, 0.8),
  grout: standard(0x6d6b65, 1),
  displaySurface: standard(0x5e422f, 0.58),
  glass: new THREE.MeshPhysicalMaterial({
    color: 0xc5dada,
    transparent: true,
    opacity: 0.22,
    roughness: 0.12,
    transmission: 0.35,
    thickness: 0.04,
    metalness: 0,
  }),
  sky: new THREE.MeshBasicMaterial({ color: 0xc9dedd }),
  facadeCoral: standard(0xc98576, 0.88),
  facadeAqua: standard(0x83aaa4, 0.86),
  facadeCream: standard(0xded1b7, 0.9),
  exteriorTrim: standard(0xf1eadb, 0.82),
  exteriorShadow: standard(0x506d70, 0.78),
}

