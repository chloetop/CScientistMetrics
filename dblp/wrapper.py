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

    def startElement(self, name, attrs):
        self.content = ""
        if name in self.pubList:
            # starting to parse a new publication
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
                split = re.split('\.|/', self.content)
                self.features['ed_abbreviation'] = split[-2]
                self.features['venue_abbr'] = split[-3]
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
            # closing the publication
            elif name in self.pubList:
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
