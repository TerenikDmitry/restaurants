from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

## import CRUD operation
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem

## Create session and connect to DB
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/restaurants')
def restaurantList():
    restaurants = session.query(Restaurant).all()

    return render_template('restaurants.html',restaurants=restaurants)

@app.route('/restaurants/<int:restaurantID>/')
@app.route('/restaurants/<int:restaurantID>/menu')
def restaurantMenu(restaurantID):
    restaurant = session.query(Restaurant).filter_by(id=restaurantID).one_or_none()
    menu_items = []

    if restaurant != None:
        menu_items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
        return render_template('menu.html',restaurant=restaurant,items=menu_items)
    else:
        return render_template('error.html',message="Oops! There is no such restaurant in the database")

@app.route('/restaurants/<int:restaurantID>/edit')
def restaurantEdit(restaurantID):
    restaurant = session.query(Restaurant).filter_by(id=restaurantID).one_or_none()

    if restaurant != None:
        return render_template('editRestaurant.html',restaurant=restaurant)
    else:
        return render_template('error.html',message="Oops! There is no such restaurant in the database")

@app.route('/restaurants/<int:restaurantID>/delete', methods=['GET','POST'])
def restaurantDelete(restaurantID):
    restaurant = session.query(Restaurant).filter_by(id=restaurantID).one_or_none()

    if restaurant != None:
        if request.method == 'POST':
            session.delete(restaurant)
            session.commit()
            return redirect(url_for('restaurantList'))
        else:
            return render_template('deleteRestaurant.html',restaurant=restaurant)
    else:
        return render_template('error.html',message="Oops! There is no such restaurant in the database")

@app.route('/restaurants/<int:restaurantID>/menu/<int:menuID>/edit')
def menuEdit(restaurantID,menuID):
    restaurant = session.query(Restaurant).filter_by(id=restaurantID).one_or_none()

    if restaurant != None:
        menu_item = session.query(MenuItem).filter_by(id=menuID).one_or_none()
        return render_template('editMenuItem.html',menu_item=menu_item,restaurant=restaurant)
    else:
        return render_template('error.html',message="Oops! There is no such restaurant in the database")

@app.route('/restaurants/<int:restaurantID>/menu/<int:menuID>/delete')
def menuDelete(restaurantID,menuID):
    restaurant = session.query(Restaurant).filter_by(id=restaurantID).one_or_none()

    if restaurant != None:
        menu_item = session.query(MenuItem).filter_by(id=menuID).one_or_none()
        return render_template('deleteMenuItem.html',menu_item=menu_item,restaurant=restaurant)
    else:
        return render_template('error.html',message="Oops! There is no such restaurant in the database")

@app.route('/restaurants/<int:restaurantID>/add')
def menuAdd(restaurantID):
    restaurant = session.query(Restaurant).filter_by(id=restaurantID).one_or_none()

    if restaurant != None:
        return render_template('addMenuItem.html',restaurant=restaurant)
    else:
        return render_template('error.html',message="Oops! There is no such restaurant in the database")

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)