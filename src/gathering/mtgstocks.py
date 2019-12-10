import datetime as dt
from aiohttp import ClientSession
from sqlalchemy.orm import Session

from database import (
    MTGStocksCard, 
    LowPrice, 
    HighPrice, 
    FoilPrice,
    AvgPrice, 
    MarketPrice, 
    MarketFoilPrice
)
from gatherer import Gatherer
from logger import get_logger

class MTGStocks(Gatherer):
    def __init__(self, 
                 http_session:ClientSession, 
                 db_session:Session
                 ):
        '''
        '''
        self.http_session = http_session
        self.db_session = db_session
        self.card_url = 'https://api.mtgstocks.com/prints/%s'
        self.price_url = 'https://api.mtgstocks.com/prints/%s/prices'
        self.logger = get_logger()

    def insert_price(self, js:dict) -> dict:
        '''
        '''
        print_id = js['card_id']
        prices = {}
        for price_type, Model in zip(['low', 'high', 'avg', 'market', 'foil', 'market_foil'],
                                     [LowPrice, HighPrice, AvgPrice, MarketPrice, FoilPrice, MarketFoilPrice]
                                    ):
            prices[price_type] = []
            rows = js.get(price_type)
            for row in rows:
                price = Model(mtgstocks_card_id=print_id,
                              date=dt.datetime.fromtimestamp(int(row[0])/1000), 
                              price=row[1]
                )
                prices[price_type].append(price)
                self.db_session.add(price)
            self.db_session.commit()
        self.logger.info(f"|print_id {print_id}|low: {len(prices['low'])}|high: {len(prices['high'])}|avg: {len(prices['avg'])}|market: {len(prices['market'])}|foil: {len(prices['foil'])}|market foil: {len(prices['market_foil'])}")
        return prices

    def insert_card(self, js:dict) -> MTGStocksCard:
        '''
        '''
        self.logger.info(f"|{js['name']}|set: {js['card_set']['name']}|")
        card = self._js_to_card(js)
        self.db_session.add(card)
        self.db_session.commit()
        return card

    def _js_to_card(self, js:dict) -> MTGStocksCard:
        all_time_high = js['all_time_high']
        if all_time_high and all_time_high.get('date') and all_time_high.get('avg'):
            all_time_high_price, all_time_high_date = all_time_high['avg'], dt.datetime.fromtimestamp(int(all_time_high['date'])/1000)
        else:
            all_time_high_price, all_time_high_date = (None, None)
        all_time_low = js['all_time_low']
        if all_time_low and all_time_low.get('date') and all_time_low.get('avg'):
            all_time_low_price, all_time_low_date = all_time_low['avg'], dt.datetime.fromtimestamp(int(all_time_low['date'])/1000)
        else:
            all_time_low_price, all_time_low_date = (None, None)
        sets = list(map(lambda x: x['set_name'], js['sets']))
        latest_price_mkm = js['latest_price_mkm']['avg'] if js.get('latest_price_mkm') else None
        latest_price_ck = js['latest_price_ck']['price'] if js.get('latest_price_ck') else None
        latest_price_mm = js['latest_price_mm']['price'] if js.get('latest_price_mm') else None
        card_set = js['card_set']['name'] if js['card_set'] else None
        latest_price = js['latest_price']['avg'] if js['latest_price'] else None
        card = js['card']
        splitcost = ''.join(card['splitcost']) if isinstance(card['splitcost'], list) else None
        card = MTGStocksCard(id=js['id'],
                             name=js['name'],
                             foil=js['foil'],
                             tcg_id=js['tcg_id'],
                             tcg_url=js['tcg_url'],
                             mkm_id=js['mkm_id'],
                             mkm_url=js['mkm_url'],
                             rarity=js['rarity'],
                             all_time_high_price=all_time_high_price,
                             all_time_high_date=all_time_high_date,
                             all_time_low_price=all_time_low_price,
                             all_time_low_date=all_time_low_date,
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
                             # MTGStocksCard Keys
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

    def get_card(self, print_id:int) -> dict:
        return self.get_json(self.card_url % print_id)

    def get_price(self, print_id:int) -> dict:
        return self.get_json(self.price_url % print_id)

