import { abis } from 'abis'
import { getContract } from 'configs/contracts'
import { convertTokenAddress } from 'configs/tokens'
import { SwapPricingType } from 'types/orders'
import { TokenPrices, TokensData } from 'types/tokens'
import {
  Abi,
  Address,
  decodeErrorResult,
  encodeFunctionData,
  withRetry,
} from 'viem'

import type { UpdownSdk } from '../'
import { extractTxnError } from './errors'
import { convertToContractPrice, getTokenData } from './tokens'

export type PriceOverrides = {
  [address: string]: TokenPrices | undefined
}

class SimulateExecuteOrderError extends Error {
  constructor(message: string, public cause: Error) {
    super(message)
  }
}

type SimulateExecuteParams = {
  createMulticallPayload: string[]
  primaryPriceOverrides: PriceOverrides
  tokensData: TokensData
  value: bigint
  swapPricingType?: SwapPricingType
}

/**
 *
 * @deprecated use simulateExecution instead
 */
export async function simulateExecuteOrder(
  sdk: UpdownSdk,
  p: SimulateExecuteParams,
) {
  const chainId = sdk.chainId
  const client = sdk.publicClient

  const account = sdk.config.account

  if (!account) {
    throw new Error('Account is not defined')
  }

  const multicallAddress = getContract(chainId, 'Multicall')
  const exchangeRouterAddress = getContract(chainId, 'ExchangeRouter')

  const blockTimestamp = await client.readContract({
    address: multicallAddress,
    abi: abis.Multicall as Abi,
    functionName: 'getCurrentBlockTimestamp',
    args: [],
  })

  const blockNumber = await client.getBlockNumber()

  const { primaryTokens, primaryPrices } = getSimulationPrices(
    chainId,
    p.tokensData,
    p.primaryPriceOverrides,
  )
  const priceTimestamp = (blockTimestamp as bigint) + 10n

  const simulationPriceParams = {
    primaryTokens: primaryTokens,
    primaryPrices: primaryPrices,
    minTimestamp: priceTimestamp,
    maxTimestamp: priceTimestamp,
  }

  let simulationPayloadData = [...p.createMulticallPayload]

  const routerAbi = abis.ExchangeRouter as Abi
  const routerAddress = exchangeRouterAddress

  let encodedFunctionData: string

  encodedFunctionData = encodeFunctionData({
    abi: routerAbi,
    functionName: 'simulateExecuteLatestOrder',
    args: [simulationPriceParams],
  })
  simulationPayloadData.push(encodedFunctionData)

  try {
    await withRetry(
      async () => {
        return await client.simulateContract({
          address: routerAddress,
          abi: routerAbi,
          functionName: 'multicall',
          args: [simulationPayloadData],
          value: p.value,
          account: account as Address,
          blockNumber,
        })
      },
      {
        retryCount: 2,
        delay: 200,
        shouldRetry: (error) => {
          const [message] = extractTxnError(error)
          return (
            message
              ?.toLocaleLowerCase()
              ?.includes('unsupported block number') ?? false
          )
        },
      },
    )
  } catch (txnError) {
    let msg: string | undefined = undefined
    try {
      const errorData =
        extractDataFromError(txnError?.info?.error?.message) ??
        extractDataFromError(txnError?.message)

      const error = new SimulateExecuteOrderError(
        'No data found in error.',
        txnError,
      )

      if (!errorData) throw error

      // Check if errorData is long enough (at least 4 bytes for error selector)
      // Error selector is 4 bytes = 8 hex characters, plus "0x" prefix = 10 characters
      if (typeof errorData === 'string' && errorData.length < 10) {
        throw error
      }

      try {
        const decodedError = decodeErrorResult<typeof abis.CustomErrors>({
          abi: abis.CustomErrors,
          data: errorData as Address,
        })

        const isSimulationPassed =
          decodedError.errorName === 'EndOfOracleSimulation'

        if (isSimulationPassed) {
          return
        }

        const parsedArgs = Object.keys(decodedError.args ?? {}).reduce(
          (acc, k) => {
            const args = ((decodedError.args ?? {}) as unknown) as Record<
              string,
              any
            >
            // Skip numeric keys (array indices)
            if (!Number.isNaN(Number(k))) {
              return acc
            }
            acc[k] = args[k]?.toString()
            return acc
          },
          {} as Record<string, string>,
        )

        msg = `${
          txnError?.info?.error?.message ??
          decodedError.errorName ??
          txnError?.message
        } ${JSON.stringify(parsedArgs, null, 2)}`
      } catch (decodeError) {
        // If decodeErrorResult fails, it means the error data format is unexpected
        // This can happen if the error is not a custom error or the data is malformed
        // In this case, we should throw the original error with a generic message
        throw error
      }
    } catch (parsingError) {
      /* eslint-disable-next-line */
      console.error('Error parsing simulation result:', parsingError)
      // If we can't parse the error, throw the original transaction error
      // This matches the frontend's behavior of showing a generic error message
      msg = `Execute order simulation failed`
      throw new Error(msg)
    }

    throw txnError
  }
}

export function extractDataFromError(errorMessage: unknown) {
  if (typeof errorMessage !== 'string') return null

  const pattern = /Unable to decode signature "([^"]+)"/
  const match = errorMessage.match(pattern)

  if (match && match[1]) {
    return match[1]
  }
  return null
}

function getSimulationPrices(
  chainId: number,
  tokensData: TokensData,
  primaryPricesMap: PriceOverrides,
) {
  const tokenAddresses = Object.keys(tokensData)

  const primaryTokens: string[] = []
  const primaryPrices: { min: bigint; max: bigint }[] = []

  for (const address of tokenAddresses) {
    const token = getTokenData(tokensData, address)
    const convertedAddress = convertTokenAddress(chainId, address, 'wrapped')

    if (!token?.prices || primaryTokens.includes(convertedAddress)) {
      continue
    }

    primaryTokens.push(convertedAddress)

    const currentPrice = {
      min: convertToContractPrice(token.prices.minPrice, token.decimals),
      max: convertToContractPrice(token.prices.maxPrice, token.decimals),
    }

    const primaryOverriddenPrice = primaryPricesMap[address]

    if (primaryOverriddenPrice) {
      primaryPrices.push({
        min: convertToContractPrice(
          primaryOverriddenPrice.minPrice,
          token.decimals,
        ),
        max: convertToContractPrice(
          primaryOverriddenPrice.maxPrice,
          token.decimals,
        ),
      })
    } else {
      primaryPrices.push(currentPrice)
    }
  }

  return {
    primaryTokens,
    primaryPrices,
  }
}
