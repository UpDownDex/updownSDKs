from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .types import Ticker


@dataclass(frozen=True)
class Token:
    address: str
    symbol: str
    decimals: int


class Tokens:
    def __init__(self, chain_id: int, oracle):
        self._chain_id = chain_id
        self._oracle = oracle
        self._cached: Optional[Tuple[Dict[str, dict], Optional[int]]] = None

    def _load_tokens_config(self) -> List[dict]:
        cfg_path = os.path.join(os.path.dirname(__file__), "config", "tokens.json")
        if not os.path.exists(cfg_path):
            return []
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(str(self._chain_id), [])

    def get_tokens_data(self) -> Tuple[Dict[str, dict], Optional[int]]:
        """
        Returns a minimal `tokensData`-like map keyed by tokenAddress, filtered to those with oracle prices.
        Also returns `pricesUpdatedAt` (best-effort: max(updatedAt) from tickers).
        """
        if self._cached is not None:
            return self._cached

        cfg_tokens = self._load_tokens_config()
        tickers: List[Ticker] = self._oracle.get_tickers()

        prices_updated_at: Optional[int] = None
        for t in tickers:
            if t.updated_at:
                prices_updated_at = max(prices_updated_at or 0, t.updated_at)

        price_by_addr = {t.token_address.lower(): t for t in tickers}

        tokens_data: Dict[str, dict] = {}
        wrapped_token_addr: Optional[str] = None
        native_token_addr: Optional[str] = None
        for tok in cfg_tokens:
            addr = tok.get("address")
            if not isinstance(addr, str):
                continue
            if tok.get("isWrapped"):
                wrapped_token_addr = addr
            if tok.get("isNative"):
                native_token_addr = addr
            ticker = price_by_addr.get(addr.lower())
            if not ticker:
                continue
            decimals = int(tok.get("decimals") or 0)
            # Mirror TS `parseContractPrice(priceItem.minPrice, tokenDecimals)`:
            # stored price is scaled by 10^tokenDecimals so convertToUsd(amount,decimals,price) works.
            min_price = int(ticker.min_price) * (10**decimals)
            max_price = int(ticker.max_price) * (10**decimals)
            tokens_data[addr] = {
                **tok,
                "prices": {
                    "minPrice": min_price,
                    "maxPrice": max_price,
                },
            }

        # Mirror TS behavior: if wrapped token has price and native (zeroAddress) doesn't, copy it.
        if wrapped_token_addr and native_token_addr:
            if wrapped_token_addr in tokens_data and native_token_addr not in tokens_data:
                wrapped = tokens_data[wrapped_token_addr]
                native_cfg = next((t for t in cfg_tokens if t.get("address") == native_token_addr), None)
                if native_cfg:
                    tokens_data[native_token_addr] = {
                        **native_cfg,
                        "prices": dict(wrapped["prices"]),
                    }
        self._cached = (tokens_data, prices_updated_at)
        return self._cached

    def get_token(self, address: str) -> dict:
        tokens_data, _ = self.get_tokens_data()
        t = tokens_data.get(address) or tokens_data.get(address.lower())  # best-effort
        if not t:
            # try case-insensitive scan
            for k, v in tokens_data.items():
                if k.lower() == address.lower():
                    return v
            raise KeyError(f"Token not found in tokensData: {address}")
        return t

    def to_wrapped_if_native(self, address: str) -> str:
        """
        Mirror TS `convertTokenAddress(..., 'wrapped')` for native CELO / ETH.
        """
        addr = (address or "").lower()
        if addr != "0x0000000000000000000000000000000000000000":
            return address
        cfg = self._load_tokens_config()
        for t in cfg:
            if t.get("isNative") and str(t.get("address", "")).lower() == addr:
                w = t.get("wrappedAddress")
                if w:
                    return str(w)
        raise ValueError("Native token address not configured with wrappedAddress in tokens.json")

    def get_token_by_address(self, market_address: str, kind: str) -> dict:
        """
        Helper for Operations: resolve index/long/short token from a market config.
        `kind` is one of: "index" | "long" | "short".
        """
        # Load markets config on-demand to avoid circular imports
        from .markets import Markets

        m = Markets(self._chain_id)
        markets = m.get_markets()
        market = next((x for x in markets if x.market_token_address.lower() == market_address.lower()), None)
        if not market:
            raise KeyError(f"Market not found: {market_address}")
        if kind == "index":
            return self.get_token(market.index_token_address)
        if kind == "long":
            return self.get_token(market.long_token_address)
        if kind == "short":
            return self.get_token(market.short_token_address)
        raise ValueError(f"Unknown kind={kind}")

