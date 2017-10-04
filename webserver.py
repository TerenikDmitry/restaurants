from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi

import os
import ntpath

## import CRUD operation
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem

## Create session and connect to DB
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Styles and scripting for the page
main_page = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Terenik!</title>
    <meta name="description" content="">
    <meta name="author" content="">

    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="//fonts.googleapis.com/css?family=Raleway:400,300,600" rel="stylesheet" type="text/css">
    <link rel="stylesheet" href="css/normalize.css">
    <link rel="stylesheet" href="css/skeleton.css">
    <link rel="stylesheet" href="css/custom.css">
</head>
<body>
    <div class="section values">
        {content}
    </div>
</body>
</html>
'''

class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith(".css"):
                head, tail = os.path.split(self.path)
                f = open(os.curdir+os.sep+"css/"+tail)
                self.send_response(200)
                self.send_header('Content-type', 'text/css')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                self.wfile.write(os.curdir+os.sep+"css/"+tail)
                return
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = '''
                <div class="section values">
                    <div class="container">
                        <h2>Hello</h2>
                        <form method="POST" action="hello" enctype="multipart/form-data">
                            <h2> What would you like me to say? </h2>
                            <input type="text" name="message">
                            <input type="submit" value="Submit">
                        </form>
                    </div>
                </div>
                '''

                self.wfile.write(main_page.format(content=output))
                return
            if self.path.endswith("/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = '''
                <div class="section values">
                    <div class="container">
                        <h2>Add a new Restaurant: </h2>
                        <form method="POST" action="new" enctype="multipart/form-data">
                            <input type="text" name="nameOfRestaurant" placeholder="Name of new restaurant">
                            <input type="submit" value="Add">
                        </form>
                        <a class="button button-primary" href="/restaurants">Back to the list of restaurants</a>
                    </div>
                </div>
                '''

                self.wfile.write(main_page.format(content=output))
                return
            if self.path.endswith("/edit"):
                idOfRestaurant = self.path.split("/")[-2]
                restaurant = session.query(Restaurant).filter_by(id = idOfRestaurant).one()
                if restaurant != []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    output = '''
                    <div class="section values">
                        <div class="container">
                            <h2>Edit "{old_name}"</h2>
                            <form method="POST" action="edit" enctype="multipart/form-data">
                                <input type="text" name="nameOfRestaurant" placeholder="New name">
                                <input type="submit" value="Edit">
                            </form>
                            <a class="button button-primary" href="/restaurants">Back to the list of restaurants</a>
                        </div>
                    </div>
                    '''

                self.wfile.write(main_page.format(content=output.format(old_name=restaurant.name)))
            if self.path.endswith("/delete"):
                idOfRestaurant = self.path.split("/")[-2]
                restaurant = session.query(Restaurant).filter_by(id = idOfRestaurant).one()
                if restaurant != []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    output = '''
                    <div class="section values">
                        <div class="container">
                            <h2>Delete "{old_name}"?</h2>
                            <form method="POST" action="delete" enctype="multipart/form-data">
                                <a class="button button-primary" href="/restaurants">Back</a>
                                <input class="button-red" type="submit" value="Delete">
                            </form>
                        </div>
                    </div>
                    '''

                self.wfile.write(main_page.format(content=output.format(old_name=restaurant.name)))
            if self.path.endswith("/restaurants"):
                # Get List of restaurants
                restaurants = session.query(Restaurant).all()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                # Restaurants entry html template
                list_restaurant_html = '''
                <div class="container">
                    {content}
                </div>
                '''
                # A single Restaurant entry html template
                list_restaurant_element_html = '''
                <div class="row">
                    <h3>{name}</h3>
                    <a class="button button-primary" href="/restaurants/{id}/edit">Edit</a>
                    <a class="button button-red" href="/restaurants/{id}/delete">Delete</a>
                </div>
                '''
                # New Restaurant html template
                add_block_html = '''
                <div class="container values">
                    <div class="row">
                        <a class="button button-primary" href="/restaurants/new">Add a new Restaurant</a>
                    </div>
                </div>
                '''

                listRestaurantElements = ""
                for restaurant in restaurants:
                    listRestaurantElements += list_restaurant_element_html.format(name=restaurant.name,id=restaurant.id)
                listRestaurant = list_restaurant_html.format(content=listRestaurantElements)

                self.wfile.write(main_page.format(content=(add_block_html + listRestaurant)))
                return
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            self.send_response(301)
            self.end_headers()

            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            output = ""

            if self.path.endswith("/hello"):
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('message')

                helloAndText = '''
                <div class="section values">
                    <div class="container">
                        <h2>You say: {text}</h2>
                        <form method="POST" action="hello" enctype="multipart/form-data">
                            <h2> What would you like me to say? </h2>
                            <input type="text" name="message"><input type="submit" value="Submit">
                        </form>
                    </div>
                </div>
                '''
                output = helloAndText.format(text=messagecontent[0])
            if self.path.endswith("/restaurants/new"):
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)

                messagecontent = fields.get("nameOfRestaurant")[0]
                restaurant = Restaurant(name = messagecontent)
                session.add(restaurant)
                session.commit()

                result = '''
                <div class="section values">
                    <div class="container">
                        <h2>Restaurant '{content}' added!</h2>
                        <a class="button button-primary" href="/restaurants">Back to the list of restaurants</a>
                    </div>
                </div>
                '''

                output = result.format(content=messagecontent)
            if self.path.endswith("/delete"):
                idOfRestaurant = self.path.split("/")[-2]

                restaurant = session.query(Restaurant).filter_by(id = idOfRestaurant).one()
                if restaurant != []:
                    result = '''
                    <div class="section values">
                        <div class="container">
                            <h2>Deleted '{old}'!</h2>
                            <a class="button button-primary" href="/restaurants">Back to the list of restaurants</a>
                        </div>
                    </div>
                    '''
                    output = result.format(old=restaurant.name)

                    session.delete(restaurant)
                    session.commit()
                else:
                    output = '''
                    <div class="section values">
                        <div class="container">
                            <h2>ERROR</h2>
                            <a class="button button-primary" href="/restaurants">Back to the list of restaurants</a>
                        </div>
                    </div>
                    '''
            if self.path.endswith("/edit"):
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)

                newName = fields.get("nameOfRestaurant")[0]
                idOfRestaurant = self.path.split("/")[-2]

                restaurant = session.query(Restaurant).filter_by(id = idOfRestaurant).one()
                if restaurant != []:
                    result = '''
                    <div class="section values">
                        <div class="container">
                            <h2>Old name '{old}' added!</h2>
                            <h2>New name '{new}' added!</h2>
                            <a class="button button-primary" href="/restaurants">Back to the list of restaurants</a>
                        </div>
                    </div>
                    '''
                    output = result.format(old=restaurant.name,new=newName)

                    restaurant.name = newName
                    session.add(restaurant)
                    session.commit()

            self.wfile.write(main_page.format(content=output))
            return
        except:
            pass

def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print ("Web Server running on port %s" % port)
        server.serve_forever()
    except KeyboardInterrupt:
        print (" ^C entered, stopping web server....")
        server.socket.close()

if __name__ == '__main__':
    main()