from flask import Flask, config, render_template, request, flash, redirect, url_for
import json

from matplotlib.pyplot import title
import plotly
import plotly.express as px
import plotly.graph_objs as go
from bot4 import BinanceBot

binance = BinanceBot()

app = Flask(__name__)

# settings

app.secret_key = 'super secret key'


@app.route('/callback', methods=['POST', 'GET'])
def cb():
    return gm(request.args.get('data'))


@app.route('/')
def index():
    paridad = 'BTCUSDT'  # request.form['paridad']
    intervalo = '1m'  # request.form['intervalo']
    comienzo = '1 hour ago UTC'  # request.form['comienzo']
    #
    binance.get_historical_klines(paridad, intervalo, comienzo)
    graficos = gm(binance.get_resultado(), paridad, intervalo, comienzo)

    return render_template('index.html',  graphJSON1=graficos[0], graphJSON2=graficos[1])


@app.route('/buscar', methods=("POST", "GET"))
def find():
    paridad = request.form['paridad']
    intervalo = request.form['intervalo']
    comienzo = request.form['comienzo']
    #
    binance.get_historical_klines(paridad, intervalo, comienzo)
    binance.get_resultado()
    graficos = gm(binance.get_resultado(), paridad, intervalo, comienzo)

    flash('Busqueda realizada con exito')

    # return redirect(url_for('Index'))
    return render_template('index.html',  graphJSON1=graficos[0], graphJSON2=graficos[1])


def gm(data, paridad, intervalo, comienzo):
    df = data
    fig = go.Figure(data=[go.Scatter(x=df.index, y=df['Cierre'], mode='lines', name='Cierre', line=dict(color='blue', width=2)),
                          go.Scatter(x=df.index, y=df['SMA3'], mode='lines', name='SMA3', line=dict(
                              color='red', dash='dash')),
                          go.Scatter(x=df.index, y=df['SMA6'], mode='lines', name='SMA6', line=dict(
                              color='green', dash='dash')),
                          go.Scatter(x=df.index, y=df['SMA9'], mode='lines', name='SMA9', line=dict(
                              color='yellow', dash='dash')),

                          go.Scatter(x=df.index, y=df['upper_band'], mode='lines', name='bollingerUp', line=dict(
                              color='#00ff00', dash='dot')),
                          go.Scatter(x=df.index, y=df['middle_band'], mode='lines', name='bollingerMi', line=dict(
                              color='#ff0000', dash='dot')),
                          go.Scatter(x=df.index, y=df['lower_band'], mode='lines', name='bollingerLo', line=dict(
                              color='#0000ff', dash='dot')),

                          go.Scatter(x=df.index, y=df['Compra'], mode='markers', name='Compra', marker=dict(
                              color='red', size=15)),
                          go.Scatter(x=df.index, y=df['Venta'], mode='markers', name='Venta', marker=dict(
                              color='green', size=15)),

                          go.Scatter(x=df.index, y=df['RSICompra'], mode='markers', name='RSICompra', marker=dict(
                              color='red', size=10)),
                          go.Scatter(x=df.index, y=df['RSIVenta'], mode='markers', name='RSIVenta', marker=dict(
                              color='green', size=10)),

                          go.Scatter(x=df.index, y=df['STOCHCompra'], mode='markers', name='STOCHCompra', marker=dict(
                              color='red', size=5)),
                          go.Scatter(x=df.index, y=df['STOCHVenta'], mode='markers', name='STOCHVenta', marker=dict(
                              color='green', size=5)),
                          ])
    fig.update_layout(
        title=f'{paridad} - {intervalo} - {comienzo}', xaxis_rangeslider_visible=True)

    fig2 = go.Figure(data=[go.Scatter(x=df.index, y=df['RSI11'], mode='lines', name='RSI11', line=dict(color='blue')),
                           go.Scatter(x=df.index, y=df['stoch_slowk'], mode='lines', name='stoch_slowk', line=dict(
                               color='red')),
                           go.Scatter(x=df.index, y=df['stoch_slowd'], mode='lines', name='stoch_slowd', line=dict(
                               color='green')),
                           go.Scatter(x=df.index, y=df['STDDEV'], mode='lines', name='STDDEV', line=dict(
                               color='yellow'))

                           ])
    fig2.update_layout(
        title=f'{paridad} - {intervalo} - {comienzo}', xaxis_rangeslider_visible=True)

    graphJSON1 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    print(fig.data[0])
    print(fig2.data[0])
    # fig.data[0]['staticPlot']=True

    return graphJSON1, graphJSON2


if __name__ == '__main__':
    app.run(debug=True)
