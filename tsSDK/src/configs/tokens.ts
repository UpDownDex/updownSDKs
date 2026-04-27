import type { Token, TokenAddressTypesMap, TokenCategory } from 'types/tokens'
import { zeroAddress } from 'viem'

import {
  ARBITRUM,
  ARBITRUM_SEPOLIA,
  AVALANCHE,
  AVALANCHE_FUJI,
  BOTANIX,
  CELO,
} from './chains'
import { getContract } from './contracts'

export const NATIVE_TOKEN_ADDRESS = zeroAddress

export const TOKENS: { [chainId: number]: Token[] } = {
  [CELO]: [
    {
      name: 'Wrapped USDT',
      symbol: 'USDT',
      decimals: 6,
      priceDecimals: 5,
      address: '0xd96a1ac57a180a3819633bCE3dC602Bd8972f595',
      categories: ['layer2', 'defi'],
      imageUrl: 'https://api.crosschainx.io/images/coins/USDT(BSC).png',
      coingeckoUrl: 'https://www.coingecko.com/en/coins/usd-coin',
      explorerUrl:
        'https://celoscan.io/address/0xd96a1ac57a180a3819633bce3dc602bd8972f595',
      isPermitSupported: true,
      contractVersion: '1',
      isStable: true,
    },
    {
      name: 'Celo native asset',
      symbol: 'CELO(Native)',
      decimals: 18,
      address: zeroAddress,
      isNative: true,
      isShortable: true,
      categories: ['layer2'],
      imageUrl:
        'https://assets.coingecko.com/coins/images/279/small/ethereum.png?1595348880',
      coingeckoUrl: 'https://www.coingecko.com/en/coins/ethereum',
      //isV1Available: true,
      isPermitSupported: true,
      priceDecimals: 4,
    },
    {
      name: 'Celo native asset',
      symbol: 'CELO',
      decimals: 18,
      address: '0x471EcE3750Da237f93B8E339c536989b8978a438',
      isWrapped: true,
      baseSymbol: 'CELO',
      isShortable: true,
      categories: ['layer2'],
      imageUrl:
        'https://assets.coingecko.com/coins/images/279/small/ethereum.png?1595348880',
      coingeckoUrl: 'https://www.coingecko.com/en/coins/ethereum',
      //isV1Available: true,
      isPermitSupported: true,
      priceDecimals: 4,
    },
    {
      name: 'Wrapped CELO',
      symbol: 'CELO',
      assetSymbol: 'CELO',
      baseSymbol: 'CELO',
      decimals: 18,
      address: '0x5B1B6DCB4E907b9755E27Db88bD62B9750a13C60',
      isShortable: true,
      imageUrl:
        'https://assets.coingecko.com/coins/images/2518/thumb/weth.png?1628852295',
      coingeckoUrl: 'https://www.coingecko.com/en/coins/ethereum',
      //isV1Available: true,
      isPermitSupported: true,
      contractVersion: '1',
      isStable: false,
      priceDecimals: 4,
    },
    {
      name: 'Wrapped ETH',
      symbol: 'ETH',
      assetSymbol: 'ETH',
      baseSymbol: 'ETH',
      decimals: 18,
      address: '0x4C2675e9067Cd7Fc859165AC5F37f1D82d825A1E',
      isShortable: true,
      imageUrl:
        'https://assets.coingecko.com/coins/images/2518/thumb/weth.png?1628852295',
      coingeckoUrl: 'https://www.coingecko.com/en/coins/ethereum',
      //isV1Available: true,
      isPermitSupported: true,
      contractVersion: '1',
      isStable: false,
      priceDecimals: 4,
    },
    {
      name: 'Wrapped BTC',
      symbol: 'BTC',
      assetSymbol: 'BTC',
      baseSymbol: 'BTC',
      decimals: 8,
      address: '0x57433eD8eC1FAD60b8E1dcFdD1fBD56aBA19C04C',
      isShortable: true,
      categories: ['layer2'],
      imageUrl:
        'https://assets.coingecko.com/coins/images/26115/thumb/btcb.png?1655921693',
      coingeckoUrl: 'https://www.coingecko.com/en/coins/wrapped-bitcoin',
      explorerUrl:
        'https://celoscan.io/address/0x57433eD8eC1FAD60b8E1dcFdD1fBD56aBA19C04C',
      //isV1Available: true,
      isPermitSupported: true,
      contractVersion: '1',
      isStable: false,
    },
    {
      name: 'Wrapped EURm',
      symbol: 'EURm',
      assetSymbol: 'EURm',
      baseSymbol: 'EURm',
      decimals: 18,
      address: '0x2350246BAE36EE301B108cA8fE58D795A8DBdb4e',
      isShortable: true,
      categories: ['layer2'],
      imageUrl:
        'https://assets.coingecko.com/coins/images/26115/thumb/btcb.png?1655921693',
      coingeckoUrl: 'https://www.coingecko.com/en/coins/wrapped-bitcoin',
      explorerUrl:
        'https://celoscan.io/address/0x2350246bae36ee301b108ca8fe58d795a8dbdb4e',
      isPermitSupported: true,
      contractVersion: '1',
      isStable: false,
      priceDecimals: 3,
    },
    {
      name: 'Wrapped JPYm',
      symbol: 'JPYm',
      assetSymbol: 'JPYm',
      baseSymbol: 'JPYm',
      decimals: 18,
      address: '0x29206D4B6183A29Ef5B68494B0850330e98f27F4',
      isShortable: true,
      categories: ['layer2'],
      imageUrl:
        'https://assets.coingecko.com/coins/images/26115/thumb/btcb.png?1655921693',
      coingeckoUrl: 'https://www.coingecko.com/en/coins/wrapped-bitcoin',
      explorerUrl:
        'https://celoscan.io/address/0x29206d4b6183a29ef5b68494b0850330e98f27f4',
      isPermitSupported: true,
      contractVersion: '1',
      isStable: false,
      priceDecimals: 6,
    },
    {
      name: 'Wrapped NGNm',
      symbol: 'NGNm',
      assetSymbol: 'NGNm',
      baseSymbol: 'NGNm',
      decimals: 18,
      address: '0xEb8A6C14e625A05F06eA914Db627dd65175b4505',
      isShortable: true,
      categories: ['layer2'],
      imageUrl:
        'https://assets.coingecko.com/coins/images/26115/thumb/btcb.png?1655921693',
      coingeckoUrl: 'https://www.coingecko.com/en/coins/wrapped-bitcoin',
      explorerUrl:
        'https://celoscan.io/address/0xeb8a6c14e625a05f06ea914db627dd65175b4505',
      isPermitSupported: true,
      contractVersion: '1',
      isStable: false,
      priceDecimals: 6,
    },
    {
      name: 'Wrapped AUDm',
      symbol: 'AUDm',
      assetSymbol: 'AUDm',
      baseSymbol: 'AUDm',
      decimals: 18,
      address: '0x91CA0318Fc30D728640f0E6329205eE1F538F17B',
      isShortable: true,
      categories: ['layer2'],
      imageUrl:
        'https://assets.coingecko.com/coins/images/26115/thumb/btcb.png?1655921693',
      coingeckoUrl: 'https://www.coingecko.com/en/coins/wrapped-bitcoin',
      explorerUrl:
        'https://celoscan.io/address/0x91ca0318fc30d728640f0e6329205ee1f538f17b',
      isPermitSupported: true,
      contractVersion: '1',
      isStable: false,
      priceDecimals: 6,
    },
    {
      name: 'Wrapped GBPm',
      symbol: 'GBPm',
      assetSymbol: 'GBPm',
      baseSymbol: 'GBPm',
      decimals: 18,
      address: '0x7Ef503a2722cdfa7E99f2A59771f7E2390c2DF76',
      isShortable: true,
      categories: ['layer2'],
      imageUrl:
        'https://assets.coingecko.com/coins/images/26115/thumb/btcb.png?1655921693',
      coingeckoUrl: 'https://www.coingecko.com/en/coins/wrapped-bitcoin',
      explorerUrl:
        'https://celoscan.io/address/0x7ef503a2722cdfa7e99f2a59771f7e2390c2df76',
      isPermitSupported: true,
      contractVersion: '1',
      isStable: false,
      priceDecimals: 6,
    },
    {
      name: 'Wrapped XAUT',
      symbol: 'XAUT',
      assetSymbol: 'XAUT',
      baseSymbol: 'XAUT',
      decimals: 18,
      address: '0xdffa5c533eb195625D15C34A82f5822C35f4EC2B',
      isShortable: true,
      categories: ['layer2'],
      imageUrl:
        'https://assets.coingecko.com/coins/images/26115/thumb/btcb.png?1655921693',
      coingeckoUrl: 'https://www.coingecko.com/en/coins/wrapped-bitcoin',
      explorerUrl:
        'https://celoscan.io/address/0x7ef503a2722cdfa7e99f2a59771f7e2390c2df76',
      isPermitSupported: true,
      contractVersion: '1',
      isStable: false,
      priceDecimals: 6,
    },
    /** Placeholder tokens */
    {
      name: 'PX Market tokens',
      symbol: 'PX',
      address: '<market-token-address>',
      decimals: 18,
      imageUrl:
        'https://raw.githubusercontent.com/perpex/gmx-assets/main/GMX-Assets/PNG/PX_LOGO.png',
      isPlatformToken: true,
    },
  ],
}

