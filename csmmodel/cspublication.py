import sqlalchemy
from csmmodel.base import Base
import csmmodel.author_pub_association


class CsPublication(Base):
    __tablename__ = 'cspublications'

    abbr = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    edition_abbr = sqlalchemy.Column(sqlalchemy.String,
                                     sqlalchemy.ForeignKey('csvenueseditions.abbr'))
    title = sqlalchemy.Column(sqlalchemy.String)
    pages = sqlalchemy.Column(sqlalchemy.String)
    doi = sqlalchemy.Column(sqlalchemy.String)

    authors = sqlalchemy.orm.relationship('CsAuthorPubAssociation',
                                          back_populates='publication')

    def __init__(self, abbr):
        self.abbr = abbr

    def __repr__(self):
        return "<Publication (abbr='%s', edition='%s', title='%s')>" \
               % (self.abbr, self.edition, self.title)
