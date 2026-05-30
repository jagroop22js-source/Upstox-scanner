import requests

url = "https://assets.upstox.com/market-quote/instruments/exchange/NSE.json"

try:
    r = requests.get(url, timeout=20)

    print("STATUS:", r.status_code)

    if r.status_code == 200:
        data = r.json()

        print("TOTAL RECORDS:", len(data))
        print(data[0])

    else:
        print("Response:")
        print(r.text[:500])

except Exception as e:
    print("ERROR:", e)
