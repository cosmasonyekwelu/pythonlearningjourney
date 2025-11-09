"""
Day 49 – Automated Trading Bot (Paper Mode)
"""

import os
import json
import time
import math
import uuid
import queue
import signal
import logging
import datetime as dt
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple

import numpy as np
import pandas as pd

try:
    import ccxt  # optional
except Exception:
    ccxt = None

try:
    from dotenv import load_dotenv  # optional
    load_dotenv()
except Exception:
    pass

# -----------------------------
# Logging setup
# -----------------------------
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, f"bot_{dt.date.today()}.log")),
        logging.StreamHandler()
    ],
)

# -----------------------------
# Config loader
# -----------------------------
DEFAULT_CONFIG = {
    "mode": "paper",                           # "paper" or "live" (live requires ccxt + exchange config)
    "symbol": "BTC/USDT",
    "exchange": "binance",                     # used if ccxt is enabled
    "timeframe": "1h",                         # used if ccxt is enabled
    "fetch_limit": 500,                        # historical candles to pull
    "data_csv": "sample_data.csv",             # fallback data if no API
    "strategy": "ma_crossover",                # "ma_crossover" or "mean_reversion"
    "ma_short": 20,
    "ma_long": 50,
    "mr_lookback": 20,
    "mr_threshold_pct": 2.0,                  # % below/above mean to trigger signal
    "risk": {
        "max_position_pct": 10.0,             # max % of equity per single position
        "per_trade_stop_pct": 2.0,            # stop-loss %
        "per_trade_take_profit_pct": 4.0,     # take-profit %
        "max_daily_drawdown_pct": 5.0         # halt for the day if equity down this %
    },
    "starting_equity": 10000.0,
    "report_dir": "reports",
    "poll_interval_seconds": 60,              # how often to run the loop
    "simulate_slippage_pct": 0.02,            # 0.02% slippage
    "save_orders_csv": "orders.csv",
    "save_trades_csv": "trades.csv",
    "save_equity_csv": "equity_curve.csv"
}

def load_config(path: str = "config.json") -> Dict[str, Any]:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        # merge with defaults (shallow)
        merged = {**DEFAULT_CONFIG, **cfg}
        # nested risk
        if "risk" in cfg:
            merged["risk"] = {**DEFAULT_CONFIG["risk"], **cfg["risk"]}
        return merged
    return DEFAULT_CONFIG.copy()

# -----------------------------
# Data feed
# -----------------------------
class DataFeed:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg
        self.exchange = None
        if ccxt and cfg.get("mode") != "paper":  # live mode (or ccxt usage)
            ex_name = cfg.get("exchange", "binance")
            self.exchange = getattr(ccxt, ex_name)() if hasattr(ccxt, ex_name) else None
            # If you want auth: self.exchange.apiKey = os.getenv("API_KEY"); self.exchange.secret = ...
        # Cache last candles
        self.df = None

    def fetch(self) -> pd.DataFrame:
        """
        Returns a DataFrame with columns: ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        Timestamp in pandas datetime (UTC).
        """
        # Try ccxt
        if self.exchange and hasattr(self.exchange, "fetch_ohlcv"):
            symbol = self.cfg["symbol"]
            timeframe = self.cfg["timeframe"]
            limit = self.cfg["fetch_limit"]
            logging.info(f"Fetching OHLCV via ccxt: {symbol} {timeframe} limit={limit}")
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            df = pd.DataFrame(
                ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
            )
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
            self.df = df
            return df

        # Fallback CSV
        csv_path = self.cfg.get("data_csv", "sample_data.csv")
        if not os.path.exists(csv_path):
            raise FileNotFoundError(
                f"No API data and CSV fallback not found: {csv_path}. "
                f"Provide sample_data.csv with columns timestamp,open,high,low,close,volume."
            )
        logging.info(f"Loading OHLCV from CSV: {csv_path}")
        df = pd.read_csv(csv_path)
        # Expect 'timestamp' as ISO string or epoch ms
        if np.issubdtype(df["timestamp"].dtype, np.number):
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        else:
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        self.df = df[["timestamp", "open", "high", "low", "close", "volume"]].copy()
        return self.df

# -----------------------------
# Indicators & strategies
# -----------------------------
def ma(series: pd.Series, n: int) -> pd.Series:
    return series.rolling(n, min_periods=n).mean()

class Strategy:
    def generate_signal(self, df: pd.DataFrame) -> Optional[str]:
        raise NotImplementedError

