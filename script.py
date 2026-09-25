import csv
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

LIMIT = 1000
REQUEST_DELAY_SECONDS = 12
RATE_LIMIT_WAIT_SECONDS = 60

example_ticker = {
    'ticker': 'GLAS',
    'name': 'Glass House Brands Inc.',
    'market': 'stocks',
    'locale': 'us',
    'primary_exchange': 'XNYS',
    'type': 'CS',
    'active': True,
    'currency_name': 'usd',
    'cik': '0001848731',
    'composite_figi': 'BBG00PQNR3J9',
    'share_class_figi': 'BBG00PH81Z90',
    'last_updated_utc': '2026-09-25T06:11:21.225211668Z'
}


def fetch_json(url):
    while True:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 429 or data.get('status') == 'ERROR':
            error = data.get('error', response.text)
            print(f'rate limited, waiting {RATE_LIMIT_WAIT_SECONDS}s: {error}')
            time.sleep(RATE_LIMIT_WAIT_SECONDS)
            continue
        if 'results' not in data:
            raise RuntimeError(f'unexpected API response: {data}')
        return data


url = f'https://api.massive.com/v3/reference/tickers?market=stocks&active=true&order=asc&limit={LIMIT}&sort=ticker&apiKey={POLYGON_API_KEY}'
tickers = []

data = fetch_json(url)
tickers.extend(data['results'])

while 'next_url' in data:
    print('requesting next page', data['next_url'])
    time.sleep(REQUEST_DELAY_SECONDS)
    data = fetch_json(data['next_url'] + f'&apiKey={POLYGON_API_KEY}')
    tickers.extend(data['results'])

fieldnames = list(example_ticker.keys())
output_path = 'tickers.csv'

with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    for ticker in tickers:
        writer.writerow({field: ticker.get(field, '') for field in fieldnames})

print(f'wrote {len(tickers)} tickers to {output_path}')
