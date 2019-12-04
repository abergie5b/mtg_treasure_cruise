import os

URL = 'https://api.mtgstocks.com/'
CONNECTION_STRING = 'postgresql://tc123:tc123@postgres:5432/MTG'
TCP_CONNECTION_LIMIT = os.getenv('TCP_CONNECTION_LIMIT') or 100
LOGFILE_PATH = 'treasure_cruise.log'
#MAX_PRINT_ID = 52431

