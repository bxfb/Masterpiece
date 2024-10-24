import json
import websocket


# Функция для обработки сообщений
def on_message(ws, message):
    data = json.loads(message)
    print("Order Book Update:")
    print("Last Update:", data['lastUpdateId'])
    print("Asks:")
    for ask in data['asks'][:5]:  # Показываем 5 лучших заявок на продажу
        print(ask)
    print("Bids:")
    for bid in data['bids'][:5]:  # Показываем 5 лучших заявок на покупку
        print(bid)
    print("\n")


# Функция для обработки ошибок
def on_error(ws, error):
    print("Error:", error)


# Функция для обработки начала соединения
def on_open(ws):
    print("Connection opened")
    # Подписываемся на ордербук (например, для пары BTCUSDT)
    subscribe_message = {
        "method": "SUBSCRIBE",
        "params": [
            "btcusdt@depth"  # Замените на нужную пару
        ],
        "id": 1
    }
    ws.send(json.dumps(subscribe_message))


# Функция для обработки закрытия соединения
def on_close(ws):
    print("Connection closed")


if __name__ == "__main__":
    # URL для подключения к WebSocket
    ws_url = "wss://testnet.binance.vision/ws-api/v3"

    # Создание WebSocket клиента
    ws = websocket.WebSocketApp(ws_url,
                                on_message=on_message,
                                on_error=on_error)

    # Метод для запуска WebSocket
    ws.on_open = on_open
    ws.run_forever()
