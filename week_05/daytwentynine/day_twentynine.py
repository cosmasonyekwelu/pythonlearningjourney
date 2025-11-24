"""
Python Learning Journey - Day Twenty Nine
Topic: Real-time Data Updates with Yahoo & CoinGecko API Comparison
Date: October 20, 2025
Author: Cosmas Onyekwelu
"""

import requests
import yfinance as yf
import time
import threading
import logging
from typing import Dict, Callable, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConnectionStatus(Enum):
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    ERROR = "error"
    POLLING = "polling"


class APIType(Enum):
    YAHOO = "yahoo"
    COINGECKO = "coingecko"


@dataclass
class PriceUpdate:
    symbol: str
    price: float
    timestamp: float
    change_24h: Optional[float] = None
    volume_24h: Optional[float] = None
    market_cap: Optional[float] = None
    name: Optional[str] = None
    api_source: Optional[str] = None

    def to_dict(self):
        return {
            'symbol': self.symbol,
            'price': self.price,
            'timestamp': self.timestamp,
            'change_24h': self.change_24h,
            'volume_24h': self.volume_24h,
            'market_cap': self.market_cap,
            'name': self.name,
            'api_source': self.api_source,
            'formatted_time': datetime.fromtimestamp(self.timestamp).strftime('%H:%M:%S')
        }


