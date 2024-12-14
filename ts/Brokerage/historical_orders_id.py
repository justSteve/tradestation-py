import requests

url = "https://api.tradestation.com/v3/brokerage/accounts/61999124,68910124/historicalorders/123456789,286179863"

querystring = {"since":"2006-01-13"}

headers = {"Authorization": "Bearer TOKEN"}

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)