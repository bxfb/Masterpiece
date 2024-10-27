import json
import websocket


def on_message(ws, message):
    data = json.loads(message)
    print("Получено сообщение:", data)


def on_error(ws, error):
    print("Ошибка:", error)


def on_close(ws, close_status_code, close_msg):
    print("Соединение закрыто")


def on_open(ws):
    print("Соединение открыто")
    subscribe_message = {
        "method": "subscribe",
        "subscription": { "type": "l2Book", "coin": "BTC" } }
    ws.send(json.dumps(subscribe_message))


def TradeStream():
    url = "wss://api.hyperliquid-testnet.xyz/ws"
    ws = websocket.WebSocketApp(url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()


if __name__ == "__main__":
    TradeStream()
