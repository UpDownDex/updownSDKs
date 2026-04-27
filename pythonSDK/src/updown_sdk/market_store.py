from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict

from web3 import Web3

from .abis import DATA_STORE_ABI
from .contracts import get_contracts


@dataclass(frozen=True)
class MarketImpactStore:
    long_interest_usd: int
    short_interest_usd: int
    position_impact_factor_positive: int
    position_impact_factor_negative: int
    position_impact_exponent_factor: int
    max_position_impact_factor_positive: int
    max_position_impact_factor_negative: int
    position_impact_pool_amount: int


def _load_json_config(name: str) -> Dict[str, Any]:
    cfg_path = os.path.join(os.path.dirname(__file__), "config", name)
    with open(cfg_path, "r", encoding="utf-8") as f:
        return json.load(f)


class MarketStore:
    """
    Minimal, deterministic subset of TS MarketsInfo required by `utils/trade/decrease.ts`
    acceptable price calculations (price impact).

    We read hashed DataStore keys prebuilt in TS and exported into pythonSDK config:
    - `config/marketConfigKeys.json`
    - `config/marketValuesKeys.json`
    """

    def __init__(self, w3: Web3, chain_id: int):
        self._w3 = w3
        self._chain_id = int(chain_id)
        c = get_contracts(chain_id)
        self._data_store = self._w3.eth.contract(address=Web3.to_checksum_address(c.data_store), abi=DATA_STORE_ABI)
        self._cfg_keys = _load_json_config("marketConfigKeys.json")
        self._val_keys = _load_json_config("marketValuesKeys.json")

    def _get_uint(self, key_hex: str) -> int:
        return int(self._data_store.functions.getUint(Web3.to_bytes(hexstr=key_hex)).call())

    def get_market_impact_store(self, market_address: str) -> MarketImpactStore:
        chain = self._cfg_keys.get(str(self._chain_id), {})
        cfg = chain.get(market_address.lower())
        if not cfg:
            raise KeyError(f"Missing market config keys for chain={self._chain_id} market={market_address}")

        vals_chain = self._val_keys.get(str(self._chain_id), {})
        vals = vals_chain.get(market_address.lower())
        if not vals:
            raise KeyError(f"Missing market values keys for chain={self._chain_id} market={market_address}")

        long_interest_usd = self._get_uint(vals["longInterestUsingLongToken"]) + self._get_uint(vals["longInterestUsingShortToken"])
        short_interest_usd = self._get_uint(vals["shortInterestUsingLongToken"]) + self._get_uint(vals["shortInterestUsingShortToken"])

        return MarketImpactStore(
            long_interest_usd=int(long_interest_usd),
            short_interest_usd=int(short_interest_usd),
            position_impact_factor_positive=self._get_uint(cfg["positionImpactFactorPositive"]),
            position_impact_factor_negative=self._get_uint(cfg["positionImpactFactorNegative"]),
            position_impact_exponent_factor=self._get_uint(cfg["positionImpactExponentFactor"]),
            max_position_impact_factor_positive=self._get_uint(cfg["maxPositionImpactFactorPositive"]),
            max_position_impact_factor_negative=self._get_uint(cfg["maxPositionImpactFactorNegative"]),
            position_impact_pool_amount=self._get_uint(vals["positionImpactPoolAmount"]),
        )

