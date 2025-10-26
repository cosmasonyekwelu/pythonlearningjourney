"""
Python Learning Journey - Day Thirty Five
Week 5 Summary -  Financial Programming Essentials
Date: October 26, 2025
Author: Cosmas Onyekwelu
"""
from src.reporting import report_generator
from src.data_collection import data_collector
from src.stock_data_analyzer import stock_analyzer
import argparse
import json
import os
import sys
from typing import List

# Make sure we can import from ./src
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Optional .env support
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Project modules


def cmd_analyze(symbol: str, period: str, interval: str, out_format: str):
    """Analyze a single stock and either print JSON summary or produce an HTML report."""
    print(f"Analyzing {symbol} for period '{period}' (interval {interval})...")
    analysis = stock_analyzer.analyze_stock(symbol, period, interval)

    if 'error' in analysis:
        print(f"Error: {analysis['error']}")
        return

    if out_format == 'json':
        summary = {
            'symbol': analysis['symbol'],
            'period': analysis['period'],
            'interval': analysis['interval'],
            'current_price': float(analysis['data']['Close'].iloc[-1]) if not analysis['data'].empty else None,
            'technical_indicators': analysis['technical_indicators'],
            'risk_metrics': analysis['risk_metrics'],
            'analysis_timestamp': analysis['analysis_timestamp'],
        }
        print(json.dumps(summary, indent=2, default=str))
    else:
        path = stock_analyzer.generate_report(
            analysis, report_type='stock', format='html')
        print(f"HTML report generated: {path}")


def cmd_compare(symbols: List[str], period: str, interval: str, portfolio_report: str = None):
    """Compare multiple stocks, print correlation and portfolio risk; optionally export a portfolio report."""
    print(
        f"Comparing {', '.join(symbols)} for period '{period}' (interval {interval})...")
    comparison = stock_analyzer.compare_stocks(symbols, period, interval)

    if 'error' in comparison:
        print(f"Error: {comparison['error']}")
        return

    corr = comparison['portfolio_analysis']['correlation_matrix']
    print("\nCorrelation Matrix:")
    try:
        print(corr.round(3))
    except Exception:
        print(corr)

    risk = comparison['portfolio_analysis']['portfolio_risk']
    print("\nPortfolio Risk Metrics:")
    for k, v in risk.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.4f}")
        else:
            print(f"  {k}: {v}")

    if portfolio_report:
        path = report_generator.generate_portfolio_report(
            comparison['portfolio_analysis'], format=portfolio_report)
        print(
            f"\nPortfolio {portfolio_report.upper()} report generated: {path}")


def cmd_report(symbol: str, fmt: str):
    """Generate single-stock report in html/csv/excel."""
    print(f"Generating {fmt.upper()} report for {symbol}...")
    analysis = stock_analyzer.analyze_stock(symbol)
    if 'error' in analysis:
        print(f"Error: {analysis['error']}")
        return
    path = stock_analyzer.generate_report(
        analysis, report_type='stock', format=fmt)
    print(f"Report generated: {path}")


def cmd_portfolio_report(symbols: List[str], period: str, interval: str, fmt: str):
    """Generate portfolio report in html/csv/excel."""
    print(
        f"Building portfolio analysis for {', '.join(symbols)} ({period}, {interval})...")
    comparison = stock_analyzer.compare_stocks(symbols, period, interval)
    if 'error' in comparison:
        print(f"Error: {comparison['error']}")
        return
    path = report_generator.generate_portfolio_report(
        comparison['portfolio_analysis'], format=fmt)
    print(f"Portfolio report generated: {path}")


def cmd_screen(max_volatility: float = None, min_sharpe: float = None):
    """Screen stocks by simple criteria and print top matches."""
    criteria = {}
    if max_volatility is not None:
        criteria['max_volatility'] = max_volatility
    if min_sharpe is not None:
        criteria['min_sharpe'] = min_sharpe

    print("Screening universe...")
    results = stock_analyzer.screen_stocks(criteria)

    print(f"\nFound {len(results)} matching stocks (showing top 10):")
    for row in results[:10]:
        sym = row['symbol']
        score = row['score']
        rm = row['analysis']['risk_metrics']
        sr = rm.get('sharpe_ratio', 0)
        vol = rm.get('volatility', 0)
        print(
            f"- {sym:6s} | Score: {score:8.2f} | Sharpe: {sr:6.3f} | Vol: {vol:6.3f}")


