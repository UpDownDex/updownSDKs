# SDK Test Suite

This directory contains test scripts for the Updown SDK, specifically for the CELO chain.

## Test Files

- `test-config.ts` - SDK configuration and helper functions
- `test-operations.ts` - **Unified operations test** (all position and pool operations)
- `test-deposit.ts` - Legacy deposit test (deprecated, use `test-operations.ts`)
- `test-withdrawal.ts` - Legacy withdrawal test (deprecated, use `test-operations.ts`)
- `test-position.ts` - Legacy position test (deprecated, use `test-operations.ts`)
- `position-helpers.ts` - Shared helper functions for position operations
- `subgraph-helpers.ts` - Helper functions for subgraph queries

## Prerequisites

1. Set environment variables:

   ```bash
   export ACCOUNT_ADDRESS="0x..."  # Your account address (required)
   export PRIVATE_KEY="0x..."      # Your private key (REQUIRED for signing transactions)
   export CELO_RPC_URL="https://forno.celo.org"  # Optional
   export ORACLE_URL="https://api.perpex.ai"  # Optional
   export SUBSQUID_URL="http://8.219.84.241:8000/subgraphs/name/gmx/synthetics-celo-stats"  # Optional
   ```

   **⚠️ IMPORTANT**: The `PRIVATE_KEY` is **REQUIRED** for signing transactions. Without it, tests will fail with "Wallet client is not initialized" error.

2. Install dependencies:
   ```bash
   cd sdk
   npm install
   ```

## Running Tests

### Using Makefile (Recommended)

The easiest way to run tests is using the Makefile:

```bash
# Deposit liquidity
make deposit

# Withdraw liquidity
make withdraw

# Open a position
make open                    # Long position
make open-short             # Short position

# Increase position
make increase                # Long position
make increase-short         # Short position

# Decrease position
make decrease                # Decrease by 50% (default)
make decrease-25            # Decrease by 25%
make decrease-75            # Decrease by 75%

# Close position
make close                   # Close long position
make close-short             # Close short position

# Create take profit order
make takeprofit              # 5% profit (default)
make takeprofit-8            # 8% profit, 100 USD
make takeprofit-10           # 10% profit

# Create stop loss order
make stoploss                # 3% loss (default)
make stoploss-5              # 5% loss, 100 USD
```

### Direct Execution

You can also run tests directly using `npx tsx`:

```bash
# Deposit
OPERATION_TYPE=deposit MARKET_ADDRESS=0x540ae5Dea435b035F32A0f3C222d73E42699d6c3 npx tsx test/test-operations.ts

# Withdraw
OPERATION_TYPE=withdraw MARKET_ADDRESS=0x540ae5Dea435b035F32A0f3C222d73E42699d6c3 WITHDRAWAL_AMOUNT=0.01 npx tsx test/test-operations.ts

# Open position
OPERATION_TYPE=open MARKET_ADDRESS=0x540ae5Dea435b035F32A0f3C222d73E42699d6c3 PAY_AMOUNT=1 LEVERAGE=1 IS_LONG=true npx tsx test/test-operations.ts

# Increase position
OPERATION_TYPE=increase MARKET_ADDRESS=0x540ae5Dea435b035F32A0f3C222d73E42699d6c3 PAY_AMOUNT=1 LEVERAGE=2 IS_LONG=true npx tsx test/test-operations.ts

# Decrease position
OPERATION_TYPE=decrease MARKET_ADDRESS=0x540ae5Dea435b035F32A0f3C222d73E42699d6c3 IS_LONG=true DECREASE_PERCENTAGE=0.5 npx tsx test/test-operations.ts

# Close position
OPERATION_TYPE=close MARKET_ADDRESS=0x540ae5Dea435b035F32A0f3C222d73E42699d6c3 IS_LONG=true npx tsx test/test-operations.ts

# Take profit
OPERATION_TYPE=takeprofit MARKET_ADDRESS=0x540ae5Dea435b035F32A0f3C222d73E42699d6c3 IS_LONG=true PROFIT_PERCENTAGE=5 npx tsx test/test-operations.ts

# Stop loss
OPERATION_TYPE=stoploss MARKET_ADDRESS=0x540ae5Dea435b035F32A0f3C222d73E42699d6c3 IS_LONG=true LOSS_PERCENTAGE=3 npx tsx test/test-operations.ts
```

## Unified Operations Test (`test-operations.ts`)

All operations (position and pool) are now handled by a single unified test file `test-operations.ts` using the `sdk.operations.executeOperation()` API.

### Supported Operations

