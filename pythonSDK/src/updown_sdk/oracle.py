from __future__ import annotations

from dataclasses import asdict
from typing import List

import requests

from .types import Ticker


def _join_url(base: str, path: str) -> str:
    base = base.rstrip("/")
    if not path.startswith("/"):
        path = "/" + path
    return base + path


class Oracle:
    def __init__(self, oracle_url: str):
        self._oracle_url = oracle_url
        # Avoid inheriting proxy env that can break access in some environments.
        self._session = requests.Session()
        self._session.trust_env = False

    def get_tickers(self) -> List[Ticker]:
        # Mirror TS behavior: oracleUrl + "/tickers"
        url = _join_url(self._oracle_url, "/tickers")
        res = self._session.get(url, timeout=20)
        res.raise_for_status()
        data = res.json()
        # API returns list[dict]
        tickers: List[Ticker] = []
        for item in data:
            tickers.append(
                Ticker(
                    token_address=item["tokenAddress"],
                    token_symbol=item.get("tokenSymbol", ""),
                    min_price=int(item["minPrice"]),
                    max_price=int(item["maxPrice"]),
                    updated_at=int(item.get("updatedAt") or item.get("timestamp") or 0),
                    chain_id=int(item["chainId"]) if "chainId" in item and item["chainId"] is not None else None,
                )
            )
        return tickers

    def dump_tickers(self) -> list[dict]:
        return [asdict(t) for t in self.get_tickers()]

