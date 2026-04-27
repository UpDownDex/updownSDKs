from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .impact import (
    get_acceptable_price_info,
    get_default_acceptable_price_impact_bps,
    get_net_price_impact_delta_usd_for_decrease,
)
from .market_store import MarketStore
from .trade_utils import MAX_UINT256


@dataclass(frozen=True)
class DecreaseAmounts:
    size_delta_usd: int
    size_delta_in_tokens: int
    collateral_delta_amount: int
    trigger_price: int
    acceptable_price: int
    decrease_swap_type: int
    trigger_order_type: Optional[int]


ORDER_TYPE_LIMIT_DECREASE = 5
ORDER_TYPE_STOP_LOSS_DECREASE = 6
DECREASE_SWAP_NO_SWAP = 0


def _round_up_div(a: int, b: int) -> int:
    if b <= 0:
        return 0
    return (int(a) + int(b) - 1) // int(b)


def get_decrease_position_amounts(
    *,
    market_store: MarketStore,
    market_address: str,
    index_prices: dict,
    index_decimals: int,
    position_size_in_usd: int,
    position_size_in_tokens: int,
    position_collateral_amount: int,
    pending_impact_amount: int = 0,
    close_size_usd: int,
    is_long: bool,
    trigger_price: Optional[int] = None,
    trigger_order_type: Optional[int] = None,
    acceptable_price_impact_buffer_bps: int = 50,
    fixed_acceptable_price_impact_bps: Optional[int] = None,
    is_set_acceptable_price_impact_enabled: bool = True,
) -> DecreaseAmounts:
    """
    Deterministic core port of TS `getDecreasePositionAmounts` sufficient to match
    TS acceptablePrice / sizeDeltaInTokens / trigger behavior for swapPath=[] (NoSwap).

    Notes:
    - This intentionally focuses on values that change the on-chain order payload hash.
    - It uses TS price impact math (PricingUtils) via DataStore keys.
    """
    size_delta_usd = int(close_size_usd)
    if size_delta_usd <= 0:
        return DecreaseAmounts(
            size_delta_usd=0,
            size_delta_in_tokens=0,
            collateral_delta_amount=0,
            trigger_price=0,
            acceptable_price=0,
            decrease_swap_type=DECREASE_SWAP_NO_SWAP,
            trigger_order_type=None,
        )

    # trigger / mark price selection matches TS decrease.ts early section
    is_trigger = trigger_order_type is not None
    if is_trigger:
        idx_price = int(trigger_price or 0)
        trigger_out = int(trigger_price or 0)
    else:
        # TS getMarkPrice({isIncrease:false,isLong})
        should_use_max = (not is_long)  # decrease: isIncrease=false => use max if !isLong
        idx_price = int(index_prices["maxPrice" if should_use_max else "minPrice"])
        trigger_out = 0

    # sizeDeltaInTokens logic (with minimal full-close shortcut)
    # TS full-close has more checks; the earliest deterministic one is remaining size < 1 USD.
    one_usd = 10**30
    is_full_close = (int(position_size_in_usd) - int(size_delta_usd)) < int(one_usd)
    if is_full_close:
        size_delta_usd = int(position_size_in_usd)
        size_delta_tokens = int(position_size_in_tokens)
        collateral_delta_amount = int(position_collateral_amount)
    else:
        if position_size_in_usd <= 0:
            size_delta_tokens = 0
        elif is_long:
            size_delta_tokens = _round_up_div(int(position_size_in_tokens) * int(size_delta_usd), int(position_size_in_usd))
        else:
            # TS uses mulDiv (rounding down)
            size_delta_tokens = (int(position_size_in_tokens) * int(size_delta_usd)) // int(position_size_in_usd)
        collateral_delta_amount = 0

    store = market_store.get_market_impact_store(market_address)
    base = get_acceptable_price_info(
        store=store,
        is_increase=False,
        is_long=bool(is_long),
        index_price=int(idx_price),
        size_delta_usd=int(size_delta_usd),
        max_negative_price_impact_bps=None,
    )

    # TS also computes net impact for collateral accounting / full-close decisions.
    # We compute it here to keep the same deterministic chain; downstream callers may use it later.
    _net = get_net_price_impact_delta_usd_for_decrease(
        store=store,
        size_in_usd=int(position_size_in_usd),
        pending_impact_amount=int(pending_impact_amount),
        size_delta_usd=int(size_delta_usd),
        price_impact_delta_usd=int(base.price_impact_delta_usd),
        index_decimals=int(index_decimals),
        index_min_price=int(index_prices["minPrice"]),
        index_max_price=int(index_prices["maxPrice"]),
    )
    _ = _net

    acceptable_price = int(base.acceptable_price)

    if is_trigger:
        if (not is_set_acceptable_price_impact_enabled) or int(trigger_order_type) == ORDER_TYPE_STOP_LOSS_DECREASE:
            acceptable_price = 0 if is_long else int(MAX_UINT256)
        else:
            max_neg_bps = fixed_acceptable_price_impact_bps
            if max_neg_bps is None:
                max_neg_bps = get_default_acceptable_price_impact_bps(
                    is_increase=False,
                    is_long=bool(is_long),
                    index_price=int(idx_price),
                    size_delta_usd=int(size_delta_usd),
                    price_impact_delta_usd=int(base.price_impact_delta_usd),
                    buffer_bps=int(acceptable_price_impact_buffer_bps),
                )
            trig = get_acceptable_price_info(
                store=store,
                is_increase=False,
                is_long=bool(is_long),
                index_price=int(idx_price),
                size_delta_usd=int(size_delta_usd),
                max_negative_price_impact_bps=int(max_neg_bps),
            )
            acceptable_price = int(trig.acceptable_price)

    return DecreaseAmounts(
        size_delta_usd=int(size_delta_usd),
        size_delta_in_tokens=int(size_delta_tokens),
        collateral_delta_amount=int(collateral_delta_amount),
        trigger_price=int(trigger_out),
        acceptable_price=int(acceptable_price),
        decrease_swap_type=DECREASE_SWAP_NO_SWAP,
        trigger_order_type=int(trigger_order_type) if trigger_order_type is not None else None,
    )

