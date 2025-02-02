import requests

BASESCAN_API_URL = "https://api.basescan.org/api"
API_KEY = "1W2NPID3JSDC7QW6EHCDA21ZCT43UMM37J"

def get_recent_transactions_basescan(address, start_block=0, end_block=99999999, sort='desc'):
    params = {
        'module': 'account',
        'action': 'txlist',
        'address': address,
        'startblock': start_block,
        'endblock': end_block,
        'limit': 10,
        'sort': sort,
        'apikey': API_KEY
    }
    response = requests.get(BASESCAN_API_URL, params=params)
    data = response.json()
    
    if data.get('status') == '1' and 'result' in data:
        return data['result']
    else:
        # You can raise an exception or return an empty list as needed
        return []
    

if __name__ == '__main__':
    address = "0x9AC7421Bb573cB84709764D0D8AB1cE759416496"
    transactions = get_recent_transactions_basescan(address)
    print(transactions)