from sys import argv
from re import findall
from logger import get_logger
from sqlalchemy.orm import Session
from asyncio import get_event_loop
from asyncio_throttle import Throttler
from aiohttp import (
    ClientSession, 
    TCPConnector, 
    ClientTimeout
)

from database import (
    get_all_card_ids_from_db,
    get_db_context, 
    init_db
)
from config import (
    URL,
    CONNECTION_STRING,
    TCP_CONNECTION_LIMIT,
    HTTP_SESSION_TIMEOUT_MINUTES,
    HTTP_REQUEST_RATE_LIMIT_SECONDS,
    LOGFILE_PATH,
    SKIP_ERRORS
)
from mtgstocks import MTGStocks
from gatherer import Gatherer, JsonWebRequest


def get_errors_list_from_logs():
    errors = []
    with open(LOGFILE_PATH, 'r') as f:
        for line in f.readlines():
            matches = findall('WARNING\D+\/(\d+)\D+Not found', line)
            if matches:
                errors.append(int(matches[0]))
    return errors

async def main():

    if len(argv) > 2:
        first_print_id, last_print_id = map(int, argv[1].split('-'))
        modes = argv[2].strip().split(',')
    else:
        print(f'usage: treasure_cruise.py [<first_print_id>-<last_print_id>] [<mode>,<mode>]')
        exit(0)

    card_ids = range(first_print_id, last_print_id+1)

    logger = get_logger()
    logger.info('starting treasure cruise gathering session')

    gatherers = [ MTGStocks ]
    #init_db(CONNECTION_STRING, drop=True)
    with get_db_context() as db_session:
        existing_cards = get_all_card_ids_from_db(db_session)
        logger.info(f'there are {len(existing_cards)} cards already in the database')

        # do not attempt to fetch cards if we already have the record in db
        card_ids = list(filter(lambda x: x not in existing_cards, card_ids))

        logger.info(f'service started for {len(card_ids)} card ids ({first_print_id}-{last_print_id})')
        logger.info(f'proxying from {JsonWebRequest.Proxy} with tcp connection limit set to {TCP_CONNECTION_LIMIT}')
        logger.info(f'http request rate set to {HTTP_REQUEST_RATE_LIMIT_SECONDS} and http session timeout limit set to {HTTP_SESSION_TIMEOUT_MINUTES} minutes')

        if SKIP_ERRORS:
            errors_list = get_errors_list_from_logs()
            logger.info(f'{len(list(filter(lambda x: x in errors_list, card_ids)))} cards will be skipped due to previous errors')
            card_ids = list(filter(lambda x: x not in errors_list, card_ids))

        for gatherer in gatherers:
            async with Throttler(
                           rate_limit=int(HTTP_REQUEST_RATE_LIMIT_SECONDS)
                       ), \
                       ClientSession(
                           connector=TCPConnector(limit=int(TCP_CONNECTION_LIMIT)), 
                           timeout=ClientTimeout(int(HTTP_SESSION_TIMEOUT_MINUTES)*60)
            ) as http_session:
                await Gatherer.execute(gatherer(http_session, db_session), 
                                       card_ids,
                                       modes=modes
                )
        logger.info(f'there are now {len(get_all_card_ids_from_db(db_session))} cards in the database')

if __name__ == '__main__':
    loop = get_event_loop()
    loop.run_until_complete(main())
    loop.close()

