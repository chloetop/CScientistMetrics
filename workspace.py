import sqlalchemy
from sqlalchemy import create_engine
from csmmodel.base import Base
import csmmodel.csvenue
#import csmmodel.csvenueedition
#import csmmodel.cspublication
#import csmmodel.author_pub_association
#import csmmodel.csauthor
from sqlalchemy.orm import sessionmaker
import xml.sax
import dblp.wrapper
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logging.getLogger().setLevel(logging.DEBUG)



logging.debug('Starting the parsing process')

database_directory = "data/"

#engine = create_engine('sqlite:///' + database_directory + '/data.db',
#                       echo=False)

engine = create_engine('postgresql://sback:piripicchio@localhost:5432/cscientists')

Base.metadata.drop_all(engine)

Base.metadata.create_all(engine)

Session = sessionmaker()
Session.configure(bind=engine)

session = Session()

source = open(database_directory + "/tiny_dblp.xml", 'r')
xml.sax.parse(source, dblp.wrapper.DBLPContentHandler(session))


# venue = csmmodel.csvenue.CsVenue(abbr='infocomm',
#                                  type='conference',
#                                  fullname='IEEE Conference on Computer Communications')
#
# edition = csmmodel.csvenueedition.CsVenueEdition(abbr='infocom15',
#                                                  venue=venue, ordinal=15,
#                                                  year=2015)
#
# venue.editions.append(edition)

# publication = csmmodel.cspublication.CsPublication(abbr="aa",
#                                                    edition=edition,
#                                                    title="a test publication",
#                                                    pages="11-12")
#
# edition.publications.append(publication)
#
#
# a = csmmodel.author_pub_association.CsAuthorPubAssociation(position=0)
# a.author = csmmodel.csauthor.CsAuthor(name='Alberto')
# publication.authors.append(a)

# instances = [venue]
#
# session.add_all(instances)
session.commit()

session.close()

logging.debug('Finished the parsing process')

