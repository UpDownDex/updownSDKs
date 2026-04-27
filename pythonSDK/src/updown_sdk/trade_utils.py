"""
Helpers mirroring TS `utils/prices.ts` and `utils/trade/trade.ts` slippage helpers
used by decrease / increase order builders.
"""

from __future__ import annotations

from typing import Optional

BPS = 10000
MAX_UINT256 = 2**256 - 1


def get_should_use_max_price(is_increase: bool, is_long: bool) -> bool:
    # TS getShouldUseMaxPrice
    return is_long if is_increase else (not is_long)


def get_mark_price(prices: dict, *, is_increase: bool, is_long: bool) -> int:
    use_max = get_should_use_max_price(is_increase, is_long)
    key = "maxPrice" if use_max else "minPrice"
    return int(prices[key])


def apply_slippage_to_price(allowed_slippage_bps: int, price: int, *, is_increase: bool, is_long: bool) -> int:
    # TS applySlippageToPrice
    should_increase_price = get_should_use_max_price(is_increase, is_long)
    slip = int(allowed_slippage_bps)
    bps = BPS + slip if should_increase_price else BPS - slip
    return (int(price) * bps) // BPS


def get_entry_price(size_in_usd: int, size_in_tokens: int, index_decimals: int) -> Optional[int]:
    # TS getEntryPrice (sizeInUsd * 10^decimals / sizeInTokens)
    if size_in_tokens <= 0:
        return None
    return (int(size_in_usd) * (10**int(index_decimals))) // int(size_in_tokens)


def round_up_div(a: int, b: int) -> int:
    if b <= 0:
        return 0
    return (int(a) + int(b) - 1) // int(b)


def trigger_price_from_percent(percent_str: str, current_price: int) -> int:
    # TS calculateTriggerPriceFromPercent
    percent_num = float(percent_str)
    mult = int(round((1 + percent_num) * 10**18))
    return (int(current_price) * mult) // 10**18
