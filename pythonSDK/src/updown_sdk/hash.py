from __future__ import annotations

from eth_abi import encode as abi_encode
from web3 import Web3


def hash_string(value: str) -> bytes:
    # TS `hashString("...")` uses keccak256(abi.encode(["string"], [value]))
    # (NOT keccak256(utf8Bytes(value))).
    encoded = abi_encode(["string"], [value])
    return Web3.keccak(encoded)


def hash_data(types: list[str], values: list[object]) -> bytes:
    # Equivalent to Solidity keccak256(abi.encode(types, values))
    encoded = abi_encode(types, values)
    return Web3.keccak(encoded)


# Mirrors TS `ACCOUNT_ORDER_LIST_KEY = hashString("ACCOUNT_ORDER_LIST")`
ACCOUNT_ORDER_LIST_KEY = hash_string("ACCOUNT_ORDER_LIST")


def account_order_list_key(account: str) -> bytes:
    return hash_data(["bytes32", "address"], [ACCOUNT_ORDER_LIST_KEY, Web3.to_checksum_address(account)])