class DualAPIProvider:
    """
    Dual API provider that fetches from both Yahoo Finance and CoinGecko
    Shows results from both and compares prices
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CryptoDashboard/1.0',
            'Accept': 'application/json'
        })

        # Both APIs we want to use
        self.all_apis = [APIType.YAHOO, APIType.COINGECKO]
        self.api_stats = {api: {'success': 0, 'errors': 0,
                                'last_used': 0} for api in self.all_apis}

        # Rate limits
        self.rate_limits = {
            APIType.COINGECKO: 5,
            APIType.YAHOO: 30,
        }
        self.last_call_time = {api: 0 for api in self.all_apis}

        # Symbol mapping for CoinGecko
        self.coingecko_mapping = {
            'BTC': 'bitcoin', 'ETH': 'ethereum', 'ADA': 'cardano',
            'DOT': 'polkadot', 'LINK': 'chainlink',
            'SOL': 'solana', 'XRP': 'ripple'
        }

    def can_make_request(self, api: APIType) -> bool:
        """Check if we can make a request based on rate limits"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time[api]
        min_interval = 60 / self.rate_limits[api]
        return time_since_last_call >= min_interval

    def record_api_call(self, api: APIType, success: bool, symbols_fetched: int = 0):
        """Record API call statistics"""
        self.last_call_time[api] = time.time()
        if success:
            self.api_stats[api]['success'] += 1
            self.api_stats[api]['last_symbols_fetched'] = symbols_fetched
        else:
            self.api_stats[api]['errors'] += 1
        self.api_stats[api]['last_used'] = time.time()

    def fetch_via_yahoo(self, symbols: List[str]) -> Dict[str, PriceUpdate]:
        """Fetch prices via Yahoo Finance"""
        if not self.can_make_request(APIType.YAHOO):
            return {}

        results = {}
        successful_symbols = 0

        print("YAHOO FINANCE RESULTS")
        print("-" * 40)

        for symbol in symbols:
            try:
                ticker_symbol = f"{symbol}-USD"
                ticker = yf.Ticker(ticker_symbol)
                hist = ticker.history(period="2d")

                if not hist.empty and len(hist) >= 2:
                    current_price = float(hist['Close'].iloc[-1])
                    prev_price = float(hist['Close'].iloc[0])
                    change_24h = (
                        (current_price - prev_price) / prev_price) * 100

                    results[symbol] = PriceUpdate(
                        symbol=symbol,
                        price=current_price,
                        timestamp=time.time(),
                        change_24h=change_24h,
                        volume_24h=float(
                            hist['Volume'].iloc[-1]) if 'Volume' in hist else None,
                        name=symbol,
                        api_source=APIType.YAHOO.value
                    )
                    successful_symbols += 1

                    # Print individual result
                    change_str = f"+{change_24h:.2f}%" if change_24h >= 0 else f"{change_24h:.2f}%"
                    print(f"{symbol}: ${current_price:.2f} ({change_str})")

                else:
                    print(f"{symbol}: No data available")

            except Exception as e:
                print(f"{symbol}: Error - {str(e)}")
                continue

        print(
            f"Yahoo Summary: {successful_symbols}/{len(symbols)} symbols successful")
        print()
        self.record_api_call(
            APIType.YAHOO, successful_symbols > 0, successful_symbols)
        return results

    def fetch_via_coingecko(self, symbols: List[str]) -> Dict[str, PriceUpdate]:
        """Fetch prices via CoinGecko API"""
        if not self.can_make_request(APIType.COINGECKO):
            return {}

        try:
            coin_ids = [self.coingecko_mapping.get(sym) for sym in symbols]
            coin_ids = [cid for cid in coin_ids if cid]

            if not coin_ids:
                return {}

            ids = ','.join(coin_ids)
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': ids,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_market_cap': 'true'
            }

            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 429:
                print("CoinGecko: Rate limit hit - waiting for next interval")
                self.record_api_call(APIType.COINGECKO, False)
                return {}

            response.raise_for_status()
            data = response.json()

            results = {}
            successful_symbols = 0

            print("COINGECKO RESULTS")
            print("-" * 40)

            for coin_id, price_data in data.items():
                symbol = next((k for k, v in self.coingecko_mapping.items()
                               if v == coin_id), coin_id.upper())

                price = price_data.get('usd', 0)
                change_24h = price_data.get('usd_24h_change', 0)

                results[symbol] = PriceUpdate(
                    symbol=symbol,
                    price=price,
                    timestamp=time.time(),
                    change_24h=change_24h,
                    volume_24h=price_data.get('usd_24h_vol'),
                    market_cap=price_data.get('usd_market_cap'),
                    name=coin_id.title(),
                    api_source=APIType.COINGECKO.value
                )
                successful_symbols += 1

                # Print individual result
                change_str = f"+{change_24h:.2f}%" if change_24h >= 0 else f"{change_24h:.2f}%"
                print(f"{symbol}: ${price:.2f} ({change_str})")

            print(
                f"CoinGecko Summary: {successful_symbols}/{len(symbols)} symbols successful")
            print()
            self.record_api_call(
                APIType.COINGECKO, successful_symbols > 0, successful_symbols)
            return results

        except Exception as e:
            print(f"CoinGecko Error: {str(e)}")
            self.record_api_call(APIType.COINGECKO, False)
            return {}

    def fetch_both_apis_and_compare(self, symbols: List[str]) -> Dict[str, PriceUpdate]:
        """
        Fetch from both APIs and compare results
        Returns combined results but shows individual API outputs
        """
        all_results = {}
        api_results = {}

        print("\n" + "="*60)
        print(
            f"FETCHING PRICES FROM BOTH APIS - {datetime.now().strftime('%H:%M:%S')}")
        print("="*60)
        print()

        # Fetch from Yahoo Finance
        yahoo_results = self.fetch_via_yahoo(symbols)
        api_results[APIType.YAHOO.value] = yahoo_results

        # Fetch from CoinGecko
        coingecko_results = self.fetch_via_coingecko(symbols)
        api_results[APIType.COINGECKO.value] = coingecko_results

        # Combine results (Yahoo takes priority for symbols available in both)
        for symbol, update in yahoo_results.items():
            all_results[symbol] = update
        for symbol, update in coingecko_results.items():
            if symbol not in all_results:  # Only add if not already from Yahoo
                all_results[symbol] = update

        # Print comparison
        self.print_api_comparison(api_results, symbols)

        return all_results

    def print_api_comparison(self, api_results: Dict, symbols: List[str]):
        """Print comparison of prices from both APIs"""
        print("="*60)
        print("PRICE COMPARISON: YAHOO FINANCE vs COINGECKO")
        print("="*60)

        comparison_data = []

        for symbol in symbols:
            yahoo_price = None
            coingecko_price = None

            if APIType.YAHOO.value in api_results and symbol in api_results[APIType.YAHOO.value]:
                yahoo_price = api_results[APIType.YAHOO.value][symbol].price

            if APIType.COINGECKO.value in api_results and symbol in api_results[APIType.COINGECKO.value]:
                coingecko_price = api_results[APIType.COINGECKO.value][symbol].price

            if yahoo_price is not None and coingecko_price is not None:
                # Both APIs have data - calculate difference
                difference = abs(yahoo_price - coingecko_price)
                difference_pct = (
                    difference / min(yahoo_price, coingecko_price)) * 100

                comparison_data.append({
                    'symbol': symbol,
                    'yahoo': yahoo_price,
                    'coingecko': coingecko_price,
                    'difference': difference,
                    'difference_pct': difference_pct,
                    'status': 'BOTH'
                })

            elif yahoo_price is not None:
                # Only Yahoo has data
                comparison_data.append({
                    'symbol': symbol,
                    'yahoo': yahoo_price,
                    'coingecko': None,
                    'difference': None,
                    'difference_pct': None,
                    'status': 'YAHOO_ONLY'
                })

            elif coingecko_price is not None:
                # Only CoinGecko has data
                comparison_data.append({
                    'symbol': symbol,
                    'yahoo': None,
                    'coingecko': coingecko_price,
                    'difference': None,
                    'difference_pct': None,
                    'status': 'COINGECKO_ONLY'
                })
            else:
                # No API has data
                comparison_data.append({
                    'symbol': symbol,
                    'yahoo': None,
                    'coingecko': None,
                    'difference': None,
                    'difference_pct': None,
                    'status': 'NONE'
                })

        # Print comparison table
        print("\nSymbol         Yahoo Finance    CoinGecko      Difference    Status")
        print("-" * 70)

        for data in comparison_data:
            symbol = data['symbol']

            if data['status'] == 'BOTH':
                yahoo_str = f"${data['yahoo']:12.2f}"
                coingecko_str = f"${data['coingecko']:12.2f}"
                diff_str = f"${data['difference']:.2f} ({data['difference_pct']:.3f}%)"
                status = "BOTH"

            elif data['status'] == 'YAHOO_ONLY':
                yahoo_str = f"${data['yahoo']:12.2f}"
                coingecko_str = "No data"
                diff_str = "N/A"
                status = "YAHOO ONLY"

            elif data['status'] == 'COINGECKO_ONLY':
                yahoo_str = "No data"
                coingecko_str = f"${data['coingecko']:12.2f}"
                diff_str = "N/A"
                status = "COINGECKO ONLY"

            else:  # NONE
                yahoo_str = "No data"
                coingecko_str = "No data"
                diff_str = "N/A"
                status = "NO DATA"

            print(
                f"{symbol:8} {yahoo_str:16} {coingecko_str:16} {diff_str:16} {status:16}")

        # Calculate overall statistics
        both_count = len([d for d in comparison_data if d['status'] == 'BOTH'])
        yahoo_only = len(
            [d for d in comparison_data if d['status'] == 'YAHOO_ONLY'])
        coingecko_only = len(
            [d for d in comparison_data if d['status'] == 'COINGECKO_ONLY'])
        none_count = len([d for d in comparison_data if d['status'] == 'NONE'])

        print("\nSUMMARY:")
        print(f"Symbols with data from both APIs: {both_count}/{len(symbols)}")
        print(f"Symbols with Yahoo data only: {yahoo_only}/{len(symbols)}")
        print(
            f"Symbols with CoinGecko data only: {coingecko_only}/{len(symbols)}")
        print(f"Symbols with no data: {none_count}/{len(symbols)}")
        print()

    def get_api_stats(self) -> Dict:
        """Get API usage statistics"""
        stats = {}
        for api, data in self.api_stats.items():
            total_calls = data['success'] + data['errors']
            stats[api.value] = {
                'success': data['success'],
                'errors': data['errors'],
                'success_rate': data['success'] / max(1, total_calls) * 100,
                'last_symbols_fetched': data.get('last_symbols_fetched', 0)
            }
        return stats


