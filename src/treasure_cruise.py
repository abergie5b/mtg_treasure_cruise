import requests

URL = 'https://api.mtgstocks.com/'
MAX_PRINT = 52431

def get_json(url):
    resp = requests.get(url)
    js = resp.json()
    return js

def get_print(print_id):
    '''
    return Dict -> keys(['id', 'name', 'foil', 'tcg_id', 'tcg_url', 'mkm_id', 'mkm_url', 'rarity', 'all_time_high', 'all_time_low', 'multiverse_id', 'latest_price_mkm', 'latest_price_ck', 'latest_price_mm', 'icon_class', 'image', 'image_flip', 'flip', 'legal', 'card_set', 'card', 'latest_price', 'sets'])
    card -> card {'id': 7655, 'name': 'Raging Kavu', 'oracle': 'Flash\nHaste', 'cost': 'RG', 'splitcost': ['1', 'r', 'g'], 'splitcost2': None, 'cmc': 3, 'pwrtgh': '(3/1)', 'supertype': 'Creature', 'subtype': 'Kavu', 'reserved': False, 'lowest_print': 7838, 'legal': {'legacy': 'legal', 'modern': 'not legal', 'pauper': 'not legal', 'vintage': 'legal', 'frontier': 'not legal', 'standard': 'not legal', 'commander': 'legal', 'pioneer': 'not legal'}, 'card_type': 'Creature'}
    '''
    return get_json(URL + f'prints/{str(print_id)}')

def get_prices(print_id):
    '''
    return Dict -> keys(['low', 'avg', 'high', 'foil', 'market', 'market_foil'])
    '''
    return get_json(URL + f'prints/{str(print_id)}/prices')

if __name__ == '__main__':
    p = get_print(20765)
    for k,v in p.items():
        print(k, v)
    print(p.keys())

