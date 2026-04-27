from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

from web3 import Web3


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from updown_sdk.hash import hash_data, hash_string


def _h(value: str) -> bytes:
    return hash_string(value)


DATASTORE_KEYS = {
    "IS_MARKET_DISABLED_KEY": _h("IS_MARKET_DISABLED"),
    "MAX_POOL_AMOUNT_KEY": _h("MAX_POOL_AMOUNT"),
    "MAX_POOL_USD_FOR_DEPOSIT_KEY": _h("MAX_POOL_USD_FOR_DEPOSIT"),
    "RESERVE_FACTOR_KEY": _h("RESERVE_FACTOR"),
    "OPEN_INTEREST_RESERVE_FACTOR_KEY": _h("OPEN_INTEREST_RESERVE_FACTOR"),
    "MAX_OPEN_INTEREST_KEY": _h("MAX_OPEN_INTEREST"),
    "MIN_POSITION_IMPACT_POOL_AMOUNT_KEY": _h("MIN_POSITION_IMPACT_POOL_AMOUNT"),
    "POSITION_IMPACT_POOL_DISTRIBUTION_RATE_KEY": _h("POSITION_IMPACT_POOL_DISTRIBUTION_RATE"),
    "BORROWING_FACTOR_KEY": _h("BORROWING_FACTOR"),
    "BORROWING_EXPONENT_FACTOR_KEY": _h("BORROWING_EXPONENT_FACTOR"),
    "FUNDING_FACTOR_KEY": _h("FUNDING_FACTOR"),
    "FUNDING_EXPONENT_FACTOR_KEY": _h("FUNDING_EXPONENT_FACTOR"),
    "FUNDING_INCREASE_FACTOR_PER_SECOND": _h("FUNDING_INCREASE_FACTOR_PER_SECOND"),
    "FUNDING_DECREASE_FACTOR_PER_SECOND": _h("FUNDING_DECREASE_FACTOR_PER_SECOND"),
    "MIN_FUNDING_FACTOR_PER_SECOND": _h("MIN_FUNDING_FACTOR_PER_SECOND"),
    "MAX_FUNDING_FACTOR_PER_SECOND": _h("MAX_FUNDING_FACTOR_PER_SECOND"),
    "THRESHOLD_FOR_STABLE_FUNDING": _h("THRESHOLD_FOR_STABLE_FUNDING"),
    "THRESHOLD_FOR_DECREASE_FUNDING": _h("THRESHOLD_FOR_DECREASE_FUNDING"),
    "MAX_PNL_FACTOR_KEY": _h("MAX_PNL_FACTOR"),
    "MAX_PNL_FACTOR_FOR_TRADERS_KEY": _h("MAX_PNL_FACTOR_FOR_TRADERS"),
    "POSITION_FEE_FACTOR_KEY": _h("POSITION_FEE_FACTOR"),
    "POSITION_IMPACT_FACTOR_KEY": _h("POSITION_IMPACT_FACTOR"),
    "MAX_POSITION_IMPACT_FACTOR_KEY": _h("MAX_POSITION_IMPACT_FACTOR"),
    "MAX_POSITION_IMPACT_FACTOR_FOR_LIQUIDATIONS_KEY": _h("MAX_POSITION_IMPACT_FACTOR_FOR_LIQUIDATIONS"),
    "MAX_LENDABLE_IMPACT_FACTOR_KEY": _h("MAX_LENDABLE_IMPACT_FACTOR"),
    "MAX_LENDABLE_IMPACT_FACTOR_FOR_WITHDRAWALS_KEY": _h("MAX_LENDABLE_IMPACT_FACTOR_FOR_WITHDRAWALS"),
    "MAX_LENDABLE_IMPACT_USD_KEY": _h("MAX_LENDABLE_IMPACT_USD"),
    "LENT_POSITION_IMPACT_POOL_AMOUNT_KEY": _h("LENT_POSITION_IMPACT_POOL_AMOUNT"),
    "MIN_COLLATERAL_FACTOR_KEY": _h("MIN_COLLATERAL_FACTOR"),
    "MIN_COLLATERAL_FACTOR_FOR_LIQUIDATION_KEY": _h("MIN_COLLATERAL_FACTOR_FOR_LIQUIDATION"),
    "MIN_COLLATERAL_FACTOR_FOR_OPEN_INTEREST_MULTIPLIER_KEY": _h("MIN_COLLATERAL_FACTOR_FOR_OPEN_INTEREST_MULTIPLIER"),
    "POSITION_IMPACT_EXPONENT_FACTOR_KEY": _h("POSITION_IMPACT_EXPONENT_FACTOR"),
    "SWAP_FEE_FACTOR_KEY": _h("SWAP_FEE_FACTOR"),
    "ATOMIC_SWAP_FEE_FACTOR_KEY": _h("ATOMIC_SWAP_FEE_FACTOR"),
    "SWAP_IMPACT_FACTOR_KEY": _h("SWAP_IMPACT_FACTOR"),
    "SWAP_IMPACT_EXPONENT_FACTOR_KEY": _h("SWAP_IMPACT_EXPONENT_FACTOR"),
    "VIRTUAL_MARKET_ID_KEY": _h("VIRTUAL_MARKET_ID"),
    "VIRTUAL_TOKEN_ID_KEY": _h("VIRTUAL_TOKEN_ID"),
    "POOL_AMOUNT_KEY": _h("POOL_AMOUNT"),
    "POSITION_IMPACT_POOL_AMOUNT_KEY": _h("POSITION_IMPACT_POOL_AMOUNT"),
    "SWAP_IMPACT_POOL_AMOUNT_KEY": _h("SWAP_IMPACT_POOL_AMOUNT"),
    "OPEN_INTEREST_KEY": _h("OPEN_INTEREST"),
    "OPEN_INTEREST_IN_TOKENS_KEY": _h("OPEN_INTEREST_IN_TOKENS"),
}


