import json
import os
import time

from google.appengine.api import memcache
from google.appengine.api import urlfetch

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),"templates")))

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

def fetchJson():
    url = "http://developer.mbta.com/lib/rthr/red.json"
    result = memcache.get('json')
    if result is not None:
        return result
    result = json.loads(urlfetch.fetch(url, headers = {'Cache-Control' : 'max-age=0'}).content)['TripList']
    memcache.add(key='json',value=result,time=10)
    return result

def getTrains():
    obj = fetchJson()
    json_time = obj["CurrentTime"]
    now = time.time()
    out = []
    for trip in [x for x in obj['Trips'] if x['Destination'] == 'Alewife']:
        for jfk_pred in [x['Seconds'] for x in trip['Predictions'] if x['Stop'] == "JFK/UMass"]:
            first_stop = trip['Predictions'][0]['Stop']
            pred_time = jfk_pred+json_time
            row = {'trip_id': trip['TripID'],"pred_time":pred_time,"secs":pred_time-now}
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
    out.sort(key=lambda k: k['pred_time'])
    return out


class MainPage(webapp2.RequestHandler):
    def get(self):
        trains = getTrains()
        template_values = { 'trains': trains,
                            'platform': trains[0]['branch'] if trains else '',
                            'caveat': (len(trains)>1 and trains[1]['secs']-trains[0]['secs']<30 and trains[0]['branch'] != trains[1]['branch'])}

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class GetData(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(getTrains()))

class RefreshTrips(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        obj = fetchJson()
        [putTrip(x) for x in obj['Trips'] if x['Destination'] == 'Alewife']
        self.response.write(json.dumps({'success':True}))

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/refresh', RefreshTrips),
    ('/data', GetData),
    ], debug=True)