| Operation Type | Description                     | Order Type                     |
| -------------- | ------------------------------- | ------------------------------ |
| `open`         | Open a new position             | MarketIncrease / LimitIncrease |
| `increase`     | Increase existing position      | MarketIncrease / LimitIncrease |
| `decrease`     | Decrease position by percentage | MarketDecrease / LimitDecrease |
| `close`        | Close position completely       | MarketDecrease / LimitDecrease |
| `takeprofit`   | Create take profit order        | LimitDecrease                  |
| `stoploss`     | Create stop loss order          | StopLossDecrease               |
| `deposit`      | Deposit liquidity to pool       | -                              |
| `withdraw`     | Withdraw liquidity from pool    | -                              |

### Position Operations

#### Open Position (`OPERATION_TYPE=open`)

Opens a new position. Supports both market and limit orders.

**Required Environment Variables:**

- `MARKET_ADDRESS` - Market address (required)
- `OPERATION_TYPE=open` - Operation type

**Optional Environment Variables:**

- `PAY_AMOUNT` - Amount to pay in collateral token (default: "10")
- `LEVERAGE` - Leverage multiplier (default: "5" = 5x)
- `IS_LONG` - "true" for long, "false" for short (default: "true")
- `COLLATERAL_TOKEN_ADDRESS` - Collateral token address (optional, defaults to long token for long positions)
- `PAY_TOKEN_ADDRESS` - Token to pay with (optional, defaults to collateral token)
- `TRIGGER_PRICE` - Trigger price for limit orders (optional, if provided creates LimitIncrease order)

**Example:**

```bash
# Market order (default)
make open

# Limit order
OPERATION_TYPE=open MARKET_ADDRESS=0x... PAY_AMOUNT=1 LEVERAGE=5 TRIGGER_PRICE=50000 npx tsx test/test-operations.ts
```

#### Increase Position (`OPERATION_TYPE=increase`)

Increases an existing position. Supports both market and limit orders.

**Required Environment Variables:**

- `MARKET_ADDRESS` - Market address (required)
- `OPERATION_TYPE=increase` - Operation type

**Optional Environment Variables:**

- Same as Open Position

**Example:**

```bash
make increase
```

#### Decrease Position (`OPERATION_TYPE=decrease`)

Decreases an existing position by a percentage. Supports both market and limit orders.

**Required Environment Variables:**

- `MARKET_ADDRESS` - Market address (required)
- `OPERATION_TYPE=decrease` - Operation type

**Optional Environment Variables:**

- `DECREASE_PERCENTAGE` - Percentage to decrease (default: "0.5" = 50%)
  - Examples: "0.25" for 25%, "0.5" for 50%, "0.75" for 75%
- `IS_LONG` - "true" for long, "false" for short (default: "true")
- `COLLATERAL_TOKEN_ADDRESS` - Collateral token address (optional)
- `TRIGGER_PRICE` - Trigger price for limit orders (optional)

**Example:**

```bash
# Decrease by 50% (default)
make decrease

# Decrease by 25%
make decrease-25

# Decrease by 75%
make decrease-75
```

#### Close Position (`OPERATION_TYPE=close`)

Closes an existing position completely. Supports both market and limit orders.

**Required Environment Variables:**

- `MARKET_ADDRESS` - Market address (required)
- `OPERATION_TYPE=close` - Operation type

**Optional Environment Variables:**

- `IS_LONG` - "true" for long, "false" for short (default: "true")
- `COLLATERAL_TOKEN_ADDRESS` - Collateral token address (optional)
- `TRIGGER_PRICE` - Trigger price for limit orders (optional)

**Example:**

```bash
make close
make close-short
```

#### Take Profit Order (`OPERATION_TYPE=takeprofit`)

Creates a take profit order (Limit Decrease Order with trigger price).

**Required Environment Variables:**

- `MARKET_ADDRESS` - Market address (required)
- `OPERATION_TYPE=takeprofit` - Operation type

**Optional Environment Variables:**

- `PROFIT_PERCENTAGE` - Profit percentage (default: "5" = 5%)
- `SIZE_AMOUNT` - Position size in USD to close (optional, default: 50% of position)
- `IS_LONG` - "true" for long, "false" for short (default: "true")
- `COLLATERAL_TOKEN_ADDRESS` - Collateral token address (optional)

**Trigger Logic:**

- **Long position**: Triggers when price goes **above** entry price by profit percentage
- **Short position**: Triggers when price goes **below** entry price by profit percentage

**Example:**

```bash
# Default 5% take profit
make takeprofit

# Custom 10% take profit
make takeprofit-10
```

