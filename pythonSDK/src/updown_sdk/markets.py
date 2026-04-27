from __future__ import annotations

from dataclasses import asdict
import json
import os
from typing import List

from .types import Market


class Markets:
    """
    Query-first port.

    TS source of truth for markets lives in `tsSDK/src/configs/markets.ts`.
    For this first Python iteration we read CELO markets directly (same set as TS config).
    """

    def __init__(self, chain_id: int):
        self._chain_id = chain_id

    def get_markets(self) -> List[Market]:
        # Prefer generated config JSON (exported from TS).
        cfg_path = os.path.join(os.path.dirname(__file__), "config", "markets.json")
        if os.path.exists(cfg_path):
            with open(cfg_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            items = data.get(str(self._chain_id), [])
            return [
                Market(
                    market_token_address=m["marketTokenAddress"],
                    index_token_address=m["indexTokenAddress"],
                    long_token_address=m["longTokenAddress"],
                    short_token_address=m["shortTokenAddress"],
                    name=m.get("name", ""),
                )
                for m in items
            ]

        # Fallback to embedded CELO list (legacy).
        if self._chain_id == 42220:
            return _CELO_MARKETS
        raise NotImplementedError(f"Markets config not yet ported for chain_id={self._chain_id}")

    def dump_markets(self) -> List[dict]:
        return [asdict(m) for m in self.get_markets()]


# --- Minimal embedded markets (CELO) ---
# Copied from TS `src/configs/markets.ts` (CELO section).
_CELO_MARKETS: List[Market] = [
    Market(
        market_token_address="0x38995e0D3c25EE78D45A45A1311A2CA0544b0E6B",
        index_token_address="0x2350246BAE36EE301B108cA8fE58D795A8DBdb4e",
        long_token_address="0x2350246BAE36EE301B108cA8fE58D795A8DBdb4e",
        short_token_address="0xd96a1ac57a180a3819633bCE3dC602Bd8972f595",
        name="EURm/USD [EURm-USDT]",
    ),
    Market(
        market_token_address="0xDbBe49A7165F40C79D00bCD3B456AaE887c3d771",
        index_token_address="0x57433eD8eC1FAD60b8E1dcFdD1fBD56aBA19C04C",
        long_token_address="0x57433eD8eC1FAD60b8E1dcFdD1fBD56aBA19C04C",
        short_token_address="0xd96a1ac57a180a3819633bCE3dC602Bd8972f595",
        name="BTC/USD [BTC-USDT]",
    ),
    Market(
        market_token_address="0x3d069FFd681B68BF281077516dd9006C2e4c818A",
        index_token_address="0x4C2675e9067Cd7Fc859165AC5F37f1D82d825A1E",
        long_token_address="0x4C2675e9067Cd7Fc859165AC5F37f1D82d825A1E",
        short_token_address="0xd96a1ac57a180a3819633bCE3dC602Bd8972f595",
        name="ETH/USD [ETH-USDT]",
    ),
    Market(
        market_token_address="0x1f39c2B41af79973b25F65E7a4234bc22aF250D7",
        index_token_address="0x5B1B6DCB4E907b9755E27Db88bD62B9750a13C60",
        long_token_address="0x5B1B6DCB4E907b9755E27Db88bD62B9750a13C60",
        short_token_address="0xd96a1ac57a180a3819633bCE3dC602Bd8972f595",
        name="CELO/USD [CELO-USDT]",
    ),
    Market(
        market_token_address="0xaaB05004Ac382adE5E70eEFC3C67035b5F31b990",
        index_token_address="0x29206D4B6183A29Ef5B68494B0850330e98f27F4",
        long_token_address="0x29206D4B6183A29Ef5B68494B0850330e98f27F4",
        short_token_address="0xd96a1ac57a180a3819633bCE3dC602Bd8972f595",
        name="JPYm/USD [JPYm-USDT]",
    ),
    Market(
        market_token_address="0x1B07C05466D7dC15244969EbCf23520Aba4df9e7",
        index_token_address="0xEb8A6C14e625A05F06eA914Db627dd65175b4505",
        long_token_address="0xEb8A6C14e625A05F06eA914Db627dd65175b4505",
        short_token_address="0xd96a1ac57a180a3819633bCE3dC602Bd8972f595",
        name="NGNm/USD [NGNm-USDT]",
    ),
    Market(
        market_token_address="0x22476a639D1bBDDE1919A226347360b32A2385Fe",
        index_token_address="0x91CA0318Fc30D728640f0E6329205eE1F538F17B",
        long_token_address="0x91CA0318Fc30D728640f0E6329205eE1F538F17B",
        short_token_address="0xd96a1ac57a180a3819633bCE3dC602Bd8972f595",
        name="AUDm/USD [AUDm-USDT]",
    ),
    Market(
        market_token_address="0xc439330b3D59Be316936Ff62d1d22b377656Fc20",
        index_token_address="0x7Ef503a2722cdfa7E99f2A59771f7E2390c2DF76",
        long_token_address="0x7Ef503a2722cdfa7E99f2A59771f7E2390c2DF76",
        short_token_address="0xd96a1ac57a180a3819633bCE3dC602Bd8972f595",
        name="GBPm/USD [GBPm-USDT]",
    ),
]

