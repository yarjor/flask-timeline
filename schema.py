#!usr/bin/python

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from os import path
from consts import *

engine = create_engine('sqlite:///{}'.format(DB_NAME), echo=False)
Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

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

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    time: Mapped[datetime]
    icon: Mapped[str] = mapped_column(default='calendar')
    color: Mapped[str] = mapped_column(default='default')
    tags: Mapped[str] = mapped_column(default='')

    def to_dict(self) -> dict:
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
            f.write(b'')

if __name__ == '__main__':
    db_create()
