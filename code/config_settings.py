import os
from dotenv import load_dotenv


class Get_Params:
    BINANCEAPIKEY = None
    BINANCEAPISECRET = None
    BINANCEAPIURLDEMO = None

    def __init__(self):
        load_dotenv()

        self.BINANCEAPIKEY = os.environ['BINANCE_API_KEY']
        self.BINANCEAPISECRET = os.environ['BINANCE_API_SECRET']
        self.BINANCEAPIURLDEMO = os.environ['BINANCE_API_URL_DEMO']
