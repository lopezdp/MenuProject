# Restaurant Menus Web Application
This is a GrubHub clone application that allows the user to view different restaurant menus and to add, edit, or delete restaurants as needed. There is functionality for the user to add new, edit, and delete menu items from the selected restaurant menus also. The project is built using Python3 to create the _Route Handlers_ in _Flask_.

## Installation
1. Python 3.6.x is needed to run the back end of this Flask application
2. *Flask* and *SQLAlchemy* are needed to run this application
3. From a Terminal Run: `pip install Flask`
4. From a Terminal Run: `pip install SQLAlchemy`

## Documentation & Additional Information
1. The documentation will include instructions and examples on how to use this application

## Issues, Current, & Future Functionality
1. Users can Add New, Edit, & Delete Restaurants.
2. Users can Add New Menu Items for each Restaurant available in the catalog.
3. Users can Edit & Delete Menu Items for each Restaurant available in the catalog.
4. Users can view Menu from Restaurant List.
5. Data Driven Application Using SQLite3.
6. Application provides JSON API Endpoints for the following:
	* showRestaurants: `/restaurants/JSON`
	* showMenu: `/restaurant/restaurant_id/menu/JSON`
	* showItem: `/restaurant/restaurant_id/menu/menu_id/JSON`
7. Need to Style the page using Jinja templates & CSS.
8. Users can login and register using Google+ API.
9. Local Permission System to allow users private access to user content.
10. Facebook authentication soon...

## License
The content of this repository is licensed under a [**GNU General Public License v3.0**](https://choosealicense.com/licenses/gpl-3.0)
