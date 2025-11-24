"""
Command Line Interface for Stock Data Analyzer
"""

from data_collection import data_collector
from stock_data_analyzer import stock_analyzer
import argparse
import sys
import os
from typing import List
import json

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='Stock Data Analyzer CLI')

    subparsers = parser.add_subparsers(
        dest='command', help='Available commands')

    # Analyze single stock
    analyze_parser = subparsers.add_parser(
        'analyze', help='Analyze a single stock')
    analyze_parser.add_argument('symbol', help='Stock symbol to analyze')
    analyze_parser.add_argument(
        '--period', default='1y', help='Time period (1y, 6mo, 3mo, etc.)')
    analyze_parser.add_argument(
        '--format', choices=['json', 'report'], default='json', help='Output format')

    # Compare multiple stocks
    compare_parser = subparsers.add_parser(
        'compare', help='Compare multiple stocks')
    compare_parser.add_argument(
        'symbols', nargs='+', help='Stock symbols to compare')
    compare_parser.add_argument('--period', default='1y', help='Time period')

    # Generate report
    report_parser = subparsers.add_parser(
        'report', help='Generate analysis report')
    report_parser.add_argument('symbol', help='Stock symbol')
    report_parser.add_argument(
        '--format', choices=['html', 'csv', 'excel'], default='html', help='Report format')

    # Screen stocks
    screen_parser = subparsers.add_parser(
        'screen', help='Screen stocks based on criteria')
    screen_parser.add_argument(
        '--max-volatility', type=float, help='Maximum volatility')
    screen_parser.add_argument(
        '--min-sharpe', type=float, help='Minimum Sharpe ratio')

    # Clear cache
    cache_parser = subparsers.add_parser(
        'clear-cache', help='Clear data cache')
    cache_parser.add_argument(
        '--days', type=int, default=7, help='Clear cache older than X days')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == 'analyze':
            analyze_stock(args.symbol, args.period, args.format)
        elif args.command == 'compare':
            compare_stocks(args.symbols, args.period)
        elif args.command == 'report':
            generate_report(args.symbol, args.format)
        elif args.command == 'screen':
            screen_stocks(args)
        elif args.command == 'clear-cache':
            clear_cache(args.days)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def analyze_stock(symbol: str, period: str, format: str):
    """Analyze a single stock"""
    print(f"Analyzing {symbol} for period {period}...")

    analysis = stock_analyzer.analyze_stock(symbol, period)

    if 'error' in analysis:
        print(f"Error: {analysis['error']}")
        return

    if format == 'json':
        # Print summary in JSON format
        summary = {
            'symbol': analysis['symbol'],
            'current_price': analysis['data']['Close'].iloc[-1] if not analysis['data'].empty else 'N/A',
            'technical_indicators': analysis['technical_indicators'],
            'risk_metrics': analysis['risk_metrics']
        }
        print(json.dumps(summary, indent=2, default=str))
    else:
        # Generate and show report path
        report_path = stock_analyzer.generate_report(analysis, 'stock', 'html')
        print(f"Report generated: {report_path}")


def compare_stocks(symbols: List[str], period: str):
    """Compare multiple stocks"""
    print(f"Comparing {', '.join(symbols)} for period {period}...")

    comparison = stock_analyzer.compare_stocks(symbols, period)

    if 'error' in comparison:
        print(f"Error: {comparison['error']}")
        return

    # Print correlation matrix
    correlation_matrix = comparison['portfolio_analysis']['correlation_matrix']
    print("\nCorrelation Matrix:")
    print(correlation_matrix.round(3))

    # Print portfolio risk metrics
    portfolio_risk = comparison['portfolio_analysis']['portfolio_risk']
    print("\nPortfolio Risk Metrics:")
    for metric, value in portfolio_risk.items():
        if isinstance(value, float):
            print(f"  {metric}: {value:.4f}")


def generate_report(symbol: str, format: str):
    """Generate analysis report"""
    print(f"Generating {format} report for {symbol}...")

    analysis = stock_analyzer.analyze_stock(symbol)

    if 'error' in analysis:
        print(f"Error: {analysis['error']}")
        return

    report_path = stock_analyzer.generate_report(analysis, 'stock', format)
    print(f"Report generated: {report_path}")


def screen_stocks(args):
    """Screen stocks based on criteria"""
    criteria = {}
    if args.max_volatility:
        criteria['max_volatility'] = args.max_volatility
    if args.min_sharpe:
        criteria['min_sharpe'] = args.min_sharpe

    print("Screening stocks...")
    screened_stocks = stock_analyzer.screen_stocks(criteria)

    print(f"\nFound {len(screened_stocks)} stocks matching criteria:")
    for stock in screened_stocks[:5]:  # Show top 5
        symbol = stock['symbol']
        score = stock['score']
        risk_metrics = stock['analysis']['risk_metrics']

        print(f"\n{symbol} (Score: {score:.2f})")
        print(f"  Sharpe Ratio: {risk_metrics.get('sharpe_ratio', 'N/A'):.3f}")
        print(f"  Volatility: {risk_metrics.get('volatility', 'N/A'):.3f}")


def clear_cache(days: int):
    """Clear data cache"""
    print(f"Clearing cache older than {days} days...")
    data_collector.clear_cache(days)
    print("Cache cleared")


if __name__ == '__main__':
    main()
