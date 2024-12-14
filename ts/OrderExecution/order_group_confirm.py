import requests

url = "https://api.tradestation.com/v3/orderexecution/ordergroupconfirm"

payload = {
    "Type": "OCO",
    "Orders": [
        {
            "AccountID": "123456782",
            "StopPrice": "337",
            "OrderType": "StopMarket",
            "Quantity": "10",
            "Route": "Intelligent",
            "Symbol": "MSFT",
            "TimeInForce": {"Duration": "GTC"},
            "TradeAction": "Buy"
        },
        {
            "AccountID": "123456782",
            "StopPrice": "333",
            "OrderType": "StopMarket",
            "Quantity": "10",
            "Route": "Intelligent",
            "Symbol": "MSFT",
            "TimeInForce": {"Duration": "GTC"},
            "TradeAction": "SellShort"
        }
    ]
}
headers = {
    "content-type": "application/json",
    "Authorization": "Bearer TOKEN"
}

response = requests.request("POST", url, json=payload, headers=headers)

print(response.text)