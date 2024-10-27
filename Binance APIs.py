import asyncio
import json
import websockets
from binance import AsyncClient


async def OrderBookStream():
    url = "wss://stream.binance.com:9443/stream?streams=btcusdt@depth"
    async with websockets.connect(url) as ws:
        while True:
            print(json.loads(await ws.recv())['data'])


async def KlineStream():
    url = "wss://stream.binance.com:9443/stream?streams=btcusdt@kline_1m"
    async with websockets.connect(url) as ws:
        while True:
            print(json.loads(await ws.recv())['data'])


async def TradeStreamSpot():
    url = "wss://stream.binance.com:9443/stream?streams=btcusdt@trade"
    async with websockets.connect(url) as ws:
        while True:
            price = json.loads(await ws.recv())['data']['p']
            quantity = json.loads(await ws.recv())['data']['q']
            is_buy = json.loads(await ws.recv())['data']['m']
            return price, quantity, is_buy


async def TradeStreamFutures():
    url = "wss://fstream.binance.com/stream?streams=btcusdt@trade"
    async with websockets.connect(url) as ws:
        while True:
            price = json.loads(await ws.recv())['data']['p']
            quantity = json.loads(await ws.recv())['data']['q']
            is_buy = json.loads(await ws.recv())['data']['m']
            print(f"{price} {quantity} {is_buy}")


async def TickerStream():
    url = "wss://stream.binance.com:9443/stream?streams=btcusdt@ticker"
    async with websockets.connect(url) as ws:
        while True:
            print(json.loads(await ws.recv())['data'])


async def MiniTickerStream():
    url = "wss://stream.binance.com:9443/stream?streams=!miniTicker@arr"
    async with websockets.connect(url) as ws:
        while True:
            print(json.loads(await ws.recv())['data'])


async def OrderBookRequest():
    client = await AsyncClient.create()

    res = await client.get_order_book(symbol='ETHUSDT', limit=1000)
    print(json.dumps(res, indent=2))

    await client.close_connection()


async def ExchangeInfo():
    client = await AsyncClient.create()

    res = await client.get_exchange_info()
    print(json.dumps(res, indent=2))

    await client.close_connection()


async def SymbolInfo():
    client = await AsyncClient.create()

    res = await client.get_symbol_info('ETHUSDT')
    print(json.dumps(res, indent=2))

    await client.close_connection()


async def KlineInfo():
    client = await AsyncClient.create()

    res = await client.get_klines(symbol='ETHUSDT', interval=AsyncClient.KLINE_INTERVAL_1MINUTE, limit = 2)
    print(json.dumps(res, indent=2))

    await client.close_connection()


async def MultiStream(is_futures: bool):     # Размер свечи корректировать вручную в url
    if is_futures:
        url = "wss://fstream.binance.com/stream?streams=btcusdt@depth/btcusdt@kline_1m/btcusdt@trade/btcusdt@ticker"
    else:
        url = "wss://stream.binance.com:9443/stream?streams=btcusdt@depth/btcusdt@kline_1m/btcusdt@trade/btcusdt@ticker"
    async with websockets.connect(url) as ws:
        while True:
            msg = json.loads(await ws.recv())
            if msg['stream'] == "btcusdt@depth":
                bids = msg['data']['b']
                asks = msg['data']['a']
            elif msg['stream'][:-3] == "btcusdt@kline":
                open_price_kline = msg['data']['k']['o']
                close_price_kline = msg['data']['k']['c']
                high_price = msg['data']['k']['h']
                low_price = msg['data']['k']['l']
                base_asset_volume = msg['data']['k']['v']
                quote_asset_volume = msg['data']['k']['q']
                taker_buy_base_asset_volume = msg['data']['k']['V']
                taker_buy_quote_asset_volume = msg['data']['k']['Q']
            elif msg['stream'] == "btcusdt@trade":
                price = msg['data']['p']
                quantity = msg['data']['q']
                is_buy = msg['data']['m']
            elif msg['stream'] == "btcusdt@ticker":
                price_change = msg['data']['p']
                price_change_percent = msg['data']['P']
                weighted_average_price = msg['data']['w']
                open_price_ticker = msg['data']['o']
                last_price_ticker = msg['data']['c']
                total_traded_base_asset_volume = msg['data']['v']
                total_traded_quote_asset_volume = msg['data']['q']


if __name__ == "__main__":

    asyncio.run(MultiStream(True))
