from pprint import pprint
#from tkinter import E
import config
from binance.client import Client
from binance.enums import *
##############
import talib as ta
##############
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

client = Client(config.API_KEY, config.API_SECRET, tld='com')
symbolTicker = 'BTCUSDT'

# recuperar datos y convertir a numpy array
klines = np.array(client.get_historical_klines(
    symbolTicker, Client.KLINE_INTERVAL_1MINUTE, "12 hours ago UTC"))

# Volcar a un dataframe
datos = pd.DataFrame(klines.reshape(-1, 12), dtype=float, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                     'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])

# Calcular media movil simple 30
#MSV30 = pd.DataFrame()
#MSV30['close'] = datos['close'].rolling(window=30).mean()

# Calcular media movil simple 100
#MSV100 = pd.DataFrame()
#MSV100['close'] = datos['close'].rolling(window=100).mean()

# Dejar solo datos relevantes
data = pd.DataFrame()
data['Cierre'] = datos['close']
#data['MVS30'] = MSV30['close']
#data['MVS100'] = MSV100['close']

# Calcular cuando se cruza la media movil simple 30 con la media movil simple 100


def senal(data):
    compra = []
    venta = []
    detrendedPriceOscillator = []
    condicion = 0
    for intervalo in range(len(data)):
        if data['SMA30'][intervalo] > data['SMA100'][intervalo]:
            if condicion != 1:
                compra.append(data['Cierre'][intervalo])
                venta.append(np.nan)
                condicion = 1
            else:
                compra.append(np.nan)
                venta.append(np.nan)
        elif data['SMA30'][intervalo] < data['SMA100'][intervalo]:
            if condicion != -1:
                venta.append(data['Cierre'][intervalo])
                compra.append(np.nan)
                condicion = -1
            else:
                venta.append(np.nan)
                compra.append(np.nan)
        else:
            compra.append(np.nan)
            venta.append(np.nan)
            condicion = 0

        if (data['Cierre'][intervalo] - data['SMA11'][intervalo]) <= 0.0001:
            detrendedPriceOscillator.append(data['Cierre'][intervalo])
        else:
            detrendedPriceOscillator.append(np.nan)

    return (compra, venta, detrendedPriceOscillator)


data['SMA11'] = ta.SMA(data['Cierre'], 11)  # media movil simple 11
data['SMA30'] = ta.SMA(data['Cierre'], 30)  # media movil simple 30
data['SMA100'] = ta.SMA(data['Cierre'], 100)  # media movil simple 100
data['EMA55'] = ta.EMA(data['Cierre'], 55)  # media movil exponencial 55

data['upper_band'], data['middle_band'], data['lower_band'] = ta.BBANDS(
    data['Cierre'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)  # bandas de Bollinger

data['RSI'] = ta.RSI(data['Cierre'], timeperiod=14)  # indicador RSI
data['STDDEV'] = ta.STDDEV(
    data['Cierre'], timeperiod=20)  # desviacion estandar


senales = senal(data)
data['Compra'] = senales[0]
data['Venta'] = senales[1]
data['DPO'] = senales[2]

# Graficar los datos
# plt.style.use('ggplot') #Estilo cuadriculas
plt.style.use('bmh')  # Estilo cuadriculas
plt.figure(figsize=(10, 5))

plt.plot(data['Cierre'], label='Cierre', alpha=0.5)

##plt.plot(data['MVS30'], label='Media Movil 30' , alpha = 0.2)
##plt.plot(data['MVS100'], label='Media Movil 100', alpha = 0.3)

plt.plot(data['SMA30'], label='SMA30', alpha=0.3)
plt.plot(data['SMA100'], label='SMA100', alpha=0.3)
#plt.plot(data['EMA55'], label='EMA55', alpha = 0.3)

#plt.plot(data['upper_band'], label='upper_band', alpha = 0.3)
#plt.plot(data['middle_band'], label='middle_band', alpha = 0.3)
#plt.plot(data['lower_band'], label='lower_band', alpha = 0.3)

plt.scatter(data.index, data['Compra'],
            label='Precio Compra', marker='^', color='green')
plt.scatter(data.index, data['Venta'],
            label='Precio Venta', marker='v', color='red')
plt.scatter(data.index, data['DPO'], label='DPO',
            marker='*', color='blue', alpha=0.5)

##plt.plot(data['STDDEV'], label='STDDEV', alpha = 0.3)
##plt.plot(data['RSI'], label='RSI', alpha = 0.7)

plt.legend(loc='upper left')
plt.show()
