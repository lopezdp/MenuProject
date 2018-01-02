from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

# import CRUD operations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Need to figure out what my db_setup file is: restaurantMenuSchema.py
from restaurantMenuSchema import Base, Restaurant, MenuItem

# Create Session and connect to SQLite db
engine = create_engine('sqlite:///restaurantmenu.db')
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


#Fake Restaurants
restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}

restaurants = [{'name': 'The CRUDdy Crab', 'id': '1'}, {'name':'Blue Burgers', 'id':'2'},{'name':'Taco Hut', 'id':'3'}]


#Fake Menu Items
items = [{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach','price':'$1.99', 'course':'Appetizer','id':'1'},
{'name':'Cheese Pizza', 'description':'made with fresh cheese', 'price':'$5.99','course' :'Entree', 'id':'2'},
{'name':'Caesar Salad', 'description':'with fresh organic vegetables','price':'$5.99', 'course':'Entree','id':'3'},
{'name':'Iced Tea', 'description':'with lemon','price':'$.99', 'course':'Beverage','id':'4'},
{'name':'Chocolate Cake','description':'made with Dutch Chocolate', 'price':'$3.99', 'course':'Dessert','id':'5'}
]

item =  {'name':'Cheese Pizza','description':'made with fresh cheese','price':'$5.99','course' :'Entree'}

# Building API Endpoints/Route Handlers (GET Request)
@app.route('/')
@app.route('/restaurants/')
def showRestaurants():
    restaurant = restaurants
    # return "This page will show all restaurants"
    return render_template('restaurants.html', restaurant = restaurant)

@app.route('/restaurant/new/')
# Method to create newRestaurant
def newRestaurant():
    if request.method == 'POST':
        # Store restaurant input from form into newRestaurant
        newRestaurant = Restaurant(
            name = request.form['name'],
            street = request.form['street'],
            city = request.form['city'],
            state = request.form['state'],
            zipCode = request.form['zipCode'],
            phone = request.form['phone'],
            email = request.form['email'],
            website = request.form['website'],
            cuisine = request.form['cuisine'],
            description = request.form['description'],
            delivery = request.form['delivery']
        )
        # add newRestaurant item to db stage
        session.add(newRestaurant)
        # commit newRestaurant item to db
        session.commit()


    # return "This page will be for adding a new restaurant"

    return render_template('newRestaurant.html', restaurant = restaurant)

@app.route('/restaurant/<int:restaurant_id>/edit/')
def editRestaurant(restaurant_id):
    restaurant = restaurants[restaurant_id]
    # return "This page will be for editing restaurant %s" % restaurant_id
    return render_template('editRestaurant.html', restaurant = restaurant)

@app.route('/restaurant/<int:restaurant_id>/delete/')
def deleteRestaurant(restaurant_id):
    restaurant = restaurants[restaurant_id]
    # return "This page will be for deleting restaurant %s" % restaurant_id
    return render_template('deleteRestaurant.html', restaurant = restaurant)

@app.route('/restaurant/<int:restaurant_id>/menu/')
@app.route('/restaurant/<int:restaurant_id>/')
def showMenu(restaurant_id):
    restaurant = restaurants[restaurant_id]
    item = items
    # return "This page is the menu for restaurant %s" % restaurant_id
    return render_template('menu.html', restaurant = restaurant, items = item)

@app.route('/restaurant/<int:restaurant_id>/new/')
def newMenuItem(restaurant_id):
    # return "This page is for making a new menu item for restaurant %s" % restaurant_id
    return render_template('newMenuItem.html', restaurant_id = restaurant_id)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit/')
def editMenuItem(restaurant_id, menu_id):
    restaurant = restaurants[restaurant_id]
    item = items[menu_id]
    # return "This page is for editing menu item %s" % menu_id
    return render_template('editMenuItem.html', restaurant = restaurant, item = item)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete/')
def deleteMenuItem(restaurant_id, menu_id):
    restaurant = restaurants[restaurant_id]
    item = items[menu_id]
    # return "This page is for deleting menu item %s" % menu_id
    return render_template('deleteMenuItem.html', restaurant = restaurant, item = item)

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)