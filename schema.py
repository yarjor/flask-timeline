#!usr/bin/python

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from os import path
from consts import *

engine = create_engine('sqlite:///{}'.format(DB_NAME), echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Event(Base):
    '''
    Table collecting timeline events

    @ title - The event title (str)
    @ description - The event text (str)
    @ time - Event time, as a datetime object (datetime.datetime)
    @ icon - Bootstrap glyphicon names. For example, to use glyphicon
      glyphicon-heart, use icon = heart (str)
    @ color - Bootstrap color-classes: One of ['default', 'primary', 'success', 'info', 
      'warning', 'danger'] (str)
    @ tags - All the tags related to the event, as one comma-separated string. (str)
    '''
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    time = Column(DateTime)
    icon = Column(String)
    color = Column(String)
    tags = Column(String)


    def __init__(self, title, description, time, icon='calendar', color='default', tags=''):
        self.title = title
        self.description = description
        self.time = time
        self.icon = icon
        self.color = color
        self.tags = tags


    def to_dict(self):
        '''
        Returns dict form of the event, in order to send it JSONified to the
        browser.
        '''
        return {
            'ID' : self.id,
            'Title' : self.title,
            'Description' : self.description,
            'Time' : self.time,
            'Icon' : self.icon,
            'Color' : self.color or 'NA',
            'Tags' : self.tags or '',
            'Space' : 0
        }


def db_create():
    '''Create the DB if it doesn't exist'''
    Base.metadata.create_all(engine)
    if not path.isfile(ALL_TAGS):
        with open(ALL_TAGS, 'wb') as f:
            f.write('')

if __name__ == '__main__':
    db_create()
