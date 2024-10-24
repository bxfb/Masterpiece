import websocket
import json

# Функция для обработки сообщений от WebSocket
def on_message(ws, message):
    data = json.loads(message)
    print("Получено сообщение:", data)

# Функция для обработки ошибок
def on_error(ws, error):
    print("Ошибка:", error)

# Функция для обработки закрытия соединения
def on_close(ws, close_status_code, close_msg):
    print("Соединение закрыто")

# Функция для открытия соединения
def on_open(ws):
    print("Соединение открыто")
    # Здесь можно отправить подписку на данные, если это необходимо
    subscribe_message = {
        "method": "subscribe",
        "subscription": { "type": "l2Book", "coin": "BTC" } }
    ws.send(json.dumps(subscribe_message))

# URL WebSocket сервера Hyperliquid
url = "wss://api.hyperliquid-testnet.xyz/ws"

# WebSocket приложение
ws = websocket.WebSocketApp(url,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
ws.on_open = on_open

# Запуск клиента
ws.run_forever()