export const TOKEN_COLOR_MAP = {
  ETH: '#6062a6',
  BTC: '#F7931A',
  WBTC: '#F7931A',
  PBTC: '#F7931A',
  USDC: '#2775CA',
  'USDC.E': '#2A5ADA',
  USDT: '#67B18A',
  MIM: '#9695F8',
  FRAX: '#000',
  DAI: '#FAC044',
  UNI: '#E9167C',
  AVAX: '#E84142',
  LINK: '#3256D6',
  DOGE: '#BA9F2F',
  SOL: '#38cbc1',
  ARB: '#162c4f',
  NEAR: '#07eb98',
  BNB: '#efb90b',
  ATOM: '#6f7390',
  XRP: '#23292f',
  LTC: '#16182e',
  OP: '#ff0421',
  DOT: '#e6007a',
  tBTC: '#000000',
  TEST: '#2d3ed7',
  SHIB: '#f00601',
  STX: '#eb6230',
  ORDI: '#000000',
  MATIC: '#6f41d8',
  EIGEN: '#1A0C6D',
  SATS: '#F7931A',
  default: '#6062a6',
}

export const TOKENS_MAP: {
  [chainId: number]: { [address: string]: Token }
} = {}
export const V1_TOKENS: { [chainId: number]: Token[] } = {}
export const V2_TOKENS: { [chainId: number]: Token[] } = {}
export const SYNTHETIC_TOKENS: { [chainId: number]: Token[] } = {}
export const TOKENS_BY_SYMBOL_MAP: {
  [chainId: number]: { [symbol: string]: Token }
} = {}
export const WRAPPED_TOKENS_MAP: { [chainId: number]: Token } = {}
export const NATIVE_TOKENS_MAP: { [chainId: number]: Token } = {}

