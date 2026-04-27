/**
 * Query helper script (markets / orders / positions).
 *
 * Run:
 *   npx tsx test/test-query.ts
 *
 * Env (see test/test-config.ts):
 *   ACCOUNT_ADDRESS (required)
 *   PRIVATE_KEY      (optional; only needed for sending tx)
 *   CELO_RPC_URL / ARBITRUM_RPC_URL (optional)
 *   ORACLE_URL (optional, e.g. "https://api.perpex.ai/prices/")
 *
 * Optional:
 *   CHAIN=celo|arbitrum  (default: celo)
 *   MARKET_ADDRESS     — if set, prints LP (GM) balance for this market
 *   ACCOUNT_ADDRESS    — optional for LP; defaults to SDK account (same as .env ACCOUNT_ADDRESS)
 */

import { abis } from '../src/abis/index'
import type { MarketInfo, MarketsInfoData } from '../src/types/markets'
import { initSdk } from './test-config'
import type { Address } from 'viem'
import { formatUnits } from 'viem'

function getMarketInfoByAddress(
  marketsInfoData: MarketsInfoData | undefined,
  marketAddress: string
): MarketInfo | undefined {
  if (!marketsInfoData) return undefined
  const lower = marketAddress.trim().toLowerCase()
  const key = Object.keys(marketsInfoData).find(
    (k) => k.toLowerCase() === lower
  )
  return key ? marketsInfoData[key] : undefined
}

function selectChain(): 'celo' | 'arbitrum' {
  const raw = (process.env.CHAIN || 'celo').toLowerCase()
  return raw === 'arbitrum' ? 'arbitrum' : 'celo'
}

async function main() {
  const chain = selectChain()
  const sdk = initSdk(chain)

  console.log('\n' + '='.repeat(80))
  console.log(`🔎 Querying SDK state (chain=${chain}, chainId=${sdk.chainId})`)
  console.log(`   account=${sdk.account}`)
  console.log('='.repeat(80) + '\n')

  // 1) Markets list (from local config; then marketInfo requires prices + multicalls)
  const { marketsAddresses, marketsData } = await sdk.markets.getMarkets()

  console.log(`📈 Markets (${marketsAddresses?.length ?? 0})`)
  for (const marketAddress of marketsAddresses || []) {
    const m = marketsData?.[marketAddress]
    console.log(
      `- ${marketAddress}  ${m?.name ?? ''}  ` +
        `(index=${m?.indexTokenAddress ?? ''} long=${
          m?.longTokenAddress ?? ''
        } short=${m?.shortTokenAddress ?? ''})`,
    )
  }
  console.log('')

  // 2) Fetch marketInfo + tokensData once; needed for orders parsing and most position helpers
  const {
    marketsInfoData,
    tokensData,
    pricesUpdatedAt,
  } = await sdk.markets.getMarketsInfo()
  // console.log(
  //   `💱 Prices: updatedAt=${
  //     pricesUpdatedAt ? new Date(pricesUpdatedAt).toISOString() : 'unknown'
  //   } ` +
  //     `(marketsInfoData=${
  //       Object.keys(marketsInfoData || {}).length
  //     }, tokensData=${Object.keys(tokensData || {}).length})`,
  // )
  console.log('')

  // 2b) LP (GM) balance for MARKET_ADDRESS + account (ACCOUNT_ADDRESS or sdk.account)
  const marketAddrEnv = process.env.MARKET_ADDRESS?.trim()
  const accountAddrEnv = process.env.ACCOUNT_ADDRESS?.trim()
  const queryAccount = (accountAddrEnv || sdk.account) as Address

  console.log('💰 LP (GM) balance')
  if (!marketAddrEnv) {
    console.log(
      '   (skip: set MARKET_ADDRESS in .env to query market token balance for an account)',
    )
  } else if (!marketsInfoData) {
    console.log('   (skip: marketsInfoData not available)')
  } else {
    const marketInfo = getMarketInfoByAddress(marketsInfoData, marketAddrEnv)
    if (!marketInfo) {
      console.log(
        `   ❌ Market not found in marketsInfoData: ${marketAddrEnv}`,
      )
    } else {
      const lpToken = marketInfo.marketTokenAddress as Address
      const decimals =
        tokensData?.[marketInfo.marketTokenAddress]?.decimals ?? 18
      const raw = (await sdk.publicClient.readContract({
        address: lpToken,
        abi: abis.ERC20 as any,
        functionName: 'balanceOf',
        args: [queryAccount],
      })) as bigint
      const human = formatUnits(raw, decimals)
      console.log(`   market:    ${marketAddrEnv}`)
      console.log(`   LP token:  ${lpToken}`)
      console.log(`   account:   ${queryAccount}`)
      console.log(`   balance:   ${raw.toString()} (${human} GM, decimals=${decimals})`)
    }
  }
  console.log('')

  // 3) Orders (current account)
  if (!marketsInfoData || !tokensData) {
    console.log('🧾 Orders: skipped (missing marketsInfoData/tokensData)')
  } else {
    const { count, ordersInfoData } = await sdk.orders.getOrders({
      marketsInfoData,
      tokensData,
    })

    console.log(`🧾 Orders (${count})`)
    for (const [orderKey, order] of Object.entries(ordersInfoData)) {
      // Keep output robust across SDK type changes.
      const market =
        (order as any).marketAddress ||
        (order as any).marketInfo?.marketTokenAddress
      const orderType = (order as any).orderType
      const isLong = (order as any).isLong
      const sizeUsd = (order as any).sizeDeltaUsd ?? (order as any).sizeInUsd
      console.log(
        `- key=${orderKey} type=${orderType} isLong=${isLong} market=${market} sizeUsd=${String(
          sizeUsd,
        )}`,
      )
    }
  }
  console.log('')

  // 4) Positions (raw positions from chain; does not require prices for fallback path)
  if (!marketsData || !tokensData) {
    console.log('📌 Positions: skipped (missing marketsData/tokensData)')
  } else {
    const { positionsData } = await sdk.positions.getPositions({
      marketsData,
      tokensData,
      start: 0,
      end: 1000,
    })

    const keys = Object.keys(positionsData || {})
    console.log(`📌 Positions (${keys.length})`)
    for (const key of keys) {
      const p = (positionsData as any)[key]
      console.log(
        `- key=${key} market=${p.marketAddress} collateral=${p.collateralTokenAddress} ` +
          `isLong=${p.isLong} sizeUsd=${String(
            p.sizeInUsd,
          )} sizeTokens=${String(p.sizeInTokens)} collateralAmount=${String(
            p.collateralAmount,
          )}`,
      )
    }
  }

  console.log('\n✅ Done.\n')
}

main().catch((e) => {
  console.error('\n❌ Query failed:')
  console.error(e?.stack || e?.message || e)
  process.exit(1)
})
