from pprint import pprint
from re import S
# from tkinter import E
from config_settings import Get_Params
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException
##############
import talib as ta
# import btalib as ta ver los comandos que deben cambiarse del talib
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

    # valores de las senales para el grafico basico
    smasl = True
    smame = True
    smahi = True
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

    # valores de las senales para el grafico indicadores
    rsi = True
    stochSlowk = True
    stochSlowd = True
    stdDev = True

    def __init__(self, demo):
        params = Get_Params()

        self.__client = Client(params.BINANCEAPIKEY,
                               params.BINANCEAPISECRET, tld='com')
        if (demo):
            self.__client.API_URL = params.BINANCEAPIURLDEMO
        self.resultado = None
        self.grafico = None

    def get_historical_klines(self, symbolTicker, interval, start_str):
        try:
            self.symbolTicker = symbolTicker
            self.interval = interval
            self.start_str = start_str
            self.klines = np.array(self.__client.get_historical_klines(
                self.symbolTicker, self.interval, self.start_str))
        except ValueError:
            print("Error al recuperar datos: get_historical_klines")
            self.klines = np.nan
        return self.klines

    def get_resultado(self, smaslow, smamedia, smahigh, rsi):
        try:
            data = pd.DataFrame(self.klines.reshape(-1, 12), dtype=float, columns=['open_time', 'open', 'high', 'low', 'close', 'volume',
                                'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
            self.resultado = pd.DataFrame()
            # obtener cierre
            self.resultado['Cierre'] = data['close']
            # medias moviles
            self.resultado['SMASL'] = ta.SMA(
                data['close'], smaslow)  # media movil simple lenta
            self.resultado['SMAME'] = ta.SMA(
                data['close'], smamedia)  # media movil simple media
            self.resultado['SMAHI'] = ta.SMA(
                data['close'], smahigh)  # media movil simple rapida

            self.resultado['SMA11'] = ta.SMA(
                data['close'], 11)  # media movil simple 11
            # bandas de Bollinger
            self.resultado['upper_band'], self.resultado['middle_band'], self.resultado['lower_band'] = ta.BBANDS(
                data['close'], timeperiod=smahigh, nbdevup=2, nbdevdn=2, matype=0)
            # indicador RSI
            self.resultado['RSI'] = ta.RSI(
                data['close'], timeperiod=rsi)
            # indicador Estocastico
            self.resultado['stoch_slowk'], self.resultado['stoch_slowd'] = ta.STOCH(
                data['high'], data['low'], data['close'], fastk_period=smahigh, slowk_period=smaslow, slowk_matype=0, slowd_period=smaslow, slowd_matype=0)  # indicador Stochastic
            # desviacion estandar
            self.resultado['STDDEV'] = ta.STDDEV(
                data['close'], timeperiod=smahigh)

            # realizar los calculos sobre los datos recolectados
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

                if (self.smasl):
                    plt.plot(self.resultado['SMASL'], label='SMASL', alpha=0.3)

                if (self.smame):
                    plt.plot(self.resultado['SMAME'], label='SMAME', alpha=0.3)

                if (self.smahi):
                    plt.plot(self.resultado['SMAHI'], label='SMAHI', alpha=0.3)

                if (self.precioCompra):
                    plt.scatter(
                        self.resultado.index, self.resultado['Compra'], label='Precio Compra', marker='^', color='green')

                if (self.precioVenta):
                    plt.scatter(
                        self.resultado.index, self.resultado['Venta'], label='Precio Venta', marker='v', color='red')

                if (self.dpo):
                    plt.scatter(
                        self.resultado.index, self.resultado['DPO'], label='DPO', marker='*', color='violet', alpha=0.5)

                if (self.rsiPrecioCompra):
                    plt.scatter(self.resultado.index, self.resultado['RSICompra'],
                                label='RSI Precio Compra', marker='^', color='blue', alpha=0.5)

                if (self.rsiPrecioVenta):
                    plt.scatter(
                        self.resultado.index, self.resultado['RSIVenta'], label='RSI Precio Venta', marker='v', color='orange', alpha=0.5)

                if (self.stochPrecioCompra):
                    plt.scatter(self.resultado.index, self.resultado['STOCHCompra'],
                                label='STOCH Precio Compra', marker='^', color='blue', alpha=0.2)

                if (self.stochPrecioVenta):
                    plt.scatter(self.resultado.index, self.resultado['STOCHVenta'],
                                label='STOCH Precio Venta', marker='v', color='orange', alpha=0.2)

                if (self.bollingerLo):
                    plt.plot(self.resultado['lower_band'],
                             label='Bollinger LO', alpha=0.3)

                if (self.bollingerMi):
                    plt.plot(self.resultado['middle_band'],
                             label='Bollinger MI', alpha=0.3)

                if (self.bollingerUp):
                    plt.plot(self.resultado['upper_band'],
                             label='Bollinger UP', alpha=0.3)

            elif (tipo == 'indicadores'):
                if (self.rsi):
                    plt.plot(self.resultado['RSI'], label='RSI', alpha=0.5)
                if (self.stochSlowk):
                    plt.plot(self.resultado['stoch_slowk'],
                             label='stoch_slowk', alpha=0.3)
                if (self.stochSlowd):
                    plt.plot(self.resultado['stoch_slowd'],
                             label='stoch_slowd', alpha=0.3)
                if (self.stdDev):
                    plt.plot(self.resultado['STDDEV'],
                             label='STDDEV', alpha=0.3)

            plt.legend(loc='upper left')

            plt.grid(True)
            plt.title('Cierre de ' + self.symbolTicker)
            plt.xlabel('Tiempo: ' + self.start_str +
                       ' en intervalos de ' + self.interval)
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
        condicion = 1
        condicionRSI = 1
        condicionStoch = 1
        senalCompra = False
        senalVenta = False
        for intervalo in range(len(data)):

            # analisis de tendencia de Stochastic
            if data['stoch_slowk'][intervalo] < 30 and data['stoch_slowd'][intervalo] < 30:
                senalCompra = True
            else:
                senalCompra = False

            if data['stoch_slowk'][intervalo] > 70 and data['stoch_slowd'][intervalo] > 70:
                senalVenta = True
            else:
                senalVenta = False

            if senalCompra and data['stoch_slowk'][intervalo] < data['stoch_slowd'][intervalo] and data['stoch_slowk'][intervalo] < 30:
                if condicionStoch != 1:
                    stochTendenciaCompra.append(data['Cierre'][intervalo])
                    stochTendenciaVenta.append(np.nan)
                    condicionStoch = 1
                else:
                    stochTendenciaCompra.append(np.nan)
                    stochTendenciaVenta.append(np.nan)
            elif senalVenta and data['stoch_slowk'][intervalo] > data['stoch_slowd'][intervalo] and data['stoch_slowk'][intervalo] > 70:
                if condicionStoch != -1:
                    stochTendenciaVenta.append(data['Cierre'][intervalo])
                    stochTendenciaCompra.append(np.nan)
                    condicionStoch = -1
                else:
                    stochTendenciaVenta.append(np.nan)
                    stochTendenciaCompra.append(np.nan)
            else:
                stochTendenciaVenta.append(np.nan)
                stochTendenciaCompra.append(np.nan)
                condicionStoch = 0

            # analisis de tendencia de RSI
            if data['RSI'][intervalo] < 30.00:
                if condicionRSI != 1:
                    rsiTendenciaCompra.append(data['Cierre'][intervalo])
                    rsiTendenciaVenta.append(np.nan)
                    condicionRSI = 1
                else:
                    rsiTendenciaCompra.append(np.nan)
                    rsiTendenciaVenta.append(np.nan)
            elif data['RSI'][intervalo] > 70.00:
                if condicionRSI != -1:
                    rsiTendenciaVenta.append(data['Cierre'][intervalo])
                    rsiTendenciaCompra.append(np.nan)
                    condicionRSI = -1
                else:
                    rsiTendenciaVenta.append(np.nan)
                    rsiTendenciaCompra.append(np.nan)
            else:
                rsiTendenciaCompra.append(np.nan)
                rsiTendenciaVenta.append(np.nan)
                condicionRSI = 0

            # analisis de SMA
            if data['SMASL'][intervalo] < data['SMAME'][intervalo] and data['SMAME'][intervalo] < data['SMAHI'][intervalo]:
                if condicion != 1:
                    compra.append(data['Cierre'][intervalo])
                    venta.append(np.nan)
                    condicion = 1
                else:
                    venta.append(np.nan)
                    compra.append(np.nan)
            elif data['SMASL'][intervalo] > data['SMAME'][intervalo] and data['SMAME'][intervalo] > data['SMAHI'][intervalo]:
                if condicion != -1:
                    venta.append(data['Cierre'][intervalo])
                    compra.append(np.nan)
                    condicion = -1
                else:
                    compra.append(np.nan)
                    venta.append(np.nan)
            else:
                compra.append(np.nan)
                venta.append(np.nan)
                condicion = 0

            # Para eliminarlo hay que ver donde se agrega
            if (data['Cierre'][intervalo] - data['SMA11'][intervalo]) <= 0.0001:
                detrendedPriceOscillator.append(data['Cierre'][intervalo])
            else:
                detrendedPriceOscillator.append(np.nan)

        return (compra, venta, detrendedPriceOscillator, rsiTendenciaCompra, rsiTendenciaVenta, stochTendenciaCompra, stochTendenciaVenta)

    def setSenalGraficoBasico(self, smasl, smame, smahi, dpo, precioCompra, precioVenta, rsiPrecioCompra, rsiPrecioVenta, stochPrecioCompra, stochPrecioVenta, bollingerUp, bollingerMi, bollingerLo):
        self.smasl = smasl
        self.smame = smame
        self.smahi = smahi
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

    def setSenalGraficoIndicadores(self, rsi, stochSlowk, stochSlowd, stdDev):
        self.rsi = rsi
        self.stochSlowk = stochSlowk
        self.stochSlowd = stochSlowd
        self.stdDev = stdDev

    def getAccount(self):
        # get balances for all assets & some account information
        return self.__client.get_account()

    def getAssetBalance(self, asset):
        # get balance for a specific asset only (example:BTC)
        return self.__client.get_asset_balance(asset=asset)

    def getTradeFee(self, simbolo):
        # get fee for one symbol
        return self.__client.get_trade_fee(symbol=simbolo)

    def getMyTrades(self, simbolo):
        # retrieve information about your trades for a particular symbol
        return self.__client.get_my_trades(symbol=simbolo)

    def getAllOrders(self, simbolo, limite):
        # To fetch all your Binance selling or buying orders for a symbol
        return self.__client.get_all_orders(symbol=simbolo, limit=limite)

    def getOrder(self, simbolo, idOrden):
        # You can check the current status of the order you placed
        return self.__client.get_order(symbol=simbolo, orderId=idOrden)

    def cancelOrder(self, simbolo, idOrden):
        # Finally, as the following script demonstrates, you can cancel your Binance order
        return self.__client.cancel_order(symbol=simbolo, orderId=idOrden)

    def futuresAccountBalance(self):
        # get balances for futures account
        return self.__client.futures_account_balance()

    def getMarginAccount(self):
        # get balances for margin account
        return self.__client.get_margin_account()

    def getSymbolTicker(self, simbolo):
        # get latest price from Binance API
        return self.__client.get_symbol_ticker(symbol=simbolo)

    def getSymbolInfo(self, simbolo):
        # get symbol values for a specific filter
        return self.__client.get_symbol_info(symbol=simbolo)

    def getAvgPrice(self, simbolo):
        # get the average price of a symbol
        return self.__client.get_avg_price(symbol=simbolo)

    def createTestOrder(self, simbolo: str, lado: str, tipo: str, tiempo: str, cantidad: float, precio: str):
        # function that allows us to create test orders.
        return self.__client.create_test_order(symbol=simbolo,
                                               side=lado,
                                               type=tipo,
                                               timeInForce=tiempo,
                                               quantity=cantidad,
                                               price=precio)

    def createOrder(self, simbolo: str, lado: str, tipo: str, tiempo: str, cantidad: float, precio: str):
        try:
            resultado = self.__client.create_order(symbol=simbolo,
                                                   side=lado,
                                                   type=tipo,
                                                   timeInForce=tiempo,
                                                   quantity=cantidad,
                                                   price=precio)
            return resultado
        except BinanceAPIException as e:
            # error handling goes here
            return (f"BinanceAPIException: {e}")
        except BinanceOrderException as e:
            # error handling goes here
            return (f"BinanceOrderException: {e}")