class MovingAverageCrossover(Strategy):
    def __init__(self, short_n: int, long_n: int):
        if short_n >= long_n:
            raise ValueError("short MA must be < long MA")
        self.short_n = short_n
        self.long_n = long_n

    def generate_signal(self, df: pd.DataFrame) -> Optional[str]:
        data = df.copy()
        data["ma_s"] = ma(data["close"], self.short_n)
        data["ma_l"] = ma(data["close"], self.long_n)
        last = data.dropna().iloc[-1] if len(data.dropna()) else None
        prev = data.dropna().iloc[-2] if len(data.dropna()) > 1 else None
        if last is None or prev is None:
            return None

        # Cross detection
        crossed_up = prev["ma_s"] <= prev["ma_l"] and last["ma_s"] > last["ma_l"]
        crossed_down = prev["ma_s"] >= prev["ma_l"] and last["ma_s"] < last["ma_l"]
        if crossed_up:
            return "buy"
        if crossed_down:
            return "sell"
        return None

class MeanReversion(Strategy):
    def __init__(self, lookback: int, threshold_pct: float):
        self.lookback = lookback
        self.threshold = threshold_pct / 100.0

    def generate_signal(self, df: pd.DataFrame) -> Optional[str]:
        if len(df) < self.lookback:
            return None
        data = df.copy()
        data["mean"] = data["close"].rolling(self.lookback, min_periods=self.lookback).mean()
        last = data.dropna().iloc[-1] if len(data.dropna()) else None
        if last is None:
            return None
        price = last["close"]
        mean = last["mean"]
        if price <= mean * (1 - self.threshold):
            return "buy"
        if price >= mean * (1 + self.threshold):
            return "sell"
        return None

# -----------------------------
# OMS + Paper Broker
# -----------------------------
@dataclass
class Order:
    id: str
    symbol: str
    side: str           # "buy" or "sell"
    qty: float
    status: str = "PENDING"
    price: Optional[float] = None
    ts: dt.datetime = field(default_factory=lambda: dt.datetime.now(dt.timezone.utc))
    filled_ts: Optional[dt.datetime] = None

@dataclass
class Position:
    symbol: str
    qty: float = 0.0
    avg_price: float = 0.0

class PaperBroker:
    """
    Super-simple paper broker that fills at last price +/- slippage.
    Tracks equity based on last known price for the symbol.
    """
    def __init__(self, starting_equity: float, slippage_pct: float):
        self.cash = starting_equity
        self.positions: Dict[str, Position] = {}
        self.orders: Dict[str, Order] = {}
        self.slippage_pct = slippage_pct / 100.0
        self.equity_curve: List[Tuple[dt.datetime, float]] = []
        self.realized_pnl = 0.0

    def _apply_slippage(self, price: float, side: str) -> float:
        slip = price * self.slippage_pct
        return price + slip if side == "buy" else price - slip

    def place_order(self, symbol: str, side: str, qty: float, last_price: float) -> Order:
        order_id = str(uuid.uuid4())
        fill_price = self._apply_slippage(last_price, side)
        o = Order(id=order_id, symbol=symbol, side=side, qty=qty, price=fill_price, status="FILLED")
        o.filled_ts = dt.datetime.now(dt.timezone.utc)
        self.orders[o.id] = o

        # Update position & cash
        pos = self.positions.get(symbol, Position(symbol))
        if side == "buy":
            total_cost = qty * fill_price
            if total_cost > self.cash:
                # insufficient funds -> reject
                o.status = "REJECTED"
                logging.warning(f"Order REJECTED (insufficient cash): {o}")
                return o
            # new avg
            new_qty = pos.qty + qty
            pos.avg_price = (pos.avg_price * pos.qty + qty * fill_price) / new_qty if new_qty != 0 else 0.0
            pos.qty = new_qty
            self.cash -= total_cost
        else:  # sell
            if qty > pos.qty:
                # allow short? Not in this simple paper broker
                qty = pos.qty
            proceeds = qty * fill_price
            # realized PnL on the sold portion
            pnl = (fill_price - pos.avg_price) * qty
            self.realized_pnl += pnl
            pos.qty -= qty
            if pos.qty == 0:
                pos.avg_price = 0.0
            self.cash += proceeds

        self.positions[symbol] = pos
        logging.info(f"FILLED {side.upper()} {qty:.6f} {symbol} @ {fill_price:.2f} | cash={self.cash:.2f}")
        return o

    def mark_to_market(self, symbol: str, last_price: float):
        # compute equity = cash + sum(pos.qty * last_price)
        pos = self.positions.get(symbol)
        pos_val = (pos.qty * last_price) if pos else 0.0
        equity = self.cash + pos_val
        self.equity_curve.append((dt.datetime.now(dt.timezone.utc), float(equity)))
        return equity

    def position_value(self, symbol: str, last_price: float) -> float:
        pos = self.positions.get(symbol)
        return (pos.qty * last_price) if pos else 0.0

