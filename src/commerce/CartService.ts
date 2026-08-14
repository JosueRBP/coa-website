import { ShopifyClient } from './ShopifyClient'
import type { CheckoutResult } from './types'

interface CartCreateData {
  cartCreate: {
    cart: { id: string; checkoutUrl: string } | null
    userErrors: Array<{ field: string[] | null; message: string }>
  }
}

const CART_CREATE = `
  mutation CartCreate($input: CartInput!) {
    cartCreate(input: $input) {
      cart { id checkoutUrl }
      userErrors { field message }
    }
  }
`

export class CartService {
  private readonly client: ShopifyClient
  constructor(client = new ShopifyClient()) { this.client = client }

  async createCheckout(merchandiseId: string): Promise<CheckoutResult> {
    if (this.client.configurationIssue) return { ok: false, kind: 'configuration', message: 'Shopify checkout is not configured yet.' }
    try {
      const data = await this.client.request<CartCreateData>(CART_CREATE, {
        input: { lines: [{ merchandiseId, quantity: 1 }] },
      })
      const errors = data.cartCreate.userErrors
      if (errors.length) return { ok: false, kind: 'api', message: errors.map((error) => error.message).join(' ') }
      const checkoutUrl = data.cartCreate.cart?.checkoutUrl
      if (!checkoutUrl) return { ok: false, kind: 'api', message: 'Shopify did not return a checkout URL.' }
      return { ok: true, checkoutUrl }
    } catch {
      return { ok: false, kind: 'api', message: 'Checkout could not be prepared. Please try again.' }
    }
  }

  // Future cartLinesAdd/cartLinesUpdate/cartLinesRemove methods belong here.
}
