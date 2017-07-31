#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask import session as login_session
from flask import make_response

import random, string

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database_setup import Base, User, Room, Item


from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json

import requests

from copy import deepcopy

# Create an app instance
app = Flask(__name__)

# Connect to database and create database session
engine = create_engine('sqlite:///room_item_user.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

# Constants
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

# Helper functions
def get_room_from_id(room_id):
	# Return a Room instance given its id
	try:
		room = session.query(Room).filter_by(id = room_id).one()
		return room
	except NoResultFound:
		return None

def get_item_from_id(item_id):
	# Return an Item instance given its id
	try:
		item = session.query(Item).filter_by(id = item_id).one()
		return item
	except NoResultFound:
		return None

def get_rooms():
	# Return all Room instances belonging the user that is currently logged in
	owner_id = getUserID(login_session.get("email"))
	return session.query(Room).filter_by(user_id = owner_id)

def createUser(login_session):
	# Create new user based on user's information stored in login_session
	newUser = User(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])
	session.add(newUser)
	session.commit()
	user = session.query(User).filter_by(email = login_session['email']).one()
	return user.id

def getUserInfo(user_id):
	# Return User instance given his/her id
	user = session.query(User).filter_by(id = user_id).one()
	return user

def getUserID(email):
	# Return a user' id given his/her email address
	try:
		user = session.query(User).filter_by(email = email).one()
		return user.id
	except:
		return None

# Main routes
@app.route('/')
@app.route('/rooms/')
def allRooms():
	# Show all rooms

	# Get all Room instances that belong to the user
	rooms = get_rooms()

	return render_template("rooms.html", rooms = rooms, login_session = login_session)


@app.route('/room/add/', methods = ['GET','POST'])
def addRoom():
	# Add new room

	# Redirect to /login if user is not logged in
	if not login_session.get("username"):
		flash("Please log in to add room")
		return(redirect(url_for("login")))

	rooms = get_rooms() # for constructing left-side bar

	if request.method == "POST":
		name = request.form['name']
		if not name:
			return "You must fill in room's name"
		new_room = Room(name = name, user_id = getUserID(login_session["email"]))
		session.add(new_room)
		session.commit()
		flash("{} is added!".format(new_room.name))
		return redirect(url_for("allRooms"))
	else:
		return render_template("addroom.html", title = "Add room",
		room_id = None, rooms = rooms, room = None, login_session = login_session)

@app.route('/room/<int:room_id>/edit/', methods = ['GET','POST'])
def editRoom(room_id):
	# Edit existing rooms

	# Check if room_id exists
	room = get_room_from_id(room_id)
	if not room:
		return "No room found for room id: {}".format(room_id)

	# Redirect to /login if user is not logged in
	email = login_session.get("email")
	if not email:

		flash("Please log in to edit your rooms")
		return(redirect(url_for("login")))

	# Get current user id:
	user_id = getUserID(email)

	# Only allow access to owner of the room
	if user_id != room.user_id:
		return "You do not have permission to edit this room!"

	rooms = get_rooms() # for constructing left-side bar

	if request.method == "POST":
		name = request.form["name"]

		if name:
			old_name = room.name
			room.name = name
			session.add(room)
			session.commit()

			flash("{} has been renamed to {}".format(old_name, name))
			return redirect(url_for("showItems", room_id = room_id))
		else:
			return "You must fill in room's name"
	else:
		return render_template("editroom.html", title = "Rename room",
		room_id = room_id, rooms = rooms, room = room, login_session = login_session)