#### Stop Loss Order (`OPERATION_TYPE=stoploss`)

Creates a stop loss order (Stop Loss Decrease Order with trigger price).

**Required Environment Variables:**

- `MARKET_ADDRESS` - Market address (required)
- `OPERATION_TYPE=stoploss` - Operation type

**Optional Environment Variables:**

- `LOSS_PERCENTAGE` - Loss percentage (default: "3" = 3%)
- `SIZE_AMOUNT` - Position size in USD to close (optional, default: 100% of position)
- `IS_LONG` - "true" for long, "false" for short (default: "true")
- `COLLATERAL_TOKEN_ADDRESS` - Collateral token address (optional)

**Trigger Logic:**

- **Long position**: Triggers when price goes **below** entry price by loss percentage
- **Short position**: Triggers when price goes **above** entry price by loss percentage

**Example:**

```bash
# Default 3% stop loss
make stoploss

# Custom 5% stop loss
make stoploss-5
```

### Pool Operations

#### Deposit (`OPERATION_TYPE=deposit`)

Deposits liquidity into a market pool.

**Required Environment Variables:**

- `MARKET_ADDRESS` - Market address (required)
- `OPERATION_TYPE=deposit` - Operation type

**Optional Environment Variables:**

- `CEUR_DEPOSIT_AMOUNT` - Amount of long token to deposit (optional)
- `USDC_DEPOSIT_AMOUNT` - Amount of short token to deposit (optional)
- `LONG_TOKEN_ADDRESS` - Long token address (optional, auto-detected from market)
- `SHORT_TOKEN_ADDRESS` - Short token address (optional, auto-detected from market)

**Example:**

```bash
make deposit
# or
OPERATION_TYPE=deposit MARKET_ADDRESS=0x... CEUR_DEPOSIT_AMOUNT=100 USDC_DEPOSIT_AMOUNT=100 npx tsx test/test-operations.ts
```

#### Withdraw (`OPERATION_TYPE=withdraw`)

Withdraws liquidity from a market pool.

**Required Environment Variables:**

- `MARKET_ADDRESS` - Market address (required)
- `OPERATION_TYPE=withdraw` - Operation type
- `WITHDRAWAL_AMOUNT` - Amount of market tokens to withdraw (required)

**Optional Environment Variables:**

- `MIN_LONG_TOKEN_AMOUNT` - Minimum long token amount (optional)
- `MIN_SHORT_TOKEN_AMOUNT` - Minimum short token amount (optional)
- `RECEIVER_ADDRESS` - Receiver address (optional, defaults to account)

**Example:**

```bash
make withdraw
# or
OPERATION_TYPE=withdraw MARKET_ADDRESS=0x... WITHDRAWAL_AMOUNT=0.01 npx tsx test/test-operations.ts
```

## Order Types

The SDK supports both **Market** and **Limit** orders:

### Market Orders (Default)

- Execute immediately at current market price
- Use `OrderType.MarketIncrease` or `OrderType.MarketDecrease`
- No `triggerPrice` parameter needed

### Limit Orders

- Execute when trigger price is reached
- Use `OrderType.LimitIncrease` or `OrderType.LimitDecrease`
- Provide `TRIGGER_PRICE` parameter in environment variables
- Example:
  ```bash
  OPERATION_TYPE=open MARKET_ADDRESS=0x... PAY_AMOUNT=10 LEVERAGE=5 TRIGGER_PRICE=50000 npx tsx test/test-operations.ts
  ```

### Supported Order Types by Operation

| Operation  | Market Order      | Limit Order                           |
| ---------- | ----------------- | ------------------------------------- |
| Open       | ✅ MarketIncrease | ✅ LimitIncrease (with TRIGGER_PRICE) |
| Increase   | ✅ MarketIncrease | ✅ LimitIncrease (with TRIGGER_PRICE) |
| Decrease   | ✅ MarketDecrease | ✅ LimitDecrease (with TRIGGER_PRICE) |
| Close      | ✅ MarketDecrease | ✅ LimitDecrease (with TRIGGER_PRICE) |
| TakeProfit | N/A               | ✅ LimitDecrease (auto)               |
| StopLoss   | N/A               | ✅ StopLossDecrease (auto)            |

## Test Flow

For a complete test flow, run tests in this order:

1. **Deposit** - Add liquidity to the pool
2. **Open Position** - Open a long or short position
3. **Increase Position** - Increase an existing position
4. **Decrease Position** - Decrease an existing position by percentage
5. **Take Profit** - Create a take profit order
6. **Stop Loss** - Create a stop loss order
7. **Close Position** - Close a position completely
8. **Withdraw** - Remove liquidity from the pool

