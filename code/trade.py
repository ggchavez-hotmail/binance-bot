from binance.client import Client
from binance.enums import *

import websocket
import talib as ta

import json
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()
# Acceder a tus variables de entorno para no mostrar las claves en tu código
api_key = os.environ["BINANCE_API_KEY"]
api_secret = os.environ["BINANCE_API_SECRET"]
url_demo = os.environ["BINANCE_API_URL_DEMO"]

TRADE_SYMBOL = "BTCUSDT"
SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"

closes = []
in_position = False
cliente = Client(api_key, api_secret, testnet=True, tld="com")

# cliente.API_URL = url_demo

SMASLOW = 12
SMAMEDIA = 17
SMAHIGH = 26

TRADE_QUANTITY = "0.00030000"

MONTO_GANADO = 0.0

# info = cliente.get_symbol_info(TRADE_SYMBOL)
# print(info)


def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):

    precio = 0.0
    try:
        print("enviando orden")
        # order = cliente.create_test_order(
        order = cliente.create_order(
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=quantity
        )
        print(f"order: {order}")
        precio = order["fills"][0]["price"]
        print(f"precio: {precio}")

        return True, precio
    except Exception as e:
        print(f"error: {e}")
        return False, precio


def on_open(wsApp):
    print("WebSocket abierto")


def on_message(wsApp, message):
    global closes, in_position

    message = json.loads(message)
    # print(message)

    candle = message['k']
    timestamp = candle['t']
    candle_is_closed = candle['x']

    if candle_is_closed:
        closes.append(float(candle['c']))
        num_closes = len(closes)

        print(num_closes)

        if num_closes > SMASLOW:
            np_closes = np.array(closes)
            smaslow = ta.SMA(np_closes, SMASLOW)  # media movil simple lenta
            last_smaslow = smaslow[-1]

        if num_closes > SMAMEDIA:
            np_closes = np.array(closes)
            smasmedia = ta.SMA(np_closes, SMAMEDIA)  # media movil simple media
            last_smasmedia = smasmedia[-1]

        if num_closes > SMAHIGH:
            np_closes = np.array(closes)
            smahigh = ta.SMA(np_closes, SMAHIGH)  # media movil simple rapida
            last_smahigh = smahigh[-1]
            print(f"SMASLOW: {last_smaslow}")
            print(f"SMAMEDIA: {last_smasmedia}")
            print(f"SMAHIGH: {last_smahigh}")

        if last_smaslow > last_smasmedia and last_smasmedia > last_smahigh:
            print("SMA de 3 tiempos se encuentra en cruce de compra")
            if in_position:
                print("Nada que Comprar.")
            else:
                print("Comprar Comprar Comprar!!!")
                order_succeded, precio = order(
                    SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                if order_succeded:
                    in_position = True
                    MONTO_GANADO = MONTO_GANADO - precio
                    print(f"MONTO_GANADO: {MONTO_GANADO}")

        if last_smaslow < last_smasmedia and last_smasmedia < last_smahigh:
            print("SMA de 3 tiempos se encuentra en cruce de venta")
            if in_position:
                print("Vender Vender Vender!!!")
                order_succeded, precio = order(
                    SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                if order_succeded:
                    in_position = False
                    MONTO_GANADO = MONTO_GANADO + precio
                    print(f"MONTO_GANADO: {MONTO_GANADO}")
            else:
                print("Nada que vender.")


def on_close(wsApp):
    print("WebSocket cerrado")


# order_succeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)

# order_succeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)

wsApp = websocket.WebSocketApp(SOCKET, on_open=on_open,
                               on_message=on_message, on_close=on_close)
wsApp.run_forever()
