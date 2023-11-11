from binance.client import Client
from binance import ThreadedWebsocketManager
import talib
import time
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()
# Acceder a tus variables de entorno para no mostrar las claves en tu código
api_key = os.environ["BINANCE_API_KEY"]
api_secret = os.environ["BINANCE_API_SECRET"]

# Inicializa el cliente de Binance
client = Client(api_key, api_secret)

# Define el par de trading y el intervalo (ejemplo: BTCUSDT, 1h)
symbol = 'MEMEUSDT'
interval = '15m'

# Parámetros para la estrategia RSI
rsi_length = 14
rsi_oversold = 30
rsi_overbought = 70

# Variables para llevar un seguimiento de las operaciones
maximo_saldo = 1.0  # Maximo
saldo_disponible = 0.0  # Reemplaza con tu saldo inicial
cantidad_compra = 0.5  # Reemplaza con la cantidad deseada para comprar
cantidad_vender = 0.5  # Reemplaza con la cantidad deseada para vender

# Función para obtener el saldo de la moneda en cuestión


def obtener_saldo(coin):
    account_info = client.get_account()
    for balance in account_info['balances']:
        if balance['asset'] == coin:
            return float(balance['free'])
    return 0.0

# Función para manejar la estrategia de trading


def estrategia_trading(msg):
    rsi_values = []

    # Obtiene los precios de cierre históricos
    historical_klines = client.futures_klines(
        symbol=symbol, interval=interval, limit=rsi_length + 1)

    # print(f"historical_klines: {historical_klines}")

    closes = [float(kline[4]) for kline in historical_klines]

    # print(f"closes: {closes}")
    # se debe convertir para utilizar RSI de TALIB
    np_closes = np.array(closes)
    # Calcula el RSI
    rsi = talib.RSI(np_closes, timeperiod=rsi_length)
    # rsi = talib.RSI(closes, timeperiod=rsi_length)

    print(f"rsi: {rsi[-1]}")

    # Actualiza la lista de valores RSI
    for rsi_value in rsi:
        rsi_values.append(rsi_value)

    # Comprueba si el RSI está por debajo del umbral de sobreventa
    if rsi[-1] < rsi_oversold and saldo_disponible > 0:
        print(
            f"RSI está por debajo del umbral de sobreventa ({rsi[-1]}). Realizando una compra...")
        # client.create_test_order(symbol=symbol, side=Client.SIDE_BUY, type=Client.ORDER_TYPE_MARKET, quantity=cantidad_compra)
        # client.create_order(symbol=symbol, side=Client.SIDE_BUY, type=Client.ORDER_TYPE_MARKET, quantity=cantidad_compra)
        saldo_disponible -= cantidad_compra
        print(f"Compra realizada. Nuevo saldo disponible: {saldo_disponible}")

    # Comprueba si el RSI está por encima del umbral de sobrecompra
    if rsi[-1] > rsi_overbought and maximo_saldo < 1.0:
        print(
            f"RSI está por encima del umbral de sobrecompra ({rsi[-1]}). Realizando una venta...")
        # client.create_test_order(symbol=symbol, side=Client.SIDE_SELL,type=Client.ORDER_TYPE_MARKET, quantity=cantidad_vender)
        # client.create_order(symbol=symbol, side=Client.SIDE_SELL, type=Client.ORDER_TYPE_MARKET, quantity=cantidad_vender)
        saldo_disponible += cantidad_vender
        print(f"Venta realizada. Nuevo saldo disponible: {saldo_disponible}")


# Inicializa el Websocket Manager
ws_manager = ThreadedWebsocketManager()
ws_manager.start()

# Regístrate para recibir actualizaciones de precios
ws_manager.start_kline_socket(
    callback=estrategia_trading, symbol=symbol, interval=interval)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    ws_manager.stop()
