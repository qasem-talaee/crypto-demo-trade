import requests
import time

class API:
    
    def historical(self, market, start_date):
        now = time.time()
        try:
            data = requests.get("https://api.coingecko.com/api/v3/coins/{market}/market_chart/range?vs_currency=usd&from={start_time}&to={now}".format(market=market, start_time=start_date, now=now))
        except:
            return 0
        else:
            data = data.json()['prices']
            result = []
            for i in range(len(data)):
                result.append(float(data[i][1]))
            return result
    
    def get_kline(self, market):
        try:
            data = requests.get("https://api.coingecko.com/api/v3/simple/price?ids={market}&vs_currencies=usd".format(market=market))
        except:
            return 0
        else:
            data = data.json()
            return data[market]['usd']    
    
    def get_list(self):
        try:
            data = requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd")
        except:
            return 0
        else:
            data = data.json()
            coin = dict()
            for i in range(len(data)):
                coin[data[i]['id']] = data[i]['symbol'].upper() + 'USDT'
            return coin