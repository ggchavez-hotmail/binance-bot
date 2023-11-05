"""  HOW TO HOST PANDAS AND MATPLOTLIB ONLINE TEMPLATE"""


# Flask imports
import random
import io
import matplotlib.pyplot as plt
from flask import Flask, render_template, send_file, make_response, url_for
from flask import Response

#Pandas and Matplotlib
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib

from pprint import pprint
#from tkinter import E
import config
from binance.client import Client
from binance.enums import *
##############
import talib as ta
##############
import numpy as np

client = Client(config.API_KEY, config.API_SECRET, tld='com')
symbolTicker = 'BTCUSDT'

# recuperar datos y convertir a numpy array
klines = np.array(client.get_historical_klines(
    symbolTicker, Client.KLINE_INTERVAL_1MINUTE, "1 hours ago UTC"))

# Volcar a un dataframe
datos = pd.DataFrame(klines.reshape(-1, 12), dtype=float, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                     'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])

# Dejar solo datos relevantes
data = pd.DataFrame()
data['Cierre'] = datos['close']

# Calcular cuando se cruza la media movil simple 30 con la media movil simple 100


def senal(data):
    compra = []
    venta = []
    detrendedPriceOscillator = []
    condicion = 0
    for intervalo in range(len(data)):
        if data['SMA3'][intervalo] > data['SMA6'][intervalo] and data['SMA6'][intervalo] > data['SMA9'][intervalo]:
            if condicion != 1:
                compra.append(data['Cierre'][intervalo])
                venta.append(np.nan)
                condicion = 1
            else:
                compra.append(np.nan)
                venta.append(np.nan)
        elif data['SMA3'][intervalo] < data['SMA6'][intervalo] and data['SMA6'][intervalo] < data['SMA9'][intervalo]:
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


data['SMA3'] = ta.SMA(data['Cierre'], 3)  # media movil simple 3
data['SMA6'] = ta.SMA(data['Cierre'], 6)  # media movil simple 6
data['SMA9'] = ta.SMA(data['Cierre'], 9)  # media movil simple 9
data['SMA11'] = ta.SMA(data['Cierre'], 11)  # media movil simple 11
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

# matplotlib.use('Agg')

# other requirements

app = Flask(__name__)

# Pandas Page


@app.route('/')
@app.route('/pandas', methods=("POST", "GET"))
def GK():
    return render_template('pandas.html',
                           PageTitle="Pandas",
                           table=[datos.to_html(classes='data', index=False)], titles=datos.columns.values)


# Matplotlib page
@app.route('/matplot', methods=("POST", "GET"))
def mpl():
    return render_template('matplot.html',
                           PageTitle="Matplotlib")


@app.route('/plot.png')
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


def create_figure():
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('#E8E5DA')

    #x = ECS_data.team
    #y = ECS_data.gw1

    # ax.bar(x, y, color="#304C89")

    plt.xticks(rotation=30, size=5)
    plt.ylabel("Expected Clean Sheets", size=5)

    plt.style.use('bmh')  # Estilo cuadriculas
    #plt.figure(figsize=(10, 5))

    plt.plot(data['Cierre'], label='Cierre', alpha=0.5)

    ##plt.plot(data['MVS30'], label='Media Movil 30' , alpha = 0.2)
    ##plt.plot(data['MVS100'], label='Media Movil 100', alpha = 0.3)

    plt.plot(data['SMA3'], label='SMA3', alpha=0.3)
    plt.plot(data['SMA6'], label='SMA6', alpha=0.3)
    plt.plot(data['SMA9'], label='SMA9', alpha=0.3)
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
    plt.grid(True)
    plt.title('GK')
    plt.xlabel('Fecha')
    plt.ylabel('Precio')
    plt.xticks(rotation=30, size=5)
    plt.yticks(size=5)
    plt.tight_layout()

    return fig


if __name__ == '__main__':
    app.run(debug=True)
