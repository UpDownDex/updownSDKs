/**
 * High-level operations module for positions and pools
 *
 * This module provides a unified interface for executing position and pool operations,
 * making it easy to use in scripts, bots, and other automation tools.
 *
 * Supports both Market and Limit orders:
 * - Market orders: Execute immediately at current market price (default)
 * - Limit orders: Execute when triggerPrice is reached (provide triggerPrice parameter)
 */

import { abis } from 'abis/index';
import { getContract } from 'configs/contracts';
import {
  convertTokenAddress,
  getTokenBySymbolSafe,
  NATIVE_TOKEN_ADDRESS,
} from 'configs/tokens';
import type {
  MarketInfo,
  MarketsInfoData,
} from 'types/markets';
import { OrderType } from 'types/orders';
import type { PositionInfo } from 'types/positions';
import type {
  TokenData,
  TokensData,
} from 'types/tokens';
import {
  Address,
  encodeFunctionData,
  parseUnits,
} from 'viem';

import { getMarkPrice } from '../../utils/prices';
import { convertToUsd } from '../../utils/tokens';
import { Module } from '../base';
import {
  type OperationParams,
  type OperationResult,
  OperationType,
  parseOperationType,
  type PoolOperationParams,
  type PositionOperationParams,
} from './types';

/**
 * Helper function to parse token amount string to bigint
 */
function parseTokenAmount(amount: string, decimals: number): bigint {
  return parseUnits(amount, decimals);
}

/**
 * Parse trigger price into protocol USD precision (30 decimals).
 * The order transaction builder will later convert it to contract precision.
 */
function parseTriggerPrice(amount: string, indexTokenDecimals: number): bigint {
  void indexTokenDecimals;
  return parseUnits(amount, 30);
}

/**
 * Helper function to calculate trigger price from percentage
 * @param percent - Percentage as string (e.g., "0.95" = 95%, "-0.05" = 5% below)
 * @param currentPrice - Current market price
 * @returns Calculated trigger price
 */
function calculateTriggerPriceFromPercent(
  percent: string,
  currentPrice: bigint
): bigint {
  const percentNum = parseFloat(percent);
  if (isNaN(percentNum)) {
    throw new Error(`Invalid trigger price percent: ${percent}`);
  }
  // Calculate: currentPrice * (1 + percent)
  // e.g., percent = 0.95 means 95% of current price
  // e.g., percent = -0.05 means 5% below current price (95% of current price)
  const multiplier = BigInt(Math.round((1 + percentNum) * 1e18));
  return (currentPrice * multiplier) / 1000000000000000000n;
}

/**
 * Helper function to get token data with fallback
 * Tries to get from tokensData, then from config, then uses default
 */
async function getTokenDataSafe(
  chainId: number,
  tokenAddress: string,
  tokensData: TokensData,
  defaultDecimals: number = 18
): Promise<TokenData> {
  // Try tokensData first
  const tokenFromData = tokensData[tokenAddress];
  if (tokenFromData) {
    return tokenFromData;
  }

  // Try to get from config by address
  try {
    const { getToken } = await import("configs/tokens");
    const tokenFromConfig = getToken(chainId, tokenAddress);
    return {
      address: tokenAddress,
      symbol: tokenFromConfig.symbol,
      name: tokenFromConfig.name || tokenFromConfig.symbol,
      decimals: tokenFromConfig.decimals,
      isNative: tokenFromConfig.isNative || false,
      isWrapped: tokenFromConfig.isWrapped || false,
      isSynthetic: tokenFromConfig.isSynthetic || false,
    } as TokenData;
  } catch {
    // If not found in config, return minimal token data with default decimals
    return {
      address: tokenAddress,
      symbol: "UNKNOWN",
      name: "Unknown Token",
      decimals: defaultDecimals,
      isNative: false,
      isWrapped: false,
      isSynthetic: false,
    } as TokenData;
  }
}

/**
 * Helper function to check if params are PositionOperationParams
 */
function isPositionOperationParams(
  params: OperationParams
): params is PositionOperationParams {
  return (
    "isLong" in params ||
    "payAmount" in params ||
    "decreasePercentage" in params
  );
}

/**
 * Helper function to check if params are PoolOperationParams
 */
function isPoolOperationParams(
  params: OperationParams
): params is PoolOperationParams {
  return "longTokenAmount" in params || "marketTokenAmount" in params;
}

