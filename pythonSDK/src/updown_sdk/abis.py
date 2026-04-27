from __future__ import annotations

# Minimal ABIs extracted from `tsSDK/src/abis/SyntheticsReader.ts`
# plus DataStore getters used by TS `buildGetOrdersMulticall`.

DATA_STORE_ABI = [
    {
        "type": "function",
        "name": "getUint",
        "stateMutability": "view",
        "inputs": [{"name": "key", "type": "bytes32"}],
        "outputs": [{"name": "", "type": "uint256"}],
    },
    {
        "type": "function",
        "name": "getBytes32Count",
        "stateMutability": "view",
        "inputs": [{"name": "setKey", "type": "bytes32"}],
        "outputs": [{"name": "", "type": "uint256"}],
    },
    {
        "type": "function",
        "name": "getBytes32ValuesAt",
        "stateMutability": "view",
        "inputs": [
            {"name": "setKey", "type": "bytes32"},
            {"name": "start", "type": "uint256"},
            {"name": "end", "type": "uint256"},
        ],
        "outputs": [{"name": "", "type": "bytes32[]"}],
    },
]


SYNTHETICS_READER_ABI = [
    # getAccountOrders(DataStore, account, start, end) -> Order.Props[]
    {
        "type": "function",
        "name": "getAccountOrders",
        "stateMutability": "view",
        "inputs": [
            {"name": "dataStore", "type": "address"},
            {"name": "account", "type": "address"},
            {"name": "start", "type": "uint256"},
            {"name": "end", "type": "uint256"},
        ],
        "outputs": [
            {
                "name": "",
                "type": "tuple[]",
                # NOTE: We keep components minimal (tuples are still decoded as nested tuples).
                # The TS SDK parses into a richer shape; here we focus on pairing results with orderKeys.
                "components": [
                    {"name": "addresses", "type": "tuple", "components": [
                        {"name": "account", "type": "address"},
                        {"name": "receiver", "type": "address"},
                        {"name": "cancellationReceiver", "type": "address"},
                        {"name": "callbackContract", "type": "address"},
                        {"name": "uiFeeReceiver", "type": "address"},
                        {"name": "market", "type": "address"},
                        {"name": "initialCollateralToken", "type": "address"},
                        {"name": "swapPath", "type": "address[]"},
                    ]},
                    {"name": "numbers", "type": "tuple", "components": [
                        {"name": "orderType", "type": "uint8"},
                        {"name": "decreasePositionSwapType", "type": "uint8"},
                        {"name": "sizeDeltaUsd", "type": "uint256"},
                        {"name": "initialCollateralDeltaAmount", "type": "uint256"},
                        {"name": "triggerPrice", "type": "uint256"},
                        {"name": "acceptablePrice", "type": "uint256"},
                        {"name": "executionFee", "type": "uint256"},
                        {"name": "callbackGasLimit", "type": "uint256"},
                        {"name": "minOutputAmount", "type": "uint256"},
                        {"name": "updatedAtTime", "type": "uint256"},
                        {"name": "validFromTime", "type": "uint256"},
                    ]},
                    {"name": "flags", "type": "tuple", "components": [
                        {"name": "isLong", "type": "bool"},
                        {"name": "shouldUnwrapNativeToken", "type": "bool"},
                        {"name": "isFrozen", "type": "bool"},
                        {"name": "autoCancel", "type": "bool"},
                    ]},
                    # No `data` here — matches tsSDK `abis/SyntheticsReader.ts` getAccountOrders (Order.Props is 3 tuples only).
                ],
            }
        ],
    },
    # getAccountPositions(DataStore, account, start, end) -> Position.Props[]
    {
        "type": "function",
        "name": "getAccountPositions",
        "stateMutability": "view",
        "inputs": [
            {"name": "dataStore", "type": "address"},
            {"name": "account", "type": "address"},
            {"name": "start", "type": "uint256"},
            {"name": "end", "type": "uint256"},
        ],
        "outputs": [
            {
                "name": "",
                "type": "tuple[]",
                "components": [
                    {"name": "addresses", "type": "tuple", "components": [
                        {"name": "account", "type": "address"},
                        {"name": "market", "type": "address"},
                        {"name": "collateralToken", "type": "address"},
                    ]},
                    {"name": "numbers", "type": "tuple", "components": [
                        {"name": "sizeInUsd", "type": "uint256"},
                        {"name": "sizeInTokens", "type": "uint256"},
                        {"name": "collateralAmount", "type": "uint256"},
                        {"name": "borrowingFactor", "type": "uint256"},
                        {"name": "fundingFeeAmountPerSize", "type": "uint256"},
                        {"name": "longTokenClaimableFundingAmountPerSize", "type": "uint256"},
                        {"name": "shortTokenClaimableFundingAmountPerSize", "type": "uint256"},
                        {"name": "increasedAtTime", "type": "uint256"},
                        {"name": "decreasedAtTime", "type": "uint256"},
                    ]},
                    {"name": "flags", "type": "tuple", "components": [
                        {"name": "isLong", "type": "bool"},
                    ]},
                ],
            }
        ],
    },
    # getAccountPositionInfoList(DataStore, ReferralStorage, account, markets, marketPrices, uiFeeReceiver, start, end)
    {
        "type": "function",
        "name": "getAccountPositionInfoList",
        "stateMutability": "view",
        "inputs": [
            {"name": "dataStore", "type": "address"},
            {"name": "referralStorage", "type": "address"},
            {"name": "account", "type": "address"},
            {"name": "markets", "type": "address[]"},
            {
                "name": "marketPrices",
                "type": "tuple[]",
                "components": [
                    {"name": "indexTokenPrice", "type": "tuple", "components": [
                        {"name": "min", "type": "uint256"},
                        {"name": "max", "type": "uint256"},
                    ]},
                    {"name": "longTokenPrice", "type": "tuple", "components": [
                        {"name": "min", "type": "uint256"},
                        {"name": "max", "type": "uint256"},
                    ]},
                    {"name": "shortTokenPrice", "type": "tuple", "components": [
                        {"name": "min", "type": "uint256"},
                        {"name": "max", "type": "uint256"},
                    ]},
                ],
            },
            {"name": "uiFeeReceiver", "type": "address"},
            {"name": "start", "type": "uint256"},
            {"name": "end", "type": "uint256"},
        ],
        "outputs": [
            {
                "name": "",
                "type": "tuple[]",
                # IMPORTANT: Must match chain return ABI exactly; otherwise web3.py decoding
                # can fail with InvalidPointer / BadFunctionCallOutput.
                "components": [
                    {"name": "positionKey", "type": "bytes32"},
                    {"name": "position", "type": "tuple", "components": [
                        {"name": "addresses", "type": "tuple", "components": [
                            {"name": "account", "type": "address"},
                            {"name": "market", "type": "address"},
                            {"name": "collateralToken", "type": "address"},
                        ]},
                        {"name": "numbers", "type": "tuple", "components": [
                            {"name": "sizeInUsd", "type": "uint256"},
                            {"name": "sizeInTokens", "type": "uint256"},
                            {"name": "collateralAmount", "type": "uint256"},
                            {"name": "borrowingFactor", "type": "uint256"},
                            {"name": "fundingFeeAmountPerSize", "type": "uint256"},
                            {"name": "longTokenClaimableFundingAmountPerSize", "type": "uint256"},
                            {"name": "shortTokenClaimableFundingAmountPerSize", "type": "uint256"},
                            {"name": "increasedAtTime", "type": "uint256"},
                            {"name": "decreasedAtTime", "type": "uint256"},
                        ]},
                        {"name": "flags", "type": "tuple", "components": [
                            {"name": "isLong", "type": "bool"},
                        ]},
                    ]},
                    {"name": "fees", "type": "tuple", "components": [
                        {"name": "referral", "type": "tuple", "components": [
                            {"name": "referralCode", "type": "bytes32"},
                            {"name": "affiliate", "type": "address"},
                            {"name": "trader", "type": "address"},
                            {"name": "totalRebateFactor", "type": "uint256"},
                            {"name": "affiliateRewardFactor", "type": "uint256"},
                            {"name": "adjustedAffiliateRewardFactor", "type": "uint256"},
                            {"name": "traderDiscountFactor", "type": "uint256"},
                            {"name": "totalRebateAmount", "type": "uint256"},
                            {"name": "traderDiscountAmount", "type": "uint256"},
                            {"name": "affiliateRewardAmount", "type": "uint256"},
                        ]},
                        {"name": "pro", "type": "tuple", "components": [
                            {"name": "traderTier", "type": "uint256"},
                            {"name": "traderDiscountFactor", "type": "uint256"},
                            {"name": "traderDiscountAmount", "type": "uint256"},
                        ]},
                        {"name": "funding", "type": "tuple", "components": [
                            {"name": "fundingFeeAmount", "type": "uint256"},
                            {"name": "claimableLongTokenAmount", "type": "uint256"},
                            {"name": "claimableShortTokenAmount", "type": "uint256"},
                            {"name": "latestFundingFeeAmountPerSize", "type": "uint256"},
                            {"name": "latestLongTokenClaimableFundingAmountPerSize", "type": "uint256"},
                            {"name": "latestShortTokenClaimableFundingAmountPerSize", "type": "uint256"},
                        ]},
                        {"name": "borrowing", "type": "tuple", "components": [
                            {"name": "borrowingFeeUsd", "type": "uint256"},
                            {"name": "borrowingFeeAmount", "type": "uint256"},
                            {"name": "borrowingFeeReceiverFactor", "type": "uint256"},
                            {"name": "borrowingFeeAmountForFeeReceiver", "type": "uint256"},
                        ]},
                        {"name": "ui", "type": "tuple", "components": [
                            {"name": "uiFeeReceiver", "type": "address"},
                            {"name": "uiFeeReceiverFactor", "type": "uint256"},
                            {"name": "uiFeeAmount", "type": "uint256"},
                        ]},
                        {"name": "liquidation", "type": "tuple", "components": [
                            {"name": "liquidationFeeUsd", "type": "uint256"},
                            {"name": "liquidationFeeAmount", "type": "uint256"},
                            {"name": "liquidationFeeReceiverFactor", "type": "uint256"},
                            {"name": "liquidationFeeAmountForFeeReceiver", "type": "uint256"},
                        ]},
                        {"name": "collateralTokenPrice", "type": "tuple", "components": [
                            {"name": "min", "type": "uint256"},
                            {"name": "max", "type": "uint256"},
                        ]},
                        {"name": "positionFeeFactor", "type": "uint256"},
                        {"name": "protocolFeeAmount", "type": "uint256"},
                        {"name": "positionFeeReceiverFactor", "type": "uint256"},
                        {"name": "feeReceiverAmount", "type": "uint256"},
                        {"name": "feeAmountForPool", "type": "uint256"},
                        {"name": "positionFeeAmountForPool", "type": "uint256"},
                        {"name": "positionFeeAmount", "type": "uint256"},
                        {"name": "totalCostAmountExcludingFunding", "type": "uint256"},
                        {"name": "totalCostAmount", "type": "uint256"},
                        {"name": "totalDiscountAmount", "type": "uint256"},
                    ]},
                    {"name": "executionPriceResult", "type": "tuple", "components": [
                        {"name": "priceImpactUsd", "type": "int256"},
                        {"name": "priceImpactDiffUsd", "type": "uint256"},
                        {"name": "executionPrice", "type": "uint256"},
                    ]},
                    {"name": "basePnlUsd", "type": "int256"},
                    {"name": "uncappedBasePnlUsd", "type": "int256"},
                    {"name": "pnlAfterPriceImpactUsd", "type": "int256"},
                ],
            }
        ],
    },
]


