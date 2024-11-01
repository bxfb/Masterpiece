import asyncio
import json
import websockets
import requests
import time

class ExchangeDataCollector:
    def __init__(self, is_futures: bool):
        self.is_futures = is_futures
        self.event_number = 0
        self.event_flag = True
        self.liq_1s = 0
        self.event_liq = 0
        self.event_large_trades = {}
        self.data = {}  # Holds collected data
        self.binance_url_futures = "wss://fstream.binance.com/stream?streams=btcusdt@depth/btcusdt@kline_1m/btcusdt@trade/btcusdt@ticker"
        self.binance_url_spot = "wss://stream.binance.com:9443/stream?streams=btcusdt@depth/btcusdt@kline_1m/btcusdt@trade/btcusdt@ticker"
        self.bybit_url_futures = "wss://stream.bybit.com/v5/public/linear"
        self.bybit_url_spot = "wss://stream.bybit.com/v5/public/spot"
        self.okx_url = "wss://ws.okx.com:8443/ws/v5/public"

    @staticmethod
    async def binance_kline_request(interval):
        response = await asyncio.to_thread(requests.get,
            "https://api.binance.com/api/v3/klines",
            params={"symbol": "BTCUSDT", "interval": interval, "limit": 100})
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
                break

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
            elif msg['stream'][:13] == "btcusdt@kline":
                binance_kline_open_price = msg['data']['k']['o']
                binance_kline_close_price = msg['data']['k']['c']
                binance_kline_high_price = msg['data']['k']['h']
                binance_kline_low_price = msg['data']['k']['l']
                binance_kline_base_asset_volume = msg['data']['k']['v']
                binance_kline_quote_asset_volume = msg['data']['k']['q']
                binance_kline_taker_buy_base_asset_volume = msg['data']['k']['V']
                binance_kline_taker_buy_quote_asset_volume = msg['data']['k']['Q']
                if self.event_flag:
                    self.store_data("Binance",
                {'binance_kline_open_price': binance_kline_open_price,
                        'binance_kline_close_price': binance_kline_close_price,
                        'binance_kline_high_price': binance_kline_high_price,
                        'binance_kline_low_price': binance_kline_low_price,
                        'binance_kline_base_asset_volume': binance_kline_base_asset_volume})
            elif msg['stream'] == "btcusdt@trade":
                binance_trade_price = msg['data']['p']
                binance_trade_quantity = msg['data']['q']
                binance_trade_direction = msg['data']['m']
            elif msg['stream'] == "btcusdt@ticker":
                binance_ticker_price_change = msg['data']['p']
                binance_ticker_price_change_percent = msg['data']['P']
                binance_ticker_weighted_average_price = msg['data']['w']
                binance_ticker_open_price = msg['data']['o']
                binance_ticker_last_price = msg['data']['c']
                binance_ticker_total_traded_base_asset_volume = msg['data']['v']
                binance_ticker_total_traded_quote_asset_volume = msg['data']['q']

            if time.time() % 30 < 1:  # Check every 30 seconds
                klines = await self.binance_kline_request("3")
                self.check_event_flag(klines)

    async def process_bybit_message(self, msg):
        """ Process messages coming from Bybit exchange """
        if 'topic' in msg:
            if msg['topic'][:9] == "orderbook":
                bybit_bids = msg['data']['b']
                bybit_asks = msg['data']['a']
            elif msg['topic'][:5] == "kline":
                bybit_kline_open_price = msg['data'][0]['open']
                bybit_kline_close_price = msg['data'][0]['close']
                bybit_kline_high_price = msg['data'][0]['high']
                bybit_kline_low_price = msg['data'][0]['low']
                bybit_kline_base_asset_volume = msg['data'][0]['volume']
                bybit_kline_quote_asset_volume = msg['data'][0]['turnover']
                if self.event_flag:
                    self.store_data("Binance",
                {'bybit_kline_open_price': bybit_kline_open_price,
                        'bybit_kline_close_price': bybit_kline_close_price,
                        'bybit_kline_high_price': bybit_kline_high_price,
                        'bybit_kline_low_price': bybit_kline_low_price,
                        'bybit_kline_base_asset_volume': bybit_kline_base_asset_volume})
            elif msg['topic'][:11] == "publicTrade":
                bybit_trade_price = msg['data'][0]['p']
                bybit_trade_quantity = msg['data'][0]['v']
                bybit_trade_direction = msg['data'][0]['S']
                bybit_trade_is_order = msg['data'][0]['BT']
                #                     Не работает надо фиксить
                # if bybit_trade_price * bybit_trade_quantity >= 1000000:
                #     # Track large trades above threshold
                #     self.event_large_trades[float(bybit_trade_price) * float(bybit_trade_quantity)] = 'buy'
            elif msg['topic'][:7] == "tickers":  # Можно добавить миллион показателей за последние 24 часа
                if 'lastPrice' in msg['data']:
                    bybit_ticker_last_price = msg['data']['lastPrice']
            elif msg['topic'][:11] == "liquidation":
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

    def store_data(self, exchange, klines):
        """ Store data from exchanges into the main data structure """
        if str(self.event_number) not in self.data:
            self.data[str(self.event_number)] = {}

        formatted_time = time.ctime(time.time())

        exchange_data = {
            "exchange": exchange,
            "time": formatted_time,
            "liquidations": self.event_liq,
            "large_trades": self.event_large_trades
        }

        if exchange == "Binance" and klines:
            exchange_data.update({
                "candle_data":{
                    "kline_open_price" : klines['binance_kline_open_price'],
                    "kline_close_price" : klines['binance_kline_close_price'],
                    "kline_high_price" : klines['binance_kline_high_price'],
                    "kline_low_price" : klines['binance_kline_low_price'],
                    "kline_base_asset_volume" : klines['binance_kline_base_asset_volume']
                },
                "orderbook":{}
            })
        elif exchange == "Bybit" and klines:
            exchange_data.update({
                "candle_data":{
                    "kline_open_price" : klines['bybit_kline_open_price'],
                    "kline_close_price" : klines['bybit_kline_close_price'],
                    "kline_high_price" : klines['bybit_kline_high_price'],
                    "kline_low_price" : klines['bybit_kline_low_price'],
                    "kline_base_asset_volume" : klines['bybit_kline_base_asset_volume']
                },
                "orderbook":{}
            })


        self.data[str(self.event_number)][formatted_time] = exchange_data
        self.write_to_file()

    # def write_to_file(self):
    #     """ Write data to the main_data.json file asynchronously """
    #     asyncio.run_coroutine_threadsafe(self._write_to_file(), asyncio.get_event_loop())
    #     # loop = asyncio.get_event_loop()
    #     # loop.run_until_complete(self._write_to_file())
    # async def _write_to_file(self):
    #     """ Actual file writing method """
    #     async with asyncio.to_thread(open, 'main_data.json', 'w') as file:
    #         json.dump(self.data, file, indent=4)

    def write_to_file(self):
        """ Write data to the main_data.json file asynchronously """
        with open('main_data.json', 'w') as file:
            json.dump(self.data, file, indent=4)

    async def run(self):
        """ Main method to run the websocket connections """
        if self.is_futures:
            binance_url = self.binance_url_futures
            bybit_url = self.bybit_url_futures
            subscriptions = {
                'bybit_subscription_message': {
                    "op": "subscribe",
                    "args": ["orderbook.200.BTCUSDT", "publicTrade.BTCUSDT", "tickers.BTCUSDT", "kline.1.BTCUSDT", "liquidation.BTCUSDT"]
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
