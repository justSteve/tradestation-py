import requests

url = "https://api.tradestation.com/v3/brokerage/accounts/61999124,68910124/orders"

headers = {"Authorization": "Bearer TOKEN"}

response = requests.request("GET", url, headers=headers)

print(response.text)