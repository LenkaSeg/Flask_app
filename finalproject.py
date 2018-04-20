from flask import Flask, render_template, url_for, redirect, request, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
app = Flask(__name__)



engine = create_engine('sqlite:///projectmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/restaurants/JSON')
def showRestaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(Restaurant=[i.serial for i in restaurants])

@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def showMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id).all()
    return jsonify(MenuItem=[i.serialize for i in items])


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuitemJSON(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    item = session.query(MenuItem).filter_by(id=restaurant.id).one()
    # but here instead of returning a template it will return this jsonify class and
    #  use a loop to serialize all my database entries
    return jsonify(MenuItem=item.serialize)

@app.route('/', methods=['GET'])
@app.route('/restaurants/', methods=['GET'])

def showRestaurants():
    restaurants = session.query(Restaurant).all()
    if not restaurants:
        flash("there are no restaurants")
    return render_template('restaurants.html', restaurants=restaurants)

@app.route('/restaurants/new/', methods=['GET', 'POST'])

def newRestaurant():
    if request.method == 'POST': # creating a new menu item, searching for POST method
        # and extracting the name field using the request.form
        newrest = Restaurant(name=request.form['name'])
        session.add(newrest)
        session.commit()
        flash("new menu item created!") # flash message
    # now to redirect the user back to the main user page I can use helper function
    #  called redirect, don't forget to import it
        return redirect(url_for('showRestaurants'))
    #restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()

    #else:
    return render_template('newrestaurant.html')


@app.route('/restaurants/<int:restaurant_id>/edit/', methods = ['GET','POST'])

def editRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        restaurant.name=request.form['name']
        session.add(restaurant)
        session.commit()
        flash('succesfully edited')
        return redirect(url_for('showRestaurants'))
    return render_template('editrestaurant.html', restaurant=restaurant)

@app.route('/restaurants/<int:restaurant_id>/delete/', methods = ['GET', 'POST'])

def deleteRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method =='POST':
        session.delete(restaurant)
        session.commit()
        flash('restaurant successfuly deleted')
        return redirect(url_for('showRestaurants', restaurant = restaurant))
    return render_template('deleterestaurant.html', restaurant=restaurant)


@app.route('/restaurants/<int:restaurant_id>/')
@app.route('/restaurants/<int:restaurant_id>/menu/')

def showMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id).all()
    if not items:
        flash("there are no menu items")
    appetizers = []
    entrees = []
    desserts = []
    beverages = []
    for item in items:
        if item.course.lower() == 'appetizer': # always compare lowercases!
            appetizers.append(item)
        elif item.course.lower() == 'entree':
            entrees.append(item)
        elif item.course.lower() == 'dessert':
            desserts.append(item)
        elif item.course.lower() == 'beverage':
            beverages.append(item)
        else:
            print(item.course, 'something is not right')
    return render_template('menu.html', restaurant=restaurant, items=items, appetizers=appetizers,
                           entrees=entrees, desserts=desserts, beverages=beverages, restaurant_id=restaurant_id)


@app.route('/restaurants/<int:restaurant_id>/menu/new/', methods=['GET', 'POST'])

def newMenuItem(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).all()
    if request.method == 'POST':
        newitem = MenuItem(name=request.form['name'], description=request.form['description'],
                           price=request.form['price'], course=request.form['course'], restaurant_id=restaurant_id)
        session.add(newitem)
        session.commit()
        flash("new menu item added")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    return render_template('newmenuitem.html', restaurant=restaurant,
                           restaurant_id=restaurant_id)


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/edit/', methods=['GET', 'POST'])

def editMenuItem(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        item.price = request.form['price']
        item.course = request.form['course']
        session.add(item)
        session.commit()
        flash("succesfully edited")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id, menu_id=menu_id))
    return render_template('editmenuitem.html', restaurant=restaurant, item = item)


@app. route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/delete/', methods=['GET', 'POST'])

def deleteMenuItem(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("menu item deleted!")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id, menu_id=menu_id))
    return render_template('deletemenuitem.html', restaurant=restaurant, restaurant_id=restaurant_id, item = item)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)