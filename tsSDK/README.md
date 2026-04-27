# <img src="https://app.updown.xyz/assets/logo_updown_black-Blc0g-YP.svg" width="28" height="28"> Updown SDK

## Install

```bash
yarn add @updown/sdk # or
npm install --save @updown/sdk
```

## Usage

```typescript
import { UpdownSdk } from '@updown/sdk'
import { useWallet } from 'wagmi'

const sdk = new UpdownSdk({
  chainId: 42161,
  rpcUrl: 'https://arb1.arbitrum.io/rpc',
  oracleUrl: 'https://api.perpex.ai/prices/',
  walletClient: useWallet().walletClient,
  subsquidUrl: 'https://graph.perpex.ai/celo/subgraphs',
})

const { marketsInfoData, tokensData } = await sdk.markets.getMarketsInfo()

sdk.setAccount('0x1234567890abcdef1234567890abcdef12345678')

sdk.positions
  .getPositions({
    marketsInfoData,
    tokensData,
    start: 0,
    end: 1000,
  })
  .then((positions) => {
    console.log(positions)
  })
```

## Documentation

### Read methods

### Markets

- `getMarkets(offset?: number, limit?: number): Promise<Market[]>` - returns a list of markets
- `getMarketsInfo(): Promise<{ marketsInfoData: MarketInfoData[], tokensData: TokenData[] }>` - returns a list of markets info and tokens data
- `getDailyVolumes(): Promise<{market: string; volume: bigint}[]>` - returns markets' daily volume data

### Positions

- `getPositions(): Promise<Position[]>` - returns a list of positions

### Tokens

- `getTokensData(): Promise<TokenData[]>` - returns a list of tokens data

### Orders

- `getOrders(): Promise<Order[]>` - returns a list of orders

### Trades

- `getTradeHistory(p: Parameters): Promise<TradeAction[]>` - returns a list of trades

### Write methods

### Operations (Recommended)

The `operations` module provides a unified, high-level interface for executing position and pool operations. This is the recommended way to interact with the SDK for most use cases.

#### Main method:

- `executeOperation(type: OperationType, params: OperationParams): Promise<OperationResult>` - executes any operation (open, increase, decrease, close, takeprofit, stoploss, deposit, withdraw)

**Supported Operations:**

- `OperationType.Open` - Open a new position
- `OperationType.Increase` - Increase an existing position
- `OperationType.Decrease` - Decrease position by percentage
- `OperationType.Close` - Close position completely
- `OperationType.TakeProfit` - Create take profit order
- `OperationType.StopLoss` - Create stop loss order
- `OperationType.Deposit` - Deposit liquidity to pool
- `OperationType.Withdraw` - Withdraw liquidity from pool

**Example:**

```typescript
import { OperationType } from '@updown/sdk'

// Open a position
const result = await sdk.operations.executeOperation(OperationType.Open, {
  marketAddress: '0x...',
  isLong: true,
  payAmount: '10',
  leverage: '5',
})

// Deposit to pool
const depositResult = await sdk.operations.executeOperation(
  OperationType.Deposit,
  {
    marketAddress: '0x...',
    longTokenAmount: '0.01',
    shortTokenAmount: '0.01',
  },
)
```

