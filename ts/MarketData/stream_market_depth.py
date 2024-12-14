import requests

url = "https://api.tradestation.com/v3/marketdata/stream/marketdepth/quotes/MSFT"

headers = {"Authorization": "Bearer TOKEN"}

response = requests.request("GET", url, headers=headers, stream=True)

for line in response.iter_lines():
    if line:
        print(line)