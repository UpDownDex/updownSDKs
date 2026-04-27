# <img src="https://app.updown.xyz/assets/logo_updown_black-Blc0g-YP.svg" width="28" height="28">Updown Python SDK (pySDK)

`pySDK/` is a Python port of the Updown TS SDK in this repository, with the goal of keeping query and trading-operation workflows close to the TS SDK experience.

## Install

```bash
cd pySDK
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -e .
```

## Quick Start

```python
from updown_sdk import UpdownSdk

sdk = UpdownSdk(
    chain_id=42220,  # celo
    rpc_url="https://forno.celo.org",
    oracle_url="https://api.perpex.ai/prices/",
    subsquid_url="https://graph.perpex.ai/celo/subgraphs",  # optional
    account="0xYourAccount",  # optional for pure query
)
```

## Configuration

`UpdownSdk` parameters:

- `chain_id`: chain ID (`42220` celo / `42161` arbitrum)
- `rpc_url`: chain RPC endpoint
- `oracle_url`: Oracle API (for example `https://api.perpex.ai/prices/`)
- `subsquid_url`: optional subgraph/indexer endpoint
- `account`: optional, but recommended when querying orders/positions or running operations
- `tokens`, `markets`: optional extension overrides (same design as TS SDK)

You can also manage environment variables via `.env` + `load_sdk_dotenv()` (see the scripts section below).

## Query

Below are the query capabilities currently aligned with the TS SDK.

### Markets

```python
markets = sdk.markets.get_markets()
markets_dump = sdk.markets.dump_markets()  # list[dict]
```

- `get_markets()` returns the market list (`marketTokenAddress/index/long/short`)
- `dump_markets()` returns a dict structure directly usable by `positions.get_positions()`

### Oracle

```python
tickers = sdk.oracle.get_tickers()
tickers_dump = sdk.oracle.dump_tickers()
```

- `get_tickers()` fetches `/tickers` and returns structured ticker data
- `dump_tickers()` returns a dict list for logging/debugging

### Tokens

```python
tokens_data, prices_updated_at = sdk.tokens.get_tokens_data()
token = sdk.tokens.get_token("0x...")
```

- `get_tokens_data()` returns a TS-style `tokensData` mapping (including `prices`)
- `get_token(address)` returns one token config and its prices

### Orders

```python
orders = sdk.orders.get_orders(account="0xYourAccount", start=0, end=1000)
```

- `get_orders()` reads account orders from-chain and returns `dict[orderKey, Order]`

### Positions

```python
markets_dump = sdk.markets.dump_markets()
positions = sdk.positions.get_positions(
    account="0xYourAccount",
    markets=markets_dump,
    start=0,
    end=1000,
)
```

- `get_positions()` prefers `getAccountPositionInfoList` (with prices)
- Falls back to `getAccountPositions` if price coverage is incomplete

## Operations

Trading operations in the Python SDK are executed via the `Operations` class (currently not via `sdk.operations.executeOperation(...)`).

Supported operation types (aligned with TS operation semantics):

- `open_position`
- `increase_position`
- `decrease_position`
- `close_position`
- `take_profit`
- `stop_loss`
- `deposit`
- `withdraw`

### Example: Open Position

```python
from updown_sdk.operations import Operations

ops = Operations(
    sdk.w3,
    sdk.chain_id,
    account="0xYourAccount",
    private_key="0xYourPrivateKey",
    tokens=sdk.tokens,
    positions=sdk.positions,
)

result = ops.open_position(
    market_address="0xMarketTokenAddress",
    is_long=True,
    pay_token_address="0xPayToken",
    collateral_token_address="0xCollateralToken",
    pay_amount="10",
    leverage="2",
    allowed_slippage_bps=100,
    trigger_price=None,           # optional
    trigger_price_percent=None,   # optional
    execution_fee_wei=None,       # optional, supports auto estimation
)

print(result.tx_hash)
```

### Example: Withdraw Liquidity

```python
result = ops.withdraw(
    market_address="0xMarketTokenAddress",
    market_token_amount="0.6",
    receiver="0xReceiverAddress",         # optional
    min_long_token_amount="0",            # optional
    min_short_token_amount="0",           # optional
    execution_fee_wei=None,               # optional
)
```

## Scripts (recommended integration entrypoints)

