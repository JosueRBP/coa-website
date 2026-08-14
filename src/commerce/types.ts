export type CommerceAction = 'reserve' | 'acquire'
export type PurchaseUIState = 'idle' | 'loading' | 'error'

export interface ShopifyConfig {
  storeDomain: string
  storefrontAccessToken: string
  apiVersion: string
}

export interface GraphQLErrorShape { message: string }

export interface GraphQLResponse<T> {
  data?: T
  errors?: GraphQLErrorShape[]
}

export type CheckoutResult =
  | { ok: true; checkoutUrl: string }
  | { ok: false; kind: 'configuration' | 'merchandise' | 'api'; message: string }