ERC20_ABI = [
    {
        "type": "function",
        "name": "balanceOf",
        "stateMutability": "view",
        "inputs": [{"name": "account", "type": "address"}],
        "outputs": [{"name": "", "type": "uint256"}],
    },
    {
        "type": "function",
        "name": "allowance",
        "stateMutability": "view",
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"},
        ],
        "outputs": [{"name": "", "type": "uint256"}],
    },
    {
        "type": "function",
        "name": "approve",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "outputs": [{"name": "", "type": "bool"}],
    },
    {
        "type": "function",
        "name": "decimals",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint8"}],
    },
]


EXCHANGE_ROUTER_ABI = [
    {
        "type": "function",
        "name": "router",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"name": "", "type": "address"}],
    },
    {
        "type": "function",
        "name": "sendWnt",
        "stateMutability": "payable",
        "inputs": [
            {"name": "receiver", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "outputs": [],
    },
    {
        "type": "function",
        "name": "sendTokens",
        "stateMutability": "payable",
        "inputs": [
            {"name": "token", "type": "address"},
            {"name": "receiver", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "outputs": [],
    },
    {
        "type": "function",
        "name": "createOrder",
        "stateMutability": "payable",
        "inputs": [
            {
                "name": "params",
                "type": "tuple",
                "components": [
                    {
                        "name": "addresses",
                        "type": "tuple",
                        "components": [
                            {"name": "receiver", "type": "address"},
                            {"name": "cancellationReceiver", "type": "address"},
                            {"name": "callbackContract", "type": "address"},
                            {"name": "uiFeeReceiver", "type": "address"},
                            {"name": "market", "type": "address"},
                            {"name": "initialCollateralToken", "type": "address"},
                            {"name": "swapPath", "type": "address[]"},
                        ],
                    },
                    {
                        "name": "numbers",
                        "type": "tuple",
                        "components": [
                            {"name": "sizeDeltaUsd", "type": "uint256"},
                            {"name": "initialCollateralDeltaAmount", "type": "uint256"},
                            {"name": "triggerPrice", "type": "uint256"},
                            {"name": "acceptablePrice", "type": "uint256"},
                            {"name": "executionFee", "type": "uint256"},
                            {"name": "callbackGasLimit", "type": "uint256"},
                            {"name": "minOutputAmount", "type": "uint256"},
                            {"name": "validFromTime", "type": "uint256"},
                        ],
                    },
                    {"name": "orderType", "type": "uint8"},
                    {"name": "decreasePositionSwapType", "type": "uint8"},
                    {"name": "isLong", "type": "bool"},
                    {"name": "shouldUnwrapNativeToken", "type": "bool"},
                    {"name": "autoCancel", "type": "bool"},
                    {"name": "referralCode", "type": "bytes32"},
                ],
            }
        ],
        "outputs": [{"name": "", "type": "bytes32"}],
    },
    {
        "type": "function",
        "name": "createDeposit",
        "stateMutability": "payable",
        "inputs": [
            {
                "name": "params",
                "type": "tuple",
                "components": [
                    {"name": "receiver", "type": "address"},
                    {"name": "callbackContract", "type": "address"},
                    {"name": "uiFeeReceiver", "type": "address"},
                    {"name": "market", "type": "address"},
                    {"name": "initialLongToken", "type": "address"},
                    {"name": "initialShortToken", "type": "address"},
                    {"name": "longTokenSwapPath", "type": "address[]"},
                    {"name": "shortTokenSwapPath", "type": "address[]"},
                    {"name": "minMarketTokens", "type": "uint256"},
                    {"name": "shouldUnwrapNativeToken", "type": "bool"},
                    {"name": "executionFee", "type": "uint256"},
                    {"name": "callbackGasLimit", "type": "uint256"},
                ],
            }
        ],
        "outputs": [{"name": "", "type": "bytes32"}],
    },
    {
        "type": "function",
        "name": "createWithdrawal",
        "stateMutability": "payable",
        "inputs": [
            {
                "name": "params",
                "type": "tuple",
                "components": [
                    {"name": "receiver", "type": "address"},
                    {"name": "callbackContract", "type": "address"},
                    {"name": "uiFeeReceiver", "type": "address"},
                    {"name": "market", "type": "address"},
                    {"name": "longTokenSwapPath", "type": "address[]"},
                    {"name": "shortTokenSwapPath", "type": "address[]"},
                    {"name": "minLongTokenAmount", "type": "uint256"},
                    {"name": "minShortTokenAmount", "type": "uint256"},
                    {"name": "shouldUnwrapNativeToken", "type": "bool"},
                    {"name": "executionFee", "type": "uint256"},
                    {"name": "callbackGasLimit", "type": "uint256"},
                ],
            }
        ],
        "outputs": [{"name": "", "type": "bytes32"}],
    },
    {
        "type": "function",
        "name": "multicall",
        "stateMutability": "payable",
        "inputs": [{"name": "data", "type": "bytes[]"}],
        "outputs": [{"name": "results", "type": "bytes[]"}],
    },
]