const CHAIN_IDS = [
  ARBITRUM,
  CELO,
  AVALANCHE,
  AVALANCHE_FUJI,
  BOTANIX,
  ARBITRUM_SEPOLIA,
]

for (let j = 0; j < CHAIN_IDS.length; j++) {
  const chainId = CHAIN_IDS[j]

  TOKENS_MAP[chainId] = {}
  TOKENS_BY_SYMBOL_MAP[chainId] = {}
  SYNTHETIC_TOKENS[chainId] = []
  V1_TOKENS[chainId] = []
  V2_TOKENS[chainId] = []

  const tokens = TOKENS[chainId] ?? []
  let wrappedTokenAddress: string | undefined

  for (let i = 0; i < tokens.length; i++) {
    const token = tokens[i]
    // Store tokens by both original and lowercased address so lookups
    // work even when upstream sources (e.g. tickers) return lowercase.
    TOKENS_MAP[chainId][token.address] = token
    if (typeof token.address === 'string') {
      TOKENS_MAP[chainId][token.address.toLowerCase()] = token
    }
    TOKENS_BY_SYMBOL_MAP[chainId][token.symbol] = token

    if (token.isWrapped) {
      WRAPPED_TOKENS_MAP[chainId] = token
      wrappedTokenAddress = token.address
    }

    if (token.isNative) {
      NATIVE_TOKENS_MAP[chainId] = token
    }

    if (token.isV1Available && !token.isTempHidden) {
      V1_TOKENS[chainId].push(token)
    }

    if (
      (!token.isPlatformToken ||
        (token.isPlatformToken && token.isPlatformTradingToken)) &&
      !token.isTempHidden
    ) {
      V2_TOKENS[chainId].push(token)
    }

    if (token.isSynthetic) {
      SYNTHETIC_TOKENS[chainId].push(token)
    }
  }

  if (NATIVE_TOKENS_MAP[chainId]) {
    NATIVE_TOKENS_MAP[chainId].wrappedAddress = wrappedTokenAddress
  }
}

