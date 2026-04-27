import os
from datetime import datetime, timezone
from typing import Optional

import json

from web3 import Web3

from updown_sdk import UpdownSdk
from updown_sdk.abis import ERC20_ABI
from updown_sdk.env import load_sdk_dotenv


def _iso(ms: Optional[int]) -> str:
    if not ms:
        return "unknown"
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _select_chain() -> str:
    raw = (os.getenv("CHAIN") or "celo").lower()
    return "arbitrum" if raw == "arbitrum" else "celo"


def _chain_id(chain: str) -> int:
    return 42161 if chain == "arbitrum" else 42220


def _rpc_url(chain: str) -> str:
    if chain == "arbitrum":
        return os.getenv("ARBITRUM_RPC_URL", "https://arb1.arbitrum.io/rpc")
    return os.getenv("CELO_RPC_URL", "https://forno.celo.org")

def _token_decimals_from_config(chain_id: int, token_address: str) -> int:
    """Decimals for any token in config (incl. market/GM token); mirrors TS tokens.json lookup."""
    import updown_sdk as pkg

    cfg_path = os.path.join(os.path.dirname(pkg.__file__), "config", "tokens.json")
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for t in data.get(str(chain_id), []):
            if str(t.get("address", "")).lower() == token_address.lower():
                return int(t.get("decimals") or 18)
    except Exception:
        pass
    return 18


def _format_token_amount(raw: int, decimals: int) -> str:
    if decimals <= 0:
        return str(raw)
    neg = raw < 0
    n = abs(int(raw))
    scale = 10**decimals
    whole = n // scale
    frac = n % scale
    s = f"{whole}.{str(frac).zfill(decimals)}".rstrip("0").rstrip(".")
    return ("-" if neg else "") + (s or "0")


def _print_lp_balance(*, w3: Web3, chain_id: int, account: str, market_token_address: str, markets) -> None:
    """
    User LP = ERC20 balance of the market (GM) token — same as TS `operations.withdraw` balanceOf check.
    `market_token_address` is `marketTokenAddress` from markets config (not index token).
    """
    acct = Web3.to_checksum_address(account.strip())
    mt = Web3.to_checksum_address(market_token_address.strip())
    token = w3.eth.contract(address=mt, abi=ERC20_ABI)
    raw = int(token.functions.balanceOf(acct).call())
    dec = _token_decimals_from_config(chain_id, mt)
    human = _format_token_amount(raw, dec)
    name = ""
    for m in markets:
        if m.market_token_address.lower() == mt.lower():
            sym_by = _token_symbol_map(chain_id)
            idx_sym = sym_by.get(m.index_token_address.lower(), "?")
            short_sym = sym_by.get(m.short_token_address.lower(), "?")
            name = (m.name or "").strip() or f"{idx_sym}/{short_sym}"
            break
    print("🏦 LP (GM) balance")
    print(f"   account:   {acct}")
    print(f"   market:    {mt}")
    if name:
        print(f"   pair/name: {name}")
    print(f"   decimals:  {dec}")
    print(f"   balance:   {human}  (raw={raw})")
    print("")


def _token_symbol_map(chain_id: int) -> dict[str, str]:
    """
    TS prints market names from config; python markets.json may omit `name`.
    Build a best-effort address->symbol map from pythonSDK config/tokens.json
    without requiring oracle prices.
    """
    import updown_sdk as pkg

    cfg_path = os.path.join(os.path.dirname(pkg.__file__), "config", "tokens.json")
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = data.get(str(chain_id), [])
        out: dict[str, str] = {}
        for t in items:
            addr = str(t.get("address") or "").lower()
            sym = str(t.get("symbol") or "")
            if addr and sym:
                out[addr] = sym
        return out
    except Exception:
        return {}


