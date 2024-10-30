import asyncio
import json
import websockets


async def receive_messages(ws, exchange_name, sub_message, is_futures):
    if sub_message:
        await ws.send(json.dumps(sub_message))
    while True:
        await asyncio.sleep(0.2)  # Задать скорость получения сообщений (надо почитать лимиты и минимизировать данные)
        try:
            msg = json.loads(await ws.recv())
            print(f"{exchange_name} message received: {msg}")

            if exchange_name == "Binance":
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
            if exchange_name == "Bybit":
                if 'topic' in msg:
                    if msg['topic'][:9] == "orderbook":  # Если придет snapshot возможно нужно все ресетать
                        bybit_bids = msg['data']['b']
                        bybit_asks = msg['data']['a']
                    elif msg['topic'][:5] == "kline":
                        bybit_kline_open_price = msg['data'][0]['open']
                        bybit_kline_close_price = msg['data'][0]['close']
                        bybit_kline_high_price = msg['data'][0]['high']
                        bybit_kline_low_price = msg['data'][0]['low']
                        bybit_kline_base_asset_volume = msg['data'][0]['volume']
                        bybit_kline_quote_asset_volume = msg['data'][0]['turnover']
                    elif msg['topic'][:11] == "publicTrade":
                        bybit_trade_price = msg['data'][0]['p']
                        bybit_trade_quantity = msg['data'][0]['v']
                        bybit_trade_direction = msg['data'][0]['S']
                        bybit_trade_is_order = msg['data'][0]['BT']
                    elif msg['topic'][:7] == "tickers":  # Можно добавить миллион показателей за последние 24 часа
                        if 'lastPrice' in msg['data']:
                            bybit_ticker_last_price = msg['data']['lastPrice']
                    elif msg['topic'][:11] == "liquidation":
                        bybit_liquidation_size = msg['data']['size']
                        bybit_liquidation_direction = msg['data']['side']
            if exchange_name == "Bitget":
                if 'action' in msg:
                    if msg['arg']['channel'][:5] == "books":
                        bitget_bids = msg['data'][0]['bids']
                        bitget_asks = msg['data'][0]['asks']
                    elif msg['arg']['channel'][:6] == "candle":  # Надо перепроверить какая цена какая
                        bitget_kline_open_price = msg['data'][0][1]  # Это самая ужасная подача данных которую только можно придумать
                        bitget_kline_close_price = msg['data'][0][4]
                        bitget_kline_high_price = msg['data'][0][2]
                        bitget_kline_low_price = msg['data'][0][3]
                        bitget_kline_base_asset_volume = msg['data'][0][5]
                    elif msg['arg']['channel'] == "trade":
                        bitget_trade_price = msg['data'][0][1]
                        bitget_trade_quantity = msg['data'][0][2]
                        bitget_trade_direction = msg['data'][0][3]
                    elif msg['arg'][
                        'channel'] == "ticker":  # Можно добавить кучу 24 часовых штук + фандинг, открытый интерес и т.д.
                        if is_futures:
                            bitget_ticker_price = msg['data'][0]['markPrice']
                            bitget_ticker_price_change_percent = msg['data'][0]['priceChangePercent']
                        bitget_ticker_price_change = msg['data'][0]['chgUTC']  # С 00:00 UTC
                        bitget_ticker_open_price = msg['data'][0]['openUtc']  # С 00:00 UTC
                        bitget_ticker_last_price = msg['data'][0]['last']
            if exchange_name == "OKX":
                if 'data' in msg:
                    if msg['arg']['channel'][:5] == "books":
                        okx_bids = msg['data'][0]['bids']
                        okx_asks = msg['data'][0]['asks']
                    elif msg['arg']['channel'] == "trades":
                        okx_trade_price = msg['data'][0]['px']
                        okx_trade_quantity = msg['data'][0]['sz']
                        okx_trade_direction = msg['data'][0]['side']
                    elif msg['arg']['channel'] == "tickers":  # Можно добавить кучу 24 часовых штук
                        okx_ticker_open_price = msg['data'][0]['sodUtc0']  # С 00:00 UTC
                        okx_ticker_last_price = msg['data'][0]['last']
                        okx_ticker_last_quantity = msg['data'][0]['lastSz']

            # Тут можешь писать первичную обработку и скидывать в файл данные
            # if exchange_name == "Binance":
            # if exchange_name == "Bybit":
            # if exchange_name == "Bitget":
            # if exchange_name == "OKX":

        except websockets.ConnectionClosed as e:
            print(f"{exchange_name} Connection Closed: {e}")
            break
        except Exception as e:
            print(f"{exchange_name} Connection Error: {e}")
            break