export function getSyntheticTokens(chainId: number) {
  return SYNTHETIC_TOKENS[chainId]
}

export function getWrappedToken(chainId: number) {
  return WRAPPED_TOKENS_MAP[chainId]
}

export function getNativeToken(chainId: number) {
  return NATIVE_TOKENS_MAP[chainId]
}

export function getTokens(chainId: number) {
  return TOKENS[chainId]
}

export function getV1Tokens(chainId: number) {
  return V1_TOKENS[chainId]
}

export function getV2Tokens(chainId: number) {
  return V2_TOKENS[chainId]
}

export function getTokensMap(chainId: number) {
  return TOKENS_MAP[chainId]
}

export function getWhitelistedV1Tokens(chainId: number) {
  return getV1Tokens(chainId)
}

export function getVisibleV1Tokens(chainId: number) {
  return getV1Tokens(chainId).filter((token) => !token.isWrapped)
}

export function isValidToken(chainId: number, address: string) {
  if (!TOKENS_MAP[chainId]) {
    throw new Error(`Incorrect chainId ${chainId}`)
  }
  return (
    address in TOKENS_MAP[chainId] ||
    address.toLowerCase() in TOKENS_MAP[chainId]
  )
}

export function isValidTokenSafe(chainId: number, address: string) {
  return (
    address in TOKENS_MAP[chainId] ||
    address.toLowerCase() in TOKENS_MAP[chainId]
  )
}

export function getToken(chainId: number, address: string) {
  // FIXME APE_deprecated token which is not in use but can be displayed
  if (
    chainId === ARBITRUM &&
    address === '0x74885b4D524d497261259B38900f54e6dbAd2210'
  ) {
    return getTokenBySymbol(chainId, 'APE')
  }

  if (!TOKENS_MAP[chainId]) {
    throw new Error(`Incorrect chainId ${chainId}`)
  }
  const token =
    TOKENS_MAP[chainId][address] ?? TOKENS_MAP[chainId][address.toLowerCase()]
  if (!token) {
    throw new Error(`Incorrect address "${address}" for chainId ${chainId}`)
  }

  return token
}

