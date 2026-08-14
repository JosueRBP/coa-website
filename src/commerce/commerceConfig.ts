import type { ShopifyConfig } from './types'

const rawDomain = import.meta.env.VITE_SHOPIFY_STORE_DOMAIN?.trim() ?? ''

export const commerceConfig: ShopifyConfig = {
  storeDomain: rawDomain.replace(/^https?:\/\//, '').replace(/\/$/, ''),
  storefrontAccessToken: import.meta.env.VITE_SHOPIFY_STOREFRONT_ACCESS_TOKEN?.trim() ?? '',
  apiVersion: import.meta.env.VITE_SHOPIFY_API_VERSION?.trim() ?? '',
}

export function getConfigurationIssue(config = commerceConfig): string | null {
  if (!config.storeDomain) return 'Store domain is missing.'
  if (!config.apiVersion) return 'Storefront API version is missing.'
  if (!config.storeDomain.endsWith('.myshopify.com')) return 'Store domain must be a myshopify.com domain.'
  return null
}