## Important Notes

### Order Execution

- **All tests only CREATE orders**. Orders are NOT executed automatically.
- Orders must be executed by a keeper with `ORDER_KEEPER` role.
- The `executionFee` you provide will be used to compensate the keeper.

### Unified Operations Module

- All operations now use the unified `sdk.operations.executeOperation()` API.
- This provides a consistent interface for scripts, bots, and automation tools.
- Operations automatically handle:
  - Market/token data fetching
  - Position fetching (for position operations)
  - Balance/allowance checking
  - Token approval
  - Execution fee calculation
  - Transaction sending
  - Error handling

### Position Fetching

- Position operations fetch positions directly from the contract (no subgraph dependency).
- The system automatically handles position lookup and validation.

### Market Configuration

- Default market address: `0x540ae5Dea435b035F32A0f3C222d73E42699d6c3` (cEUR/USD on CELO)
- Long token: cEUR (`0xD8763CBa276a3738E6DE85b4b3bF5FDed6D6cA73`)
- Short token: USDC (`0xcebA9300f2b948710d2653dD7B07f33A8B32118C`)

### Token Handling

- Tests automatically check balances and approve tokens as needed.
- Make sure you have sufficient balances and native tokens (CELO) for execution fees.
- The SDK handles token address conversion automatically (wrapped/unwrapped native tokens).

## Troubleshooting

1. **Insufficient balance**: Ensure you have enough tokens and native tokens (CELO) for execution fees
2. **Market not found**: Verify the market address or let the test auto-detect it
3. **Token approval failed**: Check that you have sufficient native tokens for gas
4. **Transaction failed**: Check the transaction hash on the explorer (celoscan.io) for details
5. **Position not found**: Make sure you have an open position before trying to increase/decrease/close
6. **Operation failed**: Check the error message for specific details about what went wrong

## Environment Variables Summary

| Variable                   | Required | Default | Description                                                                              |
| -------------------------- | -------- | ------- | ---------------------------------------------------------------------------------------- |
| `ACCOUNT_ADDRESS`          | Yes      | -       | Your account address                                                                     |
| `PRIVATE_KEY`              | Yes      | -       | Your private key for signing transactions                                                |
| `OPERATION_TYPE`           | Yes\*    | -       | Operation type: open, increase, decrease, close, takeprofit, stoploss, deposit, withdraw |
| `MARKET_ADDRESS`           | Yes\*    | -       | Market address (\*required for most tests)                                               |
| `PAY_AMOUNT`               | No       | "10"    | Amount to pay in collateral token                                                        |
| `LEVERAGE`                 | No       | "5"     | Leverage multiplier (5 = 5x)                                                             |
| `IS_LONG`                  | No       | "true"  | "true" for long, "false" for short                                                       |
| `DECREASE_PERCENTAGE`      | No       | "0.5"   | Percentage to decrease (0.5 = 50%)                                                       |
| `PROFIT_PERCENTAGE`        | No       | "5"     | Profit percentage for take profit (5 = 5%)                                               |
| `LOSS_PERCENTAGE`          | No       | "3"     | Loss percentage for stop loss (3 = 3%)                                                   |
| `SIZE_AMOUNT`              | No       | -       | Position size in USD (for take profit/stop loss)                                         |
| `TRIGGER_PRICE`            | No       | -       | Trigger price for limit orders                                                           |
| `WITHDRAWAL_AMOUNT`        | No\*     | -       | Amount of market tokens to withdraw (\*required for withdraw)                            |
| `CEUR_DEPOSIT_AMOUNT`      | No       | -       | Amount of long token to deposit                                                          |
| `USDC_DEPOSIT_AMOUNT`      | No       | -       | Amount of short token to deposit                                                         |
| `COLLATERAL_TOKEN_ADDRESS` | No       | -       | Collateral token address (auto-detected)                                                 |
| `PAY_TOKEN_ADDRESS`        | No       | -       | Token to pay with (defaults to collateral token)                                         |
| `CELO_RPC_URL`             | No       | -       | CELO RPC URL                                                                             |
| `ORACLE_URL`               | No       | -       | Oracle URL                                                                               |
| `SUBSQUID_URL`             | No       | -       | Subsquid URL for subgraph queries                                                        |

## Using the Operations Module in Your Code

You can also use the operations module directly in your scripts or bots:

```typescript
import { UpdownSdk } from './src/index'
import { OperationType } from './src/modules/operations'

const sdk = new UpdownSdk(config)

// Open position
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
