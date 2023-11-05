# Flask imports
import random
import io
import matplotlib.pyplot as plt
from flask import Flask, render_template, send_file, make_response, url_for
from flask import Response, request, redirect, url_for, flash

#Pandas and Matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from pprint import pprint
from binance.enums import *
##############
import talib as ta
##############
import numpy as np

from bot4 import BinanceBot

# other requirements

app = Flask(__name__)

# settings

app.secret_key = 'super secret key'

# Pandas Page

binance = BinanceBot()

@app.route('/')
def Index():
    return render_template('index.html')

@app.route('/buscar')
@app.route('/buscar', methods=("POST", "GET"))
def find():
    paridad = request.form['paridad'] 
    intervalo = request.form['intervalo']
    comienzo = request.form['comienzo']
    #
    binance.get_historical_klines(paridad, intervalo, comienzo)
    binance.get_resultado()
    
    flash('Busqueda realizada con exito')

    return redirect(url_for('Index'))

@app.route('/graficarSimple')
@app.route('/graficarSimple', methods=("POST", "GET"))
def graficar_simple():
    #
    sma3 = request.form.get('sma3') != None
    sma6 = request.form.get('sma6') != None
    sma9 = request.form.get('sma9') != None
    dpo = request.form.get('dpo') != None
    precioCompra = request.form.get('preciocompra') != None
    precioVenta = request.form.get('precioventa') != None
    rsiPrecioCompra = request.form.get('rsipreciocompra') != None
    rsiPrecioVenta = request.form.get('rsiprecioventa') != None
    stochPrecioCompra = request.form.get('stochpreciocompra') != None
    stochPrecioVenta = request.form.get('stochprecioventa') != None
    bollingerUp = request.form.get('bollingerup') != None
    bollingerMi = request.form.get('bollingermi') != None
    bollingerLo = request.form.get('bollingerlo') != None
    
    binance.setSenalGraficoBasico(sma3, sma6, sma9, dpo, precioCompra, precioVenta, rsiPrecioCompra, rsiPrecioVenta, stochPrecioCompra, stochPrecioVenta, bollingerUp, bollingerMi, bollingerLo)

    flash('Gráfico realizado con exito')

    return redirect(url_for('Index'))

@app.route('/graficarIndicadores')
@app.route('/graficarIndicadores', methods=("POST", "GET"))
def graficar_indicadores():
    #
    rsi11 = request.form.get('rsi11') != None
    stochSlowk = request.form.get('stochslowk') != None
    stochSlowd = request.form.get('stochslowd') != None
    stdDev = request.form.get('stddev') != None
    
    binance.setSenalGraficoIndicadores(rsi11, stochSlowk, stochSlowd, stdDev)

    flash('Gráfico realizado con exito')

    return redirect(url_for('Index'))

@app.route('/figuraSimple.png')
def plot_figure_simple_png():
    fig = create_figure_data('simple')
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@app.route('/figuraIndicadores.png')
def plot_figure_indicadores_png():
    fig = create_figure_data('indicadores')
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_figure_data(tipo):
    
    binance.get_historical_klines("BTCUSDT","1m", "1 hour ago UTC")
    binance.get_resultado()

    binance.get_grafico(tipo)

    fig, ax = plt.subplots(figsize=(10, 5))

    fig.patch.set_facecolor('#E8E5DA')

    fig = binance.grafico
    return fig



@app.route('/pandas')
@app.route('/pandas', methods=("POST", "GET"))
def GK():
    binance.get_historical_klines("1m", "1 hour ago UTC")
    binance.get_resultado()
    datos = binance.resultado
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
    fig = create_figure('simple')
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@app.route('/plot2.png')
def plot_png2():
    fig = create_figure('indicadores')
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


def create_figure(tipo):
    binance.get_historical_klines("1m", "6 hours ago UTC")
    binance.get_resultado()
    binance.get_grafico(tipo)

    fig, ax = plt.subplots(figsize=(10, 5))

    fig.patch.set_facecolor('#E8E5DA')

    #x = ECS_data.team
    #y = ECS_data.gw1
    #ax.bar(x, y, color="#304C89")

    fig = binance.grafico
    return fig


if __name__ == '__main__':
    app.run(debug=True)
