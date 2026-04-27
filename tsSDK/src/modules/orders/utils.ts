import type { ContractsChainId } from "configs/chains";
import { getContract } from "configs/contracts";
import { accountOrderListKey } from "configs/dataStore";
import { getWrappedToken } from "configs/tokens";
import type {
  MarketFilterLongShortDirection,
  MarketFilterLongShortItemData,
} from "modules/trades/trades";
import type { GasLimitsConfig } from "types/fees";
import type { MarketsInfoData } from "types/markets";
import {
  DecreasePositionSwapType,
  Order,
  OrderType,
} from "types/orders";
import {
  SidecarLimitOrderEntry,
  SidecarSlTpOrderEntry,
} from "types/sidecarOrders";
import type { TokensData } from "types/tokens";
import {
  estimateOrderOraclePriceCount,
} from "utils/fees/estimateOraclePriceCount";
import {
  estimateExecuteDecreaseOrderGasLimit,
  getExecutionFee,
} from "utils/fees/executionFee";
import type {
  MulticallRequestConfig,
  MulticallResult,
} from "utils/multicall";
import {
  isIncreaseOrderType,
  isLimitOrderType,
  isSwapOrderType,
  isTriggerDecreaseOrderType,
} from "utils/orders";
import { getSwapPathOutputAddresses } from "utils/swap/swapStats";
import {
  Address,
  isAddressEqual,
} from "viem";

import type { UpdownSdk } from "../../index";

export const getOrderExecutionFee = (
  sdk: UpdownSdk,
  swapsCount: number,
  decreasePositionSwapType: DecreasePositionSwapType | undefined,
  gasLimits: GasLimitsConfig | undefined,
  tokensData: TokensData | undefined,
  gasPrice: bigint | undefined
) => {
  if (!gasLimits || !tokensData || gasPrice === undefined) return;

  const estimatedGas = estimateExecuteDecreaseOrderGasLimit(gasLimits, {
    decreaseSwapType: decreasePositionSwapType,
    swapsCount: swapsCount ?? 0,
  });

  const oraclePriceCount = estimateOrderOraclePriceCount(swapsCount);

  return getExecutionFee(sdk.chainId, gasLimits, tokensData, estimatedGas, gasPrice, oraclePriceCount);
};

export const getExecutionFeeAmountForEntry = (
  sdk: UpdownSdk,
  entry: SidecarSlTpOrderEntry | SidecarLimitOrderEntry,
  gasLimits: GasLimitsConfig,
  tokensData: TokensData,
  gasPrice: bigint | undefined
) => {
  if (!entry.txnType || entry.txnType === "cancel") return undefined;
  const securedExecutionFee = entry.order?.executionFee ?? 0n;

  let swapsCount = 0;

  const executionFee = getOrderExecutionFee(
    sdk,
    swapsCount,
    entry.decreaseAmounts?.decreaseSwapType,
    gasLimits,
    tokensData,
    gasPrice
  );

  if (!executionFee || securedExecutionFee >= executionFee.feeTokenAmount) return undefined;

  return executionFee.feeTokenAmount - securedExecutionFee;
};

export function matchByMarket({
  order,
  nonSwapRelevantDefinedFiltersLowercased,
  hasNonSwapRelevantDefinedMarkets,
  pureDirectionFilters,
  hasPureDirectionFilters,
  swapRelevantDefinedMarketsLowercased,
  hasSwapRelevantDefinedMarkets,
  marketsInfoData,
  chainId,
}: {
  order: ReturnType<typeof parseGetOrdersResponse>["orders"][number];
  nonSwapRelevantDefinedFiltersLowercased: MarketFilterLongShortItemData[];
  hasNonSwapRelevantDefinedMarkets: boolean;
  pureDirectionFilters: MarketFilterLongShortDirection[];
  hasPureDirectionFilters: boolean;
  swapRelevantDefinedMarketsLowercased: Address[];
  hasSwapRelevantDefinedMarkets: boolean;
  marketsInfoData?: MarketsInfoData;
  chainId: number;
}) {
  if (!hasNonSwapRelevantDefinedMarkets && !hasSwapRelevantDefinedMarkets && !hasPureDirectionFilters) {
    return true;
  }

  const isSwapOrder = isSwapOrderType(order.orderType);

  const matchesPureDirectionFilter =
    hasPureDirectionFilters &&
    (isSwapOrder
      ? pureDirectionFilters.includes("swap")
      : pureDirectionFilters.includes(order.isLong ? "long" : "short"));

  if (hasPureDirectionFilters && !matchesPureDirectionFilter) {
    return false;
  }

  if (!hasNonSwapRelevantDefinedMarkets && !hasSwapRelevantDefinedMarkets) {
    return true;
  }

  if (isSwapOrder) {
    const sourceMarketInSwapPath = swapRelevantDefinedMarketsLowercased.includes(
      order.swapPath.at(0)!.toLowerCase() as Address
    );

    const destinationMarketInSwapPath = swapRelevantDefinedMarketsLowercased.includes(
      order.swapPath.at(-1)!.toLowerCase() as Address
    );

    return sourceMarketInSwapPath || destinationMarketInSwapPath;
  } else if (!isSwapOrder) {
    return nonSwapRelevantDefinedFiltersLowercased.some((filter) => {
      const marketMatch = filter.marketAddress === "any" || filter.marketAddress === order.marketAddress.toLowerCase();
      const directionMath = filter.direction === "any" || filter.direction === (order.isLong ? "long" : "short");
      const initialCollateralAddress = order.initialCollateralTokenAddress.toLowerCase();

      let collateralMatch = true;
      if (!filter.collateralAddress) {
        collateralMatch = true;
      } else if (isLimitOrderType(order.orderType)) {
        const wrappedToken = getWrappedToken(chainId);

        if (!marketsInfoData) {
          collateralMatch = true;
        } else {
          const { outTokenAddress } = getSwapPathOutputAddresses({
            marketsInfoData,
            initialCollateralAddress,
            isIncrease: isIncreaseOrderType(order.orderType),
            shouldUnwrapNativeToken: order.shouldUnwrapNativeToken,
            swapPath: order.swapPath,
            wrappedNativeTokenAddress: wrappedToken.address,
          });

          collateralMatch =
            outTokenAddress !== undefined && isAddressEqual(outTokenAddress as Address, filter.collateralAddress);
        }
      } else if (isTriggerDecreaseOrderType(order.orderType)) {
        collateralMatch = isAddressEqual(order.initialCollateralTokenAddress as Address, filter.collateralAddress);
      }

      return marketMatch && directionMath && collateralMatch;
    });
  }

  return false;
}