The project includes Python scripts corresponding to the TS test scripts:

- `scripts/test_query.py`: full query flow
- `scripts/test_orders.py`: orders-only query
- `scripts/test_positions.py`: positions-only query
- `scripts/test_operations.py`: full operations test entrypoint

### What `test_query.py` prints

`scripts/test_query.py` prints in this order:

- Markets list (including index/long/short token addresses)
- Prices status (`pricesUpdatedAt` + `marketsInfoData/tokensData` counts)
- Orders (if `ACCOUNT_ADDRESS` is provided)
- Positions (if `ACCOUNT_ADDRESS` is provided)
- LP token balance (if both `MARKET_ADDRESS` and `ACCOUNT_ADDRESS` are provided)

Notes:

- Position queries prefer `getAccountPositionInfoList` (with prices)
- Automatically falls back to `getAccountPositions` when oracle coverage is insufficient
- LP balance reads ERC20 `balanceOf` for `marketTokenAddress`

### Key env vars for `test_query.py`

- `CHAIN` (default: `celo`)
- `CELO_RPC_URL` / `ARBITRUM_RPC_URL`
- `ORACLE_URL`
- `SUBSQUID_URL` or `SUBGRAPH_URL`
- `ACCOUNT_ADDRESS` (required for orders/positions queries)
- `MARKET_ADDRESS` or `MARKET_TOKEN_ADDRESS` (for LP/GM balance query)

### `test_operations.py` parameter matrix (by `OPERATION_TYPE`)

- `open` / `increase`
  - required: `ACCOUNT_ADDRESS`, `PRIVATE_KEY`, `MARKET_ADDRESS`, `PAY_TOKEN_ADDRESS`, `COLLATERAL_TOKEN_ADDRESS`
  - optional: `IS_LONG`(default `true`), `PAY_AMOUNT`(default `10`), `LEVERAGE`(default `2`), `TRIGGER_PRICE`, `TRIGGER_PRICE_PERCENT`, `ALLOWED_SLIPPAGE_BPS`(default `100`), `EXECUTION_FEE_WEI`
- `decrease`
  - required: `ACCOUNT_ADDRESS`, `PRIVATE_KEY`, `MARKET_ADDRESS`, `COLLATERAL_TOKEN_ADDRESS`
  - optional: `IS_LONG`(default `true`), `DECREASE_PERCENTAGE`(default `0.5`), `TRIGGER_PRICE`, `TRIGGER_PRICE_PERCENT`, `ALLOWED_SLIPPAGE_BPS`, `EXECUTION_FEE_WEI`
- `close`
  - required: `ACCOUNT_ADDRESS`, `PRIVATE_KEY`, `MARKET_ADDRESS`, `COLLATERAL_TOKEN_ADDRESS`
  - optional: `IS_LONG`, `ALLOWED_SLIPPAGE_BPS`, `EXECUTION_FEE_WEI`
- `takeprofit`
  - required: `ACCOUNT_ADDRESS`, `PRIVATE_KEY`, `MARKET_ADDRESS`, `COLLATERAL_TOKEN_ADDRESS`
  - optional: `IS_LONG`, `PROFIT_PERCENTAGE`(default `5`), `SIZE_AMOUNT`, `ALLOWED_SLIPPAGE_BPS`, `EXECUTION_FEE_WEI`
- `stoploss`
  - required: `ACCOUNT_ADDRESS`, `PRIVATE_KEY`, `MARKET_ADDRESS`, `COLLATERAL_TOKEN_ADDRESS`
  - optional: `IS_LONG`, `LOSS_PERCENTAGE`(default `3`), `SIZE_AMOUNT`, `ALLOWED_SLIPPAGE_BPS`, `EXECUTION_FEE_WEI`
- `deposit`
  - required: `ACCOUNT_ADDRESS`, `PRIVATE_KEY`, `MARKET_ADDRESS`
  - amount: `LONG_TOKEN_AMOUNT`/`SHORT_TOKEN_AMOUNT` (or aliases `CEUR_DEPOSIT_AMOUNT`/`USDC_DEPOSIT_AMOUNT`)
  - optional: `LONG_TOKEN_ADDRESS`, `SHORT_TOKEN_ADDRESS`, `RECEIVER_ADDRESS`, `EXECUTION_FEE_WEI`
