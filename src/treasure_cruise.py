import datetime as dt
import requests
#from database import Price, Card

URL = 'https://api.mtgstocks.com/'
MAX_PRINT = 52431

class _Card(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

def get_json(url):
    resp = requests.get(url)
    js = resp.json()
    return js

def get_print(print_id):
    return get_json(URL + f'prints/{str(print_id)}')

def get_prices(print_id):
    return get_json(URL + f'prints/{str(print_id)}/prices')

def get_card(print_id):
    js = get_print(print_id)
    all_time_high = js['all_time_high']
    all_time_low = js['all_time_low']
    sets = list(map(lambda x: x['set_name'], js['sets']))
    latest_price_mkm = js['latest_price_mkm']['avg'] if js['latest_price_mkm'] else None
    latest_price_ck = js['latest_price_ck']['avg'] if js['latest_price_ck'] else None
    latest_price_mm = js['latest_price_mm']['avg'] if js['latest_price_mm'] else None
    card_set = js['card_set']['name'] if js['card_set'] else None
    latest_price = js['latest_price']['avg'] if js['latest_price'] else None
    card = js['card']
    splitcost = ''.join(card['splitcost']) if isinstance(card['splitcost'], list) else None
    card = _Card(id=js['id'],
                 name=js['name'],
                 foil=js['foil'],
                 tcg_id=js['tcg_id'],
                 tcg_url=js['tcg_url'],
                 mkm_id=js['mkm_id'],
                 mkm_url=js['mkm_url'],
                 rarity=js['rarity'],
                 all_time_high_price=all_time_high['avg'],
                 all_time_high_date=dt.datetime.fromtimestamp(int(all_time_high['date'])/1000),
                 all_time_low_price=all_time_low['avg'],
                 all_time_low_date=dt.datetime.fromtimestamp(int(all_time_low['date'])/1000),
                 multiverse_id=js['multiverse_id'],
                 latest_price_mkm=latest_price_mkm,
                 latest_price_ck=latest_price_ck,
                 latest_price_mm=latest_price_mm,
                 icon_class=js['icon_class'],
                 image=js['image'],
                 image_flip=js['image_flip'],
                 flip=js['flip'],
                 legal=js['legal'],
                 card_set=card_set,
                 latest_price=latest_price,
                 sets='|'.join(sets),
                 # Card Keys
                 oracle=card['oracle'],
                 cost=card['cost'],
                 splitcost=splitcost,
                 cmc=card['cmc'],
                 pwrtgh=card['pwrtgh'],
                 supertype=card['supertype'],
                 reserved=card['reserved'],
                 card_type=card['card_type'],
                 # Timestamp
                 updated_at=dt.datetime.now()
    )
    return card

if __name__ == '__main__':
    card = get_card(20765)
    for k,v in card.items():
        print(k, v)

