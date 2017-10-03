from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Restaurant, Base, MenuItem

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
				f = open(os.curdir+os.sep+self.path)
				self.send_response(200)
				self.send_header('Content-type', 'text/css')
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
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
							<input type="text" name="message"><input type="submit" value="Submit">
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
							<input type="text" name="nameOfRestaurant" placeholder="Name of new restaurant"><input type="submit" value="Submit">
						</form>
					</div>
				</div>
				'''

				self.wfile.write(main_page.format(content=output))
				return
			if self.path.endswith("/restaurants"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				engine = create_engine('sqlite:///restaurantmenu.db')
				Base.metadata.bind = engine
				DBSession = sessionmaker(bind=engine)
				sessinon = DBSession()	

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
					<a class="button button-primary" href="#">Edit</a>
					<a class="button button-red" href="#">Delete</a>
				</div>
				'''
				# New Restaurant html template
				add_block_html = '''
				<div class="container values">
					<div class="row">
						<a class="button button-primary" href="/new">Add a new Restaurant</a>
					</div>
				</div>
				'''

				restaurants = sessinon.query(Restaurant).all()
				listRestaurantElements = ""
				# Get List of restaurants
				for restaurant in restaurants:
					listRestaurantElements += list_restaurant_element_html.format(name=restaurant.name)
				listRestaurant = list_restaurant_html.format(content=listRestaurantElements)

				output = listRestaurant + add_block_html

				self.wfile.write(main_page.format(content=output))
				return
		except IOError:
			self.send_error(404, 'File Not Found: %s' % self.path)

	def do_POST(self):
		try:
			self.send_response(301)
			self.end_headers()

			ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
			if ctype == 'multipart/form-data':
				fields = cgi.parse_multipart(self.rfile, pdict)
				messagecontent = fields.get('message')

			output = '''
				<div class="section values">
					<div class="container">
						<h2>Okay, how about this:</h2>
						<h2>{text}</h2>
						<form method="POST" action="hello" enctype="multipart/form-data">
							<h2> What would you like me to say? </h2>
							<input type="text" name="message"><input type="submit" value="Submit">
						</form>
					</div>
				</div>
				'''

			self.wfile.write(main_page.format(content=output.format(text=messagecontent[0])))
			return
		except:
			pass

def main():
	try:
		port = 8080
		server = HTTPServer(('', port), WebServerHandler)
		print "Web Server running on port %s" % port
		server.serve_forever()
	except KeyboardInterrupt:
		print " ^C entered, stopping web server...."
		server.socket.close()

if __name__ == '__main__':
	main()