See [Operations Examples](#operations-examples) for more details.

### Orders (Advanced)

For advanced use cases, you can use the lower-level `orders` module directly.

#### Quick methods:

- `long(p: Parameters)` - creates long positions (see [examples](#helpers))
- `short(p: Parameters)` - creates short positions (see [examples](#helpers))
- `swap(p: Parameters)` - creates a swap order (see [examples](#helpers))

#### Full methods:

- `cancelOrders(orderKeys: string[])` - cancels orders by order keys
- `createIncreaseOrder(p: Parameters)` - creates an increase order (see [examples](#examples))
- `createDecreaseOrder(p: Parameters)` - creates a decrease order (see [examples](#examples))
- `createSwapOrder(p: Parameters)` - creates a swap order (see [examples](#examples))

## Configuration

```typescript
interface UpdownSdkConfig {
  chainId: number
  rpcUrl: string
  oracleUrl: string
  subsquidUrl?: string
  account?: string
  publicClient: PublicClient
  walletClient: WalletClient
  tokens?: Record<string, Partial<Token>>
  markets?: Record<
    string,
    {
      isListed: boolean
    }
  >
}
```

### Custom Viem clients

When using custom Viem clients, pass batching configuration to the client.

```typescript
import { BATCH_CONFIGS } from '@updown/sdk/configs/batch'

const publicClient = createPublicClient({
  ...your_config,
  batch: BATCH_CONFIGS[chainId].client,
})
```

### Urls

- RPC URLs - use preferred RPC URL
- [Actual Oracle URLs](https://api.perpex.ai/prices/)
- [Actual Subsquid/Subgraph URLs](https://graph.perpex.ai/celo/subgraphs) (subgraph url is `synthetics-stats` field)

### Tokens customization

If you need to override some field in tokens, just pass extension object in SDK config:

```typescript
const sdk = new UpdownSdk({
  ...arbitrumSdkConfig,
  tokens: {
    '0x912CE59144191C1204E64559FE8253a0e49E6548': {
      name: 'My Custom Name for ARB',
    },
  },
})
```

Here and further, `name` field in tokens data object will be taken from the extension object.

### Markets customization

To enable/disable market in SDK use config field `markets

```typescript
const sdk = new UpdownSdk({
  ...arbitrumSdkConfig,
  markets: {
    '0x47c031236e19d024b42f8AE6780E44A573170703': {
      isListed: false,
    },
  },
})
```

## Examples

### Operations Examples (Recommended)

The `operations` module provides a simple, unified interface for all operations. It automatically handles market data fetching, position lookup, balance checking, token approval, and transaction sending.

#### Open Position

```typescript
import { OperationType } from '@updown/sdk'

// Open a long position (market order)
const result = await sdk.operations.executeOperation(OperationType.Open, {
  marketAddress: '0x70d95587d40A2caf56bd97485aB3Eec10Bee6336',
  isLong: true,
  payAmount: '10',
  leverage: '5', // 5x leverage
  payTokenAddress: '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1', // WETH
  collateralTokenAddress: '0xaf88d065e77c8cC2239327C5EDb3A432268e5831', // USDC
})

console.log('Transaction hash:', result.txHash)
```

#### Open Position with Limit Order

```typescript
// Open a long position with limit order
const result = await sdk.operations.executeOperation(OperationType.Open, {
  marketAddress: '0x70d95587d40A2caf56bd97485aB3Eec10Bee6336',
  isLong: true,
  payAmount: '10',
  leverage: '5',
  triggerPrice: '50000', // Trigger price for limit order
})
```

#### Increase Position

```typescript
// Increase an existing position
const result = await sdk.operations.executeOperation(OperationType.Increase, {
  marketAddress: '0x70d95587d40A2caf56bd97485aB3Eec10Bee6336',
  isLong: true,
  payAmount: '5',
  leverage: '3',
})
```

#### Decrease Position

```typescript
// Decrease position by 50%
const result = await sdk.operations.executeOperation(OperationType.Decrease, {
  marketAddress: '0x70d95587d40A2caf56bd97485aB3Eec10Bee6336',
  isLong: true,
  decreasePercentage: '0.5', // 50%
})
```

#### Close Position

```typescript
// Close position completely
const result = await sdk.operations.executeOperation(OperationType.Close, {
  marketAddress: '0x70d95587d40A2caf56bd97485aB3Eec10Bee6336',
  isLong: true,
})
```

#### Take Profit Order

```typescript
// Create take profit order (5% profit)
const result = await sdk.operations.executeOperation(OperationType.TakeProfit, {
  marketAddress: '0x70d95587d40A2caf56bd97485aB3Eec10Bee6336',
  isLong: true,
  profitPercentage: '5', // 5% profit
})
```

#### Stop Loss Order

```typescript
// Create stop loss order (3% loss)
const result = await sdk.operations.executeOperation(OperationType.StopLoss, {
  marketAddress: '0x70d95587d40A2caf56bd97485aB3Eec10Bee6336',
  isLong: true,
  lossPercentage: '3', // 3% loss
})
```

#### Deposit to Pool

```typescript
// Deposit liquidity to market pool
const result = await sdk.operations.executeOperation(OperationType.Deposit, {
  marketAddress: '0x70d95587d40A2caf56bd97485aB3Eec10Bee6336',
  longTokenAmount: '0.01',
  shortTokenAmount: '0.01',
})
```

#### Withdraw from Pool

```typescript
// Withdraw liquidity from market pool
const result = await sdk.operations.executeOperation(OperationType.Withdraw, {
  marketAddress: '0x70d95587d40A2caf56bd97485aB3Eec10Bee6336',
  marketTokenAmount: '0.01',
})
```

### Advanced Examples

#### Open long position (using orders module directly)

```typescript
import type { IncreasePositionAmounts } from '@updown/sdk/types/orders'

const { marketsInfoData, tokensData } = await sdk.markets.getMarketsInfo()

if (!marketsInfoData || !tokensData) {
  throw new Error('No markets or tokens info data')
}

const marketInfo = marketsInfo['0x47c031236e19d024b42f8AE6780E44A573170703']
const collateralToken = tokensData['0x912CE59144191C1204E64559FE8253a0e49E6548']
sdk.orders.createIncreaseOrder({
  marketsInfoData: marketsInfoData!,
  tokensData,
  isLimit: false,
  isLong: true,
  marketAddress: marketInfo.marketTokenAddress,
  allowedSlippage: 50,
  collateralToken,
  collateralTokenAddress: collateralToken.address,
  receiveTokenAddress: collateralToken.address,
  fromToken: tokensData['0x912CE59144191C1204E64559FE8253a0e49E6548'],
  marketInfo,
  indexToken: marketInfo.indexToken,
  increaseAmounts: {
    initialCollateralAmount: 3000000n,
    initialCollateralUsd: 2999578868393486100000000000000n,
    collateralDeltaAmount: 2997003n,
    collateralDeltaUsd: 2996582289103961007386100000000n,
    indexTokenAmount: 1919549334876037n,
    sizeDeltaUsd: 5993158579050185227800000000000n,
    sizeDeltaInTokens: 1919536061202302n,
    estimatedLeverage: 20000n,
    indexPrice: 3122169600000000000000000000000000n,
    initialCollateralPrice: 999859622797828700000000000000n,
    collateralPrice: 999859622797828700000000000000n,
    triggerPrice: 0n,
    acceptablePrice: 3122191190655414690893787784152819n,
    acceptablePriceDeltaBps: 0n,
    positionFeeUsd: 2996579289525092613900000000n,
    swapPathStats: undefined,
    uiFeeUsd: 0n,
    swapUiFeeUsd: 0n,
    feeDiscountUsd: 0n,
    borrowingFeeUsd: 0n,
    fundingFeeUsd: 0n,
    positionPriceImpactDeltaUsd: 41444328240807630917223064n,
  },
})
```

### Helpers

Helpers are a set of functions that help you create orders without manually calculating the amounts, swap paths, etc. By default helpers will fetch the latest data from the API, but you can pass both `marketsInfoData` and `tokensData` to the helpers to avoid extra calls to the API.

```typescript
sdk.orders.long({
  payAmount: 100031302n,
  marketAddress: '0x70d95587d40A2caf56bd97485aB3Eec10Bee6336', // ETH/USD [WETH-USDC]
  payTokenAddress: '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1', // WETH
  collateralTokenAddress: '0xaf88d065e77c8cC2239327C5EDb3A432268e5831', // USDC
  allowedSlippageBps: 125,
  leverage: 50000n,
})

sdk.orders.swap({
  fromAmount: 1000n,
  fromTokenAddress: '0x912CE59144191C1204E64559FE8253a0e49E6548', // ARB
  toTokenAddress: '0xf97f4df75117a78c1A5a0DBb814Af92458539FB4', // LINK
  allowedSlippageBps: 125,
})
```

Pay attention to the `payTokenAddress` and `collateralTokenAddress` fields. They are the addresses of ERC20 tokens that you are paying for and receiving, respectively, some markets may have synthetic tokens in these fields, so you need to pass the correct address. For instance BTC/USD [WETH-USDC] market has synthetic BTC token in `indexTokenAddress` so you need to pass WBTC address instead of BTC.

## Testing and Examples

### Test Files

For complete, working examples of all operations, see the test files in the `test/` directory:

- **`test/test-operations.ts`** - Unified operations test (recommended)
  - Demonstrates all 8 operation types (open, increase, decrease, close, takeprofit, stoploss, deposit, withdraw)
  - Shows how to use `sdk.operations.executeOperation()` API
  - Supports both market and limit orders
  - See [test/README.md](./test/README.md) for detailed usage

### Running Tests

You can run the tests to see how the SDK is used:

```bash
# Set environment variables
export ACCOUNT_ADDRESS="0x..."
export PRIVATE_KEY="0x..."
export MARKET_ADDRESS="0x..."

# Run operations test
OPERATION_TYPE=open MARKET_ADDRESS=0x... PAY_AMOUNT=1 LEVERAGE=5 npx tsx test/test-operations.ts

# Or use the Makefile
make open
make increase
make decrease
make close
```

### Test Examples Reference

The test files provide complete, production-ready examples:

1. **Position Operations** (`test/test-operations.ts`)

   - Open, increase, decrease, close positions
   - Create take profit and stop loss orders
   - Handle both market and limit orders

2. **Pool Operations** (`test/test-operations.ts`)

   - Deposit and withdraw liquidity
   - Handle native token wrapping/unwrapping

3. **Error Handling**
   - Balance checking
   - Token approval
   - Position validation
   - Market data validation

For more details, see [test/README.md](./test/README.md).
