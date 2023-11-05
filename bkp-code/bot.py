from pprint import pprint
import config
from binance.client import Client
from binance.enums import *
import time
import threading
import math
import csv
import itertools
import datetime

client = Client(config.API_KEY, config.API_SECRET, tld='com')
symbolTicker = 'BTCUSDT'
symbolPrice = 0
ma20 = 0

dineroFinal = 0.0

ma20_local = 0
values = []
sum = 0
cantCompra = 0
margenCompra=0.99
comisionBinanceCompra=1.00075
comisionBinanceVenta=0.99925
margenVenta=1.01
cantVenta = 0
cantidadParaPromedio = 5
q = 5

klines = client.get_historical_klines(symbolTicker, Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
print(len(klines))

for i in range(cantidadParaPromedio + 1,len(klines)):
    sum = 0
    prom = 0
    valorSiCompro = 0.0
    valorSiVendo = 0.0
    criterioCompra = 0.0
    criterioVenta = 0.0

    for j in range(i-cantidadParaPromedio,i):
        sum = sum + float(klines[j][4])

    prom = sum / cantidadParaPromedio
    criterioCompra = prom * margenCompra
    criterioVenta = prom * margenVenta
    valorSiCompro = criterioCompra * comisionBinanceCompra
    valorSiVendo = criterioVenta * comisionBinanceVenta

    if ( float(klines[i][4]) < criterioCompra and 0 <= q < 5 and cantVenta > 0 and dineroFinal > valorSiCompro):
        #compra
        q = q + 1
        cantCompra = cantCompra +1
        dineroFinal = dineroFinal - valorSiCompro
    if ( float(klines[i][4]) > criterioVenta and 0 < q <= 5):
        #venta
        q = q - 1
        cantVenta = cantVenta +1
        dineroFinal = dineroFinal + valorSiVendo

print(dineroFinal)
print(cantCompra)
print(cantVenta)
