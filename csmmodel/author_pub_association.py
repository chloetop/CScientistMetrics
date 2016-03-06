import sqlalchemy
from csmmodel.base import Base
import csmmodel.csauthor
import csmmodel.cspublication


class CsAuthorPubAssociation(Base):
    __tablename__ = 'csauthpub'

    author_name = sqlalchemy.Column(sqlalchemy.String,
                                    sqlalchemy.ForeignKey('csauthors.name'),
                                    primary_key=True)
    pub_abbr = sqlalchemy.Column(sqlalchemy.String,
                                 sqlalchemy.ForeignKey('cspublications.abbr'),
                                 primary_key=True)

    position = sqlalchemy.Column(sqlalchemy.Integer)

    author = sqlalchemy.orm.relationship('CsAuthor',
                                         back_populates='publications')
    publication = sqlalchemy.orm.relationship('CsPublication',
                                              back_populates='authors')


    def __init__(self, position):
        self.position = position