def cmd_recommend(symbol: str, period: str):
    """Get a simple recommendation (BUY/HOLD/SELL) with reasons."""
    rec = stock_analyzer.get_stock_recommendation(symbol, period)
    if 'error' in rec:
        print(f"Error: {rec['error']}")
        return
    print(
        f"\nRecommendation for {symbol} ({period}): {rec['recommendation']}  (Confidence: {rec['confidence']})")
    if rec.get('reasons'):
        print("Reasons:")
        for r in rec['reasons']:
            print(f"  - {r}")
    if rec.get('analysis_summary'):
        print("\nAnalysis summary:")
        for k, v in rec['analysis_summary'].items():
            print(f"  {k}: {v}")


def cmd_clear_cache(days: int):
    """Clear cached data older than N days."""
    print(f"Clearing cache older than {days} day(s)...")
    data_collector.clear_cache(days)
    print("Cache cleared.")


def cmd_dashboard(host: str, port: int, debug: bool):
    """Launch the Dash dashboard within this unified launcher."""
    print(f"Starting dashboard at http://{host}:{port} (debug={debug})")
    # Import here so CLI runs fast when dashboard isn't requested
    import dashboard as _dash_app
    _dash_app.app.run_server(debug=debug, host=host, port=port)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Day 35 - Stock Data Analyzer")
    sub = p.add_subparsers(dest="command")

    # analyze
    ap = sub.add_parser("analyze", help="Analyze a single stock")
    ap.add_argument("symbol", help="Ticker, e.g. AAPL")
    ap.add_argument("--period", default=os.getenv("DEFAULT_PERIOD",
                    "1y"), help="e.g. 1y, 6mo, 3mo, 2y")
    ap.add_argument("--interval", default="1d", help="e.g. 1d, 1h, 1wk")
    ap.add_argument(
        "--format", choices=["json", "report"], default="json", dest="out_format")

    # compare
    cp = sub.add_parser("compare", help="Compare multiple stocks")
    cp.add_argument("symbols", nargs="+", help="Tickers, e.g. AAPL MSFT GOOGL")
    cp.add_argument("--period", default=os.getenv("DEFAULT_PERIOD", "1y"))
    cp.add_argument("--interval", default="1d")
    cp.add_argument("--portfolio-report",
                    choices=["html", "csv", "excel"], dest="portfolio_report")

    # report
    rp = sub.add_parser("report", help="Generate single-stock report")
    rp.add_argument("symbol")
    rp.add_argument(
        "--format", choices=["html", "csv", "excel"], default="html")

    # portfolio-report
    pr = sub.add_parser("portfolio-report",
                        help="Generate portfolio report for symbols")
    pr.add_argument("symbols", nargs="+")
    pr.add_argument("--period", default=os.getenv("DEFAULT_PERIOD", "1y"))
    pr.add_argument("--interval", default="1d")
    pr.add_argument(
        "--format", choices=["html", "csv", "excel"], default="html")

    # screen
    sp = sub.add_parser("screen", help="Screen stocks by simple criteria")
    sp.add_argument("--max-volatility", type=float,
                    help="e.g. 0.30 for 30%% annualized")
    sp.add_argument("--min-sharpe", type=float, help="e.g. 0.5")

    # recommend
    recp = sub.add_parser(
        "recommend", help="Get a BUY/HOLD/SELL recommendation")
    recp.add_argument("symbol")
    recp.add_argument("--period", default=os.getenv("DEFAULT_PERIOD", "1y"))

    # clear-cache
    ccp = sub.add_parser("clear-cache", help="Clear cached data files")
    ccp.add_argument("--days", type=int, default=7)

    # dashboard
    dbp = sub.add_parser("dashboard", help="Launch the interactive dashboard")
    dbp.add_argument("--host", default="0.0.0.0")
    dbp.add_argument("--port", type=int, default=8050)
    dbp.add_argument("--debug", action="store_true")

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "analyze":
            cmd_analyze(args.symbol, args.period,
                        args.interval, args.out_format)
        elif args.command == "compare":
            cmd_compare(args.symbols, args.period,
                        args.interval, args.portfolio_report)
        elif args.command == "report":
            cmd_report(args.symbol, args.format)
        elif args.command == "portfolio-report":
            cmd_portfolio_report(args.symbols, args.period,
                                 args.interval, args.format)
        elif args.command == "screen":
            cmd_screen(args.max_volatility, args.min_sharpe)
        elif args.command == "recommend":
            cmd_recommend(args.symbol, args.period)
        elif args.command == "clear-cache":
            cmd_clear_cache(args.days)
        elif args.command == "dashboard":
            cmd_dashboard(args.host, args.port, args.debug)
        else:
            parser.print_help()
    except KeyboardInterrupt:
        print("\nInterrupted.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
