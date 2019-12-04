from asyncio import gather
from aiohttp import ClientSession, ServerDisconnectedError
from aiohttp.client_exceptions import ClientOSError
from sqlalchemy.orm import Session
from requests import get
from typing import List

from database import Card

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

    async def get_json_async(self, url:str, card_id:int) -> dict:
        try:
            response = await self.http_session.get(url)
        except ServerDisconnectedError as e:
            return self.http_error(url, e)
        except ClientOSError as e:
            return self.http_error(url, e)
        if response.status == 200:
            js =  await response.json()
            js['card_id'] = card_id
            return js
        text = await response.text()
        return {'error': text}

    def http_error(self, url, message):
        self.logger.warn(f'Request failed for {url}\n{message}')
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
            cards_url:str
            prices_url:str
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
    def insert_prices(self, js:dict) -> dict:
        raise NotImplementedError()

    ''' Optional '''
    def get_card(self, card_id:int) -> dict:
        raise NotImplementedError()

    ''' Optional '''
    def get_prices(self, card_id:int) -> dict:
        raise NotImplementedError()

    @staticmethod
    async def execute(gatherer:object, card_ids:List[int]) -> dict:
        results = {'cards': [], 'prices': []}
        cards =  await gather(
                *[ gatherer.get_json_async(gatherer.cards_url % card_id, card_id) \
                   for card_id in card_ids 
                  ]
        )
        for js in filter(lambda x: x.get('error') is None, cards):
            results['cards'].append(
                gatherer.insert_card(js)
            )

        prices =  await gather(
                *[ gatherer.get_json_async(gatherer.prices_url % card_id, card_id) \
                   for card_id in card_ids 
                  ]
        )
        for js in filter(lambda x: x.get('error') is None, prices):
            results['prices'].append(
                gatherer.insert_prices(js)
            )
        return results