def _norm_addr(address: str) -> str:
    return Web3.to_checksum_address(address)


def _hex_hash(types: list[str], values: list[object]) -> str:
    return Web3.to_hex(hash_data(types, values))


def hash_market_config_keys(market: dict[str, Any]) -> dict[str, str]:
    m = _norm_addr(market["marketTokenAddress"])
    long_t = _norm_addr(market["longTokenAddress"])
    short_t = _norm_addr(market["shortTokenAddress"])
    return {
        "isDisabled": _hex_hash(["bytes32", "address"], [DATASTORE_KEYS["IS_MARKET_DISABLED_KEY"], m]),
        "maxLongPoolAmount": _hex_hash(["bytes32", "address", "address"], [DATASTORE_KEYS["MAX_POOL_AMOUNT_KEY"], m, long_t]),
        "maxShortPoolAmount": _hex_hash(["bytes32", "address", "address"], [DATASTORE_KEYS["MAX_POOL_AMOUNT_KEY"], m, short_t]),
        "maxLongPoolUsdForDeposit": _hex_hash(
            ["bytes32", "address", "address"], [DATASTORE_KEYS["MAX_POOL_USD_FOR_DEPOSIT_KEY"], m, long_t]
        ),
        "maxShortPoolUsdForDeposit": _hex_hash(
            ["bytes32", "address", "address"], [DATASTORE_KEYS["MAX_POOL_USD_FOR_DEPOSIT_KEY"], m, short_t]
        ),
        "reserveFactorLong": _hex_hash(["bytes32", "address", "bool"], [DATASTORE_KEYS["RESERVE_FACTOR_KEY"], m, True]),
        "reserveFactorShort": _hex_hash(["bytes32", "address", "bool"], [DATASTORE_KEYS["RESERVE_FACTOR_KEY"], m, False]),
        "openInterestReserveFactorLong": _hex_hash(
            ["bytes32", "address", "bool"], [DATASTORE_KEYS["OPEN_INTEREST_RESERVE_FACTOR_KEY"], m, True]
        ),
        "openInterestReserveFactorShort": _hex_hash(
            ["bytes32", "address", "bool"], [DATASTORE_KEYS["OPEN_INTEREST_RESERVE_FACTOR_KEY"], m, False]
        ),
        "maxOpenInterestLong": _hex_hash(["bytes32", "address", "bool"], [DATASTORE_KEYS["MAX_OPEN_INTEREST_KEY"], m, True]),
        "maxOpenInterestShort": _hex_hash(
            ["bytes32", "address", "bool"], [DATASTORE_KEYS["MAX_OPEN_INTEREST_KEY"], m, False]
        ),
        "minPositionImpactPoolAmount": _hex_hash(
            ["bytes32", "address"], [DATASTORE_KEYS["MIN_POSITION_IMPACT_POOL_AMOUNT_KEY"], m]
        ),
        "positionImpactPoolDistributionRate": _hex_hash(
            ["bytes32", "address"], [DATASTORE_KEYS["POSITION_IMPACT_POOL_DISTRIBUTION_RATE_KEY"], m]
        ),
        "borrowingFactorLong": _hex_hash(["bytes32", "address", "bool"], [DATASTORE_KEYS["BORROWING_FACTOR_KEY"], m, True]),
        "borrowingFactorShort": _hex_hash(
            ["bytes32", "address", "bool"], [DATASTORE_KEYS["BORROWING_FACTOR_KEY"], m, False]
        ),
        "borrowingExponentFactorLong": _hex_hash(
            ["bytes32", "address", "bool"], [DATASTORE_KEYS["BORROWING_EXPONENT_FACTOR_KEY"], m, True]
        ),
        "borrowingExponentFactorShort": _hex_hash(
            ["bytes32", "address", "bool"], [DATASTORE_KEYS["BORROWING_EXPONENT_FACTOR_KEY"], m, False]
        ),
        "fundingFactor": _hex_hash(["bytes32", "address"], [DATASTORE_KEYS["FUNDING_FACTOR_KEY"], m]),
        "fundingExponentFactor": _hex_hash(["bytes32", "address"], [DATASTORE_KEYS["FUNDING_EXPONENT_FACTOR_KEY"], m]),
        "fundingIncreaseFactorPerSecond": _hex_hash(
            ["bytes32", "address"], [DATASTORE_KEYS["FUNDING_INCREASE_FACTOR_PER_SECOND"], m]
        ),
        "fundingDecreaseFactorPerSecond": _hex_hash(
            ["bytes32", "address"], [DATASTORE_KEYS["FUNDING_DECREASE_FACTOR_PER_SECOND"], m]
        ),
        "thresholdForStableFunding": _hex_hash(
            ["bytes32", "address"], [DATASTORE_KEYS["THRESHOLD_FOR_STABLE_FUNDING"], m]
        ),
        "thresholdForDecreaseFunding": _hex_hash(
            ["bytes32", "address"], [DATASTORE_KEYS["THRESHOLD_FOR_DECREASE_FUNDING"], m]
        ),
        "minFundingFactorPerSecond": _hex_hash(
            ["bytes32", "address"], [DATASTORE_KEYS["MIN_FUNDING_FACTOR_PER_SECOND"], m]
        ),
        "maxFundingFactorPerSecond": _hex_hash(
            ["bytes32", "address"], [DATASTORE_KEYS["MAX_FUNDING_FACTOR_PER_SECOND"], m]
        ),
        "maxPnlFactorForTradersLong": _hex_hash(
            ["bytes32", "bytes32", "address", "bool"],
            [DATASTORE_KEYS["MAX_PNL_FACTOR_KEY"], DATASTORE_KEYS["MAX_PNL_FACTOR_FOR_TRADERS_KEY"], m, True],
        ),
        "maxPnlFactorForTradersShort": _hex_hash(
            ["bytes32", "bytes32", "address", "bool"],
            [DATASTORE_KEYS["MAX_PNL_FACTOR_KEY"], DATASTORE_KEYS["MAX_PNL_FACTOR_FOR_TRADERS_KEY"], m, False],
        ),
        "positionFeeFactorForBalanceWasImproved": _hex_hash(
            ["bytes32", "address", "bool"], [DATASTORE_KEYS["POSITION_FEE_FACTOR_KEY"], m, True]
        ),
        "positionFeeFactorForBalanceWasNotImproved": _hex_hash(
            ["bytes32", "address", "bool"], [DATASTORE_KEYS["POSITION_FEE_FACTOR_KEY"], m, False]
        ),
        "positionImpactFactorPositive": _hex_hash(
            ["bytes32", "address", "bool"], [DATASTORE_KEYS["POSITION_IMPACT_FACTOR_KEY"], m, True]
        ),
        "positionImpactFactorNegative": _hex_hash(
            ["bytes32", "address", "bool"], [DATASTORE_KEYS["POSITION_IMPACT_FACTOR_KEY"], m, False]
        ),
        "maxPositionImpactFactorPositive": _hex_hash(
            ["bytes32", "address", "bool"], [DATASTORE_KEYS["MAX_POSITION_IMPACT_FACTOR_KEY"], m, True]
        ),
        "maxPositionImpactFactorNegative": _hex_hash(
            ["bytes32", "address", "bool"], [DATASTORE_KEYS["MAX_POSITION_IMPACT_FACTOR_KEY"], m, False]
        ),
        "maxPositionImpactFactorForLiquidations": _hex_hash(
            ["bytes32", "address"], [DATASTORE_KEYS["MAX_POSITION_IMPACT_FACTOR_FOR_LIQUIDATIONS_KEY"], m]
        ),
        "maxLendableImpactFactor": _hex_hash(["bytes32", "address"], [DATASTORE_KEYS["MAX_LENDABLE_IMPACT_FACTOR_KEY"], m]),
        "maxLendableImpactFactorForWithdrawals": _hex_hash(
            ["bytes32", "address"], [DATASTORE_KEYS["MAX_LENDABLE_IMPACT_FACTOR_FOR_WITHDRAWALS_KEY"], m]
        ),
        "maxLendableImpactUsd": _hex_hash(["bytes32", "address"], [DATASTORE_KEYS["MAX_LENDABLE_IMPACT_USD_KEY"], m]),
        "lentPositionImpactPoolAmount": _hex_hash(
            ["bytes32", "address"], [DATASTORE_KEYS["LENT_POSITION_IMPACT_POOL_AMOUNT_KEY"], m]
        ),
        "minCollateralFactor": _hex_hash(["bytes32", "address"], [DATASTORE_KEYS["MIN_COLLATERAL_FACTOR_KEY"], m]),
        "minCollateralFactorForLiquidation": _hex_hash(
            ["bytes32", "address"], [DATASTORE_KEYS["MIN_COLLATERAL_FACTOR_FOR_LIQUIDATION_KEY"], m]
        ),
        "minCollateralFactorForOpenInterestLong": _hex_hash(
            ["bytes32", "address", "bool"], [DATASTORE_KEYS["MIN_COLLATERAL_FACTOR_FOR_OPEN_INTEREST_MULTIPLIER_KEY"], m, True]
        ),
        "minCollateralFactorForOpenInterestShort": _hex_hash(
            ["bytes32", "address", "bool"], [DATASTORE_KEYS["MIN_COLLATERAL_FACTOR_FOR_OPEN_INTEREST_MULTIPLIER_KEY"], m, False]
        ),
        "positionImpactExponentFactor": _hex_hash(
            ["bytes32", "address"], [DATASTORE_KEYS["POSITION_IMPACT_EXPONENT_FACTOR_KEY"], m]
        ),
        "swapFeeFactorForBalanceWasImproved": _hex_hash(
            ["bytes32", "address", "bool"], [DATASTORE_KEYS["SWAP_FEE_FACTOR_KEY"], m, True]
        ),
        "swapFeeFactorForBalanceWasNotImproved": _hex_hash(
            ["bytes32", "address", "bool"], [DATASTORE_KEYS["SWAP_FEE_FACTOR_KEY"], m, False]
        ),
        "atomicSwapFeeFactor": _hex_hash(["bytes32", "address"], [DATASTORE_KEYS["ATOMIC_SWAP_FEE_FACTOR_KEY"], m]),
        "swapImpactFactorPositive": _hex_hash(
            ["bytes32", "address", "bool"], [DATASTORE_KEYS["SWAP_IMPACT_FACTOR_KEY"], m, True]
        ),
        "swapImpactFactorNegative": _hex_hash(
            ["bytes32", "address", "bool"], [DATASTORE_KEYS["SWAP_IMPACT_FACTOR_KEY"], m, False]
        ),
        "swapImpactExponentFactor": _hex_hash(
            ["bytes32", "address"], [DATASTORE_KEYS["SWAP_IMPACT_EXPONENT_FACTOR_KEY"], m]
        ),
        "virtualMarketId": _hex_hash(["bytes32", "address"], [DATASTORE_KEYS["VIRTUAL_MARKET_ID_KEY"], m]),
        "virtualLongTokenId": _hex_hash(["bytes32", "address"], [DATASTORE_KEYS["VIRTUAL_TOKEN_ID_KEY"], long_t]),
        "virtualShortTokenId": _hex_hash(["bytes32", "address"], [DATASTORE_KEYS["VIRTUAL_TOKEN_ID_KEY"], short_t]),
    }


