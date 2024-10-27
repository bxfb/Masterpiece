import okx.MarketData as MarketData
import requests
import datetime
import asyncio
import json
import websockets


async def TickerStream():
    url = "wss://ws.okx.com:8443/ws/v5/public"
    async with websockets.connect(url, ping_interval=20, ping_timeout=60) as ws:
        subs = dict(
            op='subscribe',
            args=[
                dict(channel="mark-price", instId='BTC-USDT')
            ]
        )
        await ws.send(json.dumps(subs))

        async for msg in ws:
            msg = json.loads(msg)
            ev = msg.get('event')
            data = msg.get('data')
            if ev:
                print(f'event {ev} = {msg.get('arg')}')
            elif data and len(data) > 0:
                symbol = data[0].get('instId')
                price = float(data[0].get('markPx', '0.0'))
                print(f'{datetime.datetime.now().isoformat()} {symbol} = {price}')


async def TradeStream():
    url = "wss://ws.okx.com:8443/ws/v5/public"
    async with websockets.connect(url, ping_interval=20, ping_timeout=60) as ws:
        subs = dict(
            op='subscribe',
            args=[
                dict(channel="trades", instId='BTC-USDT')
            ]
        )
        await ws.send(json.dumps(subs))

        async for msg in ws:
            msg = json.loads(msg)
            ev = msg.get('event')
            data = msg.get('data')
            if ev:
                print(f'event {ev} = {msg.get('arg')}')
            elif data and len(data) > 0:
                symbol = data[0].get('instId')
                price = float(data[0].get('markPx', '0.0'))
                print(f'{datetime.datetime.now().isoformat()} {symbol} = {data[0]}')


async def OrderBookStream():
    url = "wss://ws.okx.com:8443/ws/v5/public"
    async with websockets.connect(url, ping_interval=20, ping_timeout=60) as ws:
        subs = dict(
            op='subscribe',
            args=[
                dict(channel="books", instId='BTC-USDT')
            ]
        )
        await ws.send(json.dumps(subs))

        async for msg in ws:
            msg = json.loads(msg)
            ev = msg.get('event')
            data = msg.get('data')
            if ev:
                print(f'event {ev} = {msg.get('arg')}')
            elif data and len(data) > 0:
                symbol = data[0].get('instId')
                price = float(data[0].get('markPx', '0.0'))
                print(f'{datetime.datetime.now().isoformat()} {symbol} = {data[0]}')


def OrderBookRequest():
    print(requests.get("https://www.okx.com/api/v5/market/books-full?instId=BTC-USDT&sz=5000").json())


def OrderBookRequest2():
    flag = "0"  # Production trading:0 , demo trading:1

    marketDataAPI = MarketData.MarketAPI(flag=flag)

    result = marketDataAPI.get_orderbook(
        instId="BTC-USDT",
        sz=400  # max sz=400
    )
    print(result)


def KlineRequest():
    flag = "0"  # Production trading:0 , demo trading:1

    marketDataAPI = MarketData.MarketAPI(flag=flag)

    result = marketDataAPI.get_candlesticks(
        instId="BTC-USDT",
        bar="1H",
        limit=100
    )
    print(result)


def VolumeRequest():
    flag = "0"  # Production trading:0 , demo trading:1

    marketDataAPI = MarketData.MarketAPI(flag=flag)

    # 24H Volume
    result = marketDataAPI.get_volume()
    print(result)


if __name__ == "__main__":
    asyncio.run(TradeStream())
