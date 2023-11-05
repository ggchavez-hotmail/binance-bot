from flask import Flask, config, render_template, request
import pandas as pd
import json
import plotly
import plotly.express as px
import plotly.graph_objs  as go
from bot4 import BinanceBot

binance = BinanceBot()

app = Flask(__name__)

# settings

app.secret_key = 'super secret key'


@app.route('/callback', methods=['POST', 'GET'])
def cb():
    return gm(request.args.get('data'))
   
@app.route('/callbackIndicator', methods=['POST', 'GET'])
def cbIndicator():
    return gmIndicator(request.args.get('data'))
   
@app.route('/')
def index():
    return render_template('chartsajax.html',  graphJSON=gm(), graphJSONIndicator=gmIndicator())

def gm(country='United Kingdom'):
    
    paridad = 'BTCUSDT' #request.form['paridad'] 
    intervalo = '1m' #request.form['intervalo']
    comienzo = '1 hour ago UTC' #request.form['comienzo']
    #
    binance.get_historical_klines(paridad, intervalo, comienzo)

    #df = pd.DataFrame(px.data.gapminder())
    #fig = px.line(df[df['Cierre']==country], x="year", y="gdpPercap")    

    df = binance.get_resultado()
    #fig = px.line(df, y='Cierre', x=df.index, title='Cierre')
    fig = go.Figure(data=[go.Scatter(x=df.index, y=df['Cierre'], mode='lines', name='Cierre', line=dict(color='blue', width=2)), 
                      go.Scatter(x=df.index, y=df['SMA3'], mode='lines', name='SMA3', line=dict(color='red', dash='dash')), 
                      go.Scatter(x=df.index, y=df['SMA6'], mode='lines', name='SMA6', line=dict(color='green', dash='dash')),
                      go.Scatter(x=df.index, y=df['SMA9'], mode='lines', name='SMA9', line=dict(color='yellow', dash='dash')),

                      go.Scatter(x=df.index, y=df['upper_band'], mode='lines', name='bollingerUp', line=dict(color='#00ff00', dash='dot')), 
                      go.Scatter(x=df.index, y=df['middle_band'], mode='lines', name='bollingerMi', line=dict(color='#ff0000', dash='dot')), 
                      go.Scatter(x=df.index, y=df['lower_band'], mode='lines', name='bollingerLo', line=dict(color='#0000ff', dash='dot')),

                      go.Scatter(x=df.index, y=df['Compra'], mode='markers', name='Compra', marker=dict(color='red', size=15)),
                      go.Scatter(x=df.index, y=df['Venta'], mode='markers', name='Venta', marker=dict(color='green',size=15)),

                      go.Scatter(x=df.index, y=df['RSICompra'], mode='markers', name='RSICompra', marker=dict(color='red', size=10)),
                      go.Scatter(x=df.index, y=df['RSIVenta'], mode='markers', name='RSIVenta', marker=dict(color='green', size=10)),

                      go.Scatter(x=df.index, y=df['STOCHCompra'], mode='markers', name='STOCHCompra', marker=dict(color='red', size=5)),
                      go.Scatter(x=df.index, y=df['STOCHVenta'], mode='markers', name='STOCHVenta', marker=dict(color='green', size=5)),
                      ])

    #fig = px.Scatter(name='Measurement', y=df['Cierre'], x=df.index, title='Cierre')

        
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    print(fig.data[0])
    #fig.data[0]['staticPlot']=True
    
    return graphJSON

def gmIndicator(country='United Kingdom'):
    
    paridad = 'BTCUSDT' #request.form['paridad'] 
    intervalo = '1m' #request.form['intervalo']
    comienzo = '1 hour ago UTC' #request.form['comienzo']
    #
    binance.get_historical_klines(paridad, intervalo, comienzo)

    #df = pd.DataFrame(px.data.gapminder())
    #fig = px.line(df[df['Cierre']==country], x="year", y="gdpPercap")    

    df = binance.get_resultado()
    #fig = px.line(df, y='Cierre', x=df.index, title='Cierre')
    fig = go.Figure(data=[go.Scatter(x=df.index, y=df['RSI11'], mode='lines', name='RSI11', line=dict(color='blue')), 
                      go.Scatter(x=df.index, y=df['stoch_slowk'], mode='lines', name='stoch_slowk', line=dict(color='red', dash='dash')), 
                      go.Scatter(x=df.index, y=df['stoch_slowd'], mode='lines', name='stoch_slowd', line=dict(color='green', dash='dash')),
                      go.Scatter(x=df.index, y=df['STDDEV'], mode='lines', name='STDDEV', line=dict(color='yellow', dash='dash'))

                      ])

    #fig = px.Scatter(name='Measurement', y=df['Cierre'], x=df.index, title='Cierre')

        
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    print(fig.data[0])
    #fig.data[0]['staticPlot']=True
    
    return graphJSON

if __name__ == '__main__':
    app.run(debug=True)
