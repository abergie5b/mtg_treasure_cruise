from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
  create_engine,
  Column, 
  Integer, 
  String, 
  Float, 
  DateTime, 
  Boolean, 
  ForeignKey
)

Base = declarative_base()

class Card(Base):
    __tablename__ = 'cards'
    # Print Keys
    id = Column(Integer, primary_key=True)
    name = Column(String)
    foil = Column(String)
    tcg_id = Column(String)
    tcg_url = Column(String)
    mkm_id = Column(String)
    mkm_url = Column(String)
    rarity = Column(String)
    all_time_high_price = Column(Float)
    all_time_high_date = Column(DateTime)
    all_time_low_price = Column(Float)
    all_time_low_date = Column(DateTime)
    multiverse_id = Column(String)
    latest_price_mkm = Column(Float)
    latest_price_ck = Column(Float)
    latest_price_mm = Column(Float)
    icon_class = Column(String)
    image = Column(String)
    image_flip = Column(String)
    flip = Column(Boolean)
    legal = Column(Boolean)
    card_set = Column(String)
    latest_price = Column(String)
    sets = Column(String)
    # Card Keys
    oracle = Column(String)
    cost = Column(String)
    splitcost = Column(String)
    cmc = Column(String)
    pwrtgh = Column(String)
    supertype = Column(String)
    reserved = Column(Boolean)
    card_type = Column(String)

class Price(Base):
    __tablename__ = 'prices'
    card_id = Column('card_id', ForeignKey('cards.id'))
    date = Column(DateTime)
    low = Column(Float)
    high = Column(Float)
    avg = Column(Float)
    foil = Column(Float)
    market = Column(Float)
    market_foil = Column(Float)

def init_db(connection_string):
    engine = create_engine(connection_string)
    base.metadata.create_all(engine)

if __name__ == '__main__':
    init_db('postgres://tc123@postgres')

