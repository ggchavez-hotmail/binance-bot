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
symbol = 'BTCUSDT'
interval = '1m'

# Parámetros para la estrategia SMA
SMASLOW = 12
SMAMEDIA = 17
SMAHIGH = 26

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
    global saldo_disponible
    # Obtiene los precios de cierre históricos
    historical_klines = client.futures_klines(
        symbol=symbol, interval=interval, limit=SMAHIGH + 1)

    # print(f"historical_klines: {historical_klines}")

    closes = [float(kline[4]) for kline in historical_klines]

    # print(f"closes: {closes}")
    # se debe convertir para utilizar RSI de TALIB
    np_closes = np.array(closes)
    # Calcula el SMAS

    smaslow = talib.SMA(np_closes, SMASLOW)  # media movil simple lenta
    smamedia = talib.SMA(np_closes, SMAMEDIA)  # media movil simple media
    smahigh = talib.SMA(np_closes, SMAHIGH)  # media movil simple rapida

    # rsi = talib.RSI(closes, timeperiod=rsi_length)

    print(f"smaslow: {smaslow[-1]}")
    print(f"smamedia: {smamedia[-1]}")
    print(f"smahigh: {smahigh[-1]}")

    # Comprueba si el RSI está por debajo del umbral de sobreventa
    if smaslow[-1] < smamedia[-1] and smamedia[-1] < smahigh[-1] and saldo_disponible > 0:
        print(
            f"SMA en Posición. Realizando una compra...")
        # client.create_test_order(symbol=symbol, side=Client.SIDE_BUY, type=Client.ORDER_TYPE_MARKET, quantity=cantidad_compra)
        # client.create_order(symbol=symbol, side=Client.SIDE_BUY, type=Client.ORDER_TYPE_MARKET, quantity=cantidad_compra)
        saldo_disponible -= cantidad_compra
        print(f"Compra realizada. Nuevo saldo disponible: {saldo_disponible}")

    # Comprueba si el RSI está por encima del umbral de sobrecompra
    if smaslow[-1] > smamedia[-1] and smamedia[-1] > smahigh[-1] and maximo_saldo < 1.0:
        print(
            f"SMA en Posición. Realizando una venta...")
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
