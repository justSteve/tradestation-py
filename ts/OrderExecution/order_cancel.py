import requests

url = "https://api.tradestation.com/v3/orderexecution/orders/123456789"

headers = {"Authorization": "Bearer TOKEN"}

response = requests.request("DELETE", url, headers=headers)

print(response.text)