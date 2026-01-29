# Day 70: Weekly Project – Integrated Crypto Portfolio Manager

**Date:** November 30, 2025

## Learning Objective
To integrate all concepts from the "Blockchain & Crypto" week into a professional portfolio management system that monitors, analyzes, and rebalances assets across multiple venues.

## Concepts Covered
- **Integrated System Architecture**: Building a "Central Brain" that communicates with exchanges and blockchains.
- **Automated Rebalancing**: Calculating deviations from target weights and suggesting trades to restore balance.
- **Holistic Risk Scoring**: A multi-factor model that weights concentration, liquidity, and smart contract risks.
- **Performance Analytics**: Real-time calculation of portfolio VaR, CVaR, and P&L.
- **Radar Visualizations**: Using multi-axis charts to visualize the risk profile of the entire portfolio.

## Code Explanation
The `day_seventy.py` script implements the `CryptoPortfolioManager`:
- **`initialize_components()`**: Sets up authenticated links to `ccxt` exchanges and `web3.py` blockchain nodes.
- **`run_portfolio_analysis()`**: The main asynchronous loop that updates prices, calculates weights, and checks for risk limit violations.
- **`ExecutionManager`**: A safety-first component that handles both "Paper" simulation and a framework for "Live" execution.
- **`generate_portfolio_charts()`**: Produces a 4-panel dashboard showing current allocations vs. targets and the overall risk radar.

## How to Run
1. Install dependencies: `pip install ccxt web3 matplotlib pandas numpy scipy seaborn`
2. Create a `portfolio_config.json` with your target weights and exchange IDs.
3. Run the manager:
```bash
python week_10/dayseventy/day_seventy.py --analyze --rebalance
```

## Reflection
A true crypto portfolio manager must look beyond simple price changes. It must account for the unique risks of the space—like protocol hacks or network congestion. This project demonstrates how Python can unify these disparate data sources into a single source of truth for an investor.
