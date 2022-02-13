import requests
import time
import json

class API:
    
    def historical(self, market, start_date):
        flag = True
        while flag:
            now = time.time()
            try:
                data = requests.get("https://api.coingecko.com/api/v3/coins/{market}/market_chart/range?vs_currency=usd&from={start_time}&to={now}".format(market=market, start_time=start_date, now=now))
            except:
                print('Try again')
            else:
                if data.status_code == 200 and ('application/json' in data.headers.get('content-type')):
                    data = data.json()['prices']
                    result = []
                    for i in range(len(data)):
                        result.append(float(data[i][1]))
                    flag = False
                    return result
                else:
                    time.sleep(2)
    
    def get_kline(self, market):
        flag = True
        while flag:
            try:
                data = requests.get("https://api.coingecko.com/api/v3/simple/price?ids={market}&vs_currencies=usd".format(market=market))
            except:
                print('Try again')
            else:
                if data.status_code == 200 and ('application/json' in data.headers.get('content-type')):
                    data = data.json()
                    flag = False
                    return data[market]['usd']
                else:
                    time.sleep(2)
    
    def get_list(self):
        try:
            data = requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd")
        except:
            return 0
        else:
            if data.status_code == 200 and ('application/json' in data.headers.get('content-type')):
                data = data.json()
                coin = dict()
                for i in range(len(data)):
                    coin[data[i]['id']] = data[i]['symbol'].upper() + 'USDT'
                return coin