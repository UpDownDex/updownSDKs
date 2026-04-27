/**
 * Load environment variables from .env file
 */
import dotenv from "dotenv";
import { dirname, join } from "path";
// Load .env file from the SDK root directory
import { fileURLToPath } from "url";
/**
 * SDK Configuration for Testing
 *
 * This file contains the configuration for initializing the SDK.
 * Update the values below according to your environment.
 */
import { createWalletClient, http } from "viem";
import { privateKeyToAccount } from "viem/accounts";

import { BATCH_CONFIGS } from "../src/configs/batch";
import type { ContractsChainId } from "../src/configs/chains";
import { ARBITRUM, CELO, getViemChain } from "../src/configs/chains";
import { UpdownSdk } from "../src/index";
import { MAX_TIMEOUT } from "../src/utils/multicall";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
dotenv.config({ path: join(__dirname, "../.env") });

// Configuration for different chains
export const SDK_CONFIGS = {
  // CELO Mainnet
  celo: {
    chainId: CELO as ContractsChainId,
    rpcUrl: process.env.CELO_RPC_URL || "https://forno.celo.org",
    oracleUrl: process.env.ORACLE_URL || "https://api.perpex.ai/prices/",
    subsquidUrl:
      process.env.SUBSQUID_URL ||
      process.env.SUBGRAPH_URL ||
      "http://8.219.84.241:8000/subgraphs/name/gmx/synthetics-celo-stats",
    account: process.env.ACCOUNT_ADDRESS as `0x${string}` | undefined,
  },

  // Arbitrum Mainnet
  arbitrum: {
    chainId: ARBITRUM as ContractsChainId,
    rpcUrl: process.env.ARBITRUM_RPC_URL || "https://arb1.arbitrum.io/rpc",
    oracleUrl: process.env.ORACLE_URL || "https://api.perpex.ai/prices/",
    subsquidUrl:
      process.env.SUBSQUID_URL ||
      "https://gmx.squids.live/gmx-synthetics-arbitrum:prod/graphql",
    account: process.env.ACCOUNT_ADDRESS as `0x${string}` | undefined,
  },
};

/**
 * Initialize SDK with the specified chain
 */
export function initSdk(chain: keyof typeof SDK_CONFIGS = "celo"): UpdownSdk {
  const config = SDK_CONFIGS[chain];

  if (!config.account) {
    throw new Error(
      "Account address is required. Set ACCOUNT_ADDRESS environment variable."
    );
  }

  // Create wallet client with private key if provided
  let walletClient;
  const privateKeyRaw = process.env.PRIVATE_KEY;
  if (privateKeyRaw) {
    const privateKey = privateKeyRaw.startsWith("0x")
      ? privateKeyRaw
      : `0x${privateKeyRaw}`;

    // viem requires a 0x-prefixed hex string
    const account = privateKeyToAccount(privateKey as `0x${string}`);
    walletClient = createWalletClient({
      account,
      chain: getViemChain(config.chainId),
      transport: http(config.rpcUrl, {
        retryCount: 0,
        retryDelay: 10000000,
        batch: BATCH_CONFIGS[config.chainId]?.http,
        timeout: MAX_TIMEOUT,
      }),
    });
  }

  return new UpdownSdk({
    chainId: config.chainId,
    account: config.account,
    rpcUrl: config.rpcUrl,
    oracleUrl: config.oracleUrl,
    subsquidUrl: config.subsquidUrl,
    walletClient,
  });
}

/**
 * Helper function to format bigint values for display
 */
export function formatTokenAmount(
  amount: bigint,
  decimals: number = 18
): string {
  const divisor = BigInt(10 ** decimals);
  const whole = amount / divisor;
  const fraction = amount % divisor;
  const fractionStr = fraction.toString().padStart(decimals, "0");
  return `${whole}.${fractionStr}`;
}

/**
 * Helper function to parse token amount
 */
export function parseTokenAmount(
  amount: string,
  decimals: number = 18
): bigint {
  const [whole, fraction = "0"] = amount.split(".");
  const wholePart = BigInt(whole) * BigInt(10 ** decimals);
  const fractionPart = BigInt(
    fraction.padEnd(decimals, "0").slice(0, decimals)
  );
  return wholePart + fractionPart;
}

/**
 * Helper function to wait for a specified number of seconds
 */
export function sleep(seconds: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, seconds * 1000));
}

/**
 * Helper function to log transaction details
 */
export function logTransaction(txHash: string, chainId: number) {
  const explorerUrls: Record<number, string> = {
    42220: "https://celoscan.io/tx/",
    42161: "https://arbiscan.io/tx/",
  };

  const explorerUrl = explorerUrls[chainId] || "https://explorer.io/tx/";
  console.log(`\n📝 Transaction Hash: ${txHash}`);
  console.log(`🔗 Explorer: ${explorerUrl}${txHash}`);
}
