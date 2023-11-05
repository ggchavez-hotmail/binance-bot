from pprint import pprint
import config
from binance.client import Client
from binance.enums import *

client = Client(config.API_KEY, config.API_SECRET, tld='com')
symbolTicker = 'BTCUSDT'
symbolPrice = 0
ma20 = 0

monedaFIAT = 0.0 #Cantidad de la moneda a intercambiar existente en la billetera
unidadFIAT = 0.0
#monedaIntercambio = 5.0
monedaIntercambio = 0.00039336 #Cantidad de la moneda a intercambiar existente en la billetera
unidadIntercambio = 0.0

maximoOperaciones = 5
indicadorVentasRestantes = maximoOperaciones
indicadorComprasRestantes = 0

cantCompra = 0
cantVenta = 0
margenCompra=0.98
margenVenta=1.02
comisionBinanceCompra=1.00075
comisionBinanceVenta=0.99925
cantidadParaPromedio = 15

ultimoKline = 0.0

klines = client.get_historical_klines(symbolTicker, Client.KLINE_INTERVAL_1MINUTE, "7 days ago UTC")
print(len(klines))

for i in range(cantidadParaPromedio,len(klines)):
    suma = 0.0
    promedio = 0.0
    criterioCompra = 0.0
    criterioVenta = 0.0
    valorSiVendo = 0.0
    valorSiCompro = 0.0

    itemActualKline = float(klines[i][4]) #4 es el precio
    
    for j in range(i-cantidadParaPromedio,i):
        suma = suma + float(klines[j][4]) #4 es el precio

    promedio = suma / (cantidadParaPromedio)
    print("--------------inicio-----------------")
    print("itemActualKline:" + str(itemActualKline))
    print("suma           :" + str(suma))
    print("promedio       :" + str(promedio))

    criterioCompra = promedio * margenCompra
    criterioVenta = promedio * margenVenta
    
    print("criterioCompra:" + str(criterioCompra))
    print("criterioVenta :" + str(criterioVenta))

    if (monedaIntercambio > 0 and indicadorVentasRestantes > 0):
        unidadIntercambio =  monedaIntercambio / indicadorVentasRestantes

    if (monedaFIAT > 0 and indicadorComprasRestantes > 0):
        unidadFIAT =  monedaFIAT / indicadorComprasRestantes

    
    print("monedaIntercambio :" + str(monedaIntercambio))
    print("monedaFIAT        :" + str(monedaFIAT))
    print("unidadIntercambio :" + str(unidadIntercambio))
    print("unidadFIAT        :" + str(unidadFIAT))

    valorSiVendo = unidadIntercambio * ( itemActualKline * comisionBinanceVenta )
    valorSiCompro = unidadFIAT / ( itemActualKline * comisionBinanceCompra )

    print("valorSiVendo        :" + str(valorSiVendo))
    print("valorSiCompro       :" + str(valorSiCompro))

    valorComparativoVenta = valorSiVendo / ( itemActualKline * comisionBinanceCompra )
    valorComparativoCompra = valorSiCompro * ( itemActualKline * comisionBinanceVenta )

    print("valorComparativoVenta        :" + str(valorComparativoVenta))
    print("valorComparativoCompra       :" + str(valorComparativoCompra))

    #if ( itemActualKline > criterioVenta and valorComparativoVenta > unidadIntercambio and 0 < indicadorVentasRestantes <= maximoOperaciones ):
    if ( itemActualKline > criterioVenta and 0 < indicadorVentasRestantes <= maximoOperaciones ):
        #venta
        indicadorVentasRestantes = indicadorVentasRestantes - 1
        indicadorComprasRestantes = indicadorComprasRestantes + 1
        cantVenta = cantVenta + 1
        monedaFIAT = monedaFIAT + valorSiVendo
        monedaIntercambio = monedaIntercambio - unidadIntercambio
        print("Vendi        :" + str(valorSiVendo))
    #if ( itemActualKline < criterioCompra and valorComparativoCompra > unidadFIAT and 0 < indicadorComprasRestantes <= maximoOperaciones ):
    if ( itemActualKline < criterioCompra and 0 < indicadorComprasRestantes <= maximoOperaciones ):
        #compra
        indicadorComprasRestantes = indicadorComprasRestantes - 1
        indicadorVentasRestantes = indicadorVentasRestantes + 1
        cantCompra = cantCompra + 1
        monedaFIAT = monedaFIAT - unidadFIAT
        monedaIntercambio = monedaIntercambio + valorSiCompro
        print("Compre        :" + str(valorSiCompro))
    
    #print("----------------fin-------------------")
    ultimoKline = itemActualKline

print("Moneda FIAT:" + str(monedaFIAT + (monedaIntercambio * ultimoKline * comisionBinanceVenta)))
print("Compras:" + str(cantCompra))
print("Ventas :" + str(cantVenta))