def main():
    load_sdk_dotenv()
    chain = _select_chain()
    sdk = UpdownSdk(
        chain_id=_chain_id(chain),
        rpc_url=_rpc_url(chain),
        oracle_url=os.getenv("ORACLE_URL", "https://api.perpex.ai/prices/"),
        subsquid_url=os.getenv("SUBSQUID_URL") or os.getenv("SUBGRAPH_URL"),
        account=os.getenv("ACCOUNT_ADDRESS"),
    )

    print("\n" + "=" * 80)
    print(f"🔎 Querying SDK state (chain={chain}, chainId={sdk.chain_id})")
    print(f"   account={sdk.account}")
    print("=" * 80 + "\n")

    markets = sdk.markets.get_markets()
    print(f"📈 Markets ({len(markets)})")
    sym_by_addr = _token_symbol_map(sdk.chain_id)
    for m in markets:
        name = (m.name or "").strip()
        if not name:
            idx_sym = sym_by_addr.get(m.index_token_address.lower(), "UNKNOWN")
            short_sym = sym_by_addr.get(m.short_token_address.lower(), "UNKNOWN")
            name = f"{idx_sym}/{short_sym}"
        print(
            f"- {m.market_token_address}  {name}  "
            f"(index={m.index_token_address} long={m.long_token_address} short={m.short_token_address})"
        )
    print("")

    # tokensData/pricesUpdatedAt (best-effort)
    try:
        tokens_data, prices_updated_at = sdk.tokens.get_tokens_data()
        # Minimal marketsInfoData count: markets that have prices for index/long/short tokens
        priced = set(a.lower() for a in tokens_data.keys())
        markets_info_count = 0
        for m in markets:
            if (
                m.index_token_address.lower() in priced
                and m.long_token_address.lower() in priced
                and m.short_token_address.lower() in priced
            ):
                markets_info_count += 1
        print(
            f"💱 Prices: updatedAt={_iso(prices_updated_at)} "
            f"(marketsInfoData={markets_info_count}, tokensData={len(tokens_data)})"
        )
    except Exception as e:
        print(f"💱 Prices: updatedAt=unknown (marketsInfoData=0, tokensData=0) error={e}")
    print("")

    # Orders
    if not sdk.account:
        print("🧾 Orders: skipped (missing account)\n")
    else:
        try:
            orders = sdk.orders.get_orders()
            print(f"🧾 Orders ({len(orders)})")
            for order_key, o in orders.items():
                print(
                    f"- key={order_key} type={o.order_type} isLong={o.is_long} "
                    f"market={o.market_address} sizeUsd={o.size_delta_usd}"
                )
        except Exception as e:
            print(f"🧾 Orders: failed ({e})")
        print("")

    # Positions
    if not sdk.account:
        print("📌 Positions: skipped (missing account)\n")
    else:
        try:
            markets_dump = sdk.markets.dump_markets()
            # Mirror TS debug: whether we can build marketsKeys with prices
            market_keys, _market_prices = sdk.positions._build_market_prices(markets_dump)  # type: ignore[attr-defined]
            if len(market_keys) == 0:
                print(
                    "⚠️  No markets with prices found. marketsKeys is empty. "
                    "This means oracle tickers did not cover required tokens. "
                    "Falling back to getAccountPositions (doesn't require prices)."
                )
            else:
                print(f"✅ Found {len(market_keys)} markets with prices. Using getAccountPositionInfoList.")

            positions = sdk.positions.get_positions(markets=markets_dump)
            print(f"📌 Positions ({len(positions)})")
            for key, p in positions.items():
                print(
                    f"- key={key} market={p.market} collateral={p.collateral_token} "
                    f"isLong={p.is_long} sizeUsd={p.size_in_usd} sizeTokens={p.size_in_tokens} collateralAmount={p.collateral_amount}"
                )
        except Exception as e:
            print(f"📌 Positions: failed ({e})")

    # LP = market (GM) token balance for account + market address (TS: ERC20 balanceOf on marketTokenAddress)
    lp_market = (os.getenv("MARKET_ADDRESS") or os.getenv("MARKET_TOKEN_ADDRESS") or "").strip()
    lp_account = (os.getenv("ACCOUNT_ADDRESS") or (sdk.account or "") or "").strip()
    if lp_market and lp_account:
        try:
            _print_lp_balance(
                w3=sdk.w3,
                chain_id=sdk.chain_id,
                account=lp_account,
                market_token_address=lp_market,
                markets=markets,
            )
        except Exception as e:
            print(f"🏦 LP (GM) balance: failed ({e})\n")
    elif lp_market and not lp_account:
        print("🏦 LP (GM) balance: skipped (set ACCOUNT_ADDRESS or pass account to UpdownSdk)\n")

    print("\n✅ Done.\n")


if __name__ == "__main__":
    main()