class OMS:
    def __init__(self, broker: PaperBroker, orders_csv: str, trades_csv: str):
        self.broker = broker
        self.queue = queue.Queue()
        self.orders_csv = orders_csv
        self.trades_csv = trades_csv
        # Ensure CSVs exist with headers
        if not os.path.exists(self.orders_csv):
            pd.DataFrame(columns=["id","symbol","side","qty","price","status","ts","filled_ts"]).to_csv(self.orders_csv, index=False)
        if not os.path.exists(self.trades_csv):
            pd.DataFrame(columns=["ts","symbol","side","qty","price"]).to_csv(self.trades_csv, index=False)

    def submit(self, symbol: str, side: str, qty: float):
        self.queue.put((symbol, side, qty))

    def process(self, last_price: float):
        while not self.queue.empty():
            symbol, side, qty = self.queue.get()
            order = self.broker.place_order(symbol, side, qty, last_price)
            self._record_order(order)
            if order.status == "FILLED":
                self._record_trade(order)

    def _record_order(self, o: Order):
        row = {
            "id": o.id, "symbol": o.symbol, "side": o.side, "qty": o.qty, "price": o.price,
            "status": o.status, "ts": o.ts.isoformat(), "filled_ts": o.filled_ts.isoformat() if o.filled_ts else ""
        }
        pd.DataFrame([row]).to_csv(self.orders_csv, mode="a", index=False, header=False)

    def _record_trade(self, o: Order):
        row = {
            "ts": o.filled_ts.isoformat() if o.filled_ts else dt.datetime.now(dt.timezone.utc).isoformat(),
            "symbol": o.symbol, "side": o.side, "qty": o.qty, "price": o.price
        }
        pd.DataFrame([row]).to_csv(self.trades_csv, mode="a", index=False, header=False)

# -----------------------------
# Risk Manager
# -----------------------------
class RiskManager:
    def __init__(self, cfg: Dict[str, Any], broker: PaperBroker):
        self.cfg = cfg
        self.broker = broker
        self.max_pos_pct = cfg["risk"]["max_position_pct"] / 100.0
        self.stop_pct = cfg["risk"]["per_trade_stop_pct"] / 100.0
        self.tp_pct = cfg["risk"]["per_trade_take_profit_pct"] / 100.0
        self.dd_pct = cfg["risk"]["max_daily_drawdown_pct"] / 100.0
        self.equity_start_day = cfg["starting_equity"]  # naive: could reset daily in production

    def can_trade(self, current_equity: float) -> bool:
        dd = (self.equity_start_day - current_equity) / self.equity_start_day
        if dd >= self.dd_pct:
            logging.warning(f"Daily drawdown {dd*100:.2f}% >= {self.dd_pct*100:.2f}% — HALTING trading for the day.")
            return False
        return True

    def position_size(self, equity: float, price: float) -> float:
        max_notional = equity * self.max_pos_pct
        qty = max_notional / price
        return max(qty, 0.0)

    def compute_stop_tp(self, entry: float) -> Tuple[float, float]:
        stop = entry * (1 - self.stop_pct)
        take = entry * (1 + self.tp_pct)
        return stop, take

# -----------------------------
# Reporter
# -----------------------------
class Reporter:
    def __init__(self, report_dir: str, equity_csv: str):
        self.report_dir = report_dir
        self.equity_csv = equity_csv
        os.makedirs(report_dir, exist_ok=True)
        if not os.path.exists(self.equity_csv):
            pd.DataFrame(columns=["ts","equity"]).to_csv(self.equity_csv, index=False)

    def save_equity(self, ts: dt.datetime, equity: float):
        pd.DataFrame([{"ts": ts.isoformat(), "equity": equity}]).to_csv(self.equity_csv, mode="a", index=False, header=False)

    def daily_summary(self, broker: PaperBroker, symbol: str, last_price: float):
        pos_val = broker.position_value(symbol, last_price)
        equity = broker.mark_to_market(symbol, last_price)
        self.save_equity(dt.datetime.now(dt.timezone.utc), equity)
        logging.info(f"[REPORT] Equity={equity:.2f} | Cash={broker.cash:.2f} | PosVal={pos_val:.2f} | RealizedPnL={broker.realized_pnl:.2f}")