class RealTimeData:
    """
    Real-time data provider that shows both API results
    """

    def __init__(
        self,
        symbols: List[str],
        on_price_update: Optional[Callable] = None,
        update_interval: int = 30,
        vs_currency: str = 'usd'
    ):
        self.symbols = symbols
        self.on_price_update = on_price_update
        self.update_interval = update_interval
        self.vs_currency = vs_currency

        self.api_provider = DualAPIProvider()
        self.prices: Dict[str, PriceUpdate] = {}
        self.price_history: Dict[str, List[PriceUpdate]] = {}
        self.connection_status = ConnectionStatus.DISCONNECTED
        self.is_running = False
        self.poll_count = 0

    def fetch_prices(self):
        """Fetch current prices from both APIs and show comparisons"""
        try:
            results = self.api_provider.fetch_both_apis_and_compare(
                self.symbols)

            for symbol, price_update in results.items():
                self.prices[symbol] = price_update

                if symbol not in self.price_history:
                    self.price_history[symbol] = []
                self.price_history[symbol].append(price_update)

                if len(self.price_history[symbol]) > 50:
                    self.price_history[symbol].pop(0)

                if self.on_price_update:
                    self.on_price_update(price_update)

            self.poll_count += 1
            return len(results) > 0

        except Exception as e:
            logger.error(f"Error in fetch_prices: {e}")
            self.connection_status = ConnectionStatus.ERROR
            return False

    def start(self):
        """Start polling for price updates"""
        self.is_running = True
        self.connection_status = ConnectionStatus.POLLING
        print(
            f"Starting dual-API comparison tracker for {len(self.symbols)} symbols")
        print(f"Update interval: {self.update_interval} seconds")
        print()

        def poll_loop():
            while self.is_running:
                success = self.fetch_prices()
                if success:
                    self.connection_status = ConnectionStatus.CONNECTED
                else:
                    self.connection_status = ConnectionStatus.ERROR
                time.sleep(self.update_interval)

        self.poll_thread = threading.Thread(target=poll_loop)
        self.poll_thread.daemon = True
        self.poll_thread.start()

    def stop(self):
        """Stop polling"""
        self.is_running = False
        self.connection_status = ConnectionStatus.DISCONNECTED
        print("Stopped dual-API comparison tracker")

    def get_all_prices(self) -> Dict[str, PriceUpdate]:
        return self.prices.copy()

    def get_price_history(self, symbol: str) -> List[dict]:
        if symbol in self.price_history:
            return [update.to_dict() for update in self.price_history[symbol]]
        return []

    def get_connection_status(self) -> str:
        return self.connection_status.value

    def get_statistics(self) -> Dict:
        api_stats = self.api_provider.get_api_stats()
        return {
            "poll_count": self.poll_count,
            "tracked_symbols": len(self.prices),
            "connection_status": self.connection_status.value,
            "update_interval": self.update_interval,
            "api_performance": api_stats
        }


