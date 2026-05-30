import requests

url = "https://assets.upstox.com/market-quote/instruments/exchange/NSE.json"

r = requests.get(url)

print("STATUS:", r.status_code)

data = r.json()

print("TOTAL RECORDS:", len(data))
print(data[0])
