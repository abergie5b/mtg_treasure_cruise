from asyncio import gather
from aiohttp import ClientSession, ServerDisconnectedError
from aiohttp.client_exceptions import ClientOSError
from sqlalchemy.orm import Session
from requests import get
from typing import List

class JsonWebRequest:
    def __init__(self, 
                 http_session:ClientSession
                 ):
        self.http_session = http_session
        self.logger = None
        raise NotImplementedError()

    def get_json(self, url:str) -> dict:
        response = get(url)
        if response.status == 200:
            js =  response.json()
            return js
        text = response.text()
        return {'error': text}

    async def get_json_async(self, 
                             url:str, 
                             card_id:int
                             ) -> dict:
        try:
            response = await self.http_session.get(url, proxy='http://157.245.124.217:3128')
        except ServerDisconnectedError as e:
            return self.http_error(url, e)
        except ClientOSError as e:
            return self.http_error(url, e)
        except Exception as e:
            return self.http_error(url, e)
        if response.status == 200:
            js = await response.json()
            js['card_id'] = card_id
            return js
        text = await response.text()
        error_codes = [ '404 Not Found' ]
        for error in error_codes:
            if error in text:
                text = error
        return self.http_error(url, text)

    def http_error(self, url, message):
        self.logger.warn(f'Request failed for {url} {message}')
        return {'error': message}


class Gatherer(JsonWebRequest):
    def __init__(self, 
                 http_session:ClientSession, 
                 db_session:Session
                 ):
        '''
        Subclasses require the following members:
            http_session:ClientSession
            db_session:Session
            card_url:str
            price_url:str
            logger:logging.Logger
        And the following methods:
            insert_card(dict)
            insert_prices(dict)
        '''
        raise NotImplementedError()

    ''' Required '''
    def insert_card(self, js:dict) -> object:
        raise NotImplementedError()

    ''' Required '''
    def insert_price(self, js:dict) -> dict:
        raise NotImplementedError()

    ''' Optional '''
    def get_card(self, card_id:int) -> dict:
        raise NotImplementedError()

    ''' Optional '''
    def get_price(self, card_id:int) -> dict:
        raise NotImplementedError()

    @staticmethod
    async def __execute(mode:str, gatherer:object, card_ids:List[int]) -> list:
        results = []
        url = getattr(gatherer, f'{mode}_url')
        tasks =  await gather(
                *[ gatherer.get_json_async(url % card_id, card_id) \
                   for card_id in card_ids 
                  ]
        )
        success = list(filter(lambda x: x.get('error') is None, tasks))
        errors = list(filter(lambda x: x.get('error') is not None, tasks))
        gatherer.logger.info(f'{len(tasks)} tasks of gathering completed with {len(success)} {mode}s found and {len(errors)} errors')

        f = getattr(gatherer, f'insert_{mode}')
        for js in success:
            model = f(js)
            results.append(model)
        return results

    @staticmethod
    async def execute(gatherer:object, card_ids:List[int]) -> dict:
        cards = await Gatherer.__execute('card', 
                                         gatherer, 
                                         card_ids
        )

        existing_price_card_ids = get_all_card_ids_from_price_tables(gatherer.db_session)
        prices = await Gatherer.__execute('price', 
                                          gatherer, 
                                          list(filter(lambda x: x not in existing_price_card_ids), card_ids)
        )
        return {'cards': cards, 'prices': prices}

