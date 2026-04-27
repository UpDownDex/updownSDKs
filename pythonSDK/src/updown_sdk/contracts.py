from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Contracts:
    data_store: str
    synthetics_reader: str
    referral_storage: str
    exchange_router: str
    order_vault: str
    deposit_vault: str
    withdrawal_vault: str


# Minimal subset from TS `src/configs/contracts.ts`
_CONTRACTS: dict[int, Contracts] = {
    # CELO
    42220: Contracts(
        data_store="0x2808EFda9b6c464208d14aF22A793AD1725D5836",
        synthetics_reader="0x357A2044aD1DfE8c93e7dcf352DD4785b1C6CD93",
        referral_storage="0x2128E99291A77e4De5ce47Db8527B6121C86eF6A",
        exchange_router="0x20095BB2Fe7C8d25D15d6e5985b29755Ef57EecE",
        order_vault="0x3153298B530048dD4E079cB9156d9A2DFdA9F0Dc",
        deposit_vault="0x2690A62C0c19F91f0d59A104955322451F951F90",
        withdrawal_vault="0x0336b6eDa5F1889092005ebb78648c2a02d406e3",
    ),
    # ARBITRUM
    42161: Contracts(
        data_store="0x755273464bF4917702Ff45Ae13788F4493c34459",
        synthetics_reader="0xe616B555f322b710FA33eBcd5895b671c6EF2FCe",
        referral_storage="0xe6fab3f0c7199b0d34d7fbe83394fc0e0d06e99d",
        exchange_router="0x909babe2dFBa13f9DC9655A19003Dbe8e9124d5b",
        order_vault="0xCFEd939845c05922B027b2BBCE06aFF5E50bc380",
        deposit_vault="0xf7f2a4751f7e26C91C0726EFDDbaA414dD09BCef",
        withdrawal_vault="0x296AC5d663Abb2551ddc7FD51c54C5F2BB03fDB3",
    ),
}


def get_contracts(chain_id: int) -> Contracts:
    if chain_id not in _CONTRACTS:
        raise NotImplementedError(f"Contracts not ported for chain_id={chain_id}")
    return _CONTRACTS[chain_id]

