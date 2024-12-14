import requests

url = "https://api.tradestation.com/v3/marketdata/options/riskreward"

payload = {
    "SpreadPrice": 0.1,
    "Legs": [
        {
            "Symbol": "string",
            "Quantity": 0,
            "TradeAction": "BUY"
        }
    ]
}
headers = {
    "content-type": "application/json",
    "Authorization": "Bearer TOKEN"
}

response = requests.request("POST", url, json=payload, headers=headers)

print(response.text)