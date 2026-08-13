export interface Product { id: string; name: string }

export const products: Product[] = Array.from({ length: 9 }, (_, index) => ({
  id: String(index + 1).padStart(2, '0'),
  name: `Frame ${String(index + 1).padStart(2, '0')}`,
}))
