import type { PositionInfo } from 'types/positions'

export enum OperationType {
  // Position operations
  Open = 'open',
  Increase = 'increase',
  Decrease = 'decrease',
  Close = 'close',
  TakeProfit = 'takeprofit',
  StopLoss = 'stoploss',

  // Pool operations
  Deposit = 'deposit',
  Withdraw = 'withdraw',
}

const OPERATION_TYPE_SET = new Set<string>(Object.values(OperationType))

/**
 * Normalize env/user input: trim + lowercase, then validate against OperationType values.
 */
export function parseOperationType(raw: string): OperationType {
  const key = raw.trim().toLowerCase()
  if (!OPERATION_TYPE_SET.has(key)) {
    throw new Error(`Unknown operation type: ${raw}`)
  }
  return key as OperationType
}

export interface PositionOperationParams {
  // Common params
  marketAddress: string
  isLong?: boolean
  collateralTokenAddress?: string

  // Open/Increase params
  payTokenAddress?: string
  payAmount?: string
  sizeAmount?: string
  leverage?: string

  // Decrease params
  decreasePercentage?: string

  // TakeProfit/StopLoss params
  profitPercentage?: string
  lossPercentage?: string

  // Order type params
  // For limit orders: provide triggerPrice (price at which order should execute)
  // If triggerPrice is provided, order will be LimitIncrease/LimitDecrease
  // If not provided, order will be MarketIncrease/MarketDecrease
  triggerPrice?: string // Trigger price for limit orders (human-readable USD price, parsed to 30 decimals)
  triggerPricePercent?: string // Trigger price as percentage of current market price (e.g., "0.95" = 95% of current price, "-0.05" = 5% below current price)

  // Options
  skipSimulation?: boolean
  allowedSlippageBps?: number
}

export interface PoolOperationParams {
  // Common params
  marketAddress: string

  // Deposit params
  longTokenAmount?: string
  shortTokenAmount?: string
  longTokenAddress?: string
  shortTokenAddress?: string

  // Withdraw params
  marketTokenAmount?: string
  minLongTokenAmount?: string
  minShortTokenAmount?: string

  // Options (deposit / withdraw: if omitted or blank, receiver defaults to the SDK signing account)
  receiver?: string
}

export type OperationParams = PositionOperationParams | PoolOperationParams

export interface OperationResult {
  txHash: string
  orderKey?: string
  position?: PositionInfo
  depositOrderKey?: string
  withdrawOrderKey?: string
}
