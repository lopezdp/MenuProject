from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response

# import CRUD operations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Need to figure out what my db_setup file is: restaurantMenuSchema.py
from restaurantMenuSchema import Base, Restaurant, MenuItem

# New Imports for Google Oauth Login functionality
from flask import session as login_session
import random
import string

# OAUTH IMPORTS
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

# Read & store the client_id from the client_secrets.json file
CLIENT_ID = json.loads(
    open('client_secrets.json','r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

app = Flask(__name__)

# Create Session and connect to SQLite db
engine = create_engine('sqlite:///restaurantMenus.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
        for x in range(32))
    login_session['state'] = state
    #return "The current session state is %s" % login_session['state']
    # RENDER the LOGIN.HTML TEMPLATE
    return render_template('login.html', STATE=state)

# Route handler to accept client-side calls from signInCallBack()
@app.route('/gconnect', methods = ['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        # if state tokens do not match then return 401
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # save request data in code variable
    code = request.data

    try:
        #Upgrade the auth code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope = '')
        oauth_flow.redirect_uri = 'postmessage'
        # credentials variable holds the request data
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to be sure the access token is valid
    access_token = credentials.access_token

    url = ("https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s" % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # Abort if there is an error with the access token
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        # Debug
        print("500 error print: " + result)
        return response

    # Ensure that the access_token is used by the intended person
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps('Token client ID does not match user ID'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is good for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current User is already Signed In'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Save the access_token for later use dude
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # Store data params into login_session params
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Format output
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    print("Done!")

    # Return output
    return output

# DISCONNECT - Revoke a user's token and reset their login session
@app.route("/gdisconnect")
def gdisconnect():
    # Only disconnect a connected user
    access_token = login_session.get('access_token')
    print("This is the access token: " + str(access_token))

    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Execute HTTP GET request to revoke current token.

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's session
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Sucessfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason the given token was invalid
        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

# Building API Endpoints/Route Handlers (GET Request)
@app.route('/')
@app.route('/restaurants/')
def showRestaurants():
    # query db and assign to restaurants variable
    restaurants = session.query(Restaurant).order_by(Restaurant.id.asc()).all()
    # return "This page will show all restaurants"
    return render_template('restaurants.html', restaurants = restaurants, title = "Restaurants")

@app.route('/restaurant/new/', methods = ['GET', 'POST'])
# Method to create newRestaurant
def newRestaurant():
    # Check to see if a user is logged in.
    if 'username' not in login_session:
        return redirect('/login')

    # If user is logged in then access newRestaurant page
    if request.method == 'POST':
        # Store restaurant input from form into newRestaurant
        newRestaurant = Restaurant(
            name = request.form['name'].strip(),
            street = request.form['street'].strip(),
            city = request.form['city'].strip(),
            state = request.form['state'].strip(),
            zipCode = request.form['zipCode'].strip(),
            phone = request.form['phone'].strip(),
            email = request.form['email'].strip(),
            website = request.form['website'].strip(),
            cuisine = request.form['cuisine'].strip(),
            description = request.form['description'].strip(),
            delivery = request.form['delivery'].strip()
        )
        # add newRestaurant item to db stage
        session.add(newRestaurant)
        # commit newRestaurant item to db
        session.commit()

        # flash message to indicate success
        flash("New Restaurant: " + newRestaurant.name + " ==> Created!")
        # redirect user to updated list of restaurants
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('newRestaurant.html', title = "New Restaurant Input")

@app.route('/restaurant/<int:restaurant_id>/edit/', methods = ['GET', 'POST'])
def editRestaurant(restaurant_id):
    # Check to see if a user is logged in.
    if 'username' not in login_session:
        return redirect('/login')

    # If user is logged in then access editRestaurant page
    # query db by restaurant_id and assign to restaurant variable
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        if request.form:
            # Store edited field data and POST to db
            restaurant.name = request.form['name'].strip()
            restaurant.street = request.form['street'].strip()
            restaurant.city = request.form['city'].strip()
            restaurant.state = request.form['state'].strip()
            restaurant.zipCode = request.form['zipCode'].strip()
            restaurant.phone = request.form['phone'].strip()
            restaurant.email = request.form['email'].strip()
            restaurant.website = request.form['website'].strip()
            restaurant.cuisine = request.form['cuisine'].strip()
            restaurant.description = request.form['description'].strip()
            restaurant.delivery = request.form['delivery'].strip()
        # add editRestaurant data to db stage
        session.add(restaurant)
        # commit editRestaurant data to db
        session.commit()

        # flash msg to indicate success
        flash("Edited Restaurant: " + restaurant.name + " ==> Updated!")
        # redirect user to updated list of restaurants
        return redirect(url_for('showRestaurants'))
    else:
        restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
        return render_template('editRestaurant.html', title = 'Edit Restaurant', restaurant = restaurant)

@app.route('/restaurant/<int:restaurant_id>/delete/', methods = ['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    # Check to see if a user is logged in.
    if 'username' not in login_session:
        return redirect('/login')

    # If user is logged in then access deleteRestaurant page
    # query db by restaurant_id and assign to restaurant variable
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        # delete restaurant object obtained from db query
        session.delete(restaurant)
        # commit delete to db
        session.commit()
        flash("Deleted Restaurant: " + restaurant.name + " ==> Deleted!")
        # redirect user to updated list of restaurants
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('deleteRestaurant.html', title = 'Confirm Delete Restaurant', restaurant = restaurant)

@app.route('/restaurant/<int:restaurant_id>/menu/')
@app.route('/restaurant/<int:restaurant_id>/')
def showMenu(restaurant_id):

    # query db to find Restaurant
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()

    # query db to find items for restaurant
    items = session.query(MenuItem).filter_by(restaurantid = restaurant_id).order_by(MenuItem.id.asc()).all()

    # return "This page is the menu for restaurant %s" % restaurant_id
    return render_template('menu.html', restaurant = restaurant, items = items)

@app.route('/restaurant/<int:restaurant_id>/new/', methods = ['GET', 'POST'])
def newMenuItem(restaurant_id):
    # Check to see if a user is logged in.
    if 'username' not in login_session:
        return redirect('/login')

    # If user is logged in then access newMenuItem page
    # query db to find Restaurant
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()

    if request.method == 'POST':
        # Store menuitem input from form into newMenuItem
        newMenuItem = MenuItem(
            name = request.form['name'].strip(),
            course = request.form['course'].strip(),
            description = request.form['description'].strip(),
            price = request.form['price'].strip(),
            restaurantid = restaurant_id
        )
        # add newMenuItem to db stage
        session.add(newMenuItem)
        # commit newMenuItem to db
        session.commit()

        # flash message to indicate success
        flash("New Menu Item: " + newMenuItem.name + " ==> Created!")
        # redirect user to updated list of menuItems for chosen restaurant
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('newMenuItem.html', title = "New Menu Item Input", restaurant = restaurant)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit/', methods = ['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    # Check to see if a user is logged in.
    if 'username' not in login_session:
        return redirect('/login')

    # If user is logged in then access editMenuItem page
    # query db by restaurant_id and menu_id and assign to restaurant and item variables
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    item = session.query(MenuItem).filter_by(id = menu_id).one()

    if request.method == 'POST':
        if request.form:
            # Store edited field data and POST to db
            item.name = request.form['name'].strip()
            item.course = request.form['course'].strip()
            item.description = request.form['description'].strip()
            item.price = request.form['price'].strip()
            #item.restaurantid = restaurant_id

        # add editMenuItem data to db stage
        session.add(item)
        # commit editMenuItem data to db
        session.commit()

        # flash msg to indicate success
        flash("Edit Item: " + item.name + " ==> Updated!")
        # redirect user to updated list of items
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
        return render_template('editMenuItem.html', title = 'Edit Menu Item', restaurant = restaurant, item = item)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete/', methods = ['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    # Check to see if a user is logged in.
    if 'username' not in login_session:
        return redirect('/login')

    # If user is logged in then access deleteMenuItem page
    # query db by restaurant_id and menu_id and assign to restaurant and item variables
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    item = session.query(MenuItem).filter_by(id = menu_id).one()

    if request.method == 'POST':
        # delete restaurant object obtained from db query
        session.delete(item)
        # commit delete to db
        session.commit()
        flash("Deleted item: " + item.name + " ==> Deleted!")
        # redirect user to updated list of restaurants
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('deleteMenuItem.html', title = 'Confirm Delete Menu Item', restaurant = restaurant, item = item)

# API Endpoints in JSON
#/restaurants/JSON
@app.route('/restaurants/JSON')
def showRestaurantsJSON():
    # query db for all restaurants to jsonify
    restaurants = session.query(Restaurant).all()
    # create json object of list of all Restaurants
    json = jsonify(Restaurants=[restaurant.serialize for restaurant in restaurants])
    # create a response object using flask make_response(responseObj, status)
    res = make_response(json, 200)
    # Change value of 'Content-Type' header as required
    res.headers['Content-Type'] = 'application/json'
    # return the response
    return res

#/restaurant/restaurant_id/menu/JSON
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def showMenuJSON(restaurant_id):
    # query db for all items to jsonify
    items = session.query(MenuItem).filter_by(restaurantid=restaurant_id)
    # create json object of list of all items for this restaurant
    json = jsonify(MenuItems=[item.serialize for item in items])
    # create a response object using flask make_response(responseObj, status)
    res = make_response(json, 200)
    # Change value of 'Content-Type' header as required
    res.headers['Content-Type'] = 'application/json'
    # return the response
    return res

#/restaurant/restaurant_id/menu/menu_id/JSON
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def showItemJSON(restaurant_id, menu_id):
    # query db for all item to jsonify
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    # create json object of single item selected from this restaurant
    json = jsonify(Item=[item.serialize])
    # create a response object using flask make_response(responseObj, status)
    res = make_response(json, 200)
    # Change value of 'Content-Type' header as required
    res.headers['Content-Type'] = 'application/json'
    # return the response
    return res




if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)