export class Operations extends Module {
  /**
   * Main entry point for executing operations
   */
  async executeOperation(
    type: OperationType | string,
    params: OperationParams
  ): Promise<OperationResult> {
    const opType = parseOperationType(String(type));

    // Validate params
    if (!params.marketAddress) {
      throw new Error("marketAddress is required");
    }

    // Get market and token data
    const { marketsInfoData, tokensData } =
      await this.sdk.markets.getMarketsInfo();
    if (!marketsInfoData || !tokensData) {
      throw new Error("Failed to fetch market information");
    }

    const marketInfo = marketsInfoData[params.marketAddress];
    if (!marketInfo) {
      throw new Error(`Market not found: ${params.marketAddress}`);
    }

    // Route to appropriate operation handler
    switch (opType) {
      case OperationType.Open:
        return this.openPosition(
          params as PositionOperationParams,
          marketInfo,
          marketsInfoData,
          tokensData
        );

      case OperationType.Increase:
        return this.increasePosition(
          params as PositionOperationParams,
          marketInfo,
          marketsInfoData,
          tokensData
        );

      case OperationType.Decrease:
        return this.decreasePosition(
          params as PositionOperationParams,
          marketInfo,
          marketsInfoData,
          tokensData
        );

      case OperationType.Close:
        return this.closePosition(
          params as PositionOperationParams,
          marketInfo,
          marketsInfoData,
          tokensData
        );

      case OperationType.TakeProfit:
        return this.createTakeProfit(
          params as PositionOperationParams,
          marketInfo,
          marketsInfoData,
          tokensData
        );

      case OperationType.StopLoss:
        return this.createStopLoss(
          params as PositionOperationParams,
          marketInfo,
          marketsInfoData,
          tokensData
        );

      case OperationType.Deposit:
        return this.deposit(
          params as PoolOperationParams,
          marketInfo,
          marketsInfoData,
          tokensData
        );

      case OperationType.Withdraw:
        return this.withdraw(
          params as PoolOperationParams,
          marketInfo,
          marketsInfoData,
          tokensData
        );

      default:
        throw new Error(`Unknown operation type: ${opType}`);
    }
  }

  /**
   * Get existing position for a market
   */
  private async getExistingPosition(
    params: PositionOperationParams,
    marketInfo: MarketInfo,
    marketsInfoData: MarketsInfoData,
    tokensData: TokensData
  ): Promise<PositionInfo | null> {
    const account = this.account;
    if (!account) {
      return null;
    }

    const isLong = params.isLong !== false;
    const collateralTokenAddress =
      params.collateralTokenAddress ||
      (isLong ? marketInfo.longTokenAddress : marketInfo.shortTokenAddress);

    // Get all positions info (this internally calls getPositions, so we don't need to call it separately)
    const positionsInfo = await this.sdk.positions.getPositionsInfo({
      marketsInfoData,
      tokensData,
      showPnlInLeverage: false,
    });

    if (!positionsInfo || Object.keys(positionsInfo).length === 0) {
      return null;
    }

    const positions = Object.values(positionsInfo) as PositionInfo[];
    const opMarket = marketInfo.marketTokenAddress?.toLowerCase() ?? "";
    const marketMatch = (p: PositionInfo) => {
      const a = p.marketInfo?.marketTokenAddress?.toLowerCase();
      const b = p.marketAddress?.toLowerCase();
      return (a != null && a === opMarket) || (b != null && b === opMarket);
    };
    const isLongMatch = (p: PositionInfo) => Boolean(p.isLong) === isLong;

    const matching = positions.find(
      (p) =>
        marketMatch(p) &&
        isLongMatch(p) &&
        p.collateralTokenAddress?.toLowerCase() === collateralTokenAddress.toLowerCase()
    );
    if (matching) return matching;

    // No strict match: if user did not specify collateral, match by (market, isLong) only
    // (e.g. long with USDC was opened via open-long-usdc, but make close defaults to longToken/cEUR)
    if (!params.collateralTokenAddress) {
      const sameDir = positions.filter((p) => marketMatch(p) && isLongMatch(p));
      if (sameDir.length >= 1) return sameDir[0];
    }

    // No (market, isLong) match: if there is a position with opposite isLong, give a clear hint
    const oppositeDir = positions.find((p) => marketMatch(p) && !isLongMatch(p));
    if (oppositeDir) {
      const need = isLong ? "long" : "short";
      const have = isLong ? "short" : "long";
      const makeTarget = oppositeDir.isLong ? "make close" : "make close-short";
      throw new Error(
        `No ${need} position found for this market. You have a ${have} position. ` +
          `Use IS_LONG=${isLong ? "false" : "true"} or ${makeTarget}.`
      );
    }
    return null;
  }

  /**
   * Check and approve token if needed
   */
  private async checkAndApproveToken(
    tokenAddress: Address,
    amount: bigint,
    spender: Address,
    token: TokenData
  ): Promise<void> {
    const account = this.account;
    if (!account) {
      throw new Error("Account is required");
    }

    const allowance = (await this.sdk.publicClient.readContract({
      address: tokenAddress,
      abi: abis.ERC20 as any,
      functionName: "allowance",
      args: [account, spender],
    })) as bigint;

    if (allowance < amount) {
      const txHash = await this.sdk.callContract(
        tokenAddress,
        abis.ERC20 as any,
        "approve",
        [spender, amount * 2n] // Approve 2x for safety
      );
      // Wait for transaction confirmation
      await this.sdk.publicClient.waitForTransactionReceipt({
        hash: txHash,
      });
    }
  }

