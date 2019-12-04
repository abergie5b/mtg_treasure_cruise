import datetime as dt
import requests
import asyncio
import aiohttp
#from database import Price, Card

URL = 'https://api.mtgstocks.com/'
MAX_PRINT = 52431

class _Price(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class _Card(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

async def get_json(url):
    connector = aiohttp.TCPConnector(limit=100)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url) as response:
            return await response.json()

async def get_print(print_id):
    return await get_json(URL + f'prints/{str(print_id)}')

async def get_prices(print_id):
    return await get_json(URL + f'prints/{str(print_id)}/prices')

async def get_price(print_id):
    async def get_field(print_id, field):
        prices = []
        for row in js[field]:
            price = _Price(card_id=print_id,
                           date=dt.datetime.fromtimestamp(int(row[0])/1000), 
                           price=row[1])
            #print(price, field)
            prices.append(price)
        return prices
    js = await get_prices(print_id)
    if js.get('error'):
        return _Price()
    prices = await asyncio.gather(*[get_field(print_id, 'market'), 
                                    get_field(print_id, 'low')],
                                    get_field(print_id, 'high')],
                                    get_field(print_id, 'avg')],
                                    get_field(print_id, 'foil')],
                                    get_field(print_id, 'market_foil')]
    )
    return prices

async def get_card(print_id):
    js = await get_print(print_id)
    if js.get('error'):
        return _Card()
    all_time_high = js['all_time_high']
    all_time_low = js['all_time_low']
    sets = list(map(lambda x: x['set_name'], js['sets']))
    latest_price_mkm = js['latest_price_mkm']['avg'] if js.get('latest_price_mkm') else None
    latest_price_ck = js['latest_price_ck']['price'] if js.get('latest_price_ck') else None
    latest_price_mm = js['latest_price_mm']['price'] if js.get('latest_price_mm') else None
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

async def fetch_cards(number_of_cards):
    for print_id in range(1, number_of_cards+1):
        card = await get_card(print_id)

async def fetch_prices(number_of_cards):
    for print_id in range(1, number_of_cards+1):
        prices = await get_price(print_id)
        print(prices)

def main(number_of_cards):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        asyncio.gather(*[ fetch_cards(number_of_cards) ])
    )
    loop.close()

def main(number_of_cards):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        asyncio.gather(*[ fetch_prices(number_of_cards) ])
    )
    loop.close()

if __name__ == '__main__':
    main(1)

