from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

# import CRUD operations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Need to figure out what my db_setup file is: restaurantMenuSchema.py
from restaurantMenuSchema import Base, Restaurant, MenuItem

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

# Building API Endpoints/Route Handlers (GET Request)
@app.route('/')
@app.route('/restaurants/')
def showRestaurants():
    # query db and assign to restaurants variable
    restaurants = session.query(Restaurant).order_by(Restaurant.id.asc()).all()
    # return "This page will show all restaurants"
    return render_template('restaurants.html', restaurants=restaurants, title="Restaurants")

@app.route('/restaurant/new/', methods=['GET', 'POST'])
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
        return render_template('newRestaurant.html', title="New Restaurant Input")

@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    # query db by restaurant_id and assign to restaurant variable
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
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
        flash("New Restaurant: " + restaurant.name + " ==> Updated!")
        # redirect user to updated list of restaurants
        return redirect(url_for('showRestaurants'))
    else:
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        return render_template('editRestaurant.html', title='Edit Restaurant', restaurant=restaurant)

@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    # query db by restaurant_id and assign to restaurant variable
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        # delete restaurant object obtained from db query
        session.delete(restaurant)
        # commit delete to db
        session.commit()
        flash("Former Restaurant: " + restaurant.name + " ==> Deleted!")
        # redirect user to updated list of restaurants
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('deleteRestaurant.html', title='Confirm Delete Restaurant', restaurant=restaurant)

@app.route('/restaurant/<int:restaurant_id>/menu/')
@app.route('/restaurant/<int:restaurant_id>/')
def showMenu(restaurant_id):

    # query db to find Restaurant
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()

    # query db to find items for restaurant
    items = session.query(MenuItem).filter_by(restaurantid = restaurant_id).order_by(MenuItem.id.asc()).all()

    # return "This page is the menu for restaurant %s" % restaurant_id
    return render_template('menu.html', restaurant = restaurant, items = items)

@app.route('/restaurant/<int:restaurant_id>/new/', methods =['GET', 'POST'])
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
        return render_template('newMenuItem.html', title = "New Menu Item Input")

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit/', methods =['GET', 'POST'])
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
            item.zipCode = request.form['zipCode'].strip()
            #item.restaurantid = restaurant_id

        # add editMenuItem data to db stage
        session.add(item)
        # commit editMenuItem data to db
        session.commit()

        # flash msg to indicate success
        flash("New Item: " + item.name + item.restaurantid + " ==> Updated!")
        # redirect user to updated list of items
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
        return render_template('editMenuItem.html', title = 'Edit Restaurant', restaurant = restaurant, item = item)








@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete/')
def deleteMenuItem(restaurant_id, menu_id):
    restaurant = restaurants[restaurant_id]
    item = items[menu_id]
    # return "This page is for deleting menu item %s" % menu_id
    return render_template('deleteMenuItem.html', restaurant = restaurant, item = item)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)