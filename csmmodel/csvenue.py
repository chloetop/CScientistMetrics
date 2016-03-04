import sqlalchemy
from csmmodel.base import Base


class CsVenue(Base):
    __tablename__ = 'csvenues'

    abbreviation = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    fullname = sqlalchemy.Column(sqlalchemy.String)
    type = sqlalchemy.Column(sqlalchemy.String)

    def __init__(self, abbreviation, name, type):
        self.abbreviation = abbreviation
        self.fullname = name
        self.type= type

    def __repr__(self):
        return "<Venue(abbr='%s', fullname='%s', type='%s')>" \
               % (self.abbreviation, self.fullname, self.type)
