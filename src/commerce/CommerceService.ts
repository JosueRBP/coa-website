import type { Product } from '../products/catalog'
import { CartService } from './CartService'
import type { CheckoutResult, CommerceAction } from './types'

export class CommerceService {
  private readonly carts: CartService
  constructor(carts = new CartService()) { this.carts = carts }

  reserveProduct(product: Product): Promise<CheckoutResult> { return this.checkout('reserve', product) }
  purchaseProduct(product: Product): Promise<CheckoutResult> { return this.checkout('acquire', product) }

  private checkout(action: CommerceAction, product: Product): Promise<CheckoutResult> {
    const merchandiseId = action === 'reserve' ? product.shopify.reservationMerchandiseId : product.shopify.purchaseMerchandiseId
    if (!merchandiseId) return Promise.resolve({ ok: false, kind: 'merchandise', message: `Shopify checkout is not configured yet. Product ${product.id} has no ${action} merchandise ID.` })
    return this.carts.createCheckout(merchandiseId)
  }
}

export const commerceService = new CommerceService()
