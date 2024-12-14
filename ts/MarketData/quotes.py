import requests

url = "https://api.tradestation.com/v3/marketdata/stream/options/quotes"

querystring = {"legs[0].Symbol":"MSFT 220916C305"}

headers = {"Authorization": "Bearer TOKEN"}

response = requests.request("GET", url, headers=headers, params=querystring, stream=True)

for line in response.iter_lines():
    if line:
        print(line)