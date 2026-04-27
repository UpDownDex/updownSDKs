"""
Orders-only query script (Python port of the orders section in `tsSDK/test/test-query.ts`).

Run (from repo root or pythonSDK, with PYTHONPATH=src or editable install):
  python3 scripts/test_orders.py

Env (align with TS `test/test-config.ts` + `test-query.ts`):
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
    print(f"🧾 Orders query (chain={chain}, chainId={sdk.chain_id})")
    print(f"   account={sdk.account}")
    print("=" * 80 + "\n")

    try:
        orders = sdk.orders.get_orders()
        print(f"🧾 Orders ({len(orders)})")
        for order_key, o in orders.items():
            # Same shape as TS test-query.ts console output
            print(
                f"- key={order_key} type={o.order_type} isLong={o.is_long} "
                f"market={o.market_address} sizeUsd={o.size_delta_usd}"
            )
    except Exception as e:
        print(f"🧾 Orders: failed ({e})")
        raise

    print("\n✅ Done.\n")


if __name__ == "__main__":
    main()
