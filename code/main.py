from bot4 import BinanceBot
import time
import pandas as pd

demo = True
bnc = BinanceBot(demo)

# Recuperar información de la cuenta
# print(f"getAccount: {bnc.getAccount()}")
# print("time.sleep(2)...")
# time.sleep(2)

# result = bnc.getAssetBalance("ETH")
# print(f"getAssetBalance: {result}")
# print("time.sleep(3)...")
# time.sleep(3)

result = bnc.getTradeFee("BNBBTC")
print(f"getTradeFee: {result}")
print("time.sleep(3)...")
time.sleep(3)

result = bnc.getMyTrades("ETHUSDT")
print(f"getMyTrades: {result}")
print("time.sleep(3)...")
time.sleep(3)

# result = bnc.getAllOrders("ETHUSDT", 10)
# print(f"getAllOrders: {result}")
# print("time.sleep(5)...")
# time.sleep(5)
#
# for item in result:
#    print(item['orderId'])
#    res = bnc.getOrder("ETHUSDT", item['orderId'])
#    print(f"getOrder: {res}")
#    print("time.sleep(5)...")
#    time.sleep(5)


# for item in result:
#    print(item['orderId'])
#    res = bnc.cancelOrder("ETHUSDT", item['orderId'])
#    print(f"cancelOrder: {res}")
#    print("time.sleep(5)...")
#    time.sleep(5)

# print(f"futuresAccountBalance: {bnc.futuresAccountBalance()}")

# print(f"getMarginAccount: {bnc.getMarginAccount()}")

# result = bnc.getSymbolTicker("ETHUSDT")
# print(f"getSymbolTicker: {result}")
# print(result["price"])
#
# print("time.sleep(3)...")
# time.sleep(3)

# result = bnc.getAvgPrice("ETHUSDT")
# print(f"getAvgPrice: {result}")
# print(result["price"])
#
# print("time.sleep(3)...")
# time.sleep(3)


# result = bnc.createTestOrder(
#    "ETHUSDT", "BUY", "LIMIT", "GTC", 100, "200")
# print(f"createTestOrder: {result}")

# result = bnc.getSymbolInfo(
#    "ETHUSDT")
# print basico
# print(f"getSymbolInfo: {result}")
#
# recorrer los filtros
# for item in result['filters']:
#    print(item)

# pandas
# new = pd.DataFrame.from_dict(result['filters'])
# new.head()
# print(new)

# {'filterType': 'PERCENT_PRICE_BY_SIDE',
# 'bidMultiplierUp': '5',1
# 'bidMultiplierDown': '0.2',
# 'askMultiplierUp': '5',
# 'askMultiplierDown': '0.2',
# 'avgPriceMins': 5}

# print("time.sleep(2)...")
# time.sleep(2)
#
# result = bnc.createOrder(
#    "ETHUSDT", "BUY", "LIMIT", "GTC", 10.00000000, "500.00000000")
# print(f"createOrder: {result}")
