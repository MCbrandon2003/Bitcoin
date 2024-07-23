import requests
from main import save_json_file

if __name__ == '__main__':
    ticker = "WIF-USD"
    scope = 'daily'
    url = f"https://tsanghi.com/api/fin/crypto/{scope}?token=1dbee267a6594d4b8947664e41f458ce&ticker={ticker}"
    data = requests.get(url).json()
    print(data)
    save_json_file(data, f"{ticker}_{scope}.json")