def hash_market_values_keys(market: dict[str, Any]) -> dict[str, str]:
    m = _norm_addr(market["marketTokenAddress"])
    long_t = _norm_addr(market["longTokenAddress"])
    short_t = _norm_addr(market["shortTokenAddress"])
    return {
        "longPoolAmount": _hex_hash(["bytes32", "address", "address"], [DATASTORE_KEYS["POOL_AMOUNT_KEY"], m, long_t]),
        "shortPoolAmount": _hex_hash(["bytes32", "address", "address"], [DATASTORE_KEYS["POOL_AMOUNT_KEY"], m, short_t]),
        "positionImpactPoolAmount": _hex_hash(["bytes32", "address"], [DATASTORE_KEYS["POSITION_IMPACT_POOL_AMOUNT_KEY"], m]),
        "swapImpactPoolAmountLong": _hex_hash(
            ["bytes32", "address", "address"], [DATASTORE_KEYS["SWAP_IMPACT_POOL_AMOUNT_KEY"], m, long_t]
        ),
        "swapImpactPoolAmountShort": _hex_hash(
            ["bytes32", "address", "address"], [DATASTORE_KEYS["SWAP_IMPACT_POOL_AMOUNT_KEY"], m, short_t]
        ),
        "longInterestUsingLongToken": _hex_hash(
            ["bytes32", "address", "address", "bool"], [DATASTORE_KEYS["OPEN_INTEREST_KEY"], m, long_t, True]
        ),
        "longInterestUsingShortToken": _hex_hash(
            ["bytes32", "address", "address", "bool"], [DATASTORE_KEYS["OPEN_INTEREST_KEY"], m, short_t, True]
        ),
        "shortInterestUsingLongToken": _hex_hash(
            ["bytes32", "address", "address", "bool"], [DATASTORE_KEYS["OPEN_INTEREST_KEY"], m, long_t, False]
        ),
        "shortInterestUsingShortToken": _hex_hash(
            ["bytes32", "address", "address", "bool"], [DATASTORE_KEYS["OPEN_INTEREST_KEY"], m, short_t, False]
        ),
        "longInterestInTokensUsingLongToken": _hex_hash(
            ["bytes32", "address", "address", "bool"], [DATASTORE_KEYS["OPEN_INTEREST_IN_TOKENS_KEY"], m, long_t, True]
        ),
        "longInterestInTokensUsingShortToken": _hex_hash(
            ["bytes32", "address", "address", "bool"], [DATASTORE_KEYS["OPEN_INTEREST_IN_TOKENS_KEY"], m, short_t, True]
        ),
        "shortInterestInTokensUsingLongToken": _hex_hash(
            ["bytes32", "address", "address", "bool"], [DATASTORE_KEYS["OPEN_INTEREST_IN_TOKENS_KEY"], m, long_t, False]
        ),
        "shortInterestInTokensUsingShortToken": _hex_hash(
            ["bytes32", "address", "address", "bool"], [DATASTORE_KEYS["OPEN_INTEREST_IN_TOKENS_KEY"], m, short_t, False]
        ),
    }