# -----------------------------
# Trading Bot
# -----------------------------
class TradingBot:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg
        self.symbol = cfg["symbol"]
        self.feed = DataFeed(cfg)
        self.broker = PaperBroker(starting_equity=cfg["starting_equity"], slippage_pct=cfg["simulate_slippage_pct"])
        self.oms = OMS(self.broker, cfg["save_orders_csv"], cfg["save_trades_csv"])
        self.reporter = Reporter(cfg["report_dir"], cfg["save_equity_csv"])
        self.strategy = self._build_strategy(cfg)
        self.risk = RiskManager(cfg, self.broker)
        self.stop_levels: Dict[str, float] = {}  # per-symbol stop
        self.tp_levels: Dict[str, float] = {}    # per-symbol take-profit
        self.running = True

    def _build_strategy(self, cfg: Dict[str, Any]) -> Strategy:
        if cfg["strategy"] == "ma_crossover":
            return MovingAverageCrossover(cfg["ma_short"], cfg["ma_long"])
        elif cfg["strategy"] == "mean_reversion":
            return MeanReversion(cfg["mr_lookback"], cfg["mr_threshold_pct"])
        else:
            raise ValueError("Unknown strategy")

    def graceful_shutdown(self, *_):
        logging.info("Received shutdown signal. Exiting...")
        self.running = False

    def run_once(self):
        df = self.feed.fetch()
        last_row = df.iloc[-1]
        last_price = float(last_row["close"])
        ts = pd.to_datetime(last_row["timestamp"])
        # Update marks
        equity = self.broker.mark_to_market(self.symbol, last_price)

        # Risk gate
        if not self.risk.can_trade(equity):
            self.reporter.daily_summary(self.broker, self.symbol, last_price)
            return

        # Strategy signal
        signal = self.strategy.generate_signal(df)
        logging.info(f"Signal: {signal} | Price={last_price:.2f}")

        # Enforce stops/take-profits if in position
        self._check_exit_rules(last_price)

        # If new signal, size & submit
        if signal in ("buy", "sell"):
            qty = self.risk.position_size(equity, last_price)
            if qty > 0:
                # Round quantity to reasonable precision
                qty = float(round(qty, 6))
                # Convert "sell" to closing position if long; in paper broker we allow selling up to current qty
                if signal == "sell":
                    # If no position, interpret as no-op (or shorting disabled)
                    pos = self.broker.positions.get(self.symbol)
                    if not pos or pos.qty <= 0:
                        logging.info("No long position to sell; skipping.")
                    else:
                        self.oms.submit(self.symbol, "sell", pos.qty)  # close entire long
                else:
                    self.oms.submit(self.symbol, "buy", qty)

        # Process OMS and update stops/TPs for new fills
        self.oms.process(last_price)
        self._refresh_stops_after_fills(last_price)

        # Report
        self.reporter.daily_summary(self.broker, self.symbol, last_price)

    def _refresh_stops_after_fills(self, last_price: float):
        # If we opened/added a long, set (or move) stop and take-profit
        pos = self.broker.positions.get(self.symbol)
        if pos and pos.qty > 0:
            stop, take = self.risk.compute_stop_tp(pos.avg_price)
            self.stop_levels[self.symbol] = stop
            self.tp_levels[self.symbol] = take

    def _check_exit_rules(self, last_price: float):
        pos = self.broker.positions.get(self.symbol)
        if not pos or pos.qty <= 0:
            return
        stop = self.stop_levels.get(self.symbol)
        take = self.tp_levels.get(self.symbol)
        if stop and last_price <= stop:
            logging.info(f"STOP triggered @ {last_price:.2f} <= {stop:.2f} — closing position.")
            self.oms.submit(self.symbol, "sell", pos.qty)
        elif take and last_price >= take:
            logging.info(f"TAKE-PROFIT triggered @ {last_price:.2f} >= {take:.2f} — closing position.")
            self.oms.submit(self.symbol, "sell", pos.qty)

    def run_loop(self):
        signal.signal(signal.SIGINT, self.graceful_shutdown)
        signal.signal(signal.SIGTERM, self.graceful_shutdown)
        interval = self.cfg["poll_interval_seconds"]
        logging.info("Starting bot loop. Press Ctrl+C to exit.")
        while self.running:
            try:
                self.run_once()
            except Exception as e:
                logging.exception(f"Loop error: {e}")
            time.sleep(interval)

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    cfg = load_config("config.json")
    os.makedirs(cfg["report_dir"], exist_ok=True)
    bot = TradingBot(cfg)
    bot.run_loop()
