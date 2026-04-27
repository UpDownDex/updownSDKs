.PHONY: help deposit withdraw open open-short open-long-usdc open-short-ceur open-limit open-limit-short increase increase-short increase-long-usdc increase-short-ceur increase-limit increase-limit-short decrease decrease-25 decrease-75 decrease-limit close close-short close-limit takeprofit takeprofit-8 takeprofit-10 stoploss stoploss-5 build

help:
	@echo "Available commands:"
	@echo ""
	@echo "Deposit & Withdraw:"
	@echo "  make deposit              - Deposit liquidity"
	@echo "  make withdraw             - Withdraw liquidity (0.01 market tokens)"
	@echo ""
	@echo "Open Position:"
	@echo "  make open                 - Open long position (1x leverage, 1 token, market order, cEUR collateral)"
	@echo "  make open-short           - Open short position (1x leverage, 1 token, market order, USDC collateral)"
	@echo "  make open-long-usdc       - Open long position with USDC collateral (shortToken)"
	@echo "  make open-short-ceur      - Open short position with cEUR collateral (longToken)"
	@echo "  make open-limit           - Open long position with limit order (set TRIGGER_PRICE_PERCENT, e.g., -0.05 for 5%% below)"
	@echo "  make open-limit-short     - Open short position with limit order (set TRIGGER_PRICE_PERCENT)"
	@echo ""
	@echo "Increase Position:"
	@echo "  make increase             - Increase long position (2x leverage, 1 token, market order, cEUR collateral)"
	@echo "  make increase-short      - Increase short position (2x leverage, 1 token, market order, USDC collateral)"
	@echo "  make increase-long-usdc   - Increase long position with USDC collateral (shortToken)"
	@echo "  make increase-short-ceur  - Increase short position with cEUR collateral (longToken)"
	@echo "  make increase-limit       - Increase long position with limit order (set TRIGGER_PRICE_PERCENT)"
	@echo "  make increase-limit-short - Increase short position with limit order (set TRIGGER_PRICE_PERCENT)"
	@echo ""
	@echo "Decrease Position:"
	@echo "  make decrease             - Decrease position by 50%% (default, market order)"
	@echo "  make decrease-25         - Decrease position by 25%% (market order)"
	@echo "  make decrease-75         - Decrease position by 75%% (market order)"
	@echo "  make decrease-limit       - Decrease position by 50%% with limit order (set TRIGGER_PRICE_PERCENT)"
	@echo ""
	@echo "Close Position:"
	@echo "  make close                - Close long position completely (market order)"
	@echo "  make close-short          - Close short position completely (market order)"
	@echo "  make close-limit          - Close long position with limit order (set TRIGGER_PRICE_PERCENT)"
	@echo ""
	@echo "Take Profit Orders:"
	@echo "  make takeprofit           - Create take profit order (5%% profit, 50%% position)"
	@echo "  make takeprofit-8         - Create take profit order (8%% profit, 100 USD)"
	@echo "  make takeprofit-10        - Create take profit order (10%% profit, 50%% position)"
	@echo ""
	@echo "Stop Loss Orders:"
	@echo "  make stoploss             - Create stop loss order (3%% loss, 100%% position)"
	@echo "  make stoploss-5           - Create stop loss order (5%% loss, 100 USD)"
	@echo ""
	@echo "Build:"
	@echo "  make build                - Build the SDK"
	@echo ""
	@echo "Note: You can override parameters using environment variables:"
	@echo "  MARKET_ADDRESS, PAY_AMOUNT, LEVERAGE, IS_LONG, DECREASE_PERCENTAGE,"
	@echo "  PROFIT_PERCENTAGE, LOSS_PERCENTAGE, SIZE_AMOUNT, TRIGGER_PRICE,"
	@echo "  TRIGGER_PRICE_PERCENT (percentage of current price, e.g., -0.05 for 5%% below),"
	@echo "  COLLATERAL_TOKEN_ADDRESS (use different collateral token), etc."

# Market address
MARKET=0x540ae5Dea435b035F32A0f3C222d73E42699d6c3

# Token addresses for cEUR/USD market
# Long token: cEUR
CEUR=0xD8763CBa276a3738E6DE85b4b3bF5FDed6D6cA73
# Short token: USDC
USDC=0xcebA9300f2b948710d2653dD7B07f33A8B32118C

# Deposit and Withdraw
deposit:
	OPERATION_TYPE=deposit MARKET_ADDRESS=$(MARKET) CEUR_DEPOSIT_AMOUNT=0.01 USDC_DEPOSIT_AMOUNT=0.01 npx tsx test/test-operations.ts

withdraw:
	OPERATION_TYPE=withdraw MARKET_ADDRESS=$(MARKET) WITHDRAWAL_AMOUNT=0.01 npx tsx test/test-operations.ts

# Open Position
open:
	OPERATION_TYPE=open MARKET_ADDRESS=$(MARKET) PAY_AMOUNT=1 LEVERAGE=1 IS_LONG=true npx tsx test/test-operations.ts

open-short:
	OPERATION_TYPE=open MARKET_ADDRESS=$(MARKET) PAY_AMOUNT=1 LEVERAGE=1 IS_LONG=false npx tsx test/test-operations.ts

# Open Position (Alternative Collateral Tokens)
open-long-usdc:
	OPERATION_TYPE=open MARKET_ADDRESS=$(MARKET) PAY_AMOUNT=1 LEVERAGE=1 IS_LONG=true COLLATERAL_TOKEN_ADDRESS=$(USDC) npx tsx test/test-operations.ts

