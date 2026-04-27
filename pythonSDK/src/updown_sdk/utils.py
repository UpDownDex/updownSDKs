from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from web3 import Web3

from .abis import DATA_STORE_ABI
from .contracts import get_contracts
from .hash import hash_string


# DataStore keys (mirror TS configs/dataStore.ts)
SINGLE_SWAP_GAS_LIMIT_KEY = hash_string("SINGLE_SWAP_GAS_LIMIT")
INCREASE_ORDER_GAS_LIMIT_KEY = hash_string("INCREASE_ORDER_GAS_LIMIT")
DECREASE_ORDER_GAS_LIMIT_KEY = hash_string("DECREASE_ORDER_GAS_LIMIT")
DEPOSIT_GAS_LIMIT_KEY = hash_string("DEPOSIT_GAS_LIMIT")
WITHDRAWAL_GAS_LIMIT_KEY = hash_string("WITHDRAWAL_GAS_LIMIT")
ESTIMATED_GAS_FEE_BASE_AMOUNT_V2_1 = hash_string("ESTIMATED_GAS_FEE_BASE_AMOUNT_V2_1")
ESTIMATED_GAS_FEE_PER_ORACLE_PRICE = hash_string("ESTIMATED_GAS_FEE_PER_ORACLE_PRICE")
ESTIMATED_GAS_FEE_MULTIPLIER_FACTOR = hash_string("ESTIMATED_GAS_FEE_MULTIPLIER_FACTOR")


# Chain execution-fee config subset (mirror TS configs/chains.ts)
EXECUTION_FEE_USE_BASE_FEE = {42220: True}
EXECUTION_FEE_PRIORITY_WEI = {42220: 2 * 10**9}  # 2 gwei
EXECUTION_FEE_MAX_GAS_PRICE_WEI = {42220: 80 * 10**9}  # cap legacy fallback
EXECUTION_FEE_DEFAULT_BUFFER_BPS = {
    42220: 3000,  # CELO defaultBufferBps
    42161: 3000,  # ARBITRUM defaultBufferBps (kept for parity)
}
EXECUTION_FEE_BUFFER_BPS = {42220: 2000}  # extra fee token amount buffer


@dataclass(frozen=True)
class GasLimits:
    singleSwap: int
    increaseOrder: int
    decreaseOrder: int
    depositToken: int
    withdrawalMultiToken: int
    estimatedGasFeeBaseAmount: int
    estimatedGasFeePerOraclePrice: int
    estimatedFeeMultiplierFactor: int


class Utils:
    def __init__(self, w3: Web3, chain_id: int):
        self._w3 = w3
        self._chain_id = chain_id
        c = get_contracts(chain_id)
        self._data_store = self._w3.eth.contract(address=Web3.to_checksum_address(c.data_store), abi=DATA_STORE_ABI)
        self._cached_gas_limits: Optional[GasLimits] = None

    def get_gas_limits(self) -> GasLimits:
        if self._cached_gas_limits is not None:
            return self._cached_gas_limits

        def get_uint(key: bytes) -> int:
            return int(self._data_store.functions.getUint(key).call())

        gl = GasLimits(
            singleSwap=get_uint(SINGLE_SWAP_GAS_LIMIT_KEY),
            increaseOrder=get_uint(INCREASE_ORDER_GAS_LIMIT_KEY),
            decreaseOrder=get_uint(DECREASE_ORDER_GAS_LIMIT_KEY),
            depositToken=get_uint(DEPOSIT_GAS_LIMIT_KEY),
            withdrawalMultiToken=get_uint(WITHDRAWAL_GAS_LIMIT_KEY),
            estimatedGasFeeBaseAmount=get_uint(ESTIMATED_GAS_FEE_BASE_AMOUNT_V2_1),
            estimatedGasFeePerOraclePrice=get_uint(ESTIMATED_GAS_FEE_PER_ORACLE_PRICE),
            estimatedFeeMultiplierFactor=get_uint(ESTIMATED_GAS_FEE_MULTIPLIER_FACTOR),
        )
        self._cached_gas_limits = gl
        return gl

    def get_execution_fee_gas_price(self) -> int:
        """
        Mirrors TS logic in configs/chains.ts:
        - On CELO, use baseFeePerGas + buffer + priority to avoid inflated legacy gasPrice.
        - Otherwise fallback to node gas_price (legacy).
        """
        if EXECUTION_FEE_USE_BASE_FEE.get(self._chain_id):
            block = self._w3.eth.get_block("pending")
            base_fee = int(block.get("baseFeePerGas") or 0)
            buffer_bps = int(EXECUTION_FEE_DEFAULT_BUFFER_BPS.get(self._chain_id, 0))
            priority = int(EXECUTION_FEE_PRIORITY_WEI.get(self._chain_id, 0))
            buffered = base_fee + (base_fee * buffer_bps) // 10000
            return buffered + priority

        gas_price = int(self._w3.eth.gas_price)
        cap = EXECUTION_FEE_MAX_GAS_PRICE_WEI.get(self._chain_id)
        if cap is not None:
            gas_price = min(gas_price, int(cap))
        return gas_price

    def get_execution_fee_buffer_bps(self) -> int:
        return int(EXECUTION_FEE_BUFFER_BPS.get(self._chain_id, 0))

