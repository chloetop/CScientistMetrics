import sqlalchemy
from sqlalchemy import create_engine
from csmmodel.base import Base
import csmmodel.csvenue
from sqlalchemy.orm import sessionmaker

database_directory = '/Users/sback/tud.gdrive/research/peer_review/quantitative_db_effects/our_dataset'

engine = create_engine('sqlite:///' + database_directory + '/data.db', echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker()
Session.configure(bind=engine)

session = Session()


venue = csmmodel.csvenue.CsVenue(abbreviation='infocom',
                                 name='IEEE Conference on Computer Communications',
                                 type='conference')

session.add(venue)
session.commit()