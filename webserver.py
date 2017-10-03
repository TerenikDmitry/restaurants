from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Restaurant, Base, MenuItem

class WebServerHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			if self.path.endswith("/hello"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				message = "<html><body>"
				message += "Hello!"
				message += "<form method='POST' action='hello' enctype='multipart/form-data'>"
				message += "<h2> What would you like me to say? </h2>"
				message += "<input type='text' name='message'><input type='submit' value='Submit'>"
				message += "</form>"
				message += "</body></html>"
				self.wfile.write(message)
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

				output = "<html><body>"

				# Get List of restaurants
				listRestaurants = "<ul>"
				for restaurant in restaurants:
					listRestaurants += "<li>" + restaurant.name + "</li>"
				listRestaurants += "</ul>"
				output += listRestaurants

				output += "</body></html>"

				self.wfile.write(output)
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

			output = "<html><body>"
			output += "<h2> Okay, how about this: </h2>"
			output += "<h2> %s </h2>" % messagecontent[0]

			output += "<form method='POST' action='hello' enctype='multipart/form-data'>"
			output += "<h2> What would you like me to say? </h2>"
			output += "<input type='text' name='message'><input type='submit' value='Submit'>"
			output += "</form>"
			output += "</body></html>"

			self.wfile.write(output)
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