  /**
   * ERC20 spender for ExchangeRouter multicall paths (sendTokens / vault pulls via Router).
   * Must match openPosition: approve Router, not the ExchangeRouter facade.
   */
  private async getRouterSpenderAddress(): Promise<Address> {
    const exchangeRouterAddress = getContract(this.chainId, "ExchangeRouter");
    return (await this.sdk.publicClient.readContract({
      address: exchangeRouterAddress as Address,
      abi: abis.ExchangeRouter as any,
      functionName: "router",
    })) as Address;
  }

  /**
   * Open a new position
   * Supports both market and limit orders
   */
  private async openPosition(
    params: PositionOperationParams,
    marketInfo: MarketInfo,
    marketsInfoData: MarketsInfoData,
    tokensData: TokensData
  ): Promise<OperationResult> {
    const account = this.account;
    if (!account) {
      throw new Error("Account is required");
    }

    const isLong = params.isLong !== false;
    const collateralTokenAddress =
      params.collateralTokenAddress ||
      (isLong ? marketInfo.longTokenAddress : marketInfo.shortTokenAddress);
    const payTokenAddress = params.payTokenAddress || collateralTokenAddress;

    // Get token data with fallback
    const collateralToken = await getTokenDataSafe(
      this.chainId,
      collateralTokenAddress,
      tokensData
    );
    const payToken = await getTokenDataSafe(
      this.chainId,
      payTokenAddress,
      tokensData
    );

    const payAmount = parseTokenAmount(
      params.payAmount || "10",
      payToken.decimals
    );
    const leverage = BigInt(params.leverage || "2") * 10000n; // Convert to basis points

    // Check minimum collateral USD requirement
    const positionsConstants = await this.sdk.positions.getPositionsConstants();
    const minCollateralUsd = positionsConstants.minCollateralUsd;
    if (minCollateralUsd) {
      // Calculate payAmount in USD using token price
      // Use minPrice for conservative check (worst case)
      const payAmountUsd = convertToUsd(
        payAmount,
        payToken.decimals,
        payToken.prices.minPrice
      );
      if (payAmountUsd && payAmountUsd < minCollateralUsd) {
        const minCollateralUsdFormatted = (
          Number(minCollateralUsd) / 1e30
        ).toFixed(2);
        const payAmountUsdFormatted = (Number(payAmountUsd) / 1e30).toFixed(2);
        throw new Error(
          `Operation amount (${payAmountUsdFormatted} USD) is less than minimum collateral requirement (${minCollateralUsdFormatted} USD). ` +
            `Please increase the PAY_AMOUNT to at least ${minCollateralUsdFormatted} USD worth of ${payToken.symbol}.`
        );
      }
    }

    // Parse trigger price if provided (for limit orders)
    // Support both absolute price (triggerPrice) and percentage (triggerPricePercent)
    let triggerPrice: bigint | undefined;
    if (params.triggerPricePercent) {
      // Calculate trigger price from percentage of current market price
      const isIncrease = true; // Opening is always an increase
      const currentPrice = getMarkPrice({
        prices: marketInfo.indexToken.prices,
        isIncrease,
        isLong,
      });
      triggerPrice = calculateTriggerPriceFromPercent(
        params.triggerPricePercent,
        currentPrice
      );
    } else if (params.triggerPrice) {
      // Use absolute trigger price
      triggerPrice = parseTriggerPrice(
        params.triggerPrice,
        marketInfo.indexToken.decimals
      );
    }

    // Check balance
    const balance = (await this.sdk.publicClient.readContract({
      address: payTokenAddress as Address,
      abi: abis.ERC20 as any,
      functionName: "balanceOf",
      args: [account],
    })) as bigint;

    if (balance < payAmount) {
      console.log("payment token balance is",balance);
      console.log("payment payAmount is",payAmount);
      console.log("payment token address is",payTokenAddress);
      throw new Error(`Insufficient ${payToken.symbol} balance`);
    }

    // Check and approve token
    const exchangeRouterAddress = getContract(this.chainId, "ExchangeRouter");
    const routerAddress = (await this.sdk.publicClient.readContract({
      address: exchangeRouterAddress as Address,
      abi: abis.ExchangeRouter as any,
      functionName: "router",
    })) as Address;

    await this.checkAndApproveToken(
      payTokenAddress as Address,
      payAmount,
      routerAddress,
      payToken
    );

    // Create order (market or limit based on triggerPrice)
    if (triggerPrice !== undefined) {
      console.log("[operations] open/increase limit order triggerPrice:", {
        triggerPriceInput: params.triggerPrice,
        triggerPricePercentInput: params.triggerPricePercent,
        indexTokenDecimals: marketInfo.indexToken.decimals,
        triggerPrice: triggerPrice.toString(),
      });
    }

    const txHash = isLong
      ? await this.sdk.orders.long({
          marketAddress: marketInfo.marketTokenAddress,
          payTokenAddress,
          collateralTokenAddress,
          payAmount,
          leverage,
          limitPrice: triggerPrice, // If provided, creates LimitIncrease order
          allowedSlippageBps: params.allowedSlippageBps || 100,
          skipSimulation: params.skipSimulation ?? true,
        })
      : await this.sdk.orders.short({
          marketAddress: marketInfo.marketTokenAddress,
          payTokenAddress,
          collateralTokenAddress,
          payAmount,
          leverage,
          limitPrice: triggerPrice, // If provided, creates LimitIncrease order
          allowedSlippageBps: params.allowedSlippageBps || 100,
          skipSimulation: params.skipSimulation ?? true,
        });

    return { txHash };
  }