export const DEFAULT_COUNT = 1000;

export function buildGetOrdersMulticall(chainId: ContractsChainId, account: string) {
  return {
    dataStore: {
      contractAddress: getContract(chainId, "DataStore"),
      abiId: "DataStore",
      calls: {
        count: {
          methodName: "getBytes32Count",
          params: [accountOrderListKey(account!)],
        },
        keys: {
          methodName: "getBytes32ValuesAt",
          params: [accountOrderListKey(account!), 0, DEFAULT_COUNT],
        },
      },
    },
    reader: {
      contractAddress: getContract(chainId, "SyntheticsReader"),
      abiId: "SyntheticsReader",
      calls: {
        orders: {
          methodName: "getAccountOrders",
          params: [getContract(chainId, "DataStore"), account, 0, DEFAULT_COUNT],
        },
      },
    },
  } satisfies MulticallRequestConfig<any>;
}

export function parseGetOrdersResponse(res: MulticallResult<ReturnType<typeof buildGetOrdersMulticall>>) {
  const count = Number(res.data.dataStore.count.returnValues[0]);
  const orderKeys = res.data.dataStore.keys.returnValues;
  const orders = res.data.reader.orders.returnValues as any[];

  return {
    count,
    orders: orders.map((order, i) => {
      const key = orderKeys[i];

      const orderData = order.order ? order.order : order;

      const orderResult: Order = {
        key,
        account: orderData.addresses.account as Address,
        receiver: orderData.addresses.receiver as Address,
        callbackContract: orderData.addresses.callbackContract as Address,
        marketAddress: orderData.addresses.market as Address,
        initialCollateralTokenAddress: orderData.addresses.initialCollateralToken as Address,
        swapPath: orderData.addresses.swapPath as Address[],
        sizeDeltaUsd: BigInt(orderData.numbers.sizeDeltaUsd),
        initialCollateralDeltaAmount: BigInt(orderData.numbers.initialCollateralDeltaAmount),
        contractTriggerPrice: BigInt(orderData.numbers.triggerPrice),
        contractAcceptablePrice: BigInt(orderData.numbers.acceptablePrice),
        executionFee: BigInt(orderData.numbers.executionFee),
        callbackGasLimit: BigInt(orderData.numbers.callbackGasLimit),
        minOutputAmount: BigInt(orderData.numbers.minOutputAmount),
        updatedAtTime: BigInt(orderData.numbers.updatedAtTime),
        isLong: orderData.flags.isLong as boolean,
        shouldUnwrapNativeToken: orderData.flags.shouldUnwrapNativeToken as boolean,
        isFrozen: orderData.flags.isFrozen as boolean,
        orderType: Number(orderData.numbers.orderType) as OrderType,
        decreasePositionSwapType: Number(orderData.numbers.decreasePositionSwapType) as DecreasePositionSwapType,
        autoCancel: orderData.flags.autoCancel as boolean,
        uiFeeReceiver: orderData.addresses.uiFeeReceiver as Address,
        validFromTime: BigInt(orderData.numbers.validFromTime),
        data: orderData._dataList || orderData.data || [],
      };

      return orderResult;
    }),
  };
}
