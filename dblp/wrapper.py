import xml.sax
import re
import csmmodel.csvenue
import csmmodel.csvenueedition
import csmmodel.cspublication
import csmmodel.author_pub_association
import csmmodel.csauthor


class DBLPContentHandler(xml.sax.ContentHandler):

    def __init__(self, session):
        xml.sax.ContentHandler.__init__(self)
        self.session = session
        self.venues = {}
        self.editions = {}
        self.authors = {}
        self.content = ""
        self.publication = None
        self.authornames = []
        self.pubList = ["article", "inproceedings",
                        # "proceedings",
                        "book",
                        "incollection",
                        # "phdthesis", "mastersthesis",
                        # "www"
                        ]

    def startElement(self, name, attrs):
        self.content = ""
        if name in self.pubList:
            self.publication = csmmodel.cspublication.CsPublication(
               attrs.getValue("key"))
            self.authornames = []

    def retrieve_venue(self, venue_abbr, type):
        if venue_abbr not in self.venues:
            self.venues[venue_abbr] = csmmodel.csvenue.CsVenue(
                abbr=venue_abbr,
                type=type)
            self.session.add(self.venues[venue_abbr])
        return self.venues[venue_abbr]

    def retrieve_edition(self, edition_abbr, venue, year):
        if edition_abbr not in self.editions:
            ordinal = re.findall('(\d+)$', edition_abbr)[-1]
            self.editions[
                edition_abbr] = csmmodel.csvenueedition.CsVenueEdition(
                abbr=edition_abbr, venue=venue, ordinal=ordinal,
                year=year)
            self.session.add(self.editions[edition_abbr])
        return self.editions[edition_abbr]

    def retrieve_authors(self, author_names):
        pub_authors = []
        for author_name in author_names:
            if author_name not in self.authors:
                self.authors[author_name] = csmmodel.csauthor.CsAuthor(
                   name=author_name)
                self.session.add(self.authors[author_name])
            pub_authors.append(self.authors[author_name])
        return pub_authors

    def endElement(self, name):
        if self.publication:
            if name == 'url':
                split = re.split('\.|/', self.content)
                self.ed_abbreviation = split[-2]
                self.venue_abbr = split[-3]
            if name == 'year':
                self.year = self.content
            if name == 'pages':
                self.publication.pages = self.content
            if name == 'author':
                self.authornames.append(self.content)
            if name == 'title':
                self.publication.title = self.content
            if name in self.pubList:
                venue = self.retrieve_venue(self.venue_abbr, name)
                edition = self.retrieve_edition(self.ed_abbreviation, venue,
                                              self.year)
                pub_authors = self.retrieve_authors(self.authornames)
                self.publication.edition = edition
                for idx, pub_author in enumerate(pub_authors):
                    a = csmmodel.author_pub_association.CsAuthorPubAssociation(position=idx)
                    a.author = pub_author
                    self.publication.authors.append(a)
                self.session.add(self.publication)
                self.session.commit()
                self.publication = None

    def characters(self, content):
        self.content += content #.encode('utf-8').replace('\\', '\\\\')


def main(sourceFileName):
    source = open(sourceFileName)
    xml.sax.parse(source, DBLPContentHandler())


if __name__ == "__main__":
    main("tiny_dblp.xml")
