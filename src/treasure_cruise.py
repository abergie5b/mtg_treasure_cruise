from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
import datetime as dt
import requests
import asyncio
import aiohttp
import logging
from typing import *

from database import *

def get_logger() -> logging.Logger:
    logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
            handlers=[logging.StreamHandler(),
                      logging.FileHandler("treasure_cruise.log", mode='w')
                      ],
    )
    return logging.getLogger()

# Globals
logger = get_logger()
URL = 'https://api.mtgstocks.com/'
CONNECTION_STRING = 'postgresql://tc123:tc123@postgres:5432/MTG'
#MAX_PRINT_ID = 52431
# End Globals

# Dummy Models
class _Price(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class _Card(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
# End Dummy Models

# Sync Funcs
def get_json(url:str) -> dict:
    response = requests.get(url)
    return response.json()

def get_card(print_id:int) -> dict:
    return get_json(URL + f'prints/{str(print_id)}')

def get_prices(print_id:int) -> dict:
    return get_json(URL + f'prints/{str(print_id)}/prices')
# End Sync Funcs

# Async Funcs
async def get_json_async(http_session:aiohttp.ClientSession, url:str) -> dict:
    response = await http_session.get(url)
    if response.status == 200:
        js =  await response.json()
        return js
    return {'error': response.text()}

async def js_to_card(js:dict) -> Card:
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
    card = Card(id=js['id'],
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

async def insert_prices_to_db(http_session:aiohttp.ClientSession, db_session:Session, print_id:int) -> dict:
    js = await get_json_async(http_session, URL + f'prints/{str(print_id)}/prices')
    if js.get('error'):
        return _Price()
    prices = {}
    for price_type, Model in zip(['low', 'high', 'avg', 'market', 'foil', 'market_foil'],
                                 [LowPrice, HighPrice, AvgPrice, MarketPrice, FoilPrice, MarketFoilPrice]
                                 ):
        prices[price_type] = []
        rows = js.get(price_type)
        logger.info(f"print_id {print_id}: |{price_type}|count: {len(rows)}|")
        for row in rows:
            price = Model(card_id=print_id,
                          date=dt.datetime.fromtimestamp(int(row[0])/1000), 
                          price=row[1])
            prices[price_type].append(price)
            db_session.add(price)
    # database calls are blocking for now
    db_session.commit()
    return prices

async def insert_card_to_db(http_session:aiohttp.ClientSession, db_session:Session, print_id:int) -> Card:
    url = URL + f'prints/{str(print_id)}'
    js = await get_json_async(http_session, url)
    if js.get('error'):
        return _Card()
    logger.info(f"{url}: {js['name']}|{js['card_set']['name']}")
    card = await js_to_card(js)
    # database calls are blocking for now
    db_session.add(card)
    db_session.commit()
    return card

async def run(func:object, db_session:Session, print_ids:List[int]) -> None:
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=100)) as http_session:
        await asyncio.gather(
                *[ func(http_session, db_session, print_id) \
                   for print_id in print_ids 
                  ]
        )
# End Async Funcs

def main():
    from sys import argv
    def get_db_session():
        engine = create_engine(CONNECTION_STRING)
        Session = sessionmaker(bind=engine)
        return Session()

    def get_all_card_ids_from_db(session):
        return [r.id for r in session.query(Card.id)]

    def print_usage_and_exit(message=''):
        print(f'usage: treasure_cruise.py <MODE> [<FIRST_PRINT_ID>-<LAST_PRINT_ID>]\n{message}')
        exit(0)

    def parse_args(argv):
        if len(argv) > 2:
            if argv[1] == 'cards':
                func = insert_card_to_db
            elif argv[1] == 'prices':
                func = insert_prices_to_db
            else:
                print_usage_and_exit()
            return func, map(int, argv[2].split('-'))
        else:
            print_usage_and_exit()

    init_db(CONNECTION_STRING, drop=False)
    db_session = get_db_session()

    func, (first_print_id, last_print_id) = parse_args(argv)
    print_id_range = range(first_print_id, last_print_id+1)

    if func == insert_card_to_db:
        # do not attempt to fetch cards if we already have the record in db
        print_ids = filter(lambda x: x not in get_all_card_ids_from_db(db_session), 
                           print_id_range
        )
    elif func == insert_prices_to_db:
        # only attempt to fetch price data if we already have the card record
        print_ids = filter(lambda x: x in get_all_card_ids_from_db(db_session),
                           print_id_range
        )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        run(func, db_session, print_ids)
    )
    loop.close()
    db_session.close()

if __name__ == '__main__':
    main()

