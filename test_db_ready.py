#!/usr/bin/env python3

''' Import all dependencies and set up the database session
for quick access to the database from IDLE '''

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Room, Item

engine = create_engine('sqlite:///room_item_user.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()