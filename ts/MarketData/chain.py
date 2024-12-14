import requests

url = "https://api.tradestation.com/v3/marketdata/stream/options/chains/AAPL"

headers = {"Authorization": "Bearer TOKEN"}

response = requests.request("GET", url, headers=headers, stream=True)

for line in response.iter_lines():
    if line:
        print(line)