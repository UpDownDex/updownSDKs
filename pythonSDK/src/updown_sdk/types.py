from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class OperationType(str, Enum):
    """
    Mirror TS `OperationType` in tsSDK/src/modules/operations/types.ts.
    Values are lowercase strings used in env / scripts.
    """

    OPEN = "open"
    INCREASE = "increase"
    DECREASE = "decrease"
    CLOSE = "close"
    TAKE_PROFIT = "takeprofit"
    STOP_LOSS = "stoploss"
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"


_OPERATION_TYPE_SET = frozenset(m.value for m in OperationType)


def parse_operation_type(raw: str) -> OperationType:
    """
    Normalize env/user input: strip + lowercase, then validate against OperationType values.
    Mirrors TS `parseOperationType`.
    """
    key = raw.strip().lower()
    if key not in _OPERATION_TYPE_SET:
        raise ValueError(f"Unknown operation type: {raw}")
    return OperationType(key)


# TS export name (tsSDK `parseOperationType`) for parity when porting callers.
parseOperationType = parse_operation_type


@dataclass(frozen=True)
class updownSdkConfig:
    chain_id: int
    rpc_url: str
    oracle_url: str
    subsquid_url: Optional[str] = None
    account: Optional[str] = None
    # Optional overrides (same concept as TS SDK)
    tokens: Optional[dict[str, dict[str, Any]]] = None
    markets: Optional[dict[str, dict[str, Any]]] = None


@dataclass(frozen=True)
class Market:
    market_token_address: str
    index_token_address: str
    long_token_address: str
    short_token_address: str
    name: str = ""


@dataclass(frozen=True)
class Ticker:
    token_address: str
    token_symbol: str
    min_price: int
    max_price: int
    updated_at: int
    chain_id: int | None = None

