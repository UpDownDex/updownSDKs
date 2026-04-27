from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Optional

from web3 import Web3

from .abis import ERC20_ABI, EXCHANGE_ROUTER_ABI
from .contracts import get_contracts
from .fees import (
    USD_DECIMALS,
    estimate_execute_decrease_order_gas_limit,
    estimate_execute_deposit_gas_limit,
    estimate_execute_increase_order_gas_limit,
    estimate_execute_withdrawal_gas_limit,
    estimate_order_oracle_price_count,
    get_execution_fee,
)
from .decrease_amounts import (
    ORDER_TYPE_LIMIT_DECREASE,
    ORDER_TYPE_STOP_LOSS_DECREASE,
    get_decrease_position_amounts,
)
from .market_store import MarketStore
from .markets import Markets
from .positions import Positions
from .trade_utils import (
    MAX_UINT256,
    apply_slippage_to_price,
    get_entry_price,
    get_mark_price,
    trigger_price_from_percent,
)
from .tx import send_tx
from .utils import Utils


ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
ZERO_BYTES32 = "0x" + "00" * 32

# TS types/orders OrderType (subset)
ORDER_TYPE_MARKET_DECREASE = 4
ORDER_TYPE_LIMIT_DECREASE = 5
ORDER_TYPE_STOP_LOSS_DECREASE = 6

DECREASE_SWAP_NO_SWAP = 0


def _optional_parse_units(amount: Optional[str], decimals: int) -> int:
    if amount is None or not str(amount).strip():
        return 0
    return _parse_units(str(amount).strip(), decimals)


def _parse_units(amount: str, decimals: int) -> int:
    # simple parseUnits for decimal strings
    if "." in amount:
        whole, frac = amount.split(".", 1)
    else:
        whole, frac = amount, ""
    frac = (frac + "0" * decimals)[:decimals]
    return int(whole) * (10**decimals) + int(frac or "0")


def _convert_to_contract_price(price: int, token_decimals: int) -> int:
    # TS convertToContractPrice(price, tokenDecimals) = price / 10^tokenDecimals
    return price // (10**token_decimals)

def _encode_call(contract, fn_name: str, args: list) -> str:
    """
    Encode calldata for a contract function call.

    Note: web3.py v7 no longer exposes `Contract.encodeABI` (used in older ports).
    """
    fn = contract.get_function_by_name(fn_name)(*args)
    return fn._encode_transaction_data()


@dataclass(frozen=True)
class OperationResult:
    tx_hash: str