def _load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: str, payload: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")


def _filter_markets(markets_by_chain: dict[str, list[dict[str, Any]]], chain_id: str | None, market: str | None):
    out: dict[str, list[dict[str, Any]]] = {}
    for cid, markets in markets_by_chain.items():
        if chain_id and cid != chain_id:
            continue
        if market:
            wanted = market.lower()
            picked = [m for m in markets if m.get("marketTokenAddress", "").lower() == wanted]
            if picked:
                out[cid] = picked
        else:
            out[cid] = markets
    return out


def build_keys(markets_by_chain: dict[str, list[dict[str, Any]]]) -> tuple[dict[str, dict[str, dict[str, str]]], dict[str, dict[str, dict[str, str]]]]:
    cfg: dict[str, dict[str, dict[str, str]]] = {}
    vals: dict[str, dict[str, dict[str, str]]] = {}
    for chain_id, markets in markets_by_chain.items():
        cfg[chain_id] = {}
        vals[chain_id] = {}
        for market in markets:
            market_addr = Web3.to_checksum_address(market["marketTokenAddress"]).lower()
            cfg[chain_id][market_addr] = hash_market_config_keys(market)
            vals[chain_id][market_addr] = hash_market_values_keys(market)
    return cfg, vals


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate marketConfigKeys/marketValuesKeys from markets.json.")
    parser.add_argument("--chain-id", help="Only generate for one chain id, e.g. 42220.")
    parser.add_argument("--market-address", help="Only generate for one marketTokenAddress.")
    parser.add_argument(
        "--markets-file",
        default=os.path.join(ROOT_DIR, "src", "updown_sdk", "config", "markets.json"),
        help="Path to markets.json",
    )
    parser.add_argument(
        "--config-out",
        default=os.path.join(ROOT_DIR, "src", "updown_sdk", "config", "marketConfigKeys.json"),
        help="Path to output marketConfigKeys.json",
    )
    parser.add_argument(
        "--values-out",
        default=os.path.join(ROOT_DIR, "src", "updown_sdk", "config", "marketValuesKeys.json"),
        help="Path to output marketValuesKeys.json",
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge into existing output files instead of replacing all content.",
    )
    args = parser.parse_args()

    markets = _load_json(args.markets_file)
    selected = _filter_markets(markets, args.chain_id, args.market_address)
    if not selected:
        raise SystemExit("No markets matched --chain-id/--market-address filter.")

    cfg_new, vals_new = build_keys(selected)

    if args.merge:
        cfg_old = _load_json(args.config_out) if os.path.exists(args.config_out) else {}
        vals_old = _load_json(args.values_out) if os.path.exists(args.values_out) else {}
        for chain_id, chain_data in cfg_new.items():
            cfg_old.setdefault(chain_id, {}).update(chain_data)
        for chain_id, chain_data in vals_new.items():
            vals_old.setdefault(chain_id, {}).update(chain_data)
        _write_json(args.config_out, cfg_old)
        _write_json(args.values_out, vals_old)
    else:
        _write_json(args.config_out, cfg_new)
        _write_json(args.values_out, vals_new)

    print(
        "Generated market keys:",
        f"chains={','.join(sorted(selected.keys()))}",
        f"market_filter={args.market_address or '*'}",
        f"merge={args.merge}",
    )
    print(f"- {args.config_out}")
    print(f"- {args.values_out}")


if __name__ == "__main__":
    main()
