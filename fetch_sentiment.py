import requests

response = requests.get('https://api.alternative.me/fng/?limit=10')
data = response.json()

for entry in data['data']:
    print(entry['timestamp'], '-', entry['value'], '-', entry['value_classification'])