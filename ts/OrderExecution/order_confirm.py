import requests

url = "https://api.tradestation.com/v3/orderexecution/orderconfirm"

payload = {
    "AccountID": "123456782",
    "Symbol": "MSFT",
    "Quantity": "10",
    "OrderType": "Market",
    "TradeAction": "BUY",
    "TimeInForce": {"Duration": "DAY"},
    "Route": "Intelligent"
}
headers = {
    "content-type": "application/json",
    "Authorization": "Bearer TOKEN"
}

response = requests.request("POST", url, json=payload, headers=headers)

print(response.text)