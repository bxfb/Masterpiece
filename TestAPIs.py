import asyncio
import json
from binance import AsyncClient, BinanceSocketManager


async def OrderBookStream():
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    ts = bm.depth_socket('ETHUSDT', depth=BinanceSocketManager.WEBSOCKET_DEPTH_5)

    async with ts as tscm:
        while True:
            res = await tscm.recv()
            print(res)

    await client.close_connection()


async def KlineStream():
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    ts = bm.kline_socket('ETHUSDT', interval=AsyncClient.KLINE_INTERVAL_1MINUTE)

    async with ts as tscm:
        while True:
            res = await tscm.recv()
            print(res)

    await client.close_connection()


async def TradeStream():
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    ts = bm.trade_socket('ETHUSDT')

    async with ts as tscm:
        while True:
            res = await tscm.recv()
            print(res)

    await client.close_connection()


async def TickerStream():
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    ts = bm.symbol_ticker_socket('ETHUSDT')

    async with ts as tscm:
        while True:
            res = await tscm.recv()
            print(res)

    await client.close_connection()


async def MiniTickerStream():
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    ts = bm.miniticker_socket()

    async with ts as tscm:
        while True:
            res = await tscm.recv()
            print(res)

    await client.close_connection()


async def OrderBookRequest():
    client = await AsyncClient.create()

    res = await client.get_order_book(symbol='ETHUSDT')
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


if __name__ == "__main__":
    print("START1")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(OrderBookStream())

