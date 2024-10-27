import asyncio
import json
import websockets
from binance import AsyncClient


async def MultiStream():
    url = "wss://stream.binance.com:9443/stream?streams=btcusdt@depth"
    async with websockets.connect(url, ping_interval=20, ping_timeout=60) as ws:
        while True:
            print(json.loads(await ws.recv())['data'])


async def OrderBookStream():
    url = "wss://stream.binance.com:9443/stream?streams=btcusdt@depth"
    async with websockets.connect(url, ping_interval=20, ping_timeout=60) as ws:
        while True:
            print(json.loads(await ws.recv())['data'])


async def KlineStream():
    url = "wss://stream.binance.com:9443/stream?streams=btcusdt@kline_1m"
    async with websockets.connect(url, ping_interval=20, ping_timeout=60) as ws:
        while True:
            print(json.loads(await ws.recv())['data'])


async def TradeStreamSpot():
    url = "wss://stream.binance.com:9443/stream?streams=btcusdt@trade"
    async with websockets.connect(url, ping_interval=20, ping_timeout=60) as ws:
        while True:
            price = json.loads(await ws.recv())['data']['p']
            quantity = json.loads(await ws.recv())['data']['q']
            buy = json.loads(await ws.recv())['data']['m']
            return price, quantity, buy


async def TickerStream():
    url = "wss://stream.binance.com:9443/stream?streams=btcusdt@ticker"
    async with websockets.connect(url, ping_interval=20, ping_timeout=60) as ws:
        while True:
            print(json.loads(await ws.recv())['data'])


async def MiniTickerStream():
    url = "wss://stream.binance.com:9443/stream?streams=!miniTicker@arr"
    async with websockets.connect(url, ping_interval=20, ping_timeout=60) as ws:
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


async def PrintToConsole():
    while True:
        price, quantity, buy = await TradeStreamSpot()
        print(f"{price} {quantity} {buy}")


if __name__ == "__main__":

    asyncio.run(PrintToConsole())