export function getTokenBySymbol(
  chainId: number,
  symbol: string,
  {
    isSynthetic,
    version,
    symbolType = 'symbol',
  }: {
    isSynthetic?: boolean
    version?: 'v1' | 'v2'
    symbolType?: 'symbol' | 'baseSymbol'
  } = {},
) {
  let tokens = Object.values(TOKENS_MAP[chainId])

  if (version) {
    tokens = version === 'v1' ? getV1Tokens(chainId) : getV2Tokens(chainId)
  }

  let token: Token | undefined

  if (isSynthetic !== undefined) {
    token = tokens.find((token) => {
      return (
        token[symbolType]?.toLowerCase() === symbol.toLowerCase() &&
        Boolean(token.isSynthetic) === isSynthetic
      )
    })
  } else {
    if (symbolType === 'symbol' && TOKENS_BY_SYMBOL_MAP[chainId][symbol]) {
      token = TOKENS_BY_SYMBOL_MAP[chainId][symbol]
    } else {
      token = tokens.find(
        (token) => token[symbolType]?.toLowerCase() === symbol.toLowerCase(),
      )
    }
  }

  if (!token) {
    throw new Error(`Incorrect symbol "${symbol}" for chainId ${chainId}`)
  }

  return token
}

export function convertTokenAddress<
  T extends keyof TokenAddressTypesMap,
  R extends TokenAddressTypesMap[T]
>(chainId: number, address: string, convertTo?: T): R {
  const wrappedToken = getWrappedToken(chainId)

  if (convertTo === 'wrapped' && address === NATIVE_TOKEN_ADDRESS) {
    return wrappedToken.address as R
  }

  if (convertTo === 'native' && address === wrappedToken.address) {
    return NATIVE_TOKEN_ADDRESS as R
  }

  return address as R
}

export function getNormalizedTokenSymbol(tokenSymbol: string) {
  if (['WBTC', 'WETH', 'WAVAX'].includes(tokenSymbol)) {
    return tokenSymbol.substr(1)
  } else if (['PBTC', 'STBTC'].includes(tokenSymbol)) {
    return 'BTC'
  } else if (tokenSymbol.includes('.')) {
    return tokenSymbol.split('.')[0]
  }
  return tokenSymbol
}

export function isChartAvailableForToken(chainId: number, tokenSymbol: string) {
  let token

  try {
    token = getTokenBySymbol(chainId, tokenSymbol)
  } catch (e) {
    return false
  }

  if (
    token.isChartDisabled ||
    (token.isPlatformToken && !token.isPlatformTradingToken)
  )
    return false

  return true
}

export function getPriceDecimals(chainId: number, tokenSymbol?: string) {
  if (!tokenSymbol) return 2

  try {
    const token = getTokenBySymbol(chainId, tokenSymbol)
    return token.priceDecimals ?? 2
  } catch (e) {
    return 2
  }
}

export function getTokenBySymbolSafe(
  chainId: number,
  symbol: string,
  params: Parameters<typeof getTokenBySymbol>[2] = {},
) {
  try {
    return getTokenBySymbol(chainId, symbol, params)
  } catch (e) {
    return
  }
}

export function isTokenInList(token: Token, tokenList: Token[]): boolean {
  return tokenList.some((t) => t.address === token.address)
}

export function isSimilarToken(tokenA: Token, tokenB: Token) {
  if (tokenA.address === tokenB.address) {
    return true
  }

  if (
    tokenA.symbol === tokenB.symbol ||
    tokenA.baseSymbol === tokenB.symbol ||
    tokenA.symbol === tokenB.baseSymbol
  ) {
    return true
  }

  return false
}

export function getTokenVisualMultiplier(token: Token): string {
  return token.visualPrefix || token.visualMultiplier?.toString() || ''
}

export function getStableTokens(chainId: number) {
  return getTokens(chainId).filter((t) => t.isStable)
}

export function getCategoryTokenAddresses(
  chainId: number,
  category: TokenCategory,
) {
  return TOKENS[chainId]
    .filter((token) => token.categories?.includes(category))
    .map((token) => token.address)
}

export const createTokensMap = (tokens: Token[]) => {
  return tokens.reduce((acc, token) => {
    acc[token.address] = token
    return acc
  }, {} as Record<string, Token>)
}
