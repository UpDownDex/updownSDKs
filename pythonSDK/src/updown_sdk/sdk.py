from __future__ import annotations

from web3 import Web3

from .markets import Markets
from .oracle import Oracle
from .orders import Orders
from .positions import Positions
from .tokens import Tokens
from .operations import Operations
from .types import updownSdkConfig


class UpdownSdk:
    """
    Python port of `src/index.ts` UpdownSdk (query-first).
    """

    def __init__(
        self,
        *,
        chain_id: int,
        rpc_url: str,
        oracle_url: str,
        subsquid_url: str | None = None,
        account: str | None = None,
        tokens: dict | None = None,
        markets: dict | None = None,
    ):
        self.config = updownSdkConfig(
            chain_id=chain_id,
            rpc_url=rpc_url,
            oracle_url=oracle_url,
            subsquid_url=subsquid_url,
            account=account,
            tokens=tokens,
            markets=markets,
        )

        self.w3 = Web3(Web3.HTTPProvider(self.config.rpc_url))
        self.oracle = Oracle(oracle_url=self.config.oracle_url)
        self.markets = Markets(chain_id=self.config.chain_id)
        self.tokens = Tokens(self.config.chain_id, self.oracle)
        self.orders = Orders(self.w3, self.config.chain_id, self.config.account)
        self.positions = Positions(self.w3, self.config.chain_id, self.config.account, self.oracle)
        self.operations = None

    @property
    def chain_id(self) -> int:
        return self.config.chain_id

    @property
    def account(self) -> str | None:
        return self.config.account

    def set_account(self, account: str) -> None:
        self.config = updownSdkConfig(
            chain_id=self.config.chain_id,
            rpc_url=self.config.rpc_url,
            oracle_url=self.config.oracle_url,
            subsquid_url=self.config.subsquid_url,
            account=account,
            tokens=self.config.tokens,
            markets=self.config.markets,
        )
        self.orders = Orders(self.w3, self.config.chain_id, self.config.account)
        self.positions = Positions(self.w3, self.config.chain_id, self.config.account, self.oracle)

