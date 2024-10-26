from pybit.unified_trading import WebSocket, HTTP


ws = WebSocket(
        testnet=False,
        channel_type="linear",
    )
session = HTTP(testnet=False)


def handle_message(message):
    print(message)


def OrderBookStream():
    ws.orderbook_stream(
        depth=50,
        symbol="BTCUSDT",
        callback=handle_message
    )


def TradeStream():
    ws.trade_stream(
        symbol="BTCUSDT",
        callback=handle_message
    )


def TickerStream():
    ws.ticker_stream(
        symbol="BTCUSDT",
        callback=handle_message
    )


def KlineStream():
    ws.kline_stream(
        interval=5,
        symbol="BTCUSDT",
        callback=handle_message
    )


def LiquidationsStream():
    ws.liquidation_stream(
        symbol="BTCUSDT",
        callback=handle_message
    )


def KlineRequest():
    print(session.get_kline(
    category="inverse",
    symbol="BTCUSDT",
    interval=60,
    start=1670601600000,
    end=1670608800000,
    ))


def OrderBookRequest():
    print(session.get_orderbook(
    category="linear",
    symbol="BTCUSDT",
    limit=500
    ))


def TickerRequest():
    print(session.get_tickers(
        category="inverse",
        symbol="BTCUSD",
    ))


if __name__ == "__main__":
    TickerRequest()