open-short-ceur:
	OPERATION_TYPE=open MARKET_ADDRESS=$(MARKET) PAY_AMOUNT=1 LEVERAGE=1 IS_LONG=false COLLATERAL_TOKEN_ADDRESS=$(CEUR) npx tsx test/test-operations.ts

# Open Position (Limit Orders)
open-limit:
	OPERATION_TYPE=open MARKET_ADDRESS=$(MARKET) PAY_AMOUNT=1 LEVERAGE=1 IS_LONG=true TRIGGER_PRICE_PERCENT=$(TRIGGER_PRICE_PERCENT) npx tsx test/test-operations.ts

open-limit-short:
	OPERATION_TYPE=open MARKET_ADDRESS=$(MARKET) PAY_AMOUNT=1 LEVERAGE=1 IS_LONG=false TRIGGER_PRICE_PERCENT=$(TRIGGER_PRICE_PERCENT) npx tsx test/test-operations.ts

# Increase Position
increase:
	OPERATION_TYPE=increase MARKET_ADDRESS=$(MARKET) PAY_AMOUNT=1 LEVERAGE=2 IS_LONG=true npx tsx test/test-operations.ts

increase-short:
	OPERATION_TYPE=increase MARKET_ADDRESS=$(MARKET) PAY_AMOUNT=1 LEVERAGE=2 IS_LONG=false npx tsx test/test-operations.ts

# Increase Position (Alternative Collateral Tokens)
increase-long-usdc:
	OPERATION_TYPE=increase MARKET_ADDRESS=$(MARKET) PAY_AMOUNT=1 LEVERAGE=2 IS_LONG=true COLLATERAL_TOKEN_ADDRESS=$(USDC) npx tsx test/test-operations.ts

increase-short-ceur:
	OPERATION_TYPE=increase MARKET_ADDRESS=$(MARKET) PAY_AMOUNT=1 LEVERAGE=2 IS_LONG=false COLLATERAL_TOKEN_ADDRESS=$(CEUR) npx tsx test/test-operations.ts

# Increase Position (Limit Orders)
TRIGGER_PRICE_PERCENT=-0.05
increase-limit:
	OPERATION_TYPE=increase MARKET_ADDRESS=$(MARKET) PAY_AMOUNT=0.5 LEVERAGE=2 IS_LONG=true TRIGGER_PRICE_PERCENT=$(TRIGGER_PRICE_PERCENT)  npx tsx test/test-operations.ts

increase-limit-usdc:
	OPERATION_TYPE=increase MARKET_ADDRESS=$(MARKET) PAY_AMOUNT=1 LEVERAGE=2 IS_LONG=true TRIGGER_PRICE_PERCENT=$(TRIGGER_PRICE_PERCENT) COLLATERAL_TOKEN_ADDRESS=$(USDC) npx tsx test/test-operations.ts

increase-limit-short:
	OPERATION_TYPE=increase MARKET_ADDRESS=$(MARKET) PAY_AMOUNT=2 LEVERAGE=2 IS_LONG=false TRIGGER_PRICE_PERCENT=$(TRIGGER_PRICE_PERCENT) npx tsx test/test-operations.ts

# Decrease Position
decrease:
	OPERATION_TYPE=decrease MARKET_ADDRESS=$(MARKET) IS_LONG=true npx tsx test/test-operations.ts

decrease-25:
	OPERATION_TYPE=decrease MARKET_ADDRESS=$(MARKET) IS_LONG=true DECREASE_PERCENTAGE=0.25 npx tsx test/test-operations.ts

decrease-75:
	OPERATION_TYPE=decrease MARKET_ADDRESS=$(MARKET) IS_LONG=true DECREASE_PERCENTAGE=0.75 npx tsx test/test-operations.ts

# Decrease Position (Limit Order)
decrease-limit:
	OPERATION_TYPE=decrease MARKET_ADDRESS=$(MARKET) IS_LONG=true TRIGGER_PRICE_PERCENT=$(TRIGGER_PRICE_PERCENT) npx tsx test/test-operations.ts

# Close Position
close:
	OPERATION_TYPE=close MARKET_ADDRESS=$(MARKET) IS_LONG=true npx tsx test/test-operations.ts

close-short:
	OPERATION_TYPE=close MARKET_ADDRESS=$(MARKET) IS_LONG=false npx tsx test/test-operations.ts

# Close Position (Limit Order)
close-limit:
	OPERATION_TYPE=close MARKET_ADDRESS=$(MARKET) IS_LONG=true TRIGGER_PRICE_PERCENT=$(TRIGGER_PRICE_PERCENT) npx tsx test/test-operations.ts

# Take Profit Orders
takeprofit:
	OPERATION_TYPE=takeprofit MARKET_ADDRESS=$(MARKET) IS_LONG=true PROFIT_PERCENTAGE=5 npx tsx test/test-operations.ts

takeprofit-8:
	OPERATION_TYPE=takeprofit MARKET_ADDRESS=$(MARKET) IS_LONG=true PROFIT_PERCENTAGE=8 SIZE_AMOUNT=100 npx tsx test/test-operations.ts

takeprofit-10:
	OPERATION_TYPE=takeprofit MARKET_ADDRESS=$(MARKET) IS_LONG=true PROFIT_PERCENTAGE=10 npx tsx test/test-operations.ts

# Stop Loss Orders
stoploss:
	OPERATION_TYPE=stoploss MARKET_ADDRESS=$(MARKET) IS_LONG=true LOSS_PERCENTAGE=3 npx tsx test/test-operations.ts

stoploss-5:
	OPERATION_TYPE=stoploss MARKET_ADDRESS=$(MARKET) IS_LONG=true LOSS_PERCENTAGE=5 SIZE_AMOUNT=100 npx tsx test/test-operations.ts

build:
	yarn build