@app.route('/room/<int:room_id>/delete/')
def deleteRoom(room_id):
	# Delete existing rooms

	# Check if room_id exists
	room = get_room_from_id(room_id)
	if not room:
		return "No room found for room id: {}".format(room_id)

	# Redirect to /login if user is not logged in
	email = login_session.get("email")
	if not email:
		flash("Please log in to delete your rooms")
		return(redirect(url_for("login")))

	# Get current user id:
	user_id = getUserID(email)

	# Only allow access to owner of the room
	if user_id != room.user_id:
		return "You do not have permission to delete this room!"

	rooms = get_rooms() # for constructing left-side bar

	# Get query parameter
	delete = request.args.get('delete')

	if not delete:
		return render_template("deleteroom.html", title = "Delete room",
		rooms = rooms, room = room, login_session = login_session)

	if delete=="true":
		# First delete all items within the room:
		items = session.query(Item).filter_by(room_id = room.id).all()
		for item in items:
			session.delete(item)
			session.commit()

		# Then delete the room itself
		name = room.name
		session.delete(room)
		session.commit()

		flash("{} and all items within it have been removed!".format(name))
		return redirect(url_for("allRooms"))

	elif delete=="false":
		return redirect(url_for("showItems", room_id = room_id))
	else:
		return "Invalid value for delete parameter: {}".format(delete)


@app.route('/room/<int:room_id>/items/')
def showItems(room_id):
	# Show all items from an existing room

	# Check if room_id exists
	room = get_room_from_id(room_id)
	if not room:
		return "No room found for room id: {}".format(room_id)

	# Redirect to /login if user is not logged in
	email = login_session.get("email")
	if not email:
		flash("Please log in to view your items")
		return(redirect(url_for("login")))

	# Get current user id:
	user_id = getUserID(email)

	# Only allow access to owner of the room
	if user_id != room.user_id:
		return "You do not have permission to view items in this room!"

	rooms = get_rooms() # for constructing left-side bar

	items = session.query(Item).filter_by(room_id = room_id).all()

	return render_template("items.html", title = "Items in {}".format(room.name),
	items = items, length = len(items), room_id = room_id,
	rooms = rooms, room = room, login_session = login_session)

@app.route('/room/<int:room_id>/items/<int:item_id>/')
def showSingleItem(room_id, item_id):
	# Show a single item

	# Check if room_id exists
	room = get_room_from_id(room_id)
	if not room:
		return "No room found for room id: {}".format(room_id)

	# Redirect to /login if user is not logged in
	email = login_session.get("email")
	if not email:
		flash("Please log in to view your items")
		return(redirect(url_for("login")))

	# Get current user id:
	user_id = getUserID(email)

	# Only allow access to owner of the room
	if user_id != room.user_id:
		return "You do not have permission to view items in this room!"

	rooms = get_rooms() # for constructing left-side bar

	item = session.query(Item).filter_by(id = item_id).one()

	# Check if the item actually belongs to the room
	if item.room_id != room.id:
		return "{} (item-id: {}) does not belong to {} (room-id: {})".format(item.name,
			item.id, room.name, room.id)

	return render_template("item.html", title = item.name,
		item = item, room_id = room_id, rooms = rooms, room = room, login_session = login_session)


@app.route('/room/<int:room_id>/items/add/', methods = ['GET','POST'])
def addItem(room_id):
	# Add a new item to an existing room

	# Check if room_id exists
	room = get_room_from_id(room_id)
	if not room:
		return "No room found for room id: {}".format(room_id)

	# Redirect to /login if user is not logged in
	email = login_session.get("email")
	if not email:
		flash("Please log in to add new items")
		return(redirect(url_for("login")))

	# Get current user id:
	user_id = getUserID(email)

	# Only allow access to owner of the room
	if user_id != room.user_id:
		return "You do not have permission to add items to this room!"

	rooms = get_rooms() # for constructing left-side bar

	if request.method == "POST":
		name = request.form["name"]
		if not name:
			return "You must fill in item's name"

		description = request.form["description"]
		price = request.form["price"]

		new_item = Item(name = name, description = description,
			price = price, room_id = room_id, user_id = user_id)

		session.add(new_item)
		session.commit()

		flash("{} is added to {}!".format(name, room.name))
		return redirect(url_for("showItems", room_id = room_id))

	else:
		return render_template("additem.html", title = "Add new item to {}".format(room.name),
			room_id = room_id, rooms = rooms, room = room, login_session = login_session)

