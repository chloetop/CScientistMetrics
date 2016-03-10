import xml.sax
import re
import csmmodel.csvenue
import csmmodel.csvenueedition
import csmmodel.cspublication
import csmmodel.author_pub_association
import csmmodel.csauthor
import logging


class DBLPContentHandler(xml.sax.ContentHandler):
    def __init__(self, session):
        xml.sax.ContentHandler.__init__(self)
        self.session = session
        self.venues = {}
        self.editions = {}
        self.authors = {}
        self.counter = 0
        self.content = ""
        self.publication = None
        self.features = None
        self.pubList = ["article", "inproceedings",
                        # "proceedings", "book", "incollection", "phdthesis",
                        # "mastersthesis", "www"
                        ]
        self.ignorable_pubs = ["dblpnote", "persons"]

    def retrieve_venue(self, venue_abbr, type):
        if venue_abbr not in self.venues:
            self.venues[venue_abbr] = csmmodel.csvenue.CsVenue(
                abbr=venue_abbr,
                type=type)
            self.session.add(self.venues[venue_abbr])
        return self.venues[venue_abbr]

    def retrieve_edition(self, features, venue):
        ed_abbr = features['ed_abbreviation']
        if ed_abbr not in self.editions:
            if venue.type == 'inproceedings':
                ordinal = features['year']
            else:
                if 'volume' in features:
                    ordinal = features['volume']
                else:
                    ordinal = re.findall('(\d+)', ed_abbr)[-1]
            self.editions[
                ed_abbr] = csmmodel.csvenueedition.CsVenueEdition(
                abbr=ed_abbr, venue=venue, ordinal=ordinal,
                year=features['year'])
            self.session.add(self.editions[ed_abbr])
        return self.editions[ed_abbr]

    def retrieve_authors(self, author_names):
        pub_authors = []
        for author_name in author_names:
            if author_name not in self.authors:
                self.authors[author_name] = csmmodel.csauthor.CsAuthor(
                    name=author_name)
                self.session.add(self.authors[author_name])
            pub_authors.append(self.authors[author_name])
        return pub_authors

    def log_ed_abbreviation(self, ed_abbr, pub_abbr):
        logging.error(
            "I had to make up the ed_abbreviation '%s' for pub '%s'" %
            (ed_abbr, pub_abbr))

    def add_venue_and_edition(self, features, url=None, pub_abbr=None):
        if url:
            split = re.split('\.|/', url)
            features['ed_abbreviation'] = split[-2]
            features['venue_abbr'] = split[-3]
        elif pub_abbr:
            split = re.split('/', pub_abbr)
            features['venue_abbr'] = split[1]
            if 'volume' in features:
                features['ed_abbreviation'] = split[1] + features['volume']
                self.log_ed_abbreviation(features['ed_abbreviation'], pub_abbr)
            elif 'year' in features:
                features['ed_abbreviation'] = split[1] + features['year']
                self.log_ed_abbreviation(features['ed_abbreviation'], pub_abbr)
            else:
                logging.error(
                    "Cannot find/make ed_abbreviation for pub '%s' used default" %
                    (pub_abbr))
                features['ed_abbreviation'] = "MADEUP00"

    def add_doi(self, text):
        if re.search('\Wdoi\W',text):
            self.publication.doi = '/'.join(text.split('/')[-2:])

    def startElement(self, name, attrs):
        self.content = ""
        if name in self.pubList:
            # starting to parse a new publication
            pub_abbr = attrs.getValue("key")
            if pub_abbr.split('/')[0] in self.ignorable_pubs:
                logging.debug(
                    "Skipping a '%s' publication" % pub_abbr.split('/')[0])
            elif 'publtype' in attrs and attrs.getValue(
                    "publtype") == 'informal publication':
                logging.debug(
                    "Skipping informal publication '%s' " % pub_abbr)
            else:
                self.publication = csmmodel.cspublication.CsPublication(
                    attrs.getValue("key"))
                self.counter += 1
                self.features = dict()
                self.features['author_names'] = []

    def endElement(self, name):
        if self.publication:
            if name == 'author':
                author_name = self.content
                if author_name not in self.features['author_names']:
                    self.features['author_names'].append(author_name)
                else:
                    logging.debug(
                        "found duplicated author %s in %s" %
                        (author_name, self.publication.abbr))
            elif name == 'url':
                self.add_venue_and_edition(self.features, url=self.content)
            # features
            elif name == 'year':
                self.features['year'] = self.content
            elif name == 'volume':
                self.features['volume'] = self.content
            # stored in publications
            elif name == 'pages':
                self.publication.pages = self.content
            elif name == 'title':
                self.publication.title = self.content
            elif name == 'ee':
                self.add_doi(self.content)
            # closing the publication
            elif name in self.pubList:
                if 'venue_abbr' not in self.features:
                    self.add_venue_and_edition(self.features,
                                               pub_abbr=self.publication.abbr)
                venue = self.retrieve_venue(self.features['venue_abbr'], name)
                edition = self.retrieve_edition(self.features, venue)
                pub_authors = self.retrieve_authors(
                    self.features['author_names'])
                self.publication.edition = edition
                for idx, pub_author in enumerate(pub_authors):
                    a = csmmodel.author_pub_association.CsAuthorPubAssociation(
                        position=idx)
                    a.author = pub_author
                    self.publication.authors.append(a)
                self.session.add(self.publication)
                if self.counter % 5000 == 0:
                    self.session.commit()
                    logging.debug("committed %s" % self.counter)
                self.publication = None

    def characters(self, content):
        self.content += content  # .encode('utf-8').replace('\\', '\\\\')


def main(sourceFileName):
    source = open(sourceFileName)
    xml.sax.parse(source, DBLPContentHandler())


if __name__ == "__main__":
    main("tiny_dblp.xml")
