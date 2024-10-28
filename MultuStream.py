import asyncio
import json
import websockets


async def MultiStream(is_futures: bool):     # Размер свечи корректировать вручную
    if is_futures:
        binance_url = "wss://fstream.binance.com/stream?streams=btcusdt@depth/btcusdt@kline_1m/btcusdt@trade/btcusdt@ticker"
        bybit_url = "wss://stream.bybit.com/v5/public/linear"
        bitget_url = "wss://ws.bitget.com/mix/v1/stream"
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
        }
    else:
        binance_url = "wss://stream.binance.com:9443/stream?streams=btcusdt@depth/btcusdt@kline_1m/btcusdt@trade/btcusdt@ticker"
        bybit_url = "wss://stream.bybit.com/v5/public/spot"
        bitget_url = "wss://ws.bitget.com/spot/v1/stream"
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
        }

    async with websockets.connect(binance_url) as binance_ws:
        async with websockets.connect(bybit_url) as bybit_ws:
            async with websockets.connect(bitget_url) as bitget_ws:
                await bybit_ws.send(json.dumps(subscriptions['bybit_subscription_message']))
                await bybit_ws.send(json.dumps(subscriptions['bitget_subscription_message']))
                while True:
                    binance_msg = json.loads(await binance_ws.recv())
                    bybit_msg = json.loads(await bybit_ws.recv())
                    bitget_msg = json.loads(await bitget_ws.recv())
                    if binance_msg['stream'] == "btcusdt@depth":
                        binance_bids = binance_msg['data']['b']
                        binance_asks = binance_msg['data']['a']
                        print(binance_asks)
                    elif binance_msg['stream'][:13] == "btcusdt@kline":
                        binance_kline_open_price = binance_msg['data']['k']['o']
                        binance_kline_close_price = binance_msg['data']['k']['c']
                        binance_kline_high_price = binance_msg['data']['k']['h']
                        binance_kline_low_price = binance_msg['data']['k']['l']
                        binance_kline_base_asset_volume = binance_msg['data']['k']['v']
                        binance_kline_quote_asset_volume = binance_msg['data']['k']['q']
                        binance_kline_taker_buy_base_asset_volume = binance_msg['data']['k']['V']
                        binance_kline_taker_buy_quote_asset_volume = binance_msg['data']['k']['Q']
                    elif binance_msg['stream'] == "btcusdt@trade":
                        binance_trade_price = binance_msg['data']['p']
                        binance_trade_quantity = binance_msg['data']['q']
                        binance_trade_direction = binance_msg['data']['m']
                    elif binance_msg['stream'] == "btcusdt@ticker":
                        binance_ticker_price_change = binance_msg['data']['p']
                        binance_ticker_price_change_percent = binance_msg['data']['P']
                        binance_ticker_weighted_average_price = binance_msg['data']['w']
                        binance_ticker_open_price = binance_msg['data']['o']
                        binance_ticker_last_price = binance_msg['data']['c']
                        binance_ticker_total_traded_base_asset_volume = binance_msg['data']['v']
                        binance_ticker_total_traded_quote_asset_volume = binance_msg['data']['q']
                    if 'topic' in bybit_msg:
                        if bybit_msg['topic'][:9] == "orderbook":     # Если придет snapshot возможно нужно все ресетать
                            bybit_bids = bybit_msg['data']['b']
                            bybit_asks = bybit_msg['data']['a']
                        elif bybit_msg['topic'][:5] == "kline":
                            bybit_kline_open_price = bybit_msg['data'][0]['open']
                            bybit_kline_close_price = bybit_msg['data'][0]['close']
                            bybit_kline_high_price = bybit_msg['data'][0]['high']
                            bybit_kline_low_price = bybit_msg['data'][0]['low']
                            bybit_kline_base_asset_volume = bybit_msg['data'][0]['volume']
                            bybit_kline_quote_asset_volume = bybit_msg['data'][0]['turnover']
                        elif bybit_msg['topic'][:11] == "publicTrade":
                            bybit_trade_price = bybit_msg['data'][0]['p']
                            bybit_trade_quantity = bybit_msg['data'][0]['v']
                            bybit_trade_direction = bybit_msg['data'][0]['S']
                            bybit_trade_is_order = bybit_msg['data'][0]['BT']
                        elif bybit_msg['topic'][:7] == "tickers": # Можно добавить миллион показателей за последние 24 часа
                            if 'lastPrice' in bybit_msg['data']:
                                bybit_ticker_last_price = bybit_msg['data']['lastPrice']
                        elif bybit_msg['topic'][:11] == "liquidation":
                            bybit_liquidation_size = bybit_msg['data']['size']
                            bybit_liquidation_direction = bybit_msg['data']['side']
                    if 'action' in bitget_msg:
                        if bitget_msg['arg']['channel'][:5] == "books":
                            bitget_bids = bitget_msg['data'][0]['bids']
                            bitget_asks = bitget_msg['data'][0]['asks']
                            print(bitget_asks)
                        elif bitget_msg['arg']['channel'][:6] == "candle":     # Надо перепроверить какая цена какая
                            bitget_kline_open_price = bitget_msg['data'][0][1] # Это самая ужасная подача данных которую только можно придумать
                            bitget_kline_close_price = bitget_msg['data'][0][4]
                            bitget_kline_high_price = bitget_msg['data'][0][2]
                            bitget_kline_low_price = bitget_msg['data'][0][3]
                            bitget_kline_base_asset_volume = bitget_msg['data'][0][5]
                            print(bitget_kline_base_asset_volume)
                        elif bitget_msg['arg']['channel'] == "trade":
                            bitget_trade_price = bitget_msg['data'][0][1]
                            bitget_trade_quantity = bitget_msg['data'][0][2]
                            bitget_trade_direction = bitget_msg['data'][0][3]
                            print(bitget_trade_direction)
                        elif bitget_msg['arg']['channel'] == "ticker":    # Можно добавить кучу 24 часовых штук + фандинг, открытый интерес и т.д.
                            bitget_ticker_price = bitget_msg['data'][0]['markPrice']
                            bitget_ticker_price_change = bitget_msg['data'][0]['chgUTC'] # С 00:00 UTC
                            bitget_ticker_price_change_percent = bitget_msg['data'][0]['priceChangePercent']
                            bitget_ticker_open_price = bitget_msg['data'][0]['openUtc'] # С 00:00 UTC
                            bitget_ticker_last_price = bitget_msg['data'][0]['last']
                            print(bitget_ticker_last_price)


if __name__ == "__main__":
    asyncio.run(MultiStream(True))