- `withdraw`
  - required: `ACCOUNT_ADDRESS`, `PRIVATE_KEY`, `MARKET_ADDRESS`, and `MARKET_TOKEN_AMOUNT` (or `WITHDRAWAL_AMOUNT`)
  - optional: `RECEIVER_ADDRESS`, `MIN_LONG_TOKEN_AMOUNT`, `MIN_SHORT_TOKEN_AMOUNT`, `EXECUTION_FEE_WEI`

Run examples:

```bash
cd pySDK
source .venv/bin/activate
python3 scripts/test_query.py
python3 scripts/test_orders.py
python3 scripts/test_positions.py
python3 scripts/test_operations.py
```

## .env Example

Base fields (matching current `.env.example`):

```dotenv
ACCOUNT_ADDRESS=""
PRIVATE_KEY=""
CELO_RPC_URL="https://forno.celo.org"
ORACLE_URL="https://api.perpex.ai/prices/"
SUBSQUID_URL="https://graph.perpex.ai/celo/subgraphs"
MARKET_ADDRESS=""
OPERATION_TYPE="withdraw"
LONG_TOKEN_AMOUNT="0.5"
SHORT_TOKEN_AMOUNT="0.01"
MARKET_TOKEN_AMOUNT="0.6"
```

Optional extended fields (supported by scripts):

- `CHAIN` (`celo` / `arbitrum`, default `celo`)
- `ARBITRUM_RPC_URL`
- `SUBGRAPH_URL` (`SUBSQUID_URL` compatibility alias)
- `PAY_TOKEN_ADDRESS`
- `COLLATERAL_TOKEN_ADDRESS`
- `PAY_AMOUNT`
- `LEVERAGE`
- `IS_LONG`
- `TRIGGER_PRICE`
- `TRIGGER_PRICE_PERCENT`
- `DECREASE_PERCENTAGE`
- `PROFIT_PERCENTAGE`
- `LOSS_PERCENTAGE`
- `SIZE_AMOUNT`
- `EXECUTION_FEE_WEI`
- `RECEIVER_ADDRESS`
- `MIN_LONG_TOKEN_AMOUNT`
- `MIN_SHORT_TOKEN_AMOUNT`
- `WITHDRAWAL_AMOUNT` (`MARKET_TOKEN_AMOUNT` alias)
- `MARKET_TOKEN_ADDRESS` (`MARKET_ADDRESS` alias for query)
- `CEUR_DEPOSIT_AMOUNT` / `USDC_DEPOSIT_AMOUNT` (deposit amount aliases)

Supported `OPERATION_TYPE` values:

- `open`
- `increase`
- `decrease`
- `close`
- `takeprofit`
- `stoploss`
- `deposit`
- `withdraw`

## Add a New Market

When adding a new market to this SDK, update configs in this order:

1. Add market addresses to `src/updown_sdk/config/markets.json`
   - Required fields per market entry:
     - `marketTokenAddress`
     - `indexTokenAddress`
     - `longTokenAddress`
     - `shortTokenAddress`
2. Ensure all market tokens exist in `src/updown_sdk/config/tokens.json`
   - At minimum, token entries should include:
     - `address`
     - `symbol`
     - `decimals`
3. Re-generate DataStore key maps for operations that depend on `MarketStore`
   - Script:
     - `python3 scripts/prebuild_market_keys.py --chain-id 42220 --market-address <MARKET_TOKEN_ADDRESS> --merge`
   - Outputs:
     - `src/updown_sdk/config/marketConfigKeys.json`
     - `src/updown_sdk/config/marketValuesKeys.json`
4. Validate end-to-end with test scripts
   - `python3 scripts/test_positions.py`
   - `python3 scripts/test_operations.py`

Notes:

- `decrease` / `close` / `takeprofit` / `stoploss` require keys in both `marketConfigKeys.json` and `marketValuesKeys.json`.
- `open` / `increase` / query scripts do not rely on those key files in the same way, but still require correct `markets.json` + `tokens.json`.
- The oracle endpoint must return tickers for your new index/long/short token addresses, otherwise position pricing paths may fall back or fail.

## Notes

- This documentation follows the current Python implementation in the repository, with naming and parameters kept as close as possible to TS.
- Both query and operations are available; the scripts cover common integration/testing workflows.
