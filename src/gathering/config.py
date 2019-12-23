from re import findall
from os import getenv
from requests import get
from bs4 import BeautifulSoup
from random import randint

URL = 'https://api.mtgstocks.com/'
CONNECTION_STRING = 'postgres://tc123:tc123@localhost:5432/mtg'
#CONNECTION_STRING = 'postgresql://tc123:tc123@postgres:5432/MTG'
TCP_CONNECTION_LIMIT = getenv('GATHERER_TCP_CONNECTION_LIMIT') or 5
HTTP_SESSION_TIMEOUT_MINUTES = getenv('GATHERER_HTTP_SESSION_TIMEOUT_MINUTES') or 30
HTTP_REQUEST_RATE_LIMIT_SECONDS = getenv('GATHERER_HTTP_REQUEST_RATE_LIMIT_SECONDS') or 1
LOGFILE_PATH = 'treasure_cruise.log'
SKIP_ERRORS = bool(int(getenv('SKIP_ERRORS'))) if getenv('SKIP_ERRORS') else True

def _get_proxies() -> list:
    url = 'https://free-proxy-list.net/'
    source = get(url).text
    soup = BeautifulSoup(source, features='lxml')
    html_table = soup.findAll('table', id='proxylisttable')
    matches = html_table[0].findAll('tr')
    result = []
    for match in matches[1:]:
        rows = str(match).split('</td>')
        if len(rows) > 6:
            ip = findall('(\d+\.\d+\.\d+\.\d+)', rows[0])
            port = findall('(\d+)', rows[1])
            http_supported = findall('(yes)', rows[6])
            # aiohttp only supports http proxies
            if ip and port and http_supported and http_supported[0] == 'yes':
                result.append(f'{ip[0]}:{port[0]}')
    return result

def random_proxy() -> str:
    proxies = _get_proxies()
    return proxies[randint(0, len(proxies)-1)]

