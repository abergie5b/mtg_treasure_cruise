import sqlite3

class MTGJson:
    def __init__(self, 
                 filepath
        ):
        self.connection = sqlite3.connect(filepath)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def execute(self, sql, *args):
        results = self.cursor.execute(sql, args)
        return results.fetchall()

    def get_card(self, **kwargs):
        sql = '''
            select
               *
            from cards c
            inner join sets s on s.code=c.setCode
            inner join legalities l on l.uuid=c.uuid
            inner join rulings r on r.uuid=c.uuid
        '''
        for k,v in kwargs.items():
            sql += f" and {k}='{v}'"
        return self.execute(sql)

def main():
    mtgjson = MTGJson('/home/chronos/user/Downloads/AllPrintings.sqlite')
    dh = mtgjson.get_card(**{'artist': 'John Avon', 'colorIdentity': 'G'})

if __name__ == '__main__':
    main()