  /**
   * Increase an existing position
   * Supports both market and limit orders
   *
   * Note: If no matching position is found (e.g., different collateral token),
   * this will open a new position with the specified collateral token.
   * In GMX/Perpex, different collateral tokens create separate positions.
   */
  private async increasePosition(
    params: PositionOperationParams,
    marketInfo: MarketInfo,
    marketsInfoData: MarketsInfoData,
    tokensData: TokensData
  ): Promise<OperationResult> {
    // Get existing position with matching collateral token
    const existingPosition = await this.getExistingPosition(
      params,
      marketInfo,
      marketsInfoData,
      tokensData
    );

    // If no matching position found, it means:
    // 1. User wants to use a different collateral token (creates a new position)
    // 2. User has no position at all (opens a new position)
    // In both cases, we can use openPosition logic which will create/increase appropriately
    // The SDK's orders.long/short will handle this correctly

    // Use same logic as openPosition (supports both market and limit)
    // This will either increase existing position or open a new one
    return this.openPosition(params, marketInfo, marketsInfoData, tokensData);
  }

  /**
   * Decrease a position by percentage
   */
  private async decreasePosition(
    params: PositionOperationParams,
    marketInfo: MarketInfo,
    marketsInfoData: MarketsInfoData,
    tokensData: TokensData,
    existingPosition?: PositionInfo | null
  ): Promise<OperationResult> {
    const account = this.account;
    if (!account) {
      throw new Error("Account is required");
    }

    // Get existing position if not provided
    const position =
      existingPosition ??
      (await this.getExistingPosition(
        params,
        marketInfo,
        marketsInfoData,
        tokensData
      ));

    if (!position) {
      throw new Error(
        "No existing position found. Please open a position first."
      );
    }

    const isLong = params.isLong !== false;
    const decreasePercentage = params.decreasePercentage
      ? parseFloat(params.decreasePercentage)
      : 0.5; // Default: 50%

    if (decreasePercentage <= 0 || decreasePercentage > 1) {
      throw new Error("decreasePercentage must be between 0 and 1");
    }

    const closeSizeUsd =
      (position.sizeInUsd * BigInt(Math.floor(decreasePercentage * 10000))) /
      10000n;

    // Get required parameters
    const uiFeeFactor = await this.sdk.utils.getUiFeeFactor();
    const positionsConstants = await this.sdk.positions.getPositionsConstants();
    const minCollateralUsd = positionsConstants.minCollateralUsd;
    const minPositionSizeUsd = positionsConstants.minPositionSizeUsd;

    if (!minCollateralUsd || !minPositionSizeUsd) {
      throw new Error("Failed to get position constants");
    }

    // Parse trigger price if provided (for limit orders)
    // Support both absolute price (triggerPrice) and percentage (triggerPricePercent)
    let triggerPrice: bigint | undefined;
    if (params.triggerPricePercent) {
      // Calculate trigger price from percentage of current market price
      const isIncrease = false; // Decreasing is not an increase
      const currentPrice = getMarkPrice({
        prices: marketInfo.indexToken.prices,
        isIncrease,
        isLong,
      });
      triggerPrice = calculateTriggerPriceFromPercent(
        params.triggerPricePercent,
        currentPrice
      );
    } else if (params.triggerPrice) {
      // Use absolute trigger price
      triggerPrice = parseTriggerPrice(
        params.triggerPrice,
        marketInfo.indexToken.decimals
      );
    }

    // Calculate decrease amounts
    const { getDecreasePositionAmounts } = await import(
      "utils/trade/decrease.js"
    );

    // Ensure position has marketInfo for getDecreasePositionAmounts
    if (!position.marketInfo) {
      throw new Error("Position marketInfo is required");
    }

    const decreaseAmounts = getDecreasePositionAmounts({
      marketInfo,
      collateralToken: position.collateralToken,
      isLong,
      position: position as any, // PositionInfo with marketInfo
      closeSizeUsd,
      keepLeverage: false,
      triggerPrice, // If provided, creates LimitDecrease order
      triggerOrderType: triggerPrice ? OrderType.LimitDecrease : undefined,
      userReferralInfo: undefined,
      minCollateralUsd,
      minPositionSizeUsd,
      uiFeeFactor,
      isSetAcceptablePriceImpactEnabled: false,
    });

    // Create decrease order (market or limit based on triggerPrice)
    if (triggerPrice !== undefined) {
      console.log("[operations] decrease/close limit order triggerPrice:", {
        triggerPriceInput: params.triggerPrice,
        triggerPricePercentInput: params.triggerPricePercent,
        indexTokenDecimals: marketInfo.indexToken.decimals,
        triggerPrice: triggerPrice.toString(),
      });
    }

    const txHash = await this.sdk.orders.createDecreaseOrder({
      marketsInfoData,
      tokensData,
      marketInfo,
      decreaseAmounts,
      collateralToken: position.collateralToken,
      allowedSlippage: params.allowedSlippageBps || 100,
      isLong,
      isTrigger: triggerPrice !== undefined, // Set to true for limit orders
    });

    return { txHash, position };
  }

