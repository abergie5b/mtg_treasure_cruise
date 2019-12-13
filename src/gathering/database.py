from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
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
from contextlib import contextmanager

from config import CONNECTION_STRING

Base = declarative_base()

class MTGStocksCard(Base):
    __tablename__ = 'mtgstocks_cards'
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
    # MTGStocksCard Keys
    oracle = Column(String)
    cost = Column(String)
    splitcost = Column(String)
    cmc = Column(String)
    pwrtgh = Column(String)
    supertype = Column(String)
    reserved = Column(Boolean)
    card_type = Column(String)
    updated_at = Column(DateTime)

class MarketPrice(Base):
    __tablename__ = 'market_prices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    mtgstocks_card_id = Column('mtgstockscard_id', ForeignKey('mtgstocks_cards.id'))
    date = Column(DateTime)
    price = Column(Float)

class LowPrice(Base):
    __tablename__ = 'low_prices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    mtgstocks_card_id = Column('mtgstockscard_id', ForeignKey('mtgstocks_cards.id'))
    date = Column(DateTime)
    price = Column(Float)

class HighPrice(Base):
    __tablename__ = 'high_prices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    mtgstocks_card_id = Column('mtgstockscard_id', ForeignKey('mtgstocks_cards.id'))
    date = Column(DateTime)
    price = Column(Float)

class AvgPrice(Base):
    __tablename__ = 'avg_prices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    mtgstocks_card_id = Column('mtgstockscard_id', ForeignKey('mtgstocks_cards.id'))
    date = Column(DateTime)
    price = Column(Float)

class FoilPrice(Base):
    __tablename__ = 'foil_prices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    mtgstocks_card_id = Column('mtgstockscard_id', ForeignKey('mtgstocks_cards.id'))
    date = Column(DateTime)
    price = Column(Float)

class MarketFoilPrice(Base):
    __tablename__ = 'market_foil_prices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    mtgstocks_card_id = Column('mtgstockscard_id', ForeignKey('mtgstocks_cards.id'))
    date = Column(DateTime)
    price = Column(Float)

def init_db(connection_string, drop=True):
    engine = create_engine(connection_string)
    if drop:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

def _get_db_session():
    engine = create_engine(CONNECTION_STRING)
    Session = sessionmaker(bind=engine)
    return Session()

@contextmanager
def get_db_context():
    session = _get_db_session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def get_all_card_ids_from_db(session):
    ids = session.query(MTGStocksCard.id)
    return [r.id for r in ids]

def get_all_card_ids_from_price_tables(session):
    market_ids = [r.mtgstocks_card_id for r in session.query(MarketPrice.mtgstocks_card_id).distinct()]
    low_price_ids = [r.mtgstocks_card_id for r in session.query(LowPrice.mtgstocks_card_id).distinct()]
    high_price_ids = [r.mtgstocks_card_id for r in session.query(HighPrice.mtgstocks_card_id).distinct()]
    foil_price_ids = [r.mtgstocks_card_id for r in session.query(FoilPrice.mtgstocks_card_id).distinct()]
    market_foil_ids = [r.mtgstocks_card_id for r in session.query(MarketFoilPrice.mtgstocks_card_id).distinct()]
    return set(market_ids + low_price_ids + high_price_ids + foil_price_ids + market_foil_ids)


if __name__ == '__main__':
    init_db('postgres://tc123@treasure_cruise_postgres')

