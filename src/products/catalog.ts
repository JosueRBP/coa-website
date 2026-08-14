export interface Product {
  id: string
  name: string
  subtitle: string
  price: number
  reservationPrice: number
  shortDescription: string
  longDescription: string
  edition: string
  dimensions: string
  material: string
  hinge: string
  madeIn: string
  leadTime: string
  gallery: string[]
  shopify: { productId: string | null; variantId: string | null }
}

const names = ['Brisa', 'Santurce', 'Miramar', 'Ventana 1960', 'Loíza', 'Coamo', 'Borinquen', 'Solimar', 'Puerto Nuevo']
const materials = ['Olive acetate', 'Smoke crystal', 'Dark mahogany acetate', 'Tortoise acetate', 'Sea-glass acetate', 'Honey crystal', 'Oxidized bronze', 'Black acetate', 'Café crystal']

export const products: Product[] = names.map((name, index) => {
  const id = String(index + 1).padStart(2, '0')
  const material = materials[index] ?? 'Italian acetate'
  return {
    id,
    name,
    subtitle: material,
    price: 1200,
    reservationPrice: 200,
    shortDescription: 'A measured silhouette shaped for tropical light and everyday ritual.',
    longDescription: 'Cut, finished, and adjusted by hand in small editions. Each frame carries subtle variations that reveal the work of its maker.',
    edition: `${String(index + 3).padStart(2, '0')} / 100`,
    dimensions: index % 2 === 0 ? '48 — 21 — 145 mm' : '50 — 20 — 145 mm',
    material,
    hinge: 'Five-barrel German hinge',
    madeIn: 'Puerto Nuevo, Puerto Rico',
    leadTime: '6–8 weeks',
    gallery: [`placeholder-${id}-front`, `placeholder-${id}-detail`],
    shopify: { productId: null, variantId: null },
  }
})

export function getProduct(id: string): Product | undefined {
  return products.find((product) => product.id === id)
}
