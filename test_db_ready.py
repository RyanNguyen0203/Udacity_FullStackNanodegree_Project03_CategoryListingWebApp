from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Room, Item
engine = create_engine('sqlite:///room_item_user.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()