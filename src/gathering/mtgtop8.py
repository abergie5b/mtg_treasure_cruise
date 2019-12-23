from requests import get, post
from bs4 import BeautifulSoup
import re

class MTGTop8:
    def __init__(self, 
                 *args, 
                 **kwargs
        ):
        self.url = 'https://mtgtop8.com'
        self.formats = self._get_all_formats()

    def _get_all_formats(self):
        formats = {}
        req = get(self.url + '/search')
        soup = BeautifulSoup(req.content, features='lxml')
        html = soup.findAll('select', {'name':'format'})
        html = html[0].findAll('option')
        for format in html:
            _code = format['value']
            _name = format.text
            if _code:
                formats[_name] = _code
        return formats

    def get_decks_with_cards(self, 
                             cards:list, 
                             format:str='', 
                             date_start:str='1/1/2019', 
                             date_end:str='1/1/2020',
                             current_page:int=1
        ):
        decks = {}
        data = {
            'cards': '\n'.join(cards),
            'format': self.formats[format],
            'date_start': date_start,
            'date_end': date_end,
            'current_page': current_page
        }
        req = post(self.url + '/search', data=data)
        data['current_page'] = current_page + 1
        soup = BeautifulSoup(req.content, features='lxml')
        html = soup.findAll('form', {'name': 'compare_decks'})[0]
        rows = html.findAll('td')
        decks['total'] = re.match('(\d+)', rows[0].div.text)[0]
        decks['currentPage'] = current_page
        decks['nextRequest'] = lambda x: post(self.url + '/search', data=data)
        decks['data'] = {}
        for row in rows:
            name = row.text
            link = self.url + '/' + row.a
            if name and link:
                decks['data'][name] = link['href']
        return decks


if __name__ == '__main__':
    mtgtop8 = MTGTop8()
    decks = mtgtop8.get_decks_with_cards(
        [
         'Duress', 
        ],
        'Pauper'
    )
    print(decks)

