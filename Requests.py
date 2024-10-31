import requests


def BinanceOrderBookRequest():
    return requests.get("https://api.binance.com/api/v3/depth?symbol=BTCUSDT&limit=100").json()


def BinanceFuturesOrderBookRequest():
    return requests.get("https://fapi.binance.com/fapi/v1/depth?symbol=BTCUSDT&limit=100").json()


def BinanceKlineRequest():
    return requests.get("https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=3").json()


def BinanceFuturesKlineRequest(interval,klines_amount):
    return requests.get(f"https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval={interval}&limit={klines_amount}").json()


def BybitOrderBookRequest():
    return requests.get("https://api.bybit.com/v5/market/orderbook?category=spot&symbol=BTCUSDT&limit=100").json()


def BybitFuturesOrderBookRequest():
    return requests.get("https://api.bybit.com/v5/market/orderbook?category=linear&symbol=BTCUSDT&limit=100").json()


def BybitKlineRequest():
    return requests.get("https://api.bybit.com/v5/market/kline?category=spot&symbol=BTCUSDT&interval=1&limit=200").json()


def BybitFuturesKlineRequest():
    return requests.get("https://api.bybit.com/v5/market/kline?category=linear&symbol=BTCUSDT&interval=1&limit=200").json()


def BitgetOrderBookRequest():
    return requests.get("https://api.bitget.com/api/spot/v1/market/depth?symbol=BTCUSDT_SPBL&type=step0&limit=150").json()


def BitgetFuturesOrderBookRequest():
    return requests.get("https://api.bitget.com/api/mix/v1/market/depth?symbol=BTCUSDT_UMCBL&limit=100").json()


def BitgetKlineRequest():
    return requests.get("https://api.bitget.com/api/spot/v1/market/candles?symbol=BTCUSDT_SPBL&period=1min&limit=100").json()


def BitgetFuturesKlineRequest():
    return requests.get("https://api.bitget.com/api/mix/v1/market/candles?symbol=BTCUSDT_UMCBL&granularity=1m&startTime=1659406928000&endTime=1659410528000&limit=100").json()


def OkxOrderBookRequest():
    return requests.get("https://www.okx.com/api/v5/market/books-full?instId=BTC-USDT&sz=100").json()


def OkxKlineRequest():
    return requests.get("https://www.okx.com/api/v5/market/candles?instId=BTC-USDT&bar=1m&limit=100").json()


if __name__ == "__main__":
    OkxKlineRequest()
