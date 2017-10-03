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
		<div class="container">
			<div class="row">
				<div class="one-half column">{content}</div>
			</div>
		</div>
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
				<h1>Hello</h1>
				<form method="POST" action="hello" enctype="multipart/form-data">
					<h2> What would you like me to say? </h2>
					<input type="text" name="message"><input type="submit" value="Submit">
				</form>
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

				restaurants = sessinon.query(Restaurant).all()

				# A single movie entry html template
				listRestaurant_element_html = '''
				<div class="row">
					<h3>{name}</h3>
					<a class="button button-primary" href="#">Edit</a>
					<a class="button button-red" href="#">Delete</a>
				</div>
				'''

				# Get List of restaurants
				listRestaurants = "<ul>"
				for restaurant in restaurants:
					listRestaurants += listRestaurant_element_html.format(name=restaurant.name)
				listRestaurants += "</ul>"

				self.wfile.write(main_page.format(content=listRestaurants))
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
				<h1>Okay, how about this: </h1>
				<h2>{text}</h2>
				<form method="POST" action="hello" enctype="multipart/form-data">
					<h2> What would you like me to say? </h2>
					<input type="text" name="message"><input type="submit" value="Submit">
				</form>
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