@app.route('/room/<int:room_id>/items/<int:item_id>/edit/', methods = ["GET", "POST"])
def editItem(room_id, item_id):
	# Edit an existing item

	# Check if room_id exists
	room = get_room_from_id(room_id)
	if not room:
		return "No room found for room id: {}".format(room_id)

	# Redirect to /login if user is not logged in
	email = login_session.get("email")
	if not email:
		flash("Please log in to edit your items")
		return(redirect(url_for("login")))

	# Get current user id:
	user_id = getUserID(email)

	# Only allow access to owner of the room
	if user_id != room.user_id:
		return "You do not have permission to edit item in this room!"

	rooms = get_rooms() # for constructing left-side bar

	# Check if the item actually exists
	item = get_item_from_id(item_id)
	if not item:
		return "Item id {} does not exist".format(item_id)

	# Check if the item belongs to the room of id: room_id
	if item.room_id != room.id:
		return "{} (item-id: {}) does not belong to {} (room-id: {})".format(item.name,
			item.id, room.name, room.id)

	if request.method == "POST":
		name = request.form["name"]
		if name:
			item.name = name
		else:
			return "You must fill in item's name"

		item.description = request.form["description"]
		item.price = request.form["price"]

		session.add(item)
		session.commit()

		flash("Item edited!")
		return redirect(url_for("showItems", room_id = room_id))

	return render_template("edititem.html", title = "Edit item", item = item,
		room_id = room_id, rooms = rooms, room = room, login_session = login_session)

@app.route('/room/<int:room_id>/items/<int:item_id>/delete/')
def deleteItem(room_id, item_id):
	# Delete an existing item

	# Check if room_id exists
	room = get_room_from_id(room_id)
	if not room:
		return "No room found for room id: {}".format(room_id)

	# Redirect to /login if user is not logged in
	email = login_session.get("email")
	if not email:
		flash("Please log in to delete your items")
		return(redirect(url_for("login")))

	# Get current user id:
	user_id = getUserID(email)

	# Only allow access to owner of the room
	if user_id != room.user_id:
		return "You do not have permission to delete item in this room!"

	rooms = get_rooms() # for constructing left-side bar

	# Check if the item actually exists
	item = get_item_from_id(item_id)
	if not item:
		return "No item found for room id: {}".format(item_id)

	# Check if the item belongs to the room of id: room_id
	if item.room_id != room.id:
		return "{} (item-id: {}) does not belong to {} (room-id: {})".format(item.name,
			item.id, room.name, room.id)

	# Get query parameter
	delete = request.args.get('delete')

	if not delete:
		return render_template("deleteitem.html", title = "Delete item",
		item = item, rooms = rooms, room = room, login_session = login_session)

	if delete == "true":
		flash("{} has been removed from {}".format(item.name, room.name))
		session.delete(item)
		session.commit()
		return redirect(url_for("showItems", item_id = item_id, room_id = room_id))

	elif delete=="false":
		flash("Cancel deleting {}".format(item.name))
		return redirect(url_for("showItems", item_id = item_id, room_id = room_id))

	else:
		return "Invalid value for delete parameter: {}".format(delete)


# Log-in and Log-out
@app.route('/login')
@app.route('/login/')
def login():
	# Generate random state token to prevent forgery
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
	# Store it in the session for later validation
	login_session['state'] = state

	return render_template("login.html", STATE = state, login_session = login_session)

