from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

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
    # return "This page will show all my restaurants"
    return render_template('restaurants.html', restaurant = restaurant)

@app.route('/restaurant/new/')
def newRestaurant():
    
    # return "This page will be for making a new restaurant"
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