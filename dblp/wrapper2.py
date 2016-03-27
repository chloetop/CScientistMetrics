import lxml.etree
import argparse
import sqlalchemy
from csmmodel.base import Base
import csmmodel.csvenue
import csmmodel.csvenueedition
import csmmodel.cspublication
import csmmodel.csauthor
import logging
import re

CLEAN_TABLES = True
TAGS = ["article", "inproceedings"]
TO_IGNORE = ["dblpnote", "persons"]
# authors = {}
author_names = set()
unsaved_author_names = set()
venues = {}
editions = {}
_session = None


def create_session(db_string):
    engine = sqlalchemy.create_engine(db_string)
    if CLEAN_TABLES:
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    Session = sqlalchemy.orm.sessionmaker(autoflush=False)
    Session.configure(bind=engine)
    return Session()


def to_ignore(elem):
    if elem.attrib['key'].split('/')[0] in TO_IGNORE:
        return True
    return 'publtype' in elem.attrib and elem.attrib[
                                             'publtype'] == 'informal publication'


def get_doi(elem):
    ee = elem.findtext('ee')
    if ee and re.search('\Wdoi\W', ee):
        return '/'.join(ee.split('/')[-2:])
    return None


def get_author(name, session):
    if name in author_names:
        if name in unsaved_author_names:
            session.commit()
            unsaved_author_names.clear()
        return session.query(csmmodel.csauthor.CsAuthor).filter_by(
            name=name).first()
    au = csmmodel.csauthor.CsAuthor(name=name)
    author_names.add(au.name)
    unsaved_author_names.add(au.name)
    session.add(au)
    return au


def get_authors(elem, pub, session):
    my_associations = dict()
    idx = 0
    for au_name in elem.itertext('author', with_tail=False):
        if au_name not in my_associations:
            au = get_author(au_name, session)
            assoc = csmmodel.author_pub_association.CsAuthorPubAssociation(
                position=idx)
            assoc.author = au
            assoc.publication = pub
            my_associations[au_name] = assoc
            idx += 1
    return list(my_associations.values())


def log_ed_abbreviation(elem, ed_abbr):
    logging.error(
        "I had to make up the ed_abbreviation '%s' for pub '%s'" %
        (ed_abbr, elem.attrib['key']))


def get_venue(elem, venue_abbr, session):
    if venue_abbr not in venues:
        venue = csmmodel.csvenue.CsVenue(
            abbr=venue_abbr,
            type=elem.tag)
        venues[venue_abbr] = venue
        session.add(venue)
    return venues[venue_abbr]


def create_edition(elem, ed_abbr, venue_abbr, session):
    venue = get_venue(elem, venue_abbr, session)
    if venue.type == 'inproceedings':
        ordinal = elem.findtext('year')
    else:
        if elem.findtext('volume'):
            ordinal = elem.findtext('volume')
        elif re.findall('(\d+)', ed_abbr):
            ordinal = re.findall('(\d+)', ed_abbr)[-1]
        else:
            ordinal = 'NA'
    editions[ed_abbr] = csmmodel.csvenueedition.CsVenueEdition(
        abbr=ed_abbr, venue=venue, ordinal=ordinal,
        year=elem.findtext('year'))
    session.add(editions[ed_abbr])
    return editions[ed_abbr]


def get_edition(elem, session):
    url = elem.findtext('url')
    if url:
        split = re.split('\.|/', url)
        ed_abbr = split[-2]
        venue_abbr = split[-3]
    else:
        split = re.split('/', elem.attrib['key'])
        venue_abbr = split[1]
        if elem.findtext('volume'):
            ed_abbr = venue_abbr + elem.findtext('volume')
        elif elem.findtext('year'):
            ed_abbr = venue_abbr + elem.findtext('year')
        else:
            ed_abbr = "MADEUP00"
        log_ed_abbreviation(elem, ed_abbr)
    if ed_abbr not in editions:
        create_edition(elem, ed_abbr, venue_abbr, session)
    return editions[ed_abbr]


def create_publication(elem, session):
    pub = csmmodel.cspublication.CsPublication(elem.attrib["key"])
    pub.title = elem.findtext('title')
    pub.pages = elem.findtext('year')
    pub.pages = elem.findtext('pages')
    pub.doi = get_doi(elem)
    pub.authors = get_authors(elem, pub, session)
    pub.edition = get_edition(elem, session)
    session.add(pub)
    return pub


def parse_and_store(source, db_string=None, session=None):
    if db_string:
        my_session = create_session(db_string)
    elif session:
        my_session = session
    else:
        raise Exception("Missing at least one valid argument")

    doc = lxml.etree.iterparse(source, load_dtd=True,
                               tag=TAGS)
    for idx, (event, elem) in enumerate(doc):
        if to_ignore(elem):
            logging.debug(
                "Ignored '%s' " % elem.attrib)
        else:
            create_publication(elem, my_session)
            if idx % 5000 == 1:
                my_session.commit()
                unsaved_author_names.clear()
                logging.debug("committed %s" % idx)
    my_session.commit()


def _get_args():
    parser = argparse.ArgumentParser(
        'Parse large XML files linearly with low memory footprint')
    parser.add_argument("input", help="file to parse")
    parser.add_argument("database", help="database string")
    parser.add_argument("-l", "--logfile", help="file to output log")
    return parser.parse_args()


def define_logging(logfile):
    logging.basicConfig(level=logging.INFO, filename=logfile,
                        format='%(asctime)s %(message)s')
    logging.getLogger().setLevel(logging.DEBUG)


def main():
    args = _get_args()
    define_logging(args.logfile)
    logging.debug('Parsing process: START')
    parse_and_store(args.input, args.database)
    logging.debug('Parsing process: END')


if __name__ == "__main__":
    main()
