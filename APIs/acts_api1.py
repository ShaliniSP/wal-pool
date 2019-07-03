#!flask/bin/python
import pymongo
from flask import Flask
from flask_cors import CORS
import datetime
import requests
import pprint
from datetime import timedelta
now = datetime.datetime.now()
print(now)

# AIzaSyBSKVzzxyz8KxaEKw4btOCIgOIOaGOZmhU
# https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=Washington,DC&destinations=New+York+City,NY&key=AIzaSyBSKVzzxyz8KxaEKw4btOCIgOIOaGOZmhU
apikey = 'AIzaSyCewtBSHxzc3KFmOjv4c3rilD88HEKEy08'

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins":"*"}})
client = pymongo.MongoClient(
            "mongodb+srv://WalPoolAdmin:walpool@walpool-wd6fo.mongodb.net/test?retryWrites=true&w=majority"
            )
order_db = client.Order
cab_db = client.Cab
order_collection = order_db.OrderCollection
cab_details = cab_db.CabDetails


def get_price_estimates(start, end):
    start_latitude = start[0]
    start_longitude = start[1]
    end_latitude = end[0]
    end_longitude = end[1]
    s = 'origin='+str(start_latitude)+','+str(start_longitude)+'&destination='+str(end_latitude)+','+str(end_longitude)
    url = 'https://maps.googleapis.com/maps/api/directions/json?'+s+'&key='+apikey
    resp = requests.get(url)
    resp1 = resp.json()['routes'][0]['legs'][0]
    dist  =resp1['distance']['value']/1000
    sec = resp1['duration']['value']
    print(sec)
    
    total = now + timedelta(seconds=sec)
    print(total)
    
    base_price = 20.0
    price =(base_price + (dist-2)*10)/4
    
    print(price)

    return price


def find_shortest_distance(pickup, current_locations):
    s = ""
    for curr in current_locations:
        s = s + str(curr[0]).strip('\n') + ',' + str(curr[1]).strip('\n') + '|'
    s = s.strip('|')
    url =  'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=' + str(pickup[0])  + ',' + str(pickup[1]) + '&destinations=' + s + '&key='+apikey
    resp = requests.get(url)
    elements = resp.json()['rows'][0]['elements']
    min = elements[0]['distance']['value']
    pos = 0
    for i in range(len(elements)):
        if(elements[i]['distance']['value'] < min):
            min = elements[i]['distance']['value']
            pos = i
    
    print(min)
    return current_locations[pos]

def set_cab_details(order):
    #Loop through cab details and find the cab with the smallest distance
    cabs  = cab_details.find()
    current_locs = []
    for cab in cabs:
        current_locs.append(cab['current'])
    loc = find_shortest_distance(order['pickup'], current_locs)
    allocated_cab = cab_details.find_one({'current':loc})
    cab_details.update_one({'_id':allocated_cab['_id']}, {'$set':{'order_id':order['_id']}})
    order_collection.update_one({'_id':order['_id']},{'$set':{'cab_allocated':True}})
    


@app.route('/v1/order/next',methods=['GET'])
def get_next_order():
    # Loop through order collection, find 
    order = order_collection.find_one({'cab_allocated':False})
    pprint(order)
    prices = get_price_estimates(order['pickup'], order['drop'])
    order_collection.update({'_id':order['_id']}, {'$set':{'price':prices}})
    print(prices)
    set_cab_details(order)


app.run(debug=True,host='0.0.0.0',port=80)