import requests

url = "https://api.tradestation.com/v3/brokerage/accounts"

headers = {"Authorization": "Bearer TOKEN"}

response = requests.request("GET", url, headers=headers)

print(response.text)

# {
#   "Accounts": [
#     {
#       "AccountID": "123456789",
#       "Currency": "USD",
#       "Status": "Active",
#       "AccountType": "Cash",
#       "AccountDetail": {
#         "IsStockLocateEligible": false,
#         "EnrolledInRegTProgram": false,
#         "RequiresBuyingPowerWarning": false,
#         "DayTradingQualified": true,
#         "OptionApprovalLevel": 0,
#         "PatternDayTrader": false
#       }
#     },
#     {
#       "AccountID": "123456782",
#       "Currency": "USD",
#       "Status": "Active",
#       "AccountType": "Margin",
#       "AccountDetail": {
#         "IsStockLocateEligible": false,
#         "EnrolledInRegTProgram": true,
#         "RequiresBuyingPowerWarning": true,
#         "DayTradingQualified": true,
#         "OptionApprovalLevel": 1,
#         "PatternDayTrader": false
#       }
#     },
#     {
#       "AccountID": "123456781",
#       "Currency": "USD",
#       "Status": "Active",
#       "AccountType": "Futures"
#     }
#   ]
# }