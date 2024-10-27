import requests
import datetime
import asyncio
import json
import websockets


async def TickerStream():
    url = "wss://ws.bitget.com/v2/ws/public"
    async with websockets.connect(url, ping_interval=20, ping_timeout=60) as ws:
        subs = dict(
            op='subscribe',
            args=[
                dict(instType='SPOT', channel='ticker', instId='BTCUSDT')
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


async def TradeStream():
    url = "wss://ws.bitget.com/v2/ws/public"
    async with websockets.connect(url, ping_interval=20, ping_timeout=60) as ws:
        subs = dict(
            op='subscribe',
            args=[
                dict(instType='SPOT', channel='trade', instId='BTCUSDT')
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
    url = "wss://ws.bitget.com/v2/ws/public"
    async with websockets.connect(url, ping_interval=20, ping_timeout=60) as ws:
        subs = dict(
            op='subscribe',
            args=[
                dict(instType='SPOT', channel='books15', instId='BTCUSDT')
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
    print(requests.get("https://api.bitget.com/api/mix/v1/market/depth?symbol=BTCUSDT_UMCBL&limit=100").json())


def TickerRequest():
    print(requests.get("https://api.bitget.com/api/mix/v1/market/ticker?symbol=BTCUSDT_UMCBL").json())


def HistoryKlineRequest():
    print(requests.get("https://api.bitget.com/api/mix/v1/market/candles?symbol=BTCUSDT_UMCBL&granularity=5m&startTime=1659406928000&endTime=1659410528000").json())


if __name__ == "__main__":
    asyncio.run(OrderBookStream())
