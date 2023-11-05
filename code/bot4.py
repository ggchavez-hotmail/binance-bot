from pprint import pprint
from re import S
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

class BinanceBot():
    __client = None
    symbolTicker = None
    interval = None
    start_str = None
    klines = None
    resultado = None
    grafico = None
    
    #valores de las senales para el grafico basico
    sma3 = True
    sma6 = True
    sma9 = True
    dpo = True
    precioCompra = True
    precioVenta = True
    rsiPrecioCompra = True
    rsiPrecioVenta = True
    stochPrecioCompra = True
    stochPrecioVenta = True
    bollingerUp = True
    bollingerMi = True
    bollingerLo = True
    
    #valores de las senales para el grafico indicadores
    rsi11 = True
    stochSlowk = True
    stochSlowd = True
    stdDev = True

    def __init__(self):
        self.__client = Client(config.API_KEY, config.API_SECRET, tld='com')
        self.resultado = None
        self.grafico = None

    def get_historical_klines(self, symbolTicker, interval, start_str):
        try:
            self.symbolTicker = symbolTicker        
            self.interval = interval
            self.start_str = start_str
            self.klines = np.array(self.__client.get_historical_klines(self.symbolTicker, self.interval, self.start_str))
        except ValueError:
            print("Error al recuperar datos: get_historical_klines")
            self.klines = np.nan
        return self.klines

    def get_resultado(self):
        try:
            data = pd.DataFrame(self.klines.reshape(-1, 12), dtype=float, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time','quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
            self.resultado = pd.DataFrame()
            self.resultado['Cierre'] = data['close']
            #self.resultado['Fecha_Cierre'] = data['close_time']
            self.resultado['SMA3'] = ta.SMA(data['close'], 3)  # media movil simple 3
            self.resultado['SMA6'] = ta.SMA(data['close'], 6)  # media movil simple 6
            self.resultado['SMA9'] = ta.SMA(data['close'], 9)  # media movil simple 9
            self.resultado['SMA11'] = ta.SMA(data['close'], 11)  # media movil simple 11
            self.resultado['upper_band'], self.resultado['middle_band'], self.resultado['lower_band'] = ta.BBANDS(data['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)  # bandas de Bollinger
            self.resultado['RSI11'] = ta.RSI(data['close'], timeperiod=11)  # indicador RSI
            self.resultado['stoch_slowk'], self.resultado['stoch_slowd']  = ta.STOCH(data['high'], data['low'], data['close'], fastk_period=6, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)  # indicador Stochastic
            self.resultado['STDDEV'] = ta.STDDEV(data['close'], timeperiod=20)  # desviacion estandar

            senales = self.__senal(self.resultado)

            self.resultado['Compra'] = senales[0]
            self.resultado['Venta'] = senales[1]
            self.resultado['DPO'] = senales[2]
            self.resultado['RSICompra'] = senales[3]
            self.resultado['RSIVenta'] = senales[4]
            self.resultado['STOCHCompra'] = senales[5]
            self.resultado['STOCHVenta'] = senales[6]

            
        except ValueError:
            print("Error al recuperar datos: get_historical_klines")
            self.resultado = pd.DataFrame()
        return self.resultado

    def get_grafico(self, tipo):
        try:            
            # Graficar los datos
            plt.style.use('bmh')  # Estilo cuadriculas
            plt.figure(figsize=(10, 5))
            if (tipo == 'simple'):
                plt.plot(self.resultado['Cierre'], label='Cierre', alpha=0.5)

                if (self.sma3):
                    plt.plot(self.resultado['SMA3'], label='SMA3', alpha=0.3)

                if (self.sma6):    
                    plt.plot(self.resultado['SMA6'], label='SMA6', alpha=0.3)
                
                if (self.sma9):
                    plt.plot(self.resultado['SMA9'], label='SMA9', alpha=0.3)
                    
                if (self.precioCompra):
                    plt.scatter(self.resultado.index, self.resultado['Compra'],label='Precio Compra', marker='^', color='green')

                if (self.precioVenta):
                    plt.scatter(self.resultado.index, self.resultado['Venta'],label='Precio Venta', marker='v', color='red')

                if (self.dpo):    
                    plt.scatter(self.resultado.index, self.resultado['DPO'], label='DPO',marker='*', color='violet', alpha=0.5)

                if (self.rsiPrecioCompra):
                    plt.scatter(self.resultado.index, self.resultado['RSICompra'],label='RSI Precio Compra', marker='^', color='blue', alpha=0.5)

                if (self.rsiPrecioVenta):
                    plt.scatter(self.resultado.index, self.resultado['RSIVenta'],label='RSI Precio Venta', marker='v', color='orange', alpha=0.5)

                if (self.stochPrecioCompra):
                    plt.scatter(self.resultado.index, self.resultado['STOCHCompra'],label='STOCH Precio Compra', marker='^', color='blue', alpha=0.2)

                if (self.stochPrecioVenta):
                    plt.scatter(self.resultado.index, self.resultado['STOCHVenta'],label='STOCH Precio Venta', marker='v', color='orange', alpha=0.2)

                if (self.bollingerLo):
                    plt.plot(self.resultado['lower_band'], label='Bollinger LO', alpha = 0.3)

                if (self.bollingerMi):
                    plt.plot(self.resultado['middle_band'], label='Bollinger MI', alpha = 0.3)
                
                if (self.bollingerUp):
                    plt.plot(self.resultado['upper_band'], label='Bollinger UP', alpha = 0.3)
                
            elif (tipo == 'indicadores'):
                if (self.rsi11):
                    plt.plot(self.resultado['RSI11'], label='RSI11', alpha=0.5)
                if (self.stochSlowk):
                    plt.plot(self.resultado['stoch_slowk'], label='stoch_slowk', alpha=0.3)
                if (self.stochSlowd):
                    plt.plot(self.resultado['stoch_slowd'], label='stoch_slowd', alpha=0.3)
                if (self.stdDev):
                    plt.plot(self.resultado['STDDEV'], label='STDDEV', alpha=0.3)

            plt.legend(loc='upper left')
            
            plt.grid(True)
            plt.title('Cierre de ' + self.symbolTicker)
            plt.xlabel('Tiempo: ' + self.start_str + ' en intervalos de ' + self.interval)
            plt.ylabel('Precios USD')
            plt.xticks(rotation=30, size=5)
            plt.yticks(size=5)
            plt.tight_layout()

            self.grafico = plt.gcf()
            
        except ValueError:
            self.grafico = plt.gcf()

        return self.grafico

    def __senal(self, data):
        compra = []
        venta = []
        detrendedPriceOscillator = []
        rsiTendenciaCompra = []
        rsiTendenciaVenta = []
        stochTendenciaCompra = []
        stochTendenciaVenta = []
        condicion = 0
        senalCompra = False
        senalVenta = False
        for intervalo in range(len(data)):
            if data['SMA3'][intervalo] > data['SMA6'][intervalo] and data['SMA6'][intervalo] > data['SMA9'][intervalo] :
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
            #analisis de tendencia de RSI
            if data['RSI11'][intervalo] > 70.00:
                rsiTendenciaCompra.append(data['Cierre'][intervalo])
            else:
                rsiTendenciaCompra.append(np.nan)

            if data['RSI11'][intervalo] < 30.00:
                rsiTendenciaVenta.append(data['Cierre'][intervalo])
            else:
                rsiTendenciaVenta.append(np.nan)

            #analisis de tendencia de Stochastic
            if data['stoch_slowk'][intervalo] < 20 and data['stoch_slowd'][intervalo] < 20:
                senalCompra = True
            else:
                senalCompra = False

            if senalCompra and data['stoch_slowk'][intervalo] < data['stoch_slowd'][intervalo] and data['stoch_slowk'][intervalo] < 20:
                stochTendenciaCompra.append(data['Cierre'][intervalo])
            else:
                stochTendenciaCompra.append(np.nan)

            if data['stoch_slowk'][intervalo] > 80 and data['stoch_slowd'][intervalo] > 80:
                senalVenta = True
            else:
                senalVenta = False

            if senalVenta and data['stoch_slowk'][intervalo] > data['stoch_slowd'][intervalo] and data['stoch_slowk'][intervalo] > 80:
                stochTendenciaVenta.append(data['Cierre'][intervalo])
            else:
                stochTendenciaVenta.append(np.nan)
                
        return (compra, venta, detrendedPriceOscillator, rsiTendenciaCompra, rsiTendenciaVenta, stochTendenciaCompra, stochTendenciaVenta)


    def setSenalGraficoBasico(self, sma3, sma6, sma9, dpo, precioCompra, precioVenta, rsiPrecioCompra, rsiPrecioVenta, stochPrecioCompra, stochPrecioVenta, bollingerUp, bollingerMi, bollingerLo):
        self.sma3 = sma3
        self.sma6 = sma6
        self.sma9 = sma9
        self.dpo = dpo
        self.precioCompra = precioCompra
        self.precioVenta = precioVenta
        self.rsiPrecioCompra = rsiPrecioCompra
        self.rsiPrecioVenta = rsiPrecioVenta
        self.stochPrecioCompra = stochPrecioCompra
        self.stochPrecioVenta = stochPrecioVenta
        self.bollingerUp = bollingerUp
        self.bollingerMi = bollingerMi
        self.bollingerLo = bollingerLo

    def setSenalGraficoIndicadores(self, rsi11, stochSlowk, stochSlowd, stdDev):
        self.rsi11 = rsi11
        self.stochSlowk = stochSlowk
        self.stochSlowd = stochSlowd
        self.stdDev = stdDev

            