async def MultiStream(is_futures: bool):
    if is_futures:
        binance_url = "wss://fstream.binance.com/stream?streams=btcusdt@depth/btcusdt@kline_1m/btcusdt@trade/btcusdt@ticker"
        bybit_url = "wss://stream.bybit.com/v5/public/linear"
        bitget_url = "wss://ws.bitget.com/mix/v1/stream"
        okx_url = "wss://ws.okx.com:8443/ws/v5/public"
        subscriptions = {
            'bybit_subscription_message': {
                "op": "subscribe",
                "args": ["orderbook.200.BTCUSDT", "publicTrade.BTCUSDT", "tickers.BTCUSDT", "kline.1.BTCUSDT",
                         "liquidation.BTCUSDT"]
            },
            'bitget_subscription_message': {
                "op": "subscribe",
                "args": [{"instType": "MC", "channel": "ticker", "instId": "BTCUSDT"},
                         {"instType": "MC", "channel": "candle1m", "instId": "BTCUSDT"},
                         {"instType": "MC", "channel": "books15", "instId": "BTCUSDT"},
                         {"instType": "MC", "channel": "trade", "instId": "BTCUSDT"}]
            },
            'okx_subscription_message': {
                "op": "subscribe",
                "args": [{"instIType": "FUTURES", "channel": "tickers", "instId": "BTC-USDT"},
                         {"instIType": "FUTURES", "channel": "trades", "instId": "BTC-USDT"},
                         {"instIType": "FUTURES", "channel": "books5", "instId": "BTC-USDT"}]
            }
        }
    else:
        binance_url = "wss://stream.binance.com:9443/stream?streams=btcusdt@depth/btcusdt@kline_1m/btcusdt@trade/btcusdt@ticker"
        bybit_url = "wss://stream.bybit.com/v5/public/spot"
        bitget_url = "wss://ws.bitget.com/spot/v1/stream"
        okx_url = "wss://ws.okx.com:8443/ws/v5/public"
        subscriptions = {
            'bybit_subscription_message': {
                "op": "subscribe",
                "args": ["orderbook.200.BTCUSDT", "publicTrade.BTCUSDT", "tickers.BTCUSDT", "kline.1.BTCUSDT"]
            },
            'bitget_subscription_message': {
                "op": "subscribe",
                "args": [{"instType": "SP", "channel": "ticker", "instId": "BTCUSDT"},
                         {"instType": "SP", "channel": "candle1m", "instId": "BTCUSDT"},
                         {"instType": "SP", "channel": "books15", "instId": "BTCUSDT"},
                         {"instType": "SP", "channel": "trade", "instId": "BTCUSDT"}]
            },
            'okx_subscription_message': {
                "op": "subscribe",
                "args": [{"instIType": "SPOT", "channel": "tickers", "instId": "BTC-USDT"},
                         {"instIType": "SPOT", "channel": "trades", "instId": "BTC-USDT"},
                         {"instIType": "SPOT", "channel": "books5", "instId": "BTC-USDT"}]
            }
        }


    async with websockets.connect(binance_url, ping_interval=None) as binance_ws, \
            websockets.connect(bybit_url, ping_interval=None) as bybit_ws, \
            websockets.connect(bitget_url, ping_interval=None) as bitget_ws, \
            websockets.connect(okx_url, ping_interval=None) as okx_ws:


        receive_tasks = [
            asyncio.create_task(receive_messages(binance_ws, "Binance", None, is_futures)),
            asyncio.create_task(receive_messages(bybit_ws, "Bybit", subscriptions['bybit_subscription_message'], is_futures)),
            asyncio.create_task(receive_messages(bitget_ws, "Bitget", subscriptions['bitget_subscription_message'], is_futures)),
            asyncio.create_task(receive_messages(okx_ws, "OKX", subscriptions['okx_subscription_message'], is_futures)),
        ]

        # Await completion of all tasks
        await asyncio.gather(*receive_tasks)


if __name__ == "__main__":
    asyncio.run(MultiStream(True))
