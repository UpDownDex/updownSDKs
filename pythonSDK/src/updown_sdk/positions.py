from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from web3 import Web3

from .abis import SYNTHETICS_READER_ABI
from .contracts import get_contracts


@dataclass(frozen=True)
class Position:
    key: str  # "account:market:collateral:isLong" (TS-style readable key)
    contract_key: str | None  # bytes32 from getAccountPositionInfoList when available
    account: str
    market: str
    collateral_token: str
    is_long: bool
    size_in_usd: int
    size_in_tokens: int
    collateral_amount: int
    pending_impact_amount: int
    raw: Any


class Positions:
    def __init__(self, w3: Web3, chain_id: int, account: Optional[str], oracle):
        self._w3 = w3
        self._chain_id = chain_id
        self._default_account = account
        self._oracle = oracle

        c = get_contracts(chain_id)
        self._reader = self._w3.eth.contract(
            address=Web3.to_checksum_address(c.synthetics_reader),
            abi=SYNTHETICS_READER_ABI,
        )

    @staticmethod
    def _position_key(account: str, market: str, collateral: str, is_long: bool) -> str:
        return f"{account}:{market}:{collateral}:{str(is_long).lower()}"

    def _build_market_prices(self, markets: List[dict]) -> Tuple[List[str], List[tuple]]:
        """
        Builds (marketsKeys, marketPrices) for getAccountPositionInfoList.

        We use oracle tickers *contract price* units directly (same inputs TS passes to the reader).
        """
        tickers = self._oracle.get_tickers()
        price_by_addr = {t.token_address.lower(): (t.min_price, t.max_price) for t in tickers}

        market_keys: List[str] = []
        market_prices: List[tuple] = []

        for m in markets:
            market_addr = Web3.to_checksum_address(m["market_token_address"])
            idx = m["index_token_address"]
            lng = m["long_token_address"]
            sht = m["short_token_address"]

            idx_p = price_by_addr.get(idx.lower())
            lng_p = price_by_addr.get(lng.lower())
            sht_p = price_by_addr.get(sht.lower())

            if not idx_p or not lng_p or not sht_p:
                continue

            market_keys.append(market_addr)
            market_prices.append(
                (
                    (int(idx_p[0]), int(idx_p[1])),
                    (int(lng_p[0]), int(lng_p[1])),
                    (int(sht_p[0]), int(sht_p[1])),
                )
            )

        return market_keys, market_prices

    def get_positions(
        self,
        *,
        account: Optional[str] = None,
        markets: Optional[List[dict]] = None,
        start: int = 0,
        end: int = 1000,
        prefer_info_list: bool = True,
    ) -> Dict[str, Position]:
        acct = account or self._default_account
        if not acct:
            return {}

        acct = Web3.to_checksum_address(acct)
        c = get_contracts(self._chain_id)

        # If markets not provided, caller should pass sdk.markets.dump_markets()
        markets = markets or []

        if prefer_info_list and markets:
            market_keys, market_prices = self._build_market_prices(markets)
            if market_keys:
                ui_fee_receiver = "0x0000000000000000000000000000000000000000"
                rows = self._reader.functions.getAccountPositionInfoList(
                    Web3.to_checksum_address(c.data_store),
                    Web3.to_checksum_address(c.referral_storage),
                    acct,
                    market_keys,
                    market_prices,
                    Web3.to_checksum_address(ui_fee_receiver),
                    start,
                    end,
                ).call()

                out: Dict[str, Position] = {}
                for row in rows:
                    # row: ReaderPositionUtils.PositionInfo
                    contract_key = Web3.to_hex(row[0])
                    position_tuple = row[1]
                    addresses = position_tuple[0]
                    numbers = position_tuple[1]
                    flags = position_tuple[2]

                    if int(numbers[7]) == 0:  # increasedAtTime == 0 -> empty
                        continue

                    key = self._position_key(addresses[0], addresses[1], addresses[2], bool(flags[0]))
                    out[key] = Position(
                        key=key,
                        contract_key=contract_key,
                        account=addresses[0],
                        market=addresses[1],
                        collateral_token=addresses[2],
                        is_long=bool(flags[0]),
                        size_in_usd=int(numbers[0]),
                        size_in_tokens=int(numbers[1]),
                        collateral_amount=int(numbers[2]),
                        pending_impact_amount=0,
                        raw={"row": row},
                    )
                return out

        # Fallback: getAccountPositions (does not require prices)
        rows = self._reader.functions.getAccountPositions(
            Web3.to_checksum_address(c.data_store),
            acct,
            start,
            end,
        ).call()

        out: Dict[str, Position] = {}
        for row in rows:
            addresses = row[0]
            numbers = row[1]
            flags = row[2]
            if int(numbers[7]) == 0:
                continue

            key = self._position_key(addresses[0], addresses[1], addresses[2], bool(flags[0]))
            out[key] = Position(
                key=key,
                contract_key=None,
                account=addresses[0],
                market=addresses[1],
                collateral_token=addresses[2],
                is_long=bool(flags[0]),
                size_in_usd=int(numbers[0]),
                size_in_tokens=int(numbers[1]),
                collateral_amount=int(numbers[2]),
                pending_impact_amount=0,
                raw=row,
            )

        return out

