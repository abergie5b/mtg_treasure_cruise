from asyncio import gather
from aiohttp import ClientSession, ServerDisconnectedError
from aiohttp.client_exceptions import ClientOSError
from sqlalchemy.orm import Session
from requests import get
from typing import List
from concurrent.futures._base import TimeoutError

from database import get_all_card_ids_from_price_tables, get_all_card_ids_from_db
from config import random_proxy

class JsonWebRequest:
    Proxy = random_proxy()
    Headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0q'
    }
    def __init__(self, 
                 http_session:ClientSession
                 ):
        self.http_session = http_session
        self.logger = None
        raise NotImplementedError()

    def get_json(self, 
                 url:str, 
                 card_id:int
                 ) -> dict:
        try:
            response = get(url, 
                           proxies={'http':f'http://{JsonWebRequest.Proxy}'},
                           headers=JsonWebRequest.Headers, 
                           #timeout=30
            )
        except Exception as e:
            return self.error('Request failed Exception', url, e)
        if response.status_code == 200:
            js =  response.json()
            js['card_id'] = card_id
            return js
        return self.error(f'Request failed (http status code {response.status_code})', url, response.content)

    async def get_json_async(self, 
                             url:str, 
                             card_id:int
                             ) -> dict:
        try:
            response = await self.http_session.get(url, 
                                                   proxy=f'http://{JsonWebRequest.Proxy}',
                                                   headers=JsonWebRequest.Headers
            )
        except ServerDisconnectedError as e:
            return self.error('Request failed ServerDisconnected', url, e)
        except ClientOSError as e:
            return self.error('Request failed ClientOSError', url, e)
        except Exception as e:
            return self.error('Request failed Exception', url, e)
        if response.status == 200:
            try:
                js = await response.json()
                js['card_id'] = card_id
                return js
            except TimeoutError as e:
                return self.error('Timed out decoding json', url, e)
        message = f'Request failed (http status code {response.status})'
        text = await response.text()
        error_codes = [ 'Not Found' ]
        for error in error_codes:
            if error in text:
                return self.error(message, url, error)
        return self.error(message, url, text)

    def error(self, message, url, error):
        self.logger.warn(f'{message} {url} {error}')
        return {'error': error}


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
    def __insert_task_results_to_db(mode:str, 
                                    gatherer:object, 
                                    tasks:list) -> list:
        results = []
        success = list(filter(lambda x: x.get('error') is None, tasks))
        errors = list(filter(lambda x: x.get('error') is not None, tasks))
        gatherer.logger.info(f'{len(tasks)} tasks of gathering completed with {len(success)} {mode}s found and {len(errors)} errors')

        f = getattr(gatherer, f'insert_{mode}')
        for js in success:
            model = f(js)
            results.append(model)
        return results

    @staticmethod
    async def __execute_async(mode:str, 
                              gatherer:object, 
                              card_ids:List[int]) -> list:
        url = getattr(gatherer, f'{mode}_url')
        tasks =  await gather(
                *[ gatherer.get_json_async(url % card_id, card_id) \
                   for card_id in card_ids 
                  ]
        )
        return Gatherer.__insert_task_results_to_db(mode, gatherer, tasks)

    @staticmethod
    def __execute_sync(mode:str, 
                       gatherer:object, 
                       card_ids:List[int]) -> list:
        results = []
        url = getattr(gatherer, f'{mode}_url')
        tasks =  [ gatherer.get_json(url % card_id, card_id) \
                   for card_id in card_ids 
                 ]
        return Gatherer._insert_task_results_to_db(mode, gatherer, tasks)

    @staticmethod
    async def execute(gatherer:object, card_ids:List[int], modes=['cards', 'prices']) -> dict:
        results = {}
        if 'cards' in modes:
            cards = await Gatherer.__execute_async('card', 
                                                   gatherer, 
                                                   card_ids
            )
            results['cards'] = cards

        if 'prices' in modes:
            existing_card_ids = get_all_card_ids_from_db(gatherer.db_session)
            existing_cards_ids_in_price_tables = get_all_card_ids_from_price_tables(gatherer.db_session)
            card_ids = [card_id for card_id in existing_card_ids \
                        if card_id not in existing_cards_ids_in_price_tables
            ]

            prices = await Gatherer.__execute_async('price', 
                                             gatherer, 
                                             card_ids 
            )
            results['prices'] = prices
        return results

