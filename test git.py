from pybit.unified_trading import WebSocket, HTTP


def handle_message(message):
    print(message)


def OrderBookStream():
    WebSocket(
        testnet=False,
        channel_type="linear",
    ).orderbook_stream(
        depth=50,
        symbol="BTCUSDT",
        callback=handle_message
    )


def TradeStream():
    WebSocket(
        testnet=False,
        channel_type="linear",
    ).trade_stream(
        symbol="BTCUSDT",
        callback=handle_message
    )


def TickerStream():
    WebSocket(
        testnet=False,
        channel_type="linear",
    ).ticker_stream(
        symbol="BTCUSDT",
        callback=handle_message
    )


def KlineStream():
    WebSocket(
        testnet=False,
        channel_type="linear",
    ).kline_stream(
        interval=5,
        symbol="BTCUSDT",
        callback=handle_message
    )


def LiquidationsStream():
    WebSocket(
        testnet=False,
        channel_type="linear",
    ).liquidation_stream(
        symbol="BTCUSDT",
        callback=handle_message
    )


def KlineRequest():
    print(HTTP(testnet=False).get_kline(
    category="inverse",
    symbol="BTCUSDT",
    interval=60,
    start=1670601600000,
    end=1670608800000,
    ))


def OrderBookRequest():
    print(HTTP(testnet=False).get_orderbook(
    category="linear",
    symbol="BTCUSDT",
    limit=500
    ))


def TickerRequest():
    print(HTTP(testnet=False).get_tickers(
        category="inverse",
        symbol="BTCUSD",
    ))


if __name__ == "__main__":
    TickerRequest()

