import os
from typing import Optional

from updown_sdk import UpdownSdk
from updown_sdk.env import load_sdk_dotenv
from updown_sdk.operations import Operations


def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.lower() not in ("0", "false", "no")


def _chain() -> str:
    raw = (os.getenv("CHAIN") or "celo").lower()
    return "arbitrum" if raw == "arbitrum" else "celo"


def _chain_id(chain: str) -> int:
    return 42161 if chain == "arbitrum" else 42220


def _rpc_url(chain: str) -> str:
    # Follow TS test-config.ts defaults
    if chain == "arbitrum":
        return os.getenv("ARBITRUM_RPC_URL", "https://arb1.arbitrum.io/rpc")
    return os.getenv("CELO_RPC_URL", "https://forno.celo.org")


def _oracle_url() -> str:
    return os.getenv("ORACLE_URL", "https://api.perpex.ai/prices/")


def _subsquid_url() -> Optional[str]:
    return os.getenv("SUBSQUID_URL") or os.getenv("SUBGRAPH_URL")


def _required(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise SystemExit(f"Missing required env var: {name}")
    return v


def _operation_type() -> str:
    return (os.getenv("OPERATION_TYPE") or "open").lower()


def main() -> None:
    try:
        load_sdk_dotenv()
        chain = _chain()
        chain_id = _chain_id(chain)
        operation_type = _operation_type()

        print("\n" + "=" * 80)
        print(f"🚀 Executing Operation: {operation_type.upper()}")
        print("=" * 80 + "\n")

        account = _required("ACCOUNT_ADDRESS")
        private_key = _required("PRIVATE_KEY")
        market_address = _required("MARKET_ADDRESS")

        sdk = UpdownSdk(
            chain_id=chain_id,
            rpc_url=_rpc_url(chain),
            oracle_url=_oracle_url(),
            subsquid_url=_subsquid_url(),
            account=account,
        )

        print("📋 Configuration:")
        print(f"   Chain ID: {sdk.chain_id}")
        print(f"   Account: {sdk.account}")
        print(f"   Operation Type: {operation_type}")
        print("")

        markets = sdk.markets.get_markets()
        market = next((m for m in markets if m.market_token_address.lower() == market_address.lower()), None)
        if not market:
            raise SystemExit(f"Market not found in config: {market_address}")

        print("📈 Market:")
        print(f"   marketAddress: {market.market_token_address}")
        print(f"   indexToken: {market.index_token_address}")
        print(f"   longToken: {market.long_token_address}")
        print(f"   shortToken: {market.short_token_address}")
        print("")

        markets_dump = sdk.markets.dump_markets()

        if operation_type in ("open", "increase"):
            is_long = _get_bool("IS_LONG", True)
            pay_amount = os.getenv("PAY_AMOUNT", "10")
            leverage = os.getenv("LEVERAGE", "2")
            trigger_price = os.getenv("TRIGGER_PRICE")
            trigger_price_percent = os.getenv("TRIGGER_PRICE_PERCENT")
            collateral_token_address = _required("COLLATERAL_TOKEN_ADDRESS")
            pay_token_address = _required("PAY_TOKEN_ADDRESS")
            execution_fee_raw = os.getenv("EXECUTION_FEE_WEI")
            execution_fee_wei = int(execution_fee_raw) if execution_fee_raw else None
            allowed_slippage_bps = int(os.getenv("ALLOWED_SLIPPAGE_BPS", "100"))

            print("🧩 Parsed params (position op):")
            print(f"   isLong: {is_long}")
            print(f"   payAmount: {pay_amount}")
            print(f"   leverage: {leverage}")
            print(f"   triggerPrice: {trigger_price}")
            print(f"   triggerPricePercent: {trigger_price_percent}")
            print(f"   collateralTokenAddress: {collateral_token_address}")
            print(f"   payTokenAddress: {pay_token_address}")
            print(f"   executionFeeWei: {execution_fee_wei}")
            print(f"   allowedSlippageBps: {allowed_slippage_bps}")
            print("")

            ops = Operations(sdk.w3, sdk.chain_id, account, private_key, sdk.tokens, sdk.positions)
            if operation_type == "increase":
                result = ops.increase_position(
                    market_address=market_address,
                    is_long=is_long,
                    pay_token_address=pay_token_address,
                    collateral_token_address=collateral_token_address,
                    pay_amount=pay_amount,
                    leverage=leverage,
                    allowed_slippage_bps=allowed_slippage_bps,
                    trigger_price=trigger_price,
                    trigger_price_percent=trigger_price_percent,
                    execution_fee_wei=execution_fee_wei,
                )
            else:
                result = ops.open_position(
                    market_address=market_address,
                    is_long=is_long,
                    pay_token_address=pay_token_address,
                    collateral_token_address=collateral_token_address,
                    pay_amount=pay_amount,
                    leverage=leverage,
                    allowed_slippage_bps=allowed_slippage_bps,
                    trigger_price=trigger_price,
                    trigger_price_percent=trigger_price_percent,
                    execution_fee_wei=execution_fee_wei,
                )

            print("\n✅ Operation completed successfully!")
            print(f"   Transaction Hash: {result.tx_hash}")
            print("\n💡 Note: The order will be executed by a keeper.")
            return

        if operation_type in ("decrease", "close", "takeprofit", "stoploss"):
            is_long = _get_bool("IS_LONG", True)
            collateral_token_address = _required("COLLATERAL_TOKEN_ADDRESS")
            execution_fee_raw = os.getenv("EXECUTION_FEE_WEI")
            execution_fee_wei = int(execution_fee_raw) if execution_fee_raw else None
            allowed_slippage_bps = int(os.getenv("ALLOWED_SLIPPAGE_BPS", "100"))

            ops = Operations(sdk.w3, sdk.chain_id, account, private_key, sdk.tokens, sdk.positions)

            if operation_type == "decrease":
                decrease_pct = float(os.getenv("DECREASE_PERCENTAGE", "0.5"))
                trigger_price = os.getenv("TRIGGER_PRICE")
                trigger_price_percent = os.getenv("TRIGGER_PRICE_PERCENT")
                print("🧩 Parsed params (decrease):")
                print(f"   isLong: {is_long}")
                print(f"   collateralTokenAddress: {collateral_token_address}")
                print(f"   decreasePercentage: {decrease_pct}")
                print(f"   triggerPrice: {trigger_price}")
                print(f"   triggerPricePercent: {trigger_price_percent}")
                print(f"   executionFeeWei: {execution_fee_wei}")
                print("")
                result = ops.decrease_position(
                    market_address=market_address,
                    is_long=is_long,
                    collateral_token_address=collateral_token_address,
                    markets=markets_dump,
                    decrease_percentage=decrease_pct,
                    trigger_price=trigger_price,
                    trigger_price_percent=trigger_price_percent,
                    allowed_slippage_bps=allowed_slippage_bps,
                    execution_fee_wei=execution_fee_wei,
                )
            elif operation_type == "close":
                print("🧩 Parsed params (close):")
                print(f"   isLong: {is_long}")
                print(f"   collateralTokenAddress: {collateral_token_address}")
                print(f"   executionFeeWei: {execution_fee_wei}")
                print("")
                result = ops.close_position(
                    market_address=market_address,
                    is_long=is_long,
                    collateral_token_address=collateral_token_address,
                    markets=markets_dump,
                    allowed_slippage_bps=allowed_slippage_bps,
                    execution_fee_wei=execution_fee_wei,
                )
            elif operation_type == "takeprofit":
                profit_pct = os.getenv("PROFIT_PERCENTAGE", "5")
                size_amount = os.getenv("SIZE_AMOUNT")
                print("🧩 Parsed params (take profit):")
                print(f"   isLong: {is_long}")
                print(f"   collateralTokenAddress: {collateral_token_address}")
                print(f"   profitPercentage: {profit_pct}")
                print(f"   sizeAmount (USD, 30 decimals): {size_amount}")
                print(f"   executionFeeWei: {execution_fee_wei}")
                print("")
                result = ops.take_profit(
                    market_address=market_address,
                    is_long=is_long,
                    collateral_token_address=collateral_token_address,
                    markets=markets_dump,
                    profit_percentage=profit_pct,
                    size_amount_usd=size_amount,
                    allowed_slippage_bps=allowed_slippage_bps,
                    execution_fee_wei=execution_fee_wei,
                )
            else:
                loss_pct = os.getenv("LOSS_PERCENTAGE", "3")
                size_amount = os.getenv("SIZE_AMOUNT")
                print("🧩 Parsed params (stop loss):")
                print(f"   isLong: {is_long}")
                print(f"   collateralTokenAddress: {collateral_token_address}")
                print(f"   lossPercentage: {loss_pct}")
                print(f"   sizeAmount (USD, 30 decimals): {size_amount}")
                print(f"   executionFeeWei: {execution_fee_wei}")
                print("")
                result = ops.stop_loss(
                    market_address=market_address,
                    is_long=is_long,
                    collateral_token_address=collateral_token_address,
                    markets=markets_dump,
                    loss_percentage=loss_pct,
                    size_amount_usd=size_amount,
                    allowed_slippage_bps=allowed_slippage_bps,
                    execution_fee_wei=execution_fee_wei,
                )

            print("\n✅ Operation completed successfully!")
            print(f"   Transaction Hash: {result.tx_hash}")
            print("\n💡 Note: The order will be executed by a keeper.")
            return

        if operation_type == "deposit":
            long_token_amount = os.getenv("CEUR_DEPOSIT_AMOUNT") or os.getenv("LONG_TOKEN_AMOUNT")
            short_token_amount = os.getenv("USDC_DEPOSIT_AMOUNT") or os.getenv("SHORT_TOKEN_AMOUNT")
            long_token_address = os.getenv("LONG_TOKEN_ADDRESS")
            short_token_address = os.getenv("SHORT_TOKEN_ADDRESS")
            receiver = os.getenv("RECEIVER_ADDRESS")
            execution_fee_raw = os.getenv("EXECUTION_FEE_WEI")
            execution_fee_wei = int(execution_fee_raw) if execution_fee_raw else None

            print("🧩 Parsed params (deposit):")
            print(f"   longTokenAmount: {long_token_amount}")
            print(f"   shortTokenAmount: {short_token_amount}")
            print(f"   longTokenAddress: {long_token_address}")
            print(f"   shortTokenAddress: {short_token_address}")
            print(f"   receiver: {receiver}")
            print(f"   executionFeeWei: {execution_fee_wei}")
            print("")

            ops = Operations(sdk.w3, sdk.chain_id, account, private_key, sdk.tokens, sdk.positions)
            result = ops.deposit(
                market_address=market_address,
                long_token_address=long_token_address,
                short_token_address=short_token_address,
                long_token_amount=long_token_amount,
                short_token_amount=short_token_amount,
                receiver=receiver,
                execution_fee_wei=execution_fee_wei,
            )
            print("\n✅ Operation completed successfully!")
            print(f"   Transaction Hash: {result.tx_hash}")
            print("\n💡 Note: The deposit will be executed by a keeper.")
            return

        if operation_type == "withdraw":
            market_token_amount = os.getenv("WITHDRAWAL_AMOUNT") or os.getenv("MARKET_TOKEN_AMOUNT")
            receiver = os.getenv("RECEIVER_ADDRESS")
            min_long = os.getenv("MIN_LONG_TOKEN_AMOUNT")
            min_short = os.getenv("MIN_SHORT_TOKEN_AMOUNT")
            execution_fee_raw = os.getenv("EXECUTION_FEE_WEI")
            execution_fee_wei = int(execution_fee_raw) if execution_fee_raw else None

            if not market_token_amount:
                raise SystemExit("Missing MARKET_TOKEN_AMOUNT or WITHDRAWAL_AMOUNT for withdraw")

            effective_receiver = receiver if receiver else account
            effective_min_long = min_long if min_long else "0"
            effective_min_short = min_short if min_short else "0"
            effective_execution_fee = str(execution_fee_wei) if execution_fee_wei is not None else "AUTO"

            print("🧩 Parsed params (withdraw):")
            print(f"   marketTokenAmount: {market_token_amount}")
            print(f"   receiver: {effective_receiver}")
            print(f"   minLongTokenAmount: {effective_min_long}")
            print(f"   minShortTokenAmount: {effective_min_short}")
            print(f"   executionFeeWei: {effective_execution_fee}")
            print("")

            ops = Operations(sdk.w3, sdk.chain_id, account, private_key, sdk.tokens, sdk.positions)
            result = ops.withdraw(
                market_address=market_address,
                market_token_amount=market_token_amount,
                receiver=receiver,
                min_long_token_amount=min_long,
                min_short_token_amount=min_short,
                execution_fee_wei=execution_fee_wei,
            )
            print("\n✅ Operation completed successfully!")
            print(f"   Transaction Hash: {result.tx_hash}")
            print("\n💡 Note: The withdrawal will be executed by a keeper.")
            return

        raise SystemExit(
            f"Unsupported OPERATION_TYPE={operation_type}. "
            "Supported: open, increase, decrease, close, takeprofit, stoploss, deposit, withdraw."
        )
    except Exception as e:
        print("\n❌ Operation failed")
        print(f"   Error: {e}")
        print("   Tip: Check OPERATION_TYPE / token addresses / isLong / position direction.")
        return


if __name__ == "__main__":
    main()