#Handling browser' resquests regarding Google API authentication
@app.route('/gconnect', methods=['POST'])
def gconnect():
	if request.args.get('state') != login_session['state']:
	# Check parameter 'state', if state code sent in does not match the one generated by server:
		response = make_response(json.dumps('Invalid state parameter'), 401)
		response.headers['content-type'] = 'application/json'
		return (response)

	# if state paramaters match, collect the one-time-code/authorization code sent by the browser
	code = request.data

	try:
		# Upgrade the authorization code into a credentials object

		# Create a flow object from the key information in client_secrets.json
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'

		# Exchange authorization code for credential object
		# Credential object returned by Google API will be stored as a variable
		credentials = oauth_flow.step2_exchange(code)

	except FlowExchangeError:
		response = make_response(json.dump('Failed to upgrade the authorization code.'), 401)
		response.headers['content-type'] = 'application/json'
		return response

	# Check that the access token (inside credential object) is valid
	access_token = credentials.access_token
		# Google API will help you verify the access token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1].decode())

	# If there was an error in the access token info, abort.
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['content-type'] = 'applicatin/json'

	# Verify that the access token is used for the intended user
	gplus_id = credentials.id_token['sub']

	if result['user_id'] != gplus_id:
		response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
		response.headers['content-type'] = 'application/json'
		return response

	# Verify that the access token is valid for this app.
	if result['issued_to'] != CLIENT_ID:
		response = make_response(json.dump("Token's client ID does not match app's."), 401)
		print("Token's client ID does not match app's.")
		response.headers["content-type"] = "application/json"
		return response

	# Check if the user is already logged in
	stored_credentials = login_session.get('credentials')
	stored_gplus_id = login_session.get('gplus_id')

	if stored_credentials is not None and gplus_id == stored_gplus_id:
		return "<h1>{} is already connected</h1>".format(login_session["username"])

	# store the access token in the session for later use
	login_session['credentials'] = credentials.to_json()
	login_session['gplus_id'] = gplus_id

	# Get user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params = params)

	data = answer.json()

	login_session["provider"] = "google"
	login_session['username'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']

	# If this is the first log in, create a new user in the database
	if getUserID(login_session['email']) == None:
		login_session['user_id'] = createUser(login_session)
	else:
		login_session['user_id'] = getUserID(login_session['email'])

	output = '''
			<h1>Login successful! Welcome, {}!</h1>
		  '''.format(login_session['username'])

	return output

# Handling Google Logout
@app.route('/logout')
@app.route('/logout/')
def logout():
	# Only disconnect a connected user:
	credentials = login_session.get("credentials")
	if credentials is None:
		response = make_response(json.dumps('Current user not connected.'), 401)
		response.headers["content-type"] = "application/json"
		return response

	# Execute HTTP GET request to revoke current token
	access_token = json.loads(credentials).get("access_token")
	url = "https://accounts.google.com/o/oauth2/revoke?token=%s" %access_token
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]

	if result['status'] == '200':
		# Reset the user's session.
		del login_session['credentials']
		del login_session['gplus_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']
		del login_session['provider']

		response = make_response(json.dumps("Successfully disconnected."), 200)
		response.headers["content-type"] = "application/json"
		return response
	else:
		# For whatever reason, the token is invalid.
		response = make_response(json.dumps("Failed to revoke token for given user! Please try to login with another Google Account"), 400)
		response.headers["content-type"] = "application/json"
		return response

# API End-points:
@app.route('/JSON')
def JSON():
	# Return information about rooms and their items in JSON format

	# Check if the user is logged in
	if not login_session.get("username"):
		response = make_response(json.dumps("Please log in at {} to get access to the API".format(url_for('login'))), 401)
		response.headers['content-type'] = 'application/json'
		return response

	# Get all Room instances that belong the currently logged-in user
	rooms = session.query(Room).filter_by(user_id = getUserID(login_session["email"])).all()

	# Constructing the object to put in to JSON file
	rooms_list = []
	for room in rooms:
		items = session.query(Item).filter_by(room_id = room.id).all()
		items_list = [item.serialize for item in items]
		room_dictionary = deepcopy(room.serialize)
		room_dictionary["items"] = items_list
		rooms_list += [room_dictionary]

	return jsonify(Rooms = rooms_list)

if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)