class Operations:
    def __init__(self, w3: Web3, chain_id: int, account: str, private_key: str, tokens, positions: Optional[Positions] = None):
        self._w3 = w3
        self._chain_id = chain_id
        self._account = Web3.to_checksum_address(account)
        self._private_key = private_key
        self._tokens = tokens
        self._positions = positions

        c = get_contracts(chain_id)
        self._exchange_router = self._w3.eth.contract(
            address=Web3.to_checksum_address(c.exchange_router),
            abi=EXCHANGE_ROUTER_ABI,
        )
        self._order_vault = Web3.to_checksum_address(c.order_vault)
        self._deposit_vault = Web3.to_checksum_address(c.deposit_vault)
        self._withdrawal_vault = Web3.to_checksum_address(c.withdrawal_vault)

    def _erc20(self, token_addr: str):
        return self._w3.eth.contract(address=Web3.to_checksum_address(token_addr), abi=ERC20_ABI)

    def _approve_if_needed(self, token_addr: str, spender: str, amount: int) -> None:
        token = self._erc20(token_addr)
        allowance = token.functions.allowance(self._account, Web3.to_checksum_address(spender)).call()
        if int(allowance) >= int(amount):
            return

        # approve 2x
        data = token.functions.approve(Web3.to_checksum_address(spender), int(amount) * 2)._encode_transaction_data()
        res = send_tx(
            self._w3,
            private_key=self._private_key,
            to=token_addr,
            data=Web3.to_bytes(hexstr=data),
            value_wei=0,
        )
        self._w3.eth.wait_for_transaction_receipt(res.tx_hash)

    def _token_decimals(self, token_address: str) -> int:
        try:
            return int(self._tokens.get_token(token_address)["decimals"])
        except KeyError:
            from . import tokens as tokens_mod

            cfg_path = os.path.join(os.path.dirname(tokens_mod.__file__), "config", "tokens.json")
            if not os.path.exists(cfg_path):
                raise ValueError(f"Token not in oracle data and no tokens.json: {token_address}") from None
            with open(cfg_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for tok in data.get(str(self._chain_id), []):
                if str(tok.get("address", "")).lower() == token_address.lower():
                    return int(tok.get("decimals") or 18)

            # GM/market tokens may not be present in tokens.json; fallback to on-chain ERC20 decimals.
            try:
                dec = self._erc20(token_address).functions.decimals().call()
                return int(dec)
            except Exception as e:
                raise ValueError(f"Token decimals not found in config or chain call failed: {token_address} ({e})") from None

    def _compute_execution_fee_wei(self, estimated_gas_limit: int) -> int:
        utils = Utils(self._w3, self._chain_id)
        gas_limits = utils.get_gas_limits().__dict__
        gas_price = utils.get_execution_fee_gas_price()
        oracle_price_count = estimate_order_oracle_price_count(0)
        tokens_data, _ = self._tokens.get_tokens_data()
        native_token = tokens_data.get(ZERO_ADDRESS)
        if not native_token:
            raise ValueError("Native token price missing in tokensData; cannot compute execution fee")
        fee = get_execution_fee(
            chain_id=self._chain_id,
            gas_limits=gas_limits,
            native_token=native_token,
            estimated_gas_limit=int(estimated_gas_limit),
            gas_price=gas_price,
            oracle_price_count=oracle_price_count,
            execution_fee_buffer_bps=utils.get_execution_fee_buffer_bps(),
        )
        return int(fee.fee_token_amount)

    def open_position(
        self,
        *,
        market_address: str,
        is_long: bool,
        pay_token_address: str,
        collateral_token_address: str,
        pay_amount: str,
        leverage: str,
        allowed_slippage_bps: int = 100,
        trigger_price: Optional[str] = None,
        trigger_price_percent: Optional[str] = None,
        execution_fee_wei: Optional[int] = None,
    ) -> OperationResult:
        # Milestone A: implement `open` with **no swaps** and **manual execution fee**.
        #
        # Limitations:
        # - PAY_TOKEN_ADDRESS must equal COLLATERAL_TOKEN_ADDRESS (swapPath=[]).
        # - EXECUTION_FEE_WEI must be provided.
        # - acceptablePrice uses oracle index price with slippage buffer.
        if pay_token_address.lower() != collateral_token_address.lower():
            raise NotImplementedError("Milestone A requires PAY_TOKEN_ADDRESS == COLLATERAL_TOKEN_ADDRESS (no swapPath).")
        if execution_fee_wei is None:
            # Milestone B: auto-calc execution fee (native token wei)
            utils = Utils(self._w3, self._chain_id)
            gas_limits = utils.get_gas_limits().__dict__
            gas_price = utils.get_execution_fee_gas_price()
            oracle_price_count = estimate_order_oracle_price_count(0)
            estimated_gas_limit = estimate_execute_increase_order_gas_limit(gas_limits, swaps_count=0)

            tokens_data, _ = self._tokens.get_tokens_data()
            native_token_addr = "0x0000000000000000000000000000000000000000"
            native_token = tokens_data.get(native_token_addr)
            if not native_token:
                raise ValueError("Native token price missing in tokensData; cannot compute execution fee")

            fee = get_execution_fee(
                chain_id=self._chain_id,
                gas_limits=gas_limits,
                native_token=native_token,
                estimated_gas_limit=estimated_gas_limit,
                gas_price=gas_price,
                oracle_price_count=oracle_price_count,
                execution_fee_buffer_bps=utils.get_execution_fee_buffer_bps(),
            )
            execution_fee_wei = int(fee.fee_token_amount)

        router_addr = self._exchange_router.functions.router().call()

        pay_token = self._tokens.get_token(pay_token_address)
        idx_token = self._tokens.get_token_by_address(market_address, kind="index")  # provided by caller tokens helper
        pay_decimals = int(pay_token["decimals"])
        idx_decimals = int(idx_token["decimals"])

        pay_amount_int = _parse_units(pay_amount, pay_decimals)

        # Balance check
        bal = self._erc20(pay_token_address).functions.balanceOf(self._account).call()
        if int(bal) < int(pay_amount_int):
            raise ValueError("Insufficient pay token balance")

        # Approve ExchangeRouter.router() as in TS
        self._approve_if_needed(pay_token_address, router_addr, pay_amount_int)

        # Convert payAmount to USD (30 decimals) using token minPrice (already scaled by 10^decimals)
        pay_min_price = int(pay_token["prices"]["minPrice"])
        pay_amount_usd = (int(pay_amount_int) * pay_min_price) // (10**pay_decimals)

        leverage_bps = int(leverage) * 10000
        size_delta_usd = (pay_amount_usd * leverage_bps) // 10000

        # Index price selection mirrors TS `getMarkPrice` for increase:
        idx_prices = idx_token["prices"]
        idx_price = int(idx_prices["maxPrice"] if is_long else idx_prices["minPrice"])

        slip = int(allowed_slippage_bps)
        if is_long:
            acceptable_price = (idx_price * (10000 + slip)) // 10000
        else:
            acceptable_price = (idx_price * (10000 - slip)) // 10000

        trigger_price_val = 0
        order_type = 2  # MarketIncrease
        if trigger_price_percent:
            trigger_price_val = trigger_price_from_percent(trigger_price_percent, idx_price)
            order_type = 3  # LimitIncrease
        elif trigger_price:
            # User-facing trigger price is a display USD price, parse to 1e30 first.
            trigger_price_val = _parse_units(trigger_price, USD_DECIMALS)
            order_type = 3  # LimitIncrease

        # ExchangeRouter expects contract-price units for trigger/acceptable
        trigger_price_contract = _convert_to_contract_price(trigger_price_val, idx_decimals)
        acceptable_price_contract = _convert_to_contract_price(acceptable_price, idx_decimals)

        order_params = (
            # addresses
            (
                self._account,  # receiver
                ZERO_ADDRESS,   # cancellationReceiver
                ZERO_ADDRESS,   # callbackContract
                ZERO_ADDRESS,   # uiFeeReceiver
                Web3.to_checksum_address(market_address),  # market
                Web3.to_checksum_address(collateral_token_address),  # initialCollateralToken
                [],  # swapPath
            ),
            # numbers
            (
                int(size_delta_usd),
                0,
                int(trigger_price_contract),
                int(acceptable_price_contract),
                int(execution_fee_wei),
                0,  # callbackGasLimit
                0,  # minOutputAmount
                0,  # validFromTime
            ),
            int(order_type),
            0,  # DecreasePositionSwapType.NoSwap
            bool(is_long),
            False,  # shouldUnwrapNativeToken
            False,  # autoCancel
            Web3.to_bytes(hexstr=ZERO_BYTES32),  # referralCode
        )

        # Build multicall: sendWnt(orderVault, executionFee) + sendTokens(payToken, orderVault, payAmount) + createOrder(orderParams)
        call_send_wnt = _encode_call(self._exchange_router, "sendWnt", [self._order_vault, int(execution_fee_wei)])
        call_send_tokens = _encode_call(
            self._exchange_router,
            "sendTokens",
            [Web3.to_checksum_address(pay_token_address), self._order_vault, int(pay_amount_int)],
        )
        call_create_order = _encode_call(self._exchange_router, "createOrder", [order_params])
        multicall_data = [
            Web3.to_bytes(hexstr=call_send_wnt),
            Web3.to_bytes(hexstr=call_send_tokens),
            Web3.to_bytes(hexstr=call_create_order),
        ]

        tx_data = _encode_call(self._exchange_router, "multicall", [multicall_data])
        tx = send_tx(
            self._w3,
            private_key=self._private_key,
            to=self._exchange_router.address,
            data=Web3.to_bytes(hexstr=tx_data),
            value_wei=int(execution_fee_wei),
        )
        return OperationResult(tx_hash=tx.tx_hash)

    def increase_position(
        self,
        *,
        market_address: str,
        is_long: bool,
        pay_token_address: str,
        collateral_token_address: str,
        pay_amount: str,
        leverage: str,
        allowed_slippage_bps: int = 100,
        trigger_price: Optional[str] = None,
        trigger_price_percent: Optional[str] = None,
        execution_fee_wei: Optional[int] = None,
    ) -> OperationResult:
        # TS parity: increase uses the same create-increase order flow as open.
        return self.open_position(
            market_address=market_address,
            is_long=is_long,
            pay_token_address=pay_token_address,
            collateral_token_address=collateral_token_address,
            pay_amount=pay_amount,
            leverage=leverage,
            allowed_slippage_bps=allowed_slippage_bps,
            trigger_price=trigger_price,
            trigger_price_percent=trigger_price_percent,
            execution_fee_wei=execution_fee_wei,
        )

    def deposit(
        self,
        *,
        market_address: str,
        long_token_address: Optional[str] = None,
        short_token_address: Optional[str] = None,
        long_token_amount: Optional[str] = None,
        short_token_amount: Optional[str] = None,
        receiver: Optional[str] = None,
        execution_fee_wei: Optional[int] = None,
    ) -> OperationResult:
        """
        GM pool deposit (no swap paths), mirroring TS `operations.deposit`.
        Native CELO/ETH uses address(0) + `sendWnt` for that side's amount.
        """
        markets = Markets(self._chain_id).get_markets()
        market = next((m for m in markets if m.market_token_address.lower() == market_address.lower()), None)
        if not market:
            raise ValueError(f"Market not found: {market_address}")

        long_addr = long_token_address or market.long_token_address
        short_addr = short_token_address or market.short_token_address
        long_dec = self._token_decimals(long_addr)
        short_dec = self._token_decimals(short_addr)

        long_amt = _optional_parse_units(long_token_amount, long_dec)
        short_amt = _optional_parse_units(short_token_amount, short_dec)
        if long_amt <= 0 and short_amt <= 0:
            raise ValueError("At least one token amount must be provided")

        is_native_long = long_addr.lower() == ZERO_ADDRESS.lower() and long_amt > 0
        is_native_short = short_addr.lower() == ZERO_ADDRESS.lower() and short_amt > 0
        wnt_deposit = (long_amt if is_native_long else 0) + (short_amt if is_native_short else 0)
        should_unwrap = bool(is_native_long or is_native_short)

        if execution_fee_wei is None:
            utils = Utils(self._w3, self._chain_id)
            est = estimate_execute_deposit_gas_limit(
                utils.get_gas_limits().__dict__,
                long_token_swaps_count=0,
                short_token_swaps_count=0,
            )
            execution_fee_wei = self._compute_execution_fee_wei(est)

        wnt_total = int(execution_fee_wei) + int(wnt_deposit)
        native_bal = int(self._w3.eth.get_balance(self._account))
        if native_bal < wnt_total:
            raise ValueError(f"Insufficient native token balance: need {wnt_total}, have {native_bal}")

        router_addr = self._exchange_router.functions.router().call()

        def _token_symbol(addr: str) -> str:
            try:
                return str(self._tokens.get_token(addr).get("symbol") or "?")
            except KeyError:
                return "?"

        if not is_native_long and long_amt > 0:
            bal = int(self._erc20(long_addr).functions.balanceOf(self._account).call())
            if bal < long_amt:
                raise ValueError(
                    "Insufficient long token balance: "
                    f"token={Web3.to_checksum_address(long_addr)} ({_token_symbol(long_addr)}), "
                    f"decimals={long_dec}, need_wei={long_amt}, balance_wei={bal}, "
                    f"LONG_TOKEN_AMOUNT_input={long_token_amount!r}. "
                    "Deposit long leg uses this ERC20 (Wrapped EURm for this market), not native CELO "
                    "unless you set LONG_TOKEN_ADDRESS=0x0000000000000000000000000000000000000000 "
                    "and fund via native + sendWnt."
                )
            self._approve_if_needed(long_addr, router_addr, long_amt)
        if not is_native_short and short_amt > 0:
            bal = int(self._erc20(short_addr).functions.balanceOf(self._account).call())
            if bal < short_amt:
                raise ValueError(
                    "Insufficient short token balance: "
                    f"token={Web3.to_checksum_address(short_addr)} ({_token_symbol(short_addr)}), "
                    f"decimals={short_dec}, need_wei={short_amt}, balance_wei={bal}, "
                    f"SHORT_TOKEN_AMOUNT_input={short_token_amount!r}."
                )
            self._approve_if_needed(short_addr, router_addr, short_amt)

        initial_long = Web3.to_checksum_address(self._tokens.to_wrapped_if_native(long_addr))
        initial_short = Web3.to_checksum_address(self._tokens.to_wrapped_if_native(short_addr))
        recv = Web3.to_checksum_address(receiver.strip()) if receiver and receiver.strip() else self._account

        # Flat tuple — must match tsSDK `abis/ExchangeRouter.ts` createDeposit (Perpex deployment).
        deposit_params = (
            recv,
            Web3.to_checksum_address(ZERO_ADDRESS),
            Web3.to_checksum_address(ZERO_ADDRESS),
            Web3.to_checksum_address(market_address),
            initial_long,
            initial_short,
            [],
            [],
            0,
            should_unwrap,
            int(execution_fee_wei),
            0,
        )

        call_send_wnt = _encode_call(self._exchange_router, "sendWnt", [self._deposit_vault, wnt_total])
        multicall_data = [Web3.to_bytes(hexstr=call_send_wnt)]
        if not is_native_long and long_amt > 0:
            multicall_data.append(
                Web3.to_bytes(
                    hexstr=_encode_call(
                        self._exchange_router,
                        "sendTokens",
                        [Web3.to_checksum_address(long_addr), self._deposit_vault, long_amt],
                    )
                )
            )
        if not is_native_short and short_amt > 0:
            multicall_data.append(
                Web3.to_bytes(
                    hexstr=_encode_call(
                        self._exchange_router,
                        "sendTokens",
                        [Web3.to_checksum_address(short_addr), self._deposit_vault, short_amt],
                    )
                )
            )
        multicall_data.append(Web3.to_bytes(hexstr=_encode_call(self._exchange_router, "createDeposit", [deposit_params])))
        tx_data = _encode_call(self._exchange_router, "multicall", [multicall_data])
        tx = send_tx(
            self._w3,
            private_key=self._private_key,
            to=self._exchange_router.address,
            data=Web3.to_bytes(hexstr=tx_data),
            value_wei=int(wnt_total),
        )
        return OperationResult(tx_hash=tx.tx_hash)

    def withdraw(
        self,
        *,
        market_address: str,
        market_token_amount: str,
        receiver: Optional[str] = None,
        min_long_token_amount: Optional[str] = None,
        min_short_token_amount: Optional[str] = None,
        execution_fee_wei: Optional[int] = None,
    ) -> OperationResult:
        """
        GM pool withdrawal (no swap paths), mirroring TS `operations.withdraw`.
        Market token amount is sent via `sendTokens`; amount is recorded from the vault transfer-in.
        """
        markets = Markets(self._chain_id).get_markets()
        market = next((m for m in markets if m.market_token_address.lower() == market_address.lower()), None)
        if not market:
            raise ValueError(f"Market not found: {market_address}")

        mt_dec = self._token_decimals(market_address)
        mt_amt = _parse_units(str(market_token_amount).strip(), mt_dec)
        if mt_amt <= 0:
            raise ValueError("market_token_amount must be positive")

        bal = self._erc20(market_address).functions.balanceOf(self._account).call()
        if int(bal) < mt_amt:
            raise ValueError("Insufficient market token balance")

        if execution_fee_wei is None:
            utils = Utils(self._w3, self._chain_id)
            est = estimate_execute_withdrawal_gas_limit(utils.get_gas_limits().__dict__)
            execution_fee_wei = self._compute_execution_fee_wei(est)

        native_bal = int(self._w3.eth.get_balance(self._account))
        if native_bal < int(execution_fee_wei):
            raise ValueError(f"Insufficient native token for execution fee: need {execution_fee_wei}, have {native_bal}")

        router_addr = self._exchange_router.functions.router().call()
        self._approve_if_needed(market_address, router_addr, mt_amt)

        long_dec = self._token_decimals(market.long_token_address)
        short_dec = self._token_decimals(market.short_token_address)
        min_long = _optional_parse_units(min_long_token_amount, long_dec)
        min_short = _optional_parse_units(min_short_token_amount, short_dec)
        recv = Web3.to_checksum_address(receiver.strip()) if receiver and receiver.strip() else self._account

        # Flat tuple — must match tsSDK `abis/ExchangeRouter.ts` createWithdrawal (Perpex deployment).
        withdrawal_params = (
            recv,
            Web3.to_checksum_address(ZERO_ADDRESS),
            Web3.to_checksum_address(ZERO_ADDRESS),
            Web3.to_checksum_address(market_address),
            [],
            [],
            int(min_long),
            int(min_short),
            False,
            int(execution_fee_wei),
            0,
        )

        call_send_wnt = _encode_call(self._exchange_router, "sendWnt", [self._withdrawal_vault, int(execution_fee_wei)])
        call_send_tokens = _encode_call(
            self._exchange_router,
            "sendTokens",
            [Web3.to_checksum_address(market_address), self._withdrawal_vault, mt_amt],
        )
        call_create = _encode_call(self._exchange_router, "createWithdrawal", [withdrawal_params])
        multicall_data = [
            Web3.to_bytes(hexstr=call_send_wnt),
            Web3.to_bytes(hexstr=call_send_tokens),
            Web3.to_bytes(hexstr=call_create),
        ]
        tx_data = _encode_call(self._exchange_router, "multicall", [multicall_data])
        tx = send_tx(
            self._w3,
            private_key=self._private_key,
            to=self._exchange_router.address,
            data=Web3.to_bytes(hexstr=tx_data),
            value_wei=int(execution_fee_wei),
        )
        return OperationResult(tx_hash=tx.tx_hash)

    def _require_positions(self) -> Positions:
        if self._positions is None:
            raise ValueError(
                "Positions module is required for decrease/close/takeprofit/stoploss. "
                "Construct Operations(..., positions=sdk.positions)."
            )
        return self._positions

    def _find_position(self, market_address: str, collateral_token: str, is_long: bool, markets: list):
        pmap = self._require_positions().get_positions(account=self._account, markets=markets, prefer_info_list=True)
        for p in pmap.values():
            if (
                p.market.lower() == market_address.lower()
                and p.collateral_token.lower() == collateral_token.lower()
                and p.is_long == is_long
            ):
                return p
        raise ValueError("No open position found for this market, collateral token, and isLong")

    def _execution_fee_decrease(self, *, decrease_swap_type: int) -> int:
        utils = Utils(self._w3, self._chain_id)
        gas_limits = utils.get_gas_limits().__dict__
        gas_price = utils.get_execution_fee_gas_price()
        oracle_price_count = estimate_order_oracle_price_count(0)
        estimated_gas_limit = estimate_execute_decrease_order_gas_limit(
            gas_limits, swaps_count=0, decrease_swap_type=decrease_swap_type
        )
        tokens_data, _ = self._tokens.get_tokens_data()
        native_token_addr = ZERO_ADDRESS
        native_token = tokens_data.get(native_token_addr)
        if not native_token:
            raise ValueError("Native token price missing in tokensData; cannot compute execution fee")
        fee = get_execution_fee(
            chain_id=self._chain_id,
            gas_limits=gas_limits,
            native_token=native_token,
            estimated_gas_limit=estimated_gas_limit,
            gas_price=gas_price,
            oracle_price_count=oracle_price_count,
            execution_fee_buffer_bps=utils.get_execution_fee_buffer_bps(),
        )
        return int(fee.fee_token_amount)

    def _send_decrease_order(
        self,
        *,
        market_address: str,
        is_long: bool,
        collateral_token_address: str,
        size_delta_usd: int,
        initial_collateral_delta_amount: int,
        order_type: int,
        base_acceptable_price_display: int,
        trigger_price_display: int,
        allowed_slippage_bps: int,
        execution_fee_wei: Optional[int],
        decrease_swap_type: int = DECREASE_SWAP_NO_SWAP,
        should_unwrap_native_token: bool = False,
        auto_cancel: bool = False,
    ) -> OperationResult:
        """
        Mirrors TS `createDecreaseOrderTxn` + `createDecreaseEncodedPayload` for swapPath=[].
        """
        if execution_fee_wei is None:
            execution_fee_wei = self._execution_fee_decrease(decrease_swap_type=decrease_swap_type)

        idx_token = self._tokens.get_token_by_address(market_address, kind="index")
        idx_decimals = int(idx_token["decimals"])

        is_market = order_type == ORDER_TYPE_MARKET_DECREASE
        if is_market:
            final_acceptable_display = apply_slippage_to_price(
                allowed_slippage_bps, int(base_acceptable_price_display), is_increase=False, is_long=is_long
            )
        else:
            final_acceptable_display = int(base_acceptable_price_display)

        trigger_contract = _convert_to_contract_price(int(trigger_price_display), idx_decimals)
        acceptable_contract = _convert_to_contract_price(int(final_acceptable_display), idx_decimals)

        wrapped_collateral = self._tokens.to_wrapped_if_native(collateral_token_address)

        order_params = (
            (
                self._account,
                ZERO_ADDRESS,
                ZERO_ADDRESS,
                ZERO_ADDRESS,
                Web3.to_checksum_address(market_address),
                Web3.to_checksum_address(wrapped_collateral),
                [],
            ),
            (
                int(size_delta_usd),
                int(initial_collateral_delta_amount),
                int(trigger_contract),
                int(acceptable_contract),
                int(execution_fee_wei),
                0,
                0,
                0,
            ),
            int(order_type),
            int(decrease_swap_type),
            bool(is_long),
            bool(should_unwrap_native_token),
            bool(auto_cancel),
            Web3.to_bytes(hexstr=ZERO_BYTES32),
        )

        call_send_wnt = _encode_call(self._exchange_router, "sendWnt", [self._order_vault, int(execution_fee_wei)])
        call_create_order = _encode_call(self._exchange_router, "createOrder", [order_params])
        multicall_data = [
            Web3.to_bytes(hexstr=call_send_wnt),
            Web3.to_bytes(hexstr=call_create_order),
        ]
        tx_data = _encode_call(self._exchange_router, "multicall", [multicall_data])
        tx = send_tx(
            self._w3,
            private_key=self._private_key,
            to=self._exchange_router.address,
            data=Web3.to_bytes(hexstr=tx_data),
            value_wei=int(execution_fee_wei),
        )
        return OperationResult(tx_hash=tx.tx_hash)

    def decrease_position(
        self,
        *,
        market_address: str,
        is_long: bool,
        collateral_token_address: str,
        markets: list,
        decrease_percentage: float = 0.5,
        trigger_price: Optional[str] = None,
        trigger_price_percent: Optional[str] = None,
        allowed_slippage_bps: int = 100,
        execution_fee_wei: Optional[int] = None,
    ) -> OperationResult:
        """
        Market or limit decrease with **no collateral↔PnL swap** (swapPath=[]).

        Pricing is a simplified port of TS `getDecreasePositionAmounts` (mark/trigger-based);
        for production parity use the TS SDK or extend this module.
        """
        if decrease_percentage <= 0 or decrease_percentage > 1:
            raise ValueError("decrease_percentage must be in (0, 1]")
        pos = self._find_position(market_address, collateral_token_address, is_long, markets)
        close_size_usd = (pos.size_in_usd * int(decrease_percentage * 10000)) // 10000
        if close_size_usd <= 0:
            raise ValueError("Computed close size is zero")

        idx_token = self._tokens.get_token_by_address(market_address, kind="index")
        idx_decimals = int(idx_token["decimals"])
        idx_prices = idx_token["prices"]

        trigger_display: Optional[int] = None
        trigger_order_type: Optional[int] = None
        order_type = ORDER_TYPE_MARKET_DECREASE
        if trigger_price or trigger_price_percent:
            if trigger_price:
                # User-facing trigger price is a display USD price, parse to 1e30 first.
                trigger_display = _parse_units(trigger_price, USD_DECIMALS)
            else:
                assert trigger_price_percent is not None
                mark = get_mark_price(idx_prices, is_increase=False, is_long=is_long)
                trigger_display = trigger_price_from_percent(trigger_price_percent, mark)
            trigger_order_type = ORDER_TYPE_LIMIT_DECREASE
            order_type = ORDER_TYPE_LIMIT_DECREASE

        # Core TS port: compute acceptablePrice and sizeDeltaInTokens deterministically from DataStore price impact.
        market_store = MarketStore(self._w3, self._chain_id)
        dec = get_decrease_position_amounts(
            market_store=market_store,
            market_address=market_address,
            index_prices=idx_prices,
            index_decimals=idx_decimals,
            position_size_in_usd=int(pos.size_in_usd),
            position_size_in_tokens=int(pos.size_in_tokens),
            position_collateral_amount=int(pos.collateral_amount),
            pending_impact_amount=int(getattr(pos, "pending_impact_amount", 0)),
            close_size_usd=int(close_size_usd),
            is_long=bool(is_long),
            trigger_price=int(trigger_display) if trigger_display is not None else None,
            trigger_order_type=trigger_order_type,
        )

        base_acceptable = int(dec.acceptable_price)
        trigger_out = int(dec.trigger_price)

        return self._send_decrease_order(
            market_address=market_address,
            is_long=is_long,
            collateral_token_address=collateral_token_address,
            size_delta_usd=int(dec.size_delta_usd),
            initial_collateral_delta_amount=int(dec.collateral_delta_amount),
            order_type=order_type,
            base_acceptable_price_display=base_acceptable,
            trigger_price_display=trigger_out,
            allowed_slippage_bps=allowed_slippage_bps,
            execution_fee_wei=execution_fee_wei,
        )

    def close_position(
        self,
        *,
        market_address: str,
        is_long: bool,
        collateral_token_address: str,
        markets: list,
        allowed_slippage_bps: int = 100,
        execution_fee_wei: Optional[int] = None,
    ) -> OperationResult:
        return self.decrease_position(
            market_address=market_address,
            is_long=is_long,
            collateral_token_address=collateral_token_address,
            markets=markets,
            decrease_percentage=1.0,
            allowed_slippage_bps=allowed_slippage_bps,
            execution_fee_wei=execution_fee_wei,
        )

    def take_profit(
        self,
        *,
        market_address: str,
        is_long: bool,
        collateral_token_address: str,
        markets: list,
        profit_percentage: str = "5",
        size_amount_usd: Optional[str] = None,
        allowed_slippage_bps: int = 100,
        execution_fee_wei: Optional[int] = None,
    ) -> OperationResult:
        pos = self._find_position(market_address, collateral_token_address, is_long, markets)
        idx_token = self._tokens.get_token_by_address(market_address, kind="index")
        idx_decimals = int(idx_token["decimals"])
        entry = get_entry_price(pos.size_in_usd, pos.size_in_tokens, idx_decimals)
        if entry is None:
            raise ValueError("Cannot derive entry price (sizeInTokens is zero)")

        pp = int(profit_percentage)
        profit_bps = pp * 100
        if is_long:
            trigger_display = (int(entry) * (10000 + profit_bps)) // 10000
        else:
            trigger_display = (int(entry) * (10000 - profit_bps)) // 10000

        if size_amount_usd:
            close_usd = _parse_units(size_amount_usd, 30)
        else:
            close_usd = int(pos.size_in_usd) // 2
        size_delta_usd = int(min(close_usd, pos.size_in_usd))
        if size_delta_usd <= 0:
            raise ValueError("Computed take-profit size is zero")

        market_store = MarketStore(self._w3, self._chain_id)
        idx_token = self._tokens.get_token_by_address(market_address, kind="index")
        idx_prices = idx_token["prices"]
        idx_decimals = int(idx_token["decimals"])
        dec = get_decrease_position_amounts(
            market_store=market_store,
            market_address=market_address,
            index_prices=idx_prices,
            index_decimals=idx_decimals,
            position_size_in_usd=int(pos.size_in_usd),
            position_size_in_tokens=int(pos.size_in_tokens),
            position_collateral_amount=int(pos.collateral_amount),
            pending_impact_amount=int(getattr(pos, "pending_impact_amount", 0)),
            close_size_usd=int(size_delta_usd),
            is_long=bool(is_long),
            trigger_price=int(trigger_display),
            trigger_order_type=ORDER_TYPE_LIMIT_DECREASE,
        )

        return self._send_decrease_order(
            market_address=market_address,
            is_long=is_long,
            collateral_token_address=collateral_token_address,
            size_delta_usd=int(dec.size_delta_usd),
            initial_collateral_delta_amount=int(dec.collateral_delta_amount),
            order_type=ORDER_TYPE_LIMIT_DECREASE,
            base_acceptable_price_display=int(dec.acceptable_price),
            trigger_price_display=int(dec.trigger_price),
            allowed_slippage_bps=allowed_slippage_bps,
            execution_fee_wei=execution_fee_wei,
        )

    def stop_loss(
        self,
        *,
        market_address: str,
        is_long: bool,
        collateral_token_address: str,
        markets: list,
        loss_percentage: str = "3",
        size_amount_usd: Optional[str] = None,
        allowed_slippage_bps: int = 100,
        execution_fee_wei: Optional[int] = None,
    ) -> OperationResult:
        pos = self._find_position(market_address, collateral_token_address, is_long, markets)
        idx_token = self._tokens.get_token_by_address(market_address, kind="index")
        idx_decimals = int(idx_token["decimals"])
        entry = get_entry_price(pos.size_in_usd, pos.size_in_tokens, idx_decimals)
        if entry is None:
            raise ValueError("Cannot derive entry price (sizeInTokens is zero)")

        lp = int(loss_percentage)
        loss_bps = lp * 100
        if is_long:
            trigger_display = (int(entry) * (10000 - loss_bps)) // 10000
        else:
            trigger_display = (int(entry) * (10000 + loss_bps)) // 10000

        if size_amount_usd:
            close_usd = _parse_units(size_amount_usd, 30)
        else:
            close_usd = int(pos.size_in_usd) // 2
        size_delta_usd = int(min(close_usd, pos.size_in_usd))
        if size_delta_usd <= 0:
            raise ValueError("Computed stop-loss size is zero")

        base_acceptable = 0 if is_long else MAX_UINT256

        return self._send_decrease_order(
            market_address=market_address,
            is_long=is_long,
            collateral_token_address=collateral_token_address,
            size_delta_usd=size_delta_usd,
            initial_collateral_delta_amount=0,
            order_type=ORDER_TYPE_STOP_LOSS_DECREASE,
            base_acceptable_price_display=int(base_acceptable),
            trigger_price_display=int(trigger_display),
            allowed_slippage_bps=allowed_slippage_bps,
            execution_fee_wei=execution_fee_wei,
        )

