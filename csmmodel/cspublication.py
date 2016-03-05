import sqlalchemy
from csmmodel.base import Base
import csmmodel.author_pub_association


class CsPublication(Base):
    __tablename__ = 'cspublications'

    abbr = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    edition = sqlalchemy.Column(sqlalchemy.String,
                                sqlalchemy.ForeignKey('csvenueseditions.abbr'))
    title = sqlalchemy.Column(sqlalchemy.String)
    pages = sqlalchemy.Column(sqlalchemy.String)
    authors = sqlalchemy.orm.relationship('CsAuthorPubAssociation',
                                          back_populates='cspublication')

    def __init__(self, abbr, edition=edition, title=title,
                 pages=pages):
        self.abbr = abbr
        self.edition = edition
        self.title = title
        self.pages = pages

    def __repr__(self):
        return "<Publication (abbr='%s', edition='%s', title='%s')>" \
               % (self.abbr, self.edition, self.title)
