import sqlalchemy
import sqlalchemy.orm
from csmmodel.base import Base
import csmmodel.author_pub_association


class CsAuthor(Base):
    __tablename__ = 'csauthors'

    name = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    publications = sqlalchemy.orm.relationship('CsAuthorPubAssociation', back_populates='author')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Author (name='%s')>" \
               % (self.name)
