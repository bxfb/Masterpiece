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


async def OrderBookRequest():
    client = await AsyncClient.create()

    res = await client.get_order_book(symbol='BTCUSDT')
    print(json.dumps(res, indent=2))

    await client.close_connection()


async def ExchangeInfo():
    client = await AsyncClient.create()

    res = await client.get_exchange_info()
    print(json.dumps(res, indent=2))

    await client.close_connection()


async def SymbolInfo():
    client = await AsyncClient.create()

    res = await client.get_symbol_info('BTCUSDT')
    print(json.dumps(res, indent=2))

    await client.close_connection()


async def TradeStream():
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    ts = bm.trade_socket('BTCUSDT')

    async with ts as tscm:
        while True:
            res = await tscm.recv()
            print(res)

    await client.close_connection()


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(TradeStream())