class PriceMonitor:
    def __init__(self):
        self.last_prices = {}

    def on_price_update(self, price_update: PriceUpdate):
        """Simple callback - prices are already printed in main flow"""
        pass


def main():
    print("Day 29 - Dual API Crypto Price Comparison")
    print("Shows results from Yahoo Finance and CoinGecko with price comparisons")
    print("=" * 70)

    symbols = ['BTC', 'ETH', 'ADA', 'DOT', 'LINK', 'SOL', 'XRP']

    monitor = PriceMonitor()
    data_provider = RealTimeData(
        symbols, monitor.on_price_update, update_interval=30)

    try:
        data_provider.start()

        while True:
            time.sleep(30)
            stats = data_provider.get_statistics()
            print(f"SUMMARY - Poll {stats['poll_count']}")
            print(
                f"Symbols tracked: {stats['tracked_symbols']}/{len(symbols)}")
            print(
                f"Status: {stats['connection_status']} | Interval: {stats['update_interval']}s")

            print("API Performance:")
            for api, perf in stats['api_performance'].items():
                print(f"  {api}: {perf['success_rate']:.1f}% success rate")
            print("=" * 70)
            print()

    except KeyboardInterrupt:
        print("\nStopping dual-API comparison tracker...")
        data_provider.stop()


if __name__ == "__main__":
    main()
