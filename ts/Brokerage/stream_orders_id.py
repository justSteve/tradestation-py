import requests

url = "https://api.tradestation.com/v3/brokerage/stream/accounts/61999124,68910124/orders/812767578,812941051"

headers = {"Authorization": "Bearer TOKEN"}

response = requests.request("GET", url, headers=headers, stream=True)

for line in response.iter_lines():
    if line:
        print(line)