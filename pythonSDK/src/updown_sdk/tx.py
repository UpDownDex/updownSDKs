from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from eth_account import Account
from web3 import Web3


@dataclass(frozen=True)
class TxResult:
    tx_hash: str


def send_tx(
    w3: Web3,
    *,
    private_key: str,
    to: str,
    data: bytes,
    value_wei: int = 0,
    gas: Optional[int] = None,
    max_fee_per_gas: Optional[int] = None,
    max_priority_fee_per_gas: Optional[int] = None,
) -> TxResult:
    acct = Account.from_key(private_key if private_key.startswith("0x") else "0x" + private_key)
    nonce = w3.eth.get_transaction_count(acct.address)
    chain_id = w3.eth.chain_id

    tx: dict[str, Any] = {
        "chainId": chain_id,
        "nonce": nonce,
        "to": Web3.to_checksum_address(to),
        "data": data,
        "value": int(value_wei),
    }

    # Fee fields: try EIP-1559; fallback to legacy if not provided/available.
    if max_fee_per_gas is not None and max_priority_fee_per_gas is not None:
        tx["maxFeePerGas"] = int(max_fee_per_gas)
        tx["maxPriorityFeePerGas"] = int(max_priority_fee_per_gas)
    else:
        tx["gasPrice"] = int(w3.eth.gas_price)

    if gas is None:
        gas = w3.eth.estimate_gas({**tx, "from": acct.address})
    tx["gas"] = int(gas)

    signed = acct.sign_transaction(tx)
    raw = getattr(signed, "rawTransaction", None)
    if raw is None:
        raw = getattr(signed, "raw_transaction")
    tx_hash = w3.eth.send_raw_transaction(raw)
    return TxResult(tx_hash=Web3.to_hex(tx_hash))

