import logging
import re
from sys import argv
from logger import get_logger
from sqlalchemy.orm import Session
from aiohttp import ClientSession, TCPConnector
from asyncio import BoundedSemaphore, get_event_loop

from database import *
from config import (
    URL,
    CONNECTION_STRING,
    TCP_CONNECTION_LIMIT,
    LOGFILE_PATH
)
from mtgstocks import MTGStocks
from gatherer import Gatherer

GATHERERS = [ MTGStocks ]

def get_errors_list_from_logs():
    errors = []
    with open(LOGFILE_PATH, 'r') as f:
        for line in f.readlines():
            matches = re.findall('WARNING\D+\/(\d+)', line)
            if matches:
                errors.append(matches[0])
    return errors

async def main():
    def print_usage_and_exit(message=''):
        print(f'usage: treasure_cruise.py [<first_print_id>-<last_print_id>]\n{message}')
        exit(0)

    def parse_args(argv):
        if len(argv) > 1:
            return map(int, argv[1].split('-'))
        else:
            print_usage_and_exit()

    logger = get_logger()

    init_db(CONNECTION_STRING, drop=False)

    first_print_id, last_print_id = parse_args(argv)
    card_ids = range(first_print_id, last_print_id+1)

    with get_db_context() as db_session:
        existing_cards = get_all_card_ids_from_db(db_session)

    # do not attempt to fetch cards if we already have the record in db
    #card_ids = list(filter(lambda x: x not in existing_cards, card_ids))

    errors_list = get_errors_list_from_logs()
    #card_ids = list(filter(lambda x: x not in errors_list, card_ids))

    logger.info(f'service started for card_ids: {first_print_id}-{last_print_id}')
    logger.info(f'tcp_connection_limit: {TCP_CONNECTION_LIMIT}')
    logger.info(f'cards in the database: {len(existing_cards)}')
    logger.info(f'previous errors: {len(errors_list)}')
    logger.info(f'fetching data for {len(card_ids)} cards')

    tcp_connector = TCPConnector(limit=int(TCP_CONNECTION_LIMIT))
    for gatherer in GATHERERS:
        with get_db_context() as db_session:
            async with ClientSession(connector=tcp_connector) as http_session:
                await Gatherer.execute(gatherer(http_session, db_session), card_ids)

if __name__ == '__main__':
    loop = get_event_loop()
    loop.run_until_complete(main())
    loop.close()

