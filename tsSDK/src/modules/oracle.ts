import fetch from 'cross-fetch'
import { MarketSdkConfig } from 'types/markets'
import { buildUrl } from 'utils/buildUrl'

import type { UpdownSdk } from '../index'

export type TickersResponse = {
  minPrice: string
  maxPrice: string
  oracleDecimals: number
  tokenSymbol: string
  tokenAddress: string
  updatedAt: number
}[]

type RawTokenResponse = {
  symbol: string
  address: string
  decimals: number
  synthetic: boolean
}

export type TokensResponse = (Omit<RawTokenResponse, 'synthetic'> & {
  isSynthetic: boolean
})[]

export class Oracle {
  private url: string

  constructor(public sdk: UpdownSdk) {
    this.url = sdk.config.oracleUrl
  }

  getMarkets(): Promise<MarketSdkConfig[]> {
    return fetch(buildUrl(this.url!, '/markets'))
      .then((res) => {
        if (!res.ok) {
          console.warn(
            `Oracle API error: ${res.status} ${res.statusText}, falling back to chain data`,
          )
          return { markets: [] }
        }
        return res.json()
      })
      .then((res) => {
        if (!res.markets || !res.markets.length) {
          console.warn(
            `Invalid markets response from Oracle API, falling back to chain data`,
          )
          return []
        }

        return res.markets
      })
      .catch((error) => {
        console.warn(
          `Failed to fetch markets from Oracle API: ${error.message}, falling back to chain data`,
        )
        return []
      })
  }

  getTokens(): Promise<TokensResponse> {
    return fetch(buildUrl(this.url!, '/tokens'))
      .then((res) => res.json())
      .then((res: { tokens: RawTokenResponse[] }) =>
        res.tokens.map(({ synthetic, ...rest }) => {
          return {
            ...rest,
            isSynthetic: synthetic,
          }
        }),
      )
  }

  getTickers(): Promise<TickersResponse> {
    // Derive tickers endpoint from configured oracleUrl so users can override it.
    // Example: oracleUrl="https://api.perpex.ai/prices/" -> "https://api.perpex.ai/prices/tickers"
    const tickersUrl = buildUrl(this.url!, '/tickers')
    return fetch(tickersUrl)
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Tickers API error: ${res.status} ${res.statusText}`)
        }
        return res.json()
      })
      .then((res) => {
        if (!res || !Array.isArray(res) || !res.length) {
          throw new Error(`Invalid tickers response: ${JSON.stringify(res)}`)
        }

        return res
      })
      .catch((error) => {
        console.warn(`Failed to fetch tickers: ${error.message}`)
        throw error
      })
  }
}
