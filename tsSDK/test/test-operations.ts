/**
 * Unified Operations Test
 *
 * This test demonstrates how to use the unified operations module
 * for executing position and pool operations.
 *
 * Usage:
 *   Set environment variables:
 *     - ACCOUNT_ADDRESS: Your account address
 *     - PRIVATE_KEY: Your private key (required for signing transactions)
 *     - OPERATION_TYPE: Operation type (open, increase, decrease, close, takeprofit, stoploss, deposit, withdraw; case-insensitive, e.g. stopLoss → stoploss)
 *     - MARKET_ADDRESS: Market address to trade (required)
 *
 *   Position operation variables:
 *     - IS_LONG: "true" for long, "false" for short (optional, default: "true")
 *     - COLLATERAL_TOKEN_ADDRESS: Collateral token address (optional)
 *     - PAY_TOKEN_ADDRESS: Token to pay with (optional)
 *     - PAY_AMOUNT: Amount to pay in collateral token (optional, default: "10")
 *     - SIZE_AMOUNT: Position size in USD (optional, default: "100")
 *     - LEVERAGE: Leverage multiplier (optional, default: "5" = 5x)
 *     - DECREASE_PERCENTAGE: Percentage to decrease position (optional, default: "0.5" = 50%)
 *     - PROFIT_PERCENTAGE: Profit percentage for take profit (optional, default: "5" = 5%)
 *     - LOSS_PERCENTAGE: Loss percentage for stop loss (optional, default: "3" = 3%)
 *     - TRIGGER_PRICE: Trigger price for limit orders (optional, absolute USD price; internally parsed to 30 decimals)
 *     - TRIGGER_PRICE_PERCENT: Trigger price as percentage of current market price (optional, e.g., "0.95" = 95%, "-0.05" = 5% below)
 *
 *   Pool operation variables:
 *     - CEUR_DEPOSIT_AMOUNT: Long token deposit amount (optional)
 *     - USDC_DEPOSIT_AMOUNT: Short token deposit amount (optional)
 *     - WITHDRAWAL_AMOUNT: Market token amount to withdraw (required for withdraw)
 *     - RECEIVER_ADDRESS: LP deposit / withdrawal receiver (optional for deposit: defaults to ACCOUNT_ADDRESS, then SDK account)
 *
 *   Then run:
 *     npx tsx test/test-operations.ts
 */

import { parseOperationType } from '../src/modules/operations'
import { initSdk, logTransaction } from './test-config'

async function main() {
  const operationType = parseOperationType(
    process.env.OPERATION_TYPE || 'open'
  )

  console.log('\n' + '='.repeat(80))
  console.log(`🚀 Executing Operation: ${operationType.toUpperCase()}`)
  console.log('='.repeat(80) + '\n')

  // Initialize SDK
  const sdk = initSdk('celo')
  const account = sdk.account

  console.log('📋 Configuration:')
  console.log(`   Chain ID: ${sdk.chainId}`)
  console.log(`   Account: ${account}`)
  console.log(`   Operation Type: ${operationType}`)
  console.log('')

  // Validate required parameters
  const marketAddress = process.env.MARKET_ADDRESS
  if (!marketAddress) {
    throw new Error('MARKET_ADDRESS environment variable is required')
  }

  // Determine if it's a position or pool operation
  const isPositionOp = [
    'open',
    'increase',
    'decrease',
    'close',
    'takeprofit',
    'stoploss',
  ].includes(operationType)

  const receiverEnv = process.env.RECEIVER_ADDRESS?.trim()
  const accountAddressEnv = process.env.ACCOUNT_ADDRESS?.trim()

  try {
    // Execute operation
    const result = await sdk.operations.executeOperation(
      operationType,
      isPositionOp
        ? {
            // Position operation params
            marketAddress,
            isLong: process.env.IS_LONG !== 'false',
            collateralTokenAddress: process.env.COLLATERAL_TOKEN_ADDRESS,
            payTokenAddress: process.env.PAY_TOKEN_ADDRESS,
            payAmount: process.env.PAY_AMOUNT,
            sizeAmount: process.env.SIZE_AMOUNT,
            leverage: process.env.LEVERAGE,
            decreasePercentage: process.env.DECREASE_PERCENTAGE,
            profitPercentage: process.env.PROFIT_PERCENTAGE,
            lossPercentage: process.env.LOSS_PERCENTAGE,
            triggerPrice: process.env.TRIGGER_PRICE, // For limit orders (absolute price)
            triggerPricePercent: process.env.TRIGGER_PRICE_PERCENT, // For limit orders (percentage of current price)
            skipSimulation: true,
            allowedSlippageBps: 100,
          }
        : {
            // Pool operation params
            marketAddress,
            longTokenAmount:
              process.env.CEUR_DEPOSIT_AMOUNT || process.env.LONG_TOKEN_AMOUNT,
            shortTokenAmount:
              process.env.USDC_DEPOSIT_AMOUNT || process.env.SHORT_TOKEN_AMOUNT,
            marketTokenAmount:
              process.env.WITHDRAWAL_AMOUNT || process.env.MARKET_TOKEN_AMOUNT,
            receiver:
              operationType === 'deposit'
                ? receiverEnv || accountAddressEnv
                : receiverEnv,
          },
    )

    // Log transaction
    logTransaction(result.txHash, sdk.chainId)

    console.log('\n✅ Operation completed successfully!')
    console.log(`   Transaction Hash: ${result.txHash}`)
    if (result.position) {
      console.log(`   Position Size: ${result.position.sizeInUsd} USD`)
    }
    console.log('\n💡 Note: The order will be executed by a keeper.')

    process.exit(0)
  } catch (error) {
    console.error('\n❌ Operation failed:')
    console.error(error.message || error)
    if (error.stack) {
      console.error(error.stack)
    }
    process.exit(1)
  }
}

// Run the test
main()
