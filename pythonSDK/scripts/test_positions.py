"""
Positions-only query script (Python port of the positions section in `tsSDK/test/test-query.ts`).

Run:
  python3 scripts/test_positions.py

Env:
  ACCOUNT_ADDRESS   (required)
  CHAIN=celo|arbitrum (default: celo)
  CELO_RPC_URL / ARBITRUM_RPC_URL (optional)
  ORACLE_URL (optional)
  SUBSQUID_URL / SUBGRAPH_URL (optional)
"""

from __future__ import annotations

import os
from typing import Optional

from updown_sdk import UpdownSdk
from updown_sdk.env import load_sdk_dotenv


def _chain() -> str:
    raw = (os.getenv("CHAIN") or "celo").lower()
    return "arbitrum" if raw == "arbitrum" else "celo"


def _chain_id(chain: str) -> int:
    return 42161 if chain == "arbitrum" else 42220


def _rpc_url(chain: str) -> str:
    if chain == "arbitrum":
        return os.getenv("ARBITRUM_RPC_URL", "https://arb1.arbitrum.io/rpc")
    return os.getenv("CELO_RPC_URL", "https://forno.celo.org")


def _oracle_url() -> str:
    return os.getenv("ORACLE_URL", "https://api.perpex.ai/prices/")


def _subsquid_url() -> Optional[str]:
    return os.getenv("SUBSQUID_URL") or os.getenv("SUBGRAPH_URL")


def _required(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise SystemExit(f"Missing required env var: {name}")
    return v


def main() -> None:
    load_sdk_dotenv()
    chain = _chain()
    account = _required("ACCOUNT_ADDRESS")

    sdk = UpdownSdk(
        chain_id=_chain_id(chain),
        rpc_url=_rpc_url(chain),
        oracle_url=_oracle_url(),
        subsquid_url=_subsquid_url(),
        account=account,
    )

    print("\n" + "=" * 80)
    print(f"📌 Positions query (chain={chain}, chainId={sdk.chain_id})")
    print(f"   account={sdk.account}")
    print("=" * 80 + "\n")

    markets_dump = sdk.markets.dump_markets()

    try:
        market_keys, _market_prices = sdk.positions._build_market_prices(markets_dump)  # type: ignore[attr-defined]
        if len(market_keys) == 0:
            print(
                "⚠️  No markets with prices found. marketsKeys is empty. "
                "Falling back to getAccountPositions (doesn't require prices)."
            )
        else:
            print(f"✅ Found {len(market_keys)} markets with prices. Using getAccountPositionInfoList.")

        positions = sdk.positions.get_positions(markets=markets_dump)
        print(f"📌 Positions ({len(positions)})")
        for key, p in positions.items():
            # TS test-query.ts line + Python SDK field pending_impact_amount (from PositionInfo list)
            print(
                f"- key={key} market={p.market} collateral={p.collateral_token} "
                f"isLong={p.is_long} sizeUsd={p.size_in_usd} sizeTokens={p.size_in_tokens} "
                f"collateralAmount={p.collateral_amount} pendingImpactAmount={p.pending_impact_amount}"
            )
    except Exception as e:
        print(f"📌 Positions: failed ({e})")
        raise

    print("\n✅ Done.\n")


if __name__ == "__main__":
    main()
