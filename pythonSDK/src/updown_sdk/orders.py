from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from web3 import Web3

from .abis import DATA_STORE_ABI, SYNTHETICS_READER_ABI
from .contracts import get_contracts
from .hash import account_order_list_key


@dataclass(frozen=True)
class Order:
    key: str  # bytes32 hex
    account: str
    callback_contract: str
    initial_collateral_token_address: str
    market_address: str
    decrease_position_swap_type: int
    receiver: str
    swap_path: list[str]
    contract_acceptable_price: int
    contract_trigger_price: int
    callback_gas_limit: int
    execution_fee: int
    initial_collateral_delta_amount: int
    min_output_amount: int
    size_delta_usd: int
    updated_at_time: int
    is_frozen: bool
    is_long: bool
    order_type: int
    should_unwrap_native_token: bool
    auto_cancel: bool
    data: list[str]
    ui_fee_receiver: str
    valid_from_time: int
    raw: Any


class Orders:
    def __init__(self, w3: Web3, chain_id: int, account: Optional[str]):
        self._w3 = w3
        self._chain_id = chain_id
        self._default_account = account

        c = get_contracts(chain_id)
        self._data_store = self._w3.eth.contract(
            address=Web3.to_checksum_address(c.data_store),
            abi=DATA_STORE_ABI,
        )
        self._reader = self._w3.eth.contract(
            address=Web3.to_checksum_address(c.synthetics_reader),
            abi=SYNTHETICS_READER_ABI,
        )

    def get_orders(self, *, account: Optional[str] = None, start: int = 0, end: int = 1000) -> Dict[str, Order]:
        acct = account or self._default_account
        if not acct:
            return {}

        acct = Web3.to_checksum_address(acct)
        c = get_contracts(self._chain_id)

        list_key = account_order_list_key(acct)

        # Mirror TS: DataStore.getBytes32ValuesAt(accountOrderListKey, 0, DEFAULT_COUNT)
        order_keys: List[bytes] = self._data_store.functions.getBytes32ValuesAt(list_key, start, end).call()
        orders_raw = self._reader.functions.getAccountOrders(
            Web3.to_checksum_address(c.data_store),
            acct,
            start,
            end,
        ).call()

        orders: Dict[str, Order] = {}
        for i, order_raw in enumerate(orders_raw):
            if i >= len(order_keys):
                break
            key_bytes = order_keys[i]
            key_hex = Web3.to_hex(key_bytes)

            # Matches TS Order.Props from getAccountOrders: (addresses, numbers, flags) — optional legacy 4th `data` tuple.
            addresses = order_raw[0]
            numbers = order_raw[1]
            flags = order_raw[2]
            if len(order_raw) > 3:
                data_hex_list = [Web3.to_hex(x) for x in order_raw[3]]
            else:
                data_hex_list = []

            orders[key_hex] = Order(
                key=key_hex,
                account=addresses[0],
                receiver=addresses[1],
                callback_contract=addresses[3],
                ui_fee_receiver=addresses[4],
                market_address=addresses[5],
                initial_collateral_token_address=addresses[6],
                swap_path=list(addresses[7]),
                order_type=int(numbers[0]),
                decrease_position_swap_type=int(numbers[1]),
                size_delta_usd=int(numbers[2]),
                initial_collateral_delta_amount=int(numbers[3]),
                contract_trigger_price=int(numbers[4]),
                contract_acceptable_price=int(numbers[5]),
                execution_fee=int(numbers[6]),
                callback_gas_limit=int(numbers[7]),
                min_output_amount=int(numbers[8]),
                updated_at_time=int(numbers[9]),
                valid_from_time=int(numbers[10]),
                is_long=bool(flags[0]),
                should_unwrap_native_token=bool(flags[1]),
                is_frozen=bool(flags[2]),
                auto_cancel=bool(flags[3]),
                data=data_hex_list,
                raw=order_raw,
            )

        return orders

