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
    return "The current session state is %s" % login_session['state']

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