  /**
   * Close a position fully
   */
  private async closePosition(
    params: PositionOperationParams,
    marketInfo: MarketInfo,
    marketsInfoData: MarketsInfoData,
    tokensData: TokensData
  ): Promise<OperationResult> {
    // Get existing position
    const existingPosition = await this.getExistingPosition(
      params,
      marketInfo,
      marketsInfoData,
      tokensData
    );

    if (!existingPosition) {
      throw new Error(
        "No existing position found. Please open a position first."
      );
    }

    // Close entire position (decreasePercentage = 1.0)
    const closeParams: PositionOperationParams = {
      ...params,
      decreasePercentage: "1.0",
    };

    // Pass existingPosition to avoid duplicate getExistingPosition call
    return this.decreasePosition(
      closeParams,
      marketInfo,
      marketsInfoData,
      tokensData,
      existingPosition
    );
  }

  /**
   * Create take profit order
   */
  private async createTakeProfit(
    params: PositionOperationParams,
    marketInfo: MarketInfo,
    marketsInfoData: MarketsInfoData,
    tokensData: TokensData
  ): Promise<OperationResult> {
    const account = this.account;
    if (!account) {
      throw new Error("Account is required");
    }

    // Get existing position
    const existingPosition = await this.getExistingPosition(
      params,
      marketInfo,
      marketsInfoData,
      tokensData
    );

    if (!existingPosition) {
      throw new Error(
        "No existing position found. Please open a position first."
      );
    }

    if (!existingPosition.entryPrice) {
      throw new Error("Entry price not available");
    }

    const isLong = params.isLong !== false;
    const profitPercentage = BigInt(params.profitPercentage || "5");
    const profitBps = profitPercentage * 100n;

    // Calculate trigger price
    let triggerPrice: bigint;
    if (isLong) {
      triggerPrice =
        (existingPosition.entryPrice * (10000n + profitBps)) / 10000n;
    } else {
      triggerPrice =
        (existingPosition.entryPrice * (10000n - profitBps)) / 10000n;
    }

    // Get close size (default: 50% of position)
    const closeSizeUsd = params.sizeAmount
      ? parseTokenAmount(params.sizeAmount, 30)
      : existingPosition.sizeInUsd / 2n;

    // Get required parameters
    const uiFeeFactor = await this.sdk.utils.getUiFeeFactor();
    const positionsConstants = await this.sdk.positions.getPositionsConstants();
    const minCollateralUsd = positionsConstants.minCollateralUsd;
    const minPositionSizeUsd = positionsConstants.minPositionSizeUsd;

    if (!minCollateralUsd || !minPositionSizeUsd) {
      throw new Error("Failed to get position constants");
    }

    // Calculate decrease amounts with trigger price
    const { getDecreasePositionAmounts } = await import(
      "utils/trade/decrease.js"
    );

    // Ensure position has marketInfo
    if (!existingPosition.marketInfo) {
      throw new Error("Position marketInfo is required");
    }

    const decreaseAmounts = getDecreasePositionAmounts({
      marketInfo,
      collateralToken: existingPosition.collateralToken,
      isLong,
      position: existingPosition as any, // PositionInfo with marketInfo
      closeSizeUsd,
      keepLeverage: false,
      triggerPrice,
      triggerOrderType: OrderType.LimitDecrease,
      userReferralInfo: undefined,
      minCollateralUsd,
      minPositionSizeUsd,
      uiFeeFactor,
      isSetAcceptablePriceImpactEnabled: false,
    });

    // Create take profit order
    const txHash = await this.sdk.orders.createDecreaseOrder({
      marketsInfoData,
      tokensData,
      marketInfo,
      decreaseAmounts,
      collateralToken: existingPosition.collateralToken,
      allowedSlippage: params.allowedSlippageBps || 100,
      isLong,
      isTrigger: true,
    });

    return { txHash, position: existingPosition };
  }

  /**
   * Create stop loss order
   */
  private async createStopLoss(
    params: PositionOperationParams,
    marketInfo: MarketInfo,
    marketsInfoData: MarketsInfoData,
    tokensData: TokensData
  ): Promise<OperationResult> {
    const account = this.account;
    if (!account) {
      throw new Error("Account is required");
    }

    // Get existing position
    const existingPosition = await this.getExistingPosition(
      params,
      marketInfo,
      marketsInfoData,
      tokensData
    );

    if (!existingPosition) {
      throw new Error(
        "No existing position found. Please open a position first."
      );
    }

    if (!existingPosition.entryPrice) {
      throw new Error("Entry price not available");
    }

    const isLong = params.isLong !== false;
    const lossPercentage = BigInt(params.lossPercentage || "3");
    const lossBps = lossPercentage * 100n;

    // Calculate trigger price (opposite of take profit)
    let triggerPrice: bigint;
    if (isLong) {
      // Long position: stop loss when price goes below entry
      triggerPrice =
        (existingPosition.entryPrice * (10000n - lossBps)) / 10000n;
    } else {
      // Short position: stop loss when price goes above entry
      triggerPrice =
        (existingPosition.entryPrice * (10000n + lossBps)) / 10000n;
    }

    // Get close size (default: 50% of position)
    const closeSizeUsd = params.sizeAmount
      ? parseTokenAmount(params.sizeAmount, 30)
      : existingPosition.sizeInUsd / 2n;

    // Get required parameters
    const uiFeeFactor = await this.sdk.utils.getUiFeeFactor();
    const positionsConstants = await this.sdk.positions.getPositionsConstants();
    const minCollateralUsd = positionsConstants.minCollateralUsd;
    const minPositionSizeUsd = positionsConstants.minPositionSizeUsd;

    if (!minCollateralUsd || !minPositionSizeUsd) {
      throw new Error("Failed to get position constants");
    }

    // Calculate decrease amounts with trigger price
    const { getDecreasePositionAmounts } = await import(
      "utils/trade/decrease.js"
    );

    // Ensure position has marketInfo
    if (!existingPosition.marketInfo) {
      throw new Error("Position marketInfo is required");
    }

    const decreaseAmounts = getDecreasePositionAmounts({
      marketInfo,
      collateralToken: existingPosition.collateralToken,
      isLong,
      position: existingPosition as any, // PositionInfo with marketInfo
      closeSizeUsd,
      keepLeverage: false,
      triggerPrice,
      triggerOrderType: OrderType.StopLossDecrease,
      userReferralInfo: undefined,
      minCollateralUsd,
      minPositionSizeUsd,
      uiFeeFactor,
      isSetAcceptablePriceImpactEnabled: false,
    });

    // Create stop loss order
    const txHash = await this.sdk.orders.createDecreaseOrder({
      marketsInfoData,
      tokensData,
      marketInfo,
      decreaseAmounts,
      collateralToken: existingPosition.collateralToken,
      allowedSlippage: params.allowedSlippageBps || 100,
      isLong,
      isTrigger: true,
    });

    return { txHash, position: existingPosition };
  }

  /**
   * Deposit tokens to market pool
   */
  private async deposit(
    params: PoolOperationParams,
    marketInfo: MarketInfo,
    marketsInfoData: MarketsInfoData,
    tokensData: TokensData
  ): Promise<OperationResult> {
    const account = this.account;
    if (!account) {
      throw new Error("Account is required");
    }

    const longTokenAddress =
      params.longTokenAddress || marketInfo.longTokenAddress;
    const shortTokenAddress =
      params.shortTokenAddress || marketInfo.shortTokenAddress;

    // Get token data with fallback
    const longToken = await getTokenDataSafe(
      this.chainId,
      longTokenAddress,
      tokensData
    );
    const shortToken = await getTokenDataSafe(
      this.chainId,
      shortTokenAddress,
      tokensData
    );

    const longTokenAmount = params.longTokenAmount
      ? parseTokenAmount(params.longTokenAmount, longToken.decimals)
      : 0n;
    const shortTokenAmount = params.shortTokenAmount
      ? parseTokenAmount(params.shortTokenAmount, shortToken.decimals)
      : 0n;

    if (longTokenAmount === 0n && shortTokenAmount === 0n) {
      throw new Error("At least one token amount must be provided");
    }

    // Check if using native token
    const isNativeLongDeposit =
      longTokenAddress.toLowerCase() === NATIVE_TOKEN_ADDRESS.toLowerCase() &&
      longTokenAmount > 0n;
    const isNativeShortDeposit =
      shortTokenAddress.toLowerCase() === NATIVE_TOKEN_ADDRESS.toLowerCase() &&
      shortTokenAmount > 0n;

    let wntDeposit = 0n;
    if (isNativeLongDeposit) {
      wntDeposit += longTokenAmount;
    }
    if (isNativeShortDeposit) {
      wntDeposit += shortTokenAmount;
    }

    const shouldUnwrapNativeToken = isNativeLongDeposit || isNativeShortDeposit;

    // Get execution fee
    const gasPrice = await this.sdk.utils.getGasPrice();
    const gasLimits = await this.sdk.utils.getGasLimits();

    const { estimateExecuteDepositGasLimit } = await import(
      "utils/fees/executionFee.js"
    );
    const { estimateOrderOraclePriceCount } = await import(
      "utils/fees/estimateOraclePriceCount.js"
    );
    const { getExecutionFee } = await import("utils/fees/executionFee.js");

    const estimatedGasLimit = estimateExecuteDepositGasLimit(gasLimits, {
      longTokenSwapsCount: 0,
      shortTokenSwapsCount: 0,
      callbackGasLimit: 0n,
    });
    const oraclePriceCount = estimateOrderOraclePriceCount(0);

    if (!gasPrice) {
      throw new Error("Gas price is required");
    }

    const executionFeeResult = getExecutionFee(
      this.chainId,
      gasLimits,
      tokensData,
      estimatedGasLimit,
      gasPrice,
      oraclePriceCount
    );

    if (!executionFeeResult) {
      throw new Error("Failed to calculate execution fee");
    }

    const executionFee = executionFeeResult.feeTokenAmount;
    const wntAmount = executionFee + wntDeposit;

    // Check native token balance
    const nativeBalance = await this.sdk.publicClient.getBalance({
      address: account,
    });

    if (nativeBalance < wntAmount) {
      throw new Error(
        `Insufficient native token balance. Need ${wntAmount}, have ${nativeBalance}`
      );
    }

    // Check and approve tokens (spender = Router, same as openPosition)
    const exchangeRouterAddress = getContract(this.chainId, "ExchangeRouter");
    const depositVaultAddress = getContract(this.chainId, "DepositVault");
    const routerSpender = await this.getRouterSpenderAddress();

    if (!isNativeLongDeposit && longTokenAmount > 0n) {
      await this.checkAndApproveToken(
        longTokenAddress as Address,
        longTokenAmount,
        routerSpender,
        longToken
      );
    }

    if (!isNativeShortDeposit && shortTokenAmount > 0n) {
      await this.checkAndApproveToken(
        shortTokenAddress as Address,
        shortTokenAmount,
        routerSpender,
        shortToken
      );
    }

    // Convert native token addresses to wrapped addresses
    const initialLongTokenAddress = convertTokenAddress(
      this.chainId,
      longTokenAddress,
      "wrapped"
    );
    const initialShortTokenAddress = convertTokenAddress(
      this.chainId,
      shortTokenAddress,
      "wrapped"
    );

    // Create deposit parameters
    const depositParams = {
      receiver: (params.receiver?.trim() || account) as Address,
      callbackContract: "0x0000000000000000000000000000000000000000" as Address,
      uiFeeReceiver: "0x0000000000000000000000000000000000000000" as Address,
      market: marketInfo.marketTokenAddress as Address,
      initialLongToken: initialLongTokenAddress as Address,
      initialShortToken: initialShortTokenAddress as Address,
      longTokenSwapPath: [] as Address[],
      shortTokenSwapPath: [] as Address[],
      minMarketTokens: 0n,
      shouldUnwrapNativeToken: shouldUnwrapNativeToken,
      executionFee: executionFee,
      callbackGasLimit: 0n,
    };

    // Build multicall payload
    const multicallArgs = [
      encodeFunctionData({
        abi: abis.ExchangeRouter as any,
        functionName: "sendWnt",
        args: [depositVaultAddress, wntAmount],
      }),
      !isNativeLongDeposit && longTokenAmount > 0n
        ? encodeFunctionData({
            abi: abis.ExchangeRouter as any,
            functionName: "sendTokens",
            args: [longTokenAddress, depositVaultAddress, longTokenAmount],
          })
        : null,
      !isNativeShortDeposit && shortTokenAmount > 0n
        ? encodeFunctionData({
            abi: abis.ExchangeRouter as any,
            functionName: "sendTokens",
            args: [shortTokenAddress, depositVaultAddress, shortTokenAmount],
          })
        : null,
      encodeFunctionData({
        abi: abis.ExchangeRouter as any,
        functionName: "createDeposit",
        args: [depositParams],
      }),
    ].filter((arg) => arg !== null);

    // Send transaction
    const txHash = await this.sdk.callContract(
      exchangeRouterAddress as Address,
      abis.ExchangeRouter as any,
      "multicall",
      [multicallArgs],
      { value: wntAmount }
    );

    return { txHash };
  }

