from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Room, Item

engine = create_engine('sqlite:///room_item_user.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create dummy user
User1 = User(name="NGUYEN TIEN DAT", email="dat.ntdat@gmail.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Create rooms for the user
living_room = Room(user_id = 1, name="Living Room")
session.add(living_room)
session.commit()

bed_room = Room(user_id=1, name="Bed Room")
session.add(bed_room)
session.commit()

bath_room = Room(user_id=1, name="Bath Room")
session.add(bath_room)
session.commit()

kitchen = Room(user_id=1, name="Kitchen")
session.add(kitchen)
session.commit()


# Create items
tv = Item(user_id=1, room_id=1, name="TV", description="Samsung 4k", price="$ 1000")
session.add(tv)
session.commit()

sofa = Item(user_id=1, room_id=1, name="Sofa", description="Leather Softness", price="$ 800")
session.add(sofa)
session.commit()

bed = Item(user_id=1, room_id=2, name="Bed", description="Zzz", price="$ 500")
session.add(bed)
session.commit()

lamp = Item(user_id=1, room_id=2, name="Lamp", description="Shine The Night", price="$ 75")
session.add(lamp)
session.commit()

toilet = Item(user_id=1, room_id=3, name="Toilet", description="Poop Premium", price="$ 2580")
session.add(toilet)
session.commit()

mirror = Item(user_id=1, room_id=3, name="Mirror", description="Beauty Me", price="$ 530")
session.add(mirror)
session.commit()

stove = Item(user_id=1, room_id=4, name="Stove", description="Roast That Soup", price="$ 990")
session.add(stove)
session.commit()

basin = Item(user_id=1, room_id=4, name="Basin", description="Wash The Food", price="$ 149")
session.add(basin)
session.commit()

# Feedback
print("Database successfully populated")