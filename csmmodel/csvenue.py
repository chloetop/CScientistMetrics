import sqlalchemy
import sqlalchemy.orm
from csmmodel.base import Base
import csmmodel.csvenueedition


class CsVenue(Base):
    __tablename__ = 'csvenues'

    abbr = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    fullname = sqlalchemy.Column(sqlalchemy.String)
    type = sqlalchemy.Column(sqlalchemy.String)
    dblp_url = sqlalchemy.Column(sqlalchemy.String)
    editions = sqlalchemy.orm.relationship('CsVenueEdition',
                                           back_populates='venue')

    def __init__(self, abbr, type, fullname=""):
        self.abbr = abbr
        self.type = type
        self.fullname = fullname


    def __repr__(self):
        return "<Venue(abbr='%s', fullname='%s', type='%s')>" \
               % (self.abbr, self.fullname, self.type)