  /**
   * Withdraw tokens from market pool
   */
  private async withdraw(
    params: PoolOperationParams,
    marketInfo: MarketInfo,
    marketsInfoData: MarketsInfoData,
    tokensData: TokensData
  ): Promise<OperationResult> {
    const account = this.account;
    if (!account) {
      throw new Error("Account is required");
    }

    if (!params.marketTokenAmount) {
      throw new Error("marketTokenAmount is required for withdrawal");
    }

    // Get market token decimals
    // Try to get from tokensData first
    let marketTokenDecimals = 18; // Default fallback
    const marketToken = tokensData[marketInfo.marketTokenAddress];
    if (marketToken) {
      marketTokenDecimals = marketToken.decimals;
    } else {
      // Try to get from config/tokens using "GM" symbol (market token symbol)
      const marketTokenFromConfig = getTokenBySymbolSafe(this.chainId, "GM", {
        isSynthetic: true,
      });
      if (marketTokenFromConfig) {
        marketTokenDecimals = marketTokenFromConfig.decimals;
      }
      // If not found, keep default 18 (already set above)
    }

    const marketTokenAmount = parseTokenAmount(
      params.marketTokenAmount,
      marketTokenDecimals
    );

    // Check balance
    const balance = (await this.sdk.publicClient.readContract({
      address: marketInfo.marketTokenAddress as Address,
      abi: abis.ERC20 as any,
      functionName: "balanceOf",
      args: [account],
    })) as bigint;

    if (balance < marketTokenAmount) {
      throw new Error(`Insufficient market token balance`);
    }

    // Get execution fee
    const gasPrice = await this.sdk.utils.getGasPrice();
    const gasLimits = await this.sdk.utils.getGasLimits();

    const { estimateExecuteWithdrawalGasLimit } = await import(
      "utils/fees/executionFee.js"
    );
    const { estimateOrderOraclePriceCount } = await import(
      "utils/fees/estimateOraclePriceCount.js"
    );
    const { getExecutionFee } = await import("utils/fees/executionFee.js");

    // Estimate gas limit for withdrawal execution
    const estimatedGasLimit = estimateExecuteWithdrawalGasLimit(gasLimits, {
      callbackGasLimit: 0n,
    });
    const oraclePriceCount = estimateOrderOraclePriceCount(0); // No swaps

    if (!gasPrice) {
      throw new Error("Gas price is required");
    }

    const executionFeeResult = getExecutionFee(
      this.chainId,
      gasLimits,
      tokensData,
      estimatedGasLimit,
      gasPrice,
      oraclePriceCount
    );

    if (!executionFeeResult) {
      throw new Error("Failed to calculate execution fee");
    }

    const executionFee = executionFeeResult.feeTokenAmount;

    // Check and approve market token (spender = Router, same as deposit)
    const exchangeRouterAddress = getContract(this.chainId, "ExchangeRouter");
    const withdrawalVaultAddress = getContract(this.chainId, "WithdrawalVault");
    const routerSpender = await this.getRouterSpenderAddress();

    // Create a minimal token data object for approval if not in tokensData
    const marketTokenForApproval: TokenData = marketToken || {
      address: marketInfo.marketTokenAddress,
      symbol: "GM",
      name: "Market Token",
      decimals: marketTokenDecimals,
      isNative: false,
      isWrapped: false,
      isSynthetic: true,
    };

    await this.checkAndApproveToken(
      marketInfo.marketTokenAddress as Address,
      marketTokenAmount,
      routerSpender,
      marketTokenForApproval
    );

    // Create withdrawal parameters
    const withdrawalParams = {
      receiver: (params.receiver || account) as Address,
      callbackContract: "0x0000000000000000000000000000000000000000" as Address,
      uiFeeReceiver: "0x0000000000000000000000000000000000000000" as Address,
      market: marketInfo.marketTokenAddress as Address,
      longTokenSwapPath: [] as Address[],
      shortTokenSwapPath: [] as Address[],
      marketTokenAmount: marketTokenAmount,
      minLongTokenAmount: params.minLongTokenAmount
        ? parseTokenAmount(
            params.minLongTokenAmount,
            marketInfo.longToken.decimals
          )
        : 0n,
      minShortTokenAmount: params.minShortTokenAmount
        ? parseTokenAmount(
            params.minShortTokenAmount,
            marketInfo.shortToken.decimals
          )
        : 0n,
      shouldUnwrapNativeToken: false,
      executionFee: executionFee,
      callbackGasLimit: 0n,
    };

    // Build multicall payload
    const multicallArgs = [
      encodeFunctionData({
        abi: abis.ExchangeRouter as any,
        functionName: "sendWnt",
        args: [withdrawalVaultAddress, executionFee],
      }),
      encodeFunctionData({
        abi: abis.ExchangeRouter as any,
        functionName: "sendTokens",
        args: [
          marketInfo.marketTokenAddress,
          withdrawalVaultAddress,
          marketTokenAmount,
        ],
      }),
      encodeFunctionData({
        abi: abis.ExchangeRouter as any,
        functionName: "createWithdrawal",
        args: [withdrawalParams],
      }),
    ];

    // Send transaction
    const txHash = await this.sdk.callContract(
      exchangeRouterAddress as Address,
      abis.ExchangeRouter as any,
      "multicall",
      [multicallArgs],
      { value: executionFee }
    );

    return { txHash };
  }
}
