import requests

url = "https://api.tradestation.com/v3/orderexecution/orders/123456789"

payload = {
    "Quantity": "10",
    "LimitPrice": "132.52"
}
headers = {
    "content-type": "application/json",
    "Authorization": "Bearer TOKEN"
}

response = requests.request("PUT", url, json=payload, headers=headers)

print(response.text)