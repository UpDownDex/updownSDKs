import { abis } from "abis";
import { getContract } from "configs/contracts";
import { Abi, encodeFunctionData } from "viem";

import type { UpdownSdk } from "../../../index";

export type CancelOrderParams = {
  orderKeys: string[];
};

export async function cancelOrdersTxn(sdk: UpdownSdk, p: CancelOrderParams) {
  const multicall = createCancelEncodedPayload(p.orderKeys);
  const exchangeRouter = getContract(sdk.chainId, "ExchangeRouter");
  return sdk.callContract(
    exchangeRouter,
    abis.ExchangeRouter as Abi,
    "multicall",
    [multicall]
  );
}

export function createCancelEncodedPayload(orderKeys: (string | null)[] = []) {
  return orderKeys.filter(Boolean).map((orderKey) =>
    encodeFunctionData({
      abi: abis.ExchangeRouter as Abi,
      functionName: "cancelOrder",
      args: [orderKey],
    })
  );
}
