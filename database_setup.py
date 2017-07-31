#!/usr/bin/env python3

# Create database

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from os import remove

Base = declarative_base()

class User(Base):
  __tablename__ = 'user'

  id = Column(Integer, primary_key = True)
  name = Column(String(250), nullable = False)
  email = Column(String(50), nullable = False)
  picture = Column(String(250))

  @property
  def serialize(self):
     """Return object data in easily serializeable format"""
     return {
         'name'         : self.name,
         'email'        : self.email,
         'picture'      : self.picture
     }

class Room(Base):
    __tablename__ = 'room'

    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)

    user_id = Column(Integer, ForeignKey('user.id'), nullable = False)
    user = relationship(User)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'           : self.id,
           'name'         : self.name,
           'owner'        : self.user.name,
       }

class Item(Base):
    __tablename__ = 'item'


    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    description = Column(String(250))
    price = Column(String(8))

    room_id = Column(Integer, ForeignKey('room.id'), nullable = False)
    room = relationship(Room)

    user_id = Column(Integer, ForeignKey('user.id'), nullable = False)
    user = relationship(User)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'           : self.id,
           'name'         : self.name,
           'owner'        : self.user.name,
           'room'         : self.room.name,
           'description'  : self.description,
           'price'        : self.price,
       }


if __name__ == "__main__":
  # Remove existing database
  try:
    remove("room_item_user.db")
    print("Existing database removed!")
  except FileNotFoundError:
    print("No existing database found. Creating new one...")

  engine = create_engine('sqlite:///room_item_user.db')
  Base.metadata.create_all(engine)
  print("Database sucessfully set up!")
  print("Type 'python populate_db.py' in your terminal to populate the database")
