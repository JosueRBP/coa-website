import { commerceConfig, getConfigurationIssue } from './commerceConfig'
import type { GraphQLResponse, ShopifyConfig } from './types'

export class ShopifyClient {
  private readonly config: ShopifyConfig
  constructor(config: ShopifyConfig = commerceConfig) { this.config = config }

  get configurationIssue(): string | null { return getConfigurationIssue(this.config) }

  async request<T>(query: string, variables: Record<string, unknown>): Promise<T> {
    const issue = this.configurationIssue
    if (issue) throw new Error(issue)
    const headers: Record<string, string> = { 'Content-Type': 'application/json' }
    if (this.config.storefrontAccessToken) headers['X-Shopify-Storefront-Access-Token'] = this.config.storefrontAccessToken

    const response = await fetch(`https://${this.config.storeDomain}/api/${this.config.apiVersion}/graphql.json`, {
      method: 'POST', headers, body: JSON.stringify({ query, variables }),
    })
    if (!response.ok) throw new Error(`Storefront request failed (${response.status}).`)
    const payload = await response.json() as GraphQLResponse<T>
    if (payload.errors?.length) throw new Error(payload.errors.map((error) => error.message).join(' '))
    if (!payload.data) throw new Error('Shopify returned no data.')
    return payload.data
  }
}
