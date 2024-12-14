import requests

url = "https://api.tradestation.com/v3/marketdata/symbols/MSFT,BTCUSD"

headers = {"Authorization": "Bearer TOKEN"}

response = requests.request("GET", url, headers=headers)

print(response.text)