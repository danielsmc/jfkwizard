import json
import urllib2
import webapp2

from google.appengine.api import memcache

ashmont_stops = set(["Ashmont","Shawmut","Fields Corner","Savin Hill"])
braintree_stops = set(["Braintree","Quincy Adams","Quincy Center","Wollaston","North Quincy"])



def putTrip(trip_data):
	if len(trip_data['Predictions']) > 0:
		trip_id = trip_data['TripID']
		first_stop = trip_data['Predictions'][0]['Stop']
		if first_stop in ashmont_stops:
			memcache.add(key=trip_id,value="Ashmont",time=3600)
		elif first_stop in braintree_stops:
			memcache.add(key=trip_id,value="Braintree",time=3600)
	

class MainPage(webapp2.RequestHandler):

	def get(self):
		self.response.headers['Content-Type'] = 'application/json'
		obj = json.load(urllib2.urlopen("http://developer.mbta.com/lib/rthr/red.json"))
		self.response.write(json.dumps(obj['TripList']))

class GetData(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'application/json'
		obj = json.load(urllib2.urlopen("http://developer.mbta.com/lib/rthr/red.json"))['TripList']
		out = []
		for trip in [x for x in obj['Trips'] if x['Destination'] == 'Alewife']:
			for jfk_pred in [x['Seconds'] for x in trip['Predictions'] if x['Stop'] == "JFK/UMass"]:
				first_stop = trip['Predictions'][0]['Stop']
				row = {"secs":jfk_pred,'trip_id': trip['TripID']}
				if first_stop == "JFK/UMass":
					cached = memcache.get(trip['TripID'])
					if cached is None:
						row["branch"] = "Unknown"
					else:
						row["branch"] = cached
						row["from_mc"] =True
				elif first_stop in ashmont_stops:
					row["branch"] = "Ashmont"
				elif first_stop in braintree_stops:
					row["branch"] = "Braintree"
				out.append(row)
		out.sort(key=lambda k: k['secs'])
		self.response.write(json.dumps(out))

class RefreshTrips(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'application/json'
		obj = json.load(urllib2.urlopen("http://developer.mbta.com/lib/rthr/red.json"))['TripList']
		[putTrip(x) for x in obj['Trips'] if x['Destination'] == 'Alewife']
		self.response.write(json.dumps({'success':True}))

application = webapp2.WSGIApplication([
	('/', MainPage),
	('/refresh', RefreshTrips),
	('/data', GetData),
	], debug=True)