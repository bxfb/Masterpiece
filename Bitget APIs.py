import requests


def OrderBookRequest():
    print(requests.get("https://api.bitget.com/api/mix/v1/market/depth?symbol=BTCUSDT_UMCBL&limit=100").json())


def TickerRequest():
    print(requests.get("https://api.bitget.com/api/mix/v1/market/ticker?symbol=BTCUSDT_UMCBL").json())


def HistoryKlineRequest():
    print(requests.get("https://api.bitget.com/api/mix/v1/market/candles?symbol=BTCUSDT_UMCBL&granularity=5m&startTime=1659406928000&endTime=1659410528000").json())


if __name__ == "__main__":
    HistoryKlineRequest()
