export interface Product {
  id: string; name: string; subtitle: string; price: number; reservationPrice: number
  shortDescription: string; longDescription: string; edition: string; dimensions: string
  material: string; hinge: string; madeIn: string; leadTime: string; gallery: string[]
  shopify: { purchaseMerchandiseId: string | null; reservationMerchandiseId: string | null }
  model: { scale: number; rotation: readonly [number, number, number]; focusScale: number; focusRotation: readonly [number, number, number] }
}

const names = ['Brisa', 'Santurce', 'Miramar', 'Ventana 1960', 'Loíza', 'Coamo', 'Borinquen', 'Solimar', 'Puerto Nuevo']
const materials = ['Acetato oliva', 'Cristal humo', 'Acetato caoba', 'Tortoise shell', 'Acetato sea-glass', 'Cristal miel', 'Bronce oxidado', 'Acetato negro', 'Cristal café']
const stories = [
  'Una silueta ligera inspirada por la brisa que atraviesa las galerías de la isla.',
  'Líneas urbanas y seguras, dibujadas desde el ritmo cultural de Santurce.',
  'Proporciones serenas que recuerdan balcones, sombra y horizonte en Miramar.',
  'Inspirada en las rejas florales de las casas de Puerto Nuevo.',
  'Color tropical contenido en una montura precisa de edición limitada.',
  'Una forma honesta y equilibrada, pulida lentamente por manos expertas.',
  'Carácter antillano y construcción robusta para el ritual cotidiano.',
  'Una montura luminosa pensada para el sol del Caribe.',
  'La pieza que reúne arquitectura residencial, oficio y memoria de barrio.',
]

export const products: Product[] = names.map((name, index) => {
  const id = String(index + 1).padStart(2, '0'); const material = materials[index] ?? 'Acetato italiano'
  return { id, name, subtitle: material, price: 1200, reservationPrice: 200, shortDescription: stories[index] ?? stories[0]!, longDescription: 'Cortada, terminada y ajustada a mano en pequeñas ediciones. Cada montura conserva las variaciones sutiles del trabajo de su artesano.', edition: `${String(index + 3).padStart(2, '0')} / 100`, dimensions: index % 2 === 0 ? '48 — 21 — 145 mm' : '50 — 20 — 145 mm', material, hinge: 'Bisagra alemana de cinco barriles', madeIn: 'Puerto Nuevo, Puerto Rico', leadTime: '6–8 semanas', gallery: [`placeholder-${id}-front`, `placeholder-${id}-detail`], shopify: { purchaseMerchandiseId: null, reservationMerchandiseId: null }, model: { scale: 1, rotation: [0, 0, 0], focusScale: 1.45, focusRotation: [-0.08, 0, 0] } }
})

export function getProduct(id: string): Product | undefined { return products.find((product) => product.id === id) }
