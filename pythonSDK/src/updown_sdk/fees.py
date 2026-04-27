from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


USD_DECIMALS = 30
PRECISION = 10**30


def apply_factor(value: int, factor: int) -> int:
    # TS applyFactor(value, factor) where factor is 1e30 precision
    return (value * factor) // PRECISION


def estimate_order_oracle_price_count(swaps_count: int) -> int:
    # TS estimateOrderOraclePriceCount: 3 + swapsCount
    return 3 + int(swaps_count)


def estimate_execute_increase_order_gas_limit(gas_limits: dict, swaps_count: int = 0, callback_gas_limit: int = 0) -> int:
    return int(gas_limits["increaseOrder"]) + int(gas_limits["singleSwap"]) * int(swaps_count) + int(callback_gas_limit)


def estimate_execute_deposit_gas_limit(
    gas_limits: dict,
    *,
    long_token_swaps_count: int = 0,
    short_token_swaps_count: int = 0,
    callback_gas_limit: int = 0,
) -> int:
    # TS estimateExecuteDepositGasLimit (GM deposit, swap counts optional)
    gas_per_swap = int(gas_limits["singleSwap"])
    swaps_count = int(long_token_swaps_count) + int(short_token_swaps_count)
    return int(gas_limits["depositToken"]) + int(callback_gas_limit) + gas_per_swap * swaps_count


def estimate_execute_withdrawal_gas_limit(gas_limits: dict, *, callback_gas_limit: int = 0) -> int:
    # TS estimateExecuteWithdrawalGasLimit
    return int(gas_limits["withdrawalMultiToken"]) + int(callback_gas_limit)


# TS DecreasePositionSwapType.NoSwap = 0
def estimate_execute_decrease_order_gas_limit(
    gas_limits: dict,
    *,
    swaps_count: int = 0,
    decrease_swap_type: int = 0,
    callback_gas_limit: int = 0,
) -> int:
    # TS estimateExecuteDecreaseOrderGasLimit
    gas_per_swap = int(gas_limits["singleSwap"])
    sc = int(swaps_count)
    if int(decrease_swap_type) != 0:
        sc += 1
    return int(gas_limits["decreaseOrder"]) + gas_per_swap * sc + int(callback_gas_limit)


@dataclass(frozen=True)
class ExecutionFee:
    fee_token_amount: int
    gas_limit: int


def convert_to_token_amount(usd_30: int, token_decimals: int, price: int) -> Optional[int]:
    # TS convertToTokenAmount(usd, decimals, price): (usd * 10^decimals) / price
    if price <= 0:
        return None
    return (int(usd_30) * (10**int(token_decimals))) // int(price)


def get_execution_fee(
    *,
    chain_id: int,
    gas_limits: dict,
    native_token: dict,
    estimated_gas_limit: int,
    gas_price: int,
    oracle_price_count: int,
    number_of_parts: int = 1,
    execution_fee_buffer_bps: int = 0,
    min_execution_fee_usd_30: Optional[int] = None,
    max_execution_fee_token_amount: Optional[int] = None,
) -> ExecutionFee:
    # Copy of TS getExecutionFee core math.
    base_gas_limit = int(gas_limits["estimatedGasFeeBaseAmount"])
    base_gas_limit += int(gas_limits["estimatedGasFeePerOraclePrice"]) * int(oracle_price_count)
    multiplier_factor = int(gas_limits["estimatedFeeMultiplierFactor"])
    gas_limit = base_gas_limit + apply_factor(int(estimated_gas_limit), multiplier_factor)

    fee_per_exec = int(gas_limit) * int(gas_price)

    if min_execution_fee_usd_30 is not None:
        min_gas_cost = convert_to_token_amount(
            int(min_execution_fee_usd_30),
            int(native_token["decimals"]),
            int(native_token["prices"]["minPrice"]),
        )
        if min_gas_cost is not None and min_gas_cost > fee_per_exec:
            fee_per_exec = int(min_gas_cost)

    if max_execution_fee_token_amount is not None and fee_per_exec > int(max_execution_fee_token_amount):
        fee_per_exec = int(max_execution_fee_token_amount)

    fee = fee_per_exec * int(number_of_parts)
    if execution_fee_buffer_bps and execution_fee_buffer_bps > 0:
        fee = (fee * (10000 + int(execution_fee_buffer_bps))) // 10000

    return ExecutionFee(fee_token_amount=int(fee), gas_limit=int(gas_limit))

