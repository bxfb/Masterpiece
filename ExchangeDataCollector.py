import asyncio
import json
import websockets
import requests
import sqlite3
from datetime import datetime, timedelta


class ExchangeDataCollector:
    def __init__(self, is_futures: bool):
        self.is_futures = is_futures
        self.event_number = 0
        self.event_flag = True
        self.liq_1s = 0
        self.event_liq = 0
        self.event_large_trades = {}
        self.data = {}

        self.binance_url_futures = "wss://fstream.binance.com/stream?streams=btcusdt@depth/btcusdt@kline_1m/btcusdt@trade/btcusdt@ticker"
        self.binance_url_spot = "wss://stream.binance.com:9443/stream?streams=btcusdt@depth/btcusdt@kline_1m/btcusdt@trade/btcusdt@ticker"
        self.bybit_url_futures = "wss://stream.bybit.com/v5/public/linear"
        self.bybit_url_spot = "wss://stream.bybit.com/v5/public/spot"
        self.okx_url = "wss://ws.okx.com:8443/ws/v5/public"

        self.conn = sqlite3.connect("market_data.db")
        self.create_table()
        self.last_kline_check_time = datetime.now()

    def create_table(self):
        """Create SQLite table to store market data if it doesn't already exist."""
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    exchange TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    event_number INTEGER NOT NULL,
                    liquidations INTEGER,
                    large_trades TEXT,
                    kline_open_price REAL,
                    kline_close_price REAL,
                    kline_high_price REAL,
                    kline_low_price REAL,
                    kline_base_asset_volume REAL
                )
            ''')

    @staticmethod
    async def binance_kline_request(limit):
        response = await asyncio.to_thread(
            requests.get,
            "https://api.binance.com/api/v3/klines",
            params={"symbol": "BTCUSDT", "interval": "5m", "limit": limit}
        )
        return response.json()

    @staticmethod
    def volatility(a, b):
        return abs(1 - float(a) / float(b)) * 100

    async def receive_messages(self, ws, exchange_name):
        while True:
            try:
                msg = json.loads(await ws.recv())
                print(f"{exchange_name} message received: {msg}")

                await self.process_message(exchange_name, msg)

            except websockets.ConnectionClosed as e:
                print(f"{exchange_name} Connection Closed: {e}")
                break
            except Exception as e:
                print(f"{exchange_name} Connection Error: {e}")
                # await asyncio.sleep(1)

    async def process_message(self, exchange_name, msg):
        if exchange_name == "Binance":
            await self.process_binance_message(msg)
        elif exchange_name == "Bybit":
            await self.process_bybit_message(msg)
        elif exchange_name == "OKX":
            await self.process_okx_message(msg)

    async def process_binance_message(self, msg):
        """ Process messages coming from Binance exchange """
        if 'stream' in msg:
            if msg['stream'] == "btcusdt@depth":
                binance_bids = msg['data']['b']
                binance_asks = msg['data']['a']
            if msg['stream'][:13] == "btcusdt@kline":
                kline_data = msg['data']['k']
                kline = {
                    'open': kline_data['o'],
                    'close': kline_data['c'],
                    'high': kline_data['h'],
                    'low': kline_data['l'],
                    'volume': kline_data['v'],
                }
                if self.event_flag:
                    self.store_data("Binance", kline)
            if msg['stream'] == "btcusdt@trade":
                binance_trade_price = msg['data']['p']
                binance_trade_quantity = msg['data']['q']
                binance_trade_direction = msg['data']['m']
            if msg['stream'] == "btcusdt@ticker":
                binance_ticker_price_change = msg['data']['p']
                binance_ticker_price_change_percent = msg['data']['P']
                binance_ticker_weighted_average_price = msg['data']['w']
                binance_ticker_open_price = msg['data']['o']
                binance_ticker_last_price = msg['data']['c']
                binance_ticker_total_traded_base_asset_volume = msg['data']['v']
                binance_ticker_total_traded_quote_asset_volume = msg['data']['q']


            if datetime.now() >= self.last_kline_check_time + timedelta(seconds=30):
                klines = await self.binance_kline_request("3")
                self.check_event_flag(klines)
                self.last_kline_check_time = datetime.now()

    async def process_bybit_message(self, msg):
        """ Process messages coming from Bybit exchange """
        if 'topic' in msg:
            if msg['topic'][:9] == "orderbook":
                bybit_bids = msg['data']['b']
                bybit_asks = msg['data']['a']
            if msg['topic'][:5] == "kline":
                kline = {
                    'open': msg['data'][0]['open'],
                    'close': msg['data'][0]['close'],
                    'high': msg['data'][0]['high'],
                    'low': msg['data'][0]['low'],
                    'volume': msg['data'][0]['volume'],
                }
                if self.event_flag:
                    self.store_data("Bybit", kline)
            if msg['topic'][:11] == "publicTrade":
                bybit_trade_price = msg['data'][0]['p']
                bybit_trade_quantity = msg['data'][0]['v']
                bybit_trade_direction = msg['data'][0]['S']
                bybit_trade_is_order = msg['data'][0]['BT']
            if msg['topic'][:11] == "liquidation":
                bybit_liquidation_size = msg['data']['size']
                self.event_liq += bybit_liquidation_size

    async def process_okx_message(self, msg):
        """ Process messages coming from OKX exchange """
        if 'data' in msg:
            if msg['arg']['channel'][:5] == "books":
                okx_bids = msg['data'][0]['bids']
                okx_asks = msg['data'][0]['asks']
            elif msg['arg']['channel'] == "trades":
                okx_trade_price = msg['data'][0]['px']
                okx_trade_quantity = msg['data'][0]['sz']
                okx_trade_direction = msg['data'][0]['side']
            elif msg['arg']['channel'] == "tickers":
                okx_ticker_open_price = msg['data'][0]['sodUtc0']
                okx_ticker_last_price = msg['data'][0]['last']
                okx_ticker_last_quantity = msg['data'][0]['lastSz']

    def check_event_flag(self, klines):
        """ Check volatility and set the event flag accordingly """
        if (self.volatility(klines[0][2], klines[2][3]) >= 0.1 or
                self.volatility(klines[0][3], klines[2][2]) >= 0.1):
            if not self.event_flag:
                self.event_flag = True
                self.event_number += 1
                self.event_liq = 0
                self.event_large_trades = {}
        else:
            self.event_flag = True

    def store_data(self, exchange, kline):
        """ Store data from exchanges into the main data structure """
        timestamp = str(datetime.now())
        large_trades = json.dumps(self.event_large_trades)

        with self.conn:
            self.conn.execute('''
                        INSERT INTO market_data (exchange, timestamp, event_number, liquidations, large_trades, 
                                                  kline_open_price, kline_close_price, kline_high_price, 
                                                  kline_low_price, kline_base_asset_volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (exchange, timestamp, self.event_number, self.event_liq, large_trades,
                          kline['open'], kline['close'], kline['high'], kline['low'], kline['volume']))

    async def run(self):
        """ Main method to run the websocket connections """
        if self.is_futures:
            binance_url = self.binance_url_futures
            bybit_url = self.bybit_url_futures
            subscriptions = {
                'bybit_subscription_message': {
                    "op": "subscribe",
                    "args": ["orderbook.200.BTCUSDT", "publicTrade.BTCUSDT", "tickers.BTCUSDT", "kline.1.BTCUSDT",
                             "liquidation.BTCUSDT"]
                },
                'okx_subscription_message': {
                    "op": "subscribe",
                    "args": [
                        {"instType": "FUTURES", "channel": "tickers", "instId": "BTC-USDT"},
                        {"instType": "FUTURES", "channel": "trades", "instId": "BTC-USDT"},
                        {"instType": "FUTURES", "channel": "books5", "instId": "BTC-USDT"}
                    ]
                }
            }
        else:
            binance_url = self.binance_url_spot
            bybit_url = self.bybit_url_spot
            subscriptions = {
                'bybit_subscription_message': {
                    "op": "subscribe",
                    "args": ["orderbook.200.BTCUSDT", "publicTrade.BTCUSDT", "tickers.BTCUSDT", "kline.1.BTCUSDT"]
                },
                'okx_subscription_message': {
                    "op": "subscribe",
                    "args": [
                        {"instType": "SPOT", "channel": "tickers", "instId": "BTC-USDT"},
                        {"instType": "SPOT", "channel": "trades", "instId": "BTC-USDT"},
                        {"instType": "SPOT", "channel": "books5", "instId": "BTC-USDT"}
                    ]
                }
            }

        async with websockets.connect(binance_url) as binance_ws, \
                websockets.connect(bybit_url) as bybit_ws, \
                websockets.connect(self.okx_url) as okx_ws:

            await bybit_ws.send(json.dumps(subscriptions['bybit_subscription_message']))
            await okx_ws.send(json.dumps(subscriptions['okx_subscription_message']))

            tasks = [
                asyncio.create_task(self.receive_messages(binance_ws, "Binance")),
                asyncio.create_task(self.receive_messages(bybit_ws, "Bybit")),
                asyncio.create_task(self.receive_messages(okx_ws, "OKX")),
            ]
            await asyncio.gather(*tasks)


if __name__ == "__main__":
    collector = ExchangeDataCollector(True)
    asyncio.run(collector.run())
