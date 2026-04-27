from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .market_store import MarketImpactStore

USD_DECIMALS = 30
PRECISION = 10**30


def _abs(x: int) -> int:
    return x if x >= 0 else -x


def _js_round(x: float) -> int:
    """
    JS Math.round semantics:
    - rounds to nearest integer
    - ties (.5) go toward +infinity (i.e. away from -infinity)
    """
    import math

    if x >= 0:
        return int(math.floor(x + 0.5))
    # for negatives: Math.round(-1.5) == -1
    return int(math.ceil(x - 0.5))


def apply_factor(value: int, factor_1e30: int) -> int:
    return (int(value) * int(factor_1e30)) // PRECISION


def convert_to_usd(amount: int, token_decimals: int, price: int) -> Optional[int]:
    if price <= 0:
        return None
    return (int(amount) * int(price)) // (10**int(token_decimals))


def mul_div(a: int, b: int, c: int, *, round_up: bool = False) -> int:
    """
    Deterministic port of `bigMath.mulDiv` subset.
    If round_up=True, rounds away from zero for negative values as TS does in some paths.
    """
    if c == 0:
        raise ZeroDivisionError("mul_div division by zero")
    num = int(a) * int(b)
    if not round_up:
        return int(num // int(c))
    # round up magnitude (used when value is negative in TS paths)
    if num >= 0:
        return int((num + int(c) - 1) // int(c))
    # negative: ceil(num/c)
    return -int((_abs(num) + int(c) - 1) // int(c))


@dataclass(frozen=True)
class PriceImpactResult:
    price_impact_delta_usd: int
    balance_was_improved: bool


def apply_impact_factor(diff_usd_30: int, factor: int, exponent_1e30: int) -> int:
    """
    Port of TS applyImpactFactor (uses IEEE754 double pow + Math.round).
    Inputs/outputs use 30-decimal USD.
    """
    # TS: const _diff = Number(diff) / 1e30; const _exponent = Number(exponent)/1e30
    diff_f = float(int(diff_usd_30)) / 10**30
    exp_f = float(int(exponent_1e30)) / 10**30
    pow_f = diff_f**exp_f
    rounded = _js_round(pow_f * 10**30)
    # TS: result = (result * factor) / 1e30
    return (int(rounded) * int(factor)) // 10**30


def calculate_impact_for_same_side_rebalance(
    *, current_diff: int, next_diff: int, has_positive_impact: bool, factor: int, exponent_factor: int
) -> int:
    current_impact = apply_impact_factor(current_diff, factor, exponent_factor)
    next_impact = apply_impact_factor(next_diff, factor, exponent_factor)
    delta = _abs(current_impact - next_impact)
    return int(delta if has_positive_impact else -delta)


def calculate_impact_for_crossover_rebalance(
    *, current_diff: int, next_diff: int, factor_positive: int, factor_negative: int, exponent_factor: int
) -> int:
    positive_impact = apply_impact_factor(current_diff, factor_positive, exponent_factor)
    negative_impact = apply_impact_factor(next_diff, factor_negative, exponent_factor)
    delta = _abs(positive_impact - negative_impact)
    return int(delta if positive_impact > negative_impact else -delta)


def get_price_impact_usd(
    *,
    current_long_usd: int,
    current_short_usd: int,
    next_long_usd: int,
    next_short_usd: int,
    factor_positive: int,
    factor_negative: int,
    exponent_factor: int,
    fallback_to_zero: bool = False,
) -> PriceImpactResult:
    if next_long_usd < 0 or next_short_usd < 0:
        if fallback_to_zero:
            return PriceImpactResult(price_impact_delta_usd=0, balance_was_improved=False)
        raise ValueError("Negative pool/open-interest amount")

    current_diff = _abs(int(current_long_usd) - int(current_short_usd))
    next_diff = _abs(int(next_long_usd) - int(next_short_usd))

    is_same_side_rebalance = (current_long_usd < current_short_usd) == (next_long_usd < next_short_usd)
    balance_was_improved = next_diff < current_diff

    if is_same_side_rebalance:
        has_positive = next_diff < current_diff
        factor = int(factor_positive) if has_positive else int(factor_negative)
        impact = calculate_impact_for_same_side_rebalance(
            current_diff=current_diff,
            next_diff=next_diff,
            has_positive_impact=has_positive,
            factor=factor,
            exponent_factor=int(exponent_factor),
        )
    else:
        impact = calculate_impact_for_crossover_rebalance(
            current_diff=current_diff,
            next_diff=next_diff,
            factor_positive=int(factor_positive),
            factor_negative=int(factor_negative),
            exponent_factor=int(exponent_factor),
        )

    return PriceImpactResult(price_impact_delta_usd=int(impact), balance_was_improved=bool(balance_was_improved))


def _next_open_interest_params(*, current_long_usd: int, current_short_usd: int, usd_delta: int, is_long: bool):
    next_long = int(current_long_usd)
    next_short = int(current_short_usd)
    if is_long:
        next_long = next_long + int(usd_delta)
    else:
        next_short = next_short + int(usd_delta)
    return current_long_usd, current_short_usd, next_long, next_short


def get_capped_position_impact_usd(
    *,
    store: MarketImpactStore,
    size_delta_usd: int,
    is_long: bool,
    is_increase: bool,
    should_cap_negative_impact: bool = False,
    fallback_to_zero: bool = False,
) -> PriceImpactResult:
    """
    Port of TS getCappedPositionImpactUsd (without virtual inventory branch).
    """
    signed_delta = int(size_delta_usd) if is_increase else -int(size_delta_usd)
    curL, curS, nextL, nextS = _next_open_interest_params(
        current_long_usd=int(store.long_interest_usd),
        current_short_usd=int(store.short_interest_usd),
        usd_delta=signed_delta,
        is_long=bool(is_long),
    )

    base = get_price_impact_usd(
        current_long_usd=curL,
        current_short_usd=curS,
        next_long_usd=nextL,
        next_short_usd=nextS,
        factor_positive=int(store.position_impact_factor_positive),
        factor_negative=int(store.position_impact_factor_negative),
        exponent_factor=int(store.position_impact_exponent_factor),
        fallback_to_zero=fallback_to_zero,
    )

    if base.price_impact_delta_usd < 0 and not should_cap_negative_impact:
        return base

    # cap by maxPositionImpactFactors (uses absolute sizeDeltaUsd)
    max_pos = int(store.max_position_impact_factor_positive)
    max_neg = int(store.max_position_impact_factor_negative)
    if max_pos > max_neg:
        max_pos = max_neg

    max_factor = max_pos if base.price_impact_delta_usd > 0 else max_neg
    max_usd = apply_factor(_abs(int(signed_delta)), int(max_factor))
    if _abs(int(base.price_impact_delta_usd)) > int(max_usd):
        capped = int(max_usd if base.price_impact_delta_usd > 0 else -max_usd)
    else:
        capped = int(base.price_impact_delta_usd)

    return PriceImpactResult(price_impact_delta_usd=capped, balance_was_improved=base.balance_was_improved)


@dataclass(frozen=True)
class AcceptablePriceInfo:
    acceptable_price: int
    acceptable_price_delta_bps: int
    price_impact_delta_usd: int
    balance_was_improved: bool


def get_acceptable_price_by_price_impact(
    *, is_increase: bool, is_long: bool, index_price: int, size_delta_usd: int, price_impact_delta_usd: int
) -> tuple[int, int]:
    # TS getAcceptablePriceByPriceImpact
    should_flip = (is_increase and is_long) or ((not is_increase) and (not is_long))
    # TS: const priceImpactForPriceAdjustment = shouldFlip ? priceImpactDeltaUsd * -1 : priceImpactDeltaUsd
    adj = -int(price_impact_delta_usd) if should_flip else int(price_impact_delta_usd)
    acceptable = (int(index_price) * (int(size_delta_usd) + int(adj))) // int(size_delta_usd)
    price_delta = (int(index_price) - int(acceptable)) * (1 if should_flip else -1)
    delta_bps = 0 if index_price == 0 else (price_delta * 10000) // int(index_price)
    return int(acceptable), int(delta_bps)


def get_acceptable_price_info(
    *,
    store: MarketImpactStore,
    is_increase: bool,
    is_long: bool,
    index_price: int,
    size_delta_usd: int,
    max_negative_price_impact_bps: Optional[int] = None,
) -> AcceptablePriceInfo:
    """
    Port of TS getAcceptablePriceInfo (only the path used by decrease.ts / increase.ts).
    """
    if int(size_delta_usd) <= 0 or int(index_price) == 0:
        return AcceptablePriceInfo(
            acceptable_price=int(index_price),
            acceptable_price_delta_bps=0,
            price_impact_delta_usd=0,
            balance_was_improved=False,
        )

    # Trigger / limit override path
    if max_negative_price_impact_bps is not None and int(max_negative_price_impact_bps) > 0:
        # TS uses bps adjustment directly
        should_flip = (is_increase and is_long) or ((not is_increase) and (not is_long))
        price_delta = (int(index_price) * int(max_negative_price_impact_bps)) // 10000
        price_delta = -price_delta if should_flip else price_delta
        acceptable = int(index_price) - int(price_delta)
        acceptable_delta_bps = -int(max_negative_price_impact_bps)
        # priceImpactDeltaUsd derived from acceptable
        should_flip_price_diff = (not is_long) if is_increase else bool(is_long)
        pd = (int(index_price) - int(acceptable)) * (-1 if should_flip_price_diff else 1)
        price_impact_delta_usd = 0 if acceptable == 0 else (int(size_delta_usd) * int(pd)) // int(acceptable)
        return AcceptablePriceInfo(
            acceptable_price=int(acceptable),
            acceptable_price_delta_bps=int(acceptable_delta_bps),
            price_impact_delta_usd=int(price_impact_delta_usd),
            balance_was_improved=False,
        )

    capped = get_capped_position_impact_usd(
        store=store,
        size_delta_usd=int(size_delta_usd),
        is_long=bool(is_long),
        is_increase=bool(is_increase),
        should_cap_negative_impact=False,
        fallback_to_zero=not bool(is_increase),
    )

    # uncapped again for acceptable price (TS does a second call; same args in their code path)
    uncapped_for_accept = get_capped_position_impact_usd(
        store=store,
        size_delta_usd=int(size_delta_usd),
        is_long=bool(is_long),
        is_increase=bool(is_increase),
        should_cap_negative_impact=False,
        fallback_to_zero=not bool(is_increase),
    )

    acceptable, acceptable_delta_bps = get_acceptable_price_by_price_impact(
        is_increase=bool(is_increase),
        is_long=bool(is_long),
        index_price=int(index_price),
        size_delta_usd=int(size_delta_usd),
        price_impact_delta_usd=int(uncapped_for_accept.price_impact_delta_usd),
    )

    return AcceptablePriceInfo(
        acceptable_price=int(acceptable),
        acceptable_price_delta_bps=int(acceptable_delta_bps),
        price_impact_delta_usd=int(capped.price_impact_delta_usd),
        balance_was_improved=bool(capped.balance_was_improved),
    )


def get_default_acceptable_price_impact_bps(
    *,
    is_increase: bool,
    is_long: bool,
    index_price: int,
    size_delta_usd: int,
    price_impact_delta_usd: int,
    buffer_bps: int = 50,  # DEFAULT_ACCEPTABLE_PRICE_IMPACT_BUFFER
) -> int:
    if int(price_impact_delta_usd) > 0:
        return int(buffer_bps)

    acceptable, delta_bps = get_acceptable_price_by_price_impact(
        is_increase=bool(is_increase),
        is_long=bool(is_long),
        index_price=int(index_price),
        size_delta_usd=int(size_delta_usd),
        price_impact_delta_usd=int(price_impact_delta_usd),
    )
    _ = acceptable
    if int(delta_bps) < 0:
        return _abs(int(delta_bps)) + int(buffer_bps)
    return int(buffer_bps)


@dataclass(frozen=True)
class ProportionalPendingImpact:
    proportional_pending_impact_delta_amount: int
    proportional_pending_impact_delta_usd: int


def get_proportional_pending_impact_values(
    *,
    size_in_usd: int,
    pending_impact_amount: int,
    size_delta_usd: int,
    index_decimals: int,
    index_min_price: int,
    index_max_price: int,
) -> ProportionalPendingImpact:
    # TS getProportionalPendingImpactValues
    if int(size_delta_usd) == 0 or int(size_in_usd) == 0:
        amt = 0
    else:
        amt = mul_div(
            int(pending_impact_amount),
            int(size_delta_usd),
            int(size_in_usd),
            round_up=(int(pending_impact_amount) < 0),
        )

    price = int(index_min_price) if amt > 0 else int(index_max_price)
    usd = convert_to_usd(int(amt), int(index_decimals), int(price)) or 0
    return ProportionalPendingImpact(
        proportional_pending_impact_delta_amount=int(amt),
        proportional_pending_impact_delta_usd=int(usd),
    )


def cap_position_impact_usd_by_max_impact_pool(
    *,
    position_impact_pool_amount: int,
    index_decimals: int,
    index_min_price: int,
    position_impact_delta_usd: int,
) -> int:
    # TS capPositionImpactUsdByMaxImpactPool
    if int(position_impact_delta_usd) < 0:
        return int(position_impact_delta_usd)
    max_usd = convert_to_usd(int(position_impact_pool_amount), int(index_decimals), int(index_min_price)) or 0
    return int(min(int(position_impact_delta_usd), int(max_usd)))


@dataclass(frozen=True)
class NetImpactForDecrease:
    total_impact_delta_usd: int
    proportional_pending_impact_delta_usd: int
    price_impact_diff_usd: int


def get_price_impact_diff_usd(*, total_impact_delta_usd: int, store: MarketImpactStore, size_delta_usd: int) -> int:
    # TS getPriceImpactDiffUsd
    if int(total_impact_delta_usd) > 0:
        return 0
    max_pos = int(store.max_position_impact_factor_positive)
    max_neg = int(store.max_position_impact_factor_negative)
    if max_pos > max_neg:
        max_pos = max_neg
    max_negative_impact_usd = -apply_factor(int(size_delta_usd), int(max_neg))
    if int(total_impact_delta_usd) < int(max_negative_impact_usd):
        return int(max_negative_impact_usd - int(total_impact_delta_usd))
    return 0


def get_net_price_impact_delta_usd_for_decrease(
    *,
    store: MarketImpactStore,
    size_in_usd: int,
    pending_impact_amount: int,
    size_delta_usd: int,
    price_impact_delta_usd: int,
    index_decimals: int,
    index_min_price: int,
    index_max_price: int,
) -> NetImpactForDecrease:
    prop = get_proportional_pending_impact_values(
        size_in_usd=int(size_in_usd),
        pending_impact_amount=int(pending_impact_amount),
        size_delta_usd=int(size_delta_usd),
        index_decimals=int(index_decimals),
        index_min_price=int(index_min_price),
        index_max_price=int(index_max_price),
    )

    total = int(price_impact_delta_usd) + int(prop.proportional_pending_impact_delta_usd)
    diff = get_price_impact_diff_usd(total_impact_delta_usd=int(total), store=store, size_delta_usd=int(size_delta_usd))

    if total > 0:
        # cap by max price impact factor (uses sizeDeltaUsd)
        max_pos = int(store.max_position_impact_factor_positive)
        max_neg = int(store.max_position_impact_factor_negative)
        if max_pos > max_neg:
            max_pos = max_neg
        max_usd = apply_factor(int(size_delta_usd), int(max_pos))
        if _abs(total) > int(max_usd):
            total = int(max_usd if total > 0 else -max_usd)

    total = cap_position_impact_usd_by_max_impact_pool(
        position_impact_pool_amount=int(store.position_impact_pool_amount),
        index_decimals=int(index_decimals),
        index_min_price=int(index_min_price),
        position_impact_delta_usd=int(total),
    )

    return NetImpactForDecrease(
        total_impact_delta_usd=int(total),
        proportional_pending_impact_delta_usd=int(prop.proportional_pending_impact_delta_usd),
        price_impact_diff_usd=int(diff),
    )

