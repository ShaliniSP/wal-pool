#!flask/bin/python
from flask import Flask, jsonify,request, abort, render_template
import pymongo
from pymongo import MongoClient
import time
import os
import base64
import json
import re
from flask_cors import CORS
import datetime
import requests

client = MongoClient("mongo-service",27017)

app = Flask(__name__)

cors = CORS(app, resources={r"/api/*": {"origins":"*"}})

count = 0
acts_count = 0
crash = 0

@app.route('/api/v1/_health',methods=['GET'])
def health_check():

    if crash==1:
        return jsonify({}),500
    try:
        db_categories = client["CC_Categories"]
        categories = db_categories.list_collection_names()
        return jsonify({}),200
    except:
        return jsonify({}),500


@app.route('/api/v1/_crash',methods=['POST'])
def crash():
	
    global crash
    crash = 1
    return jsonify({}),200


@app.route('/api/v1/_count',methods=['GET'])
def counter():

    if crash==1:
        return jsonify({}),500
    global count
    if request.method!='GET':
        abort(405) #method is incorrect - 405 error
    ret = []
    ret.append(count)
    return jsonify(ret),200
	
	
@app.route('/api/v1/_count',methods=['DELETE'])
def reset():

    if crash==1:
        return jsonify({}),500
    global count
    if request.method!='DELETE':
        abort(405) #method is incorrect - 405 error
    count = 0
    return jsonify({}),200
	
	
@app.route('/api/v1/acts/count',methods=['GET'])
def acts_counter():

    if crash==1:
        return jsonify({}),500
    global  acts_count
    if request.method!='GET':
        abort(405) #method is incorrect - 405 error
    ret = []
    ret.append(acts_count)
    return jsonify(ret),200


def check_user_exists(username):
	
    URL = "http://selfless-Acts-404780607.us-east-1.elb.amazonaws.com/api/v1/users"
    headers = {'origin': '23.22.218.204'}
    r = requests.get(url = URL, headers=headers)
    data = r.json()
    data = list(data)
    if username in data:
        return True
    else:
        return False
    

@app.route('/api/v1/categories',methods=['GET'])
def show_category_list():

    if crash==1:
        return jsonify({}),500
    global count
    count += 1
    if request.method!='GET':
        abort(405) #method is incorrect - 405 error
        
    db_categories = client["CC_Categories"]
    categories = db_categories.list_collection_names()
    try:
        categories.remove("test")
    except:
        print("test not found")

    if len(categories)==0 :
       return('',204)
    
    ret = {}
    for category in categories:
        col = db_categories[category]
        ret[category] = col.count()

    #if check_user_exists("user1"):
    #    print("user1 exists")

    response = jsonify(ret)
    #response.headers.add('Access-Control-Allow-Origin','*')
    return response,200
    

@app.route('/api/v1/categories', methods=['POST'])
def add_category():

    if crash==1:
        return jsonify({}),500
    global count
    count += 1
    if request.method!='POST':
        abort(405)
        
    if not request.get_data() or len(request.get_data())==0:
        abort(400)
    if request.get_data() == "":
        abort(400)
    db_categories = client["CC_Categories"]
    categories = db_categories.list_collection_names()
    try:
        categories.remove("test")
    except:
        print("test not found")
    
    token = request.get_data().decode('utf-8')
    match = re.search("[a-zA-Z0-9_ ]+",token)
    if match is None:
        abort(400)
    token = match.group(0)
    if token.isspace():
        abort(400)
    if token in categories:
        abort(400)
        
    try:
        db_categories.create_collection(token)
        return jsonify({}), 201
    except:
        abort(405)
        
    
@app.route('/api/v1/categories/<category>', methods=['DELETE'])
def remove_category(category):

    if crash==1:
        return jsonify({}),500
    global count
    count += 1
    if request.method!='DELETE':
        abort(405)
    
    db_categories = client["CC_Categories"]
    categories = db_categories.list_collection_names()
    try:
        categories.remove("test")
    except:
        print("test not found")
      
    if category not in categories:
        abort(400)
        
    try:
        db_categories[category].drop()
        #category_id_mappings.pop(category)
        return jsonify({}), 200
    except:
        abort(405)


@app.route('/api/v1/categories/<category>/acts',methods=['GET'])
def show_category_acts(category):

    if crash==1:
        return jsonify({}),500
    global count
    count += 1
    qs = request.query_string
    startrange = request.args.get('start',None)
    endrange = request.args.get('end',None)
    
    if request.method!='GET':
        abort(405)
        
    db_categories = client["CC_Categories"]
    categories = db_categories.list_collection_names()
    try:
        categories.remove("test")
    except:
        print("test not found")
	
    if len(categories)==0:
        return('',204)
    
    if category not in categories:
        return('',204)
        
    acts_list = list(db_categories[category].find({},{'_id':0}))
    
    if len(acts_list)==0:
        return ('',204)
        
    if len(qs)==0:
        
        if len(acts_list)>100:
            abort(413)
   
        return jsonify(acts_list),200
        
    else:
        
        if startrange is None or endrange is None:
            return('',204)
        startrange = int(startrange)
        endrange = int(endrange)
        
        if startrange > endrange:
            return('',204)
    
        if endrange>len(acts_list) or startrange<1:
            return('',204)
    
        size = endrange - startrange + 1       
        if size>100:
            abort(413)
        
        acts_list_size = list(db_categories[category].find({},{'_id':0}).sort('_id',-1))
        acts_list_size = acts_list_size[(startrange-1):endrange]
        
        return jsonify(acts_list_size),200
    


@app.route('/api/v1/categories/<category>/acts/size',methods=['GET'])
def show_acts_size(category):

    if crash==1:
        return jsonify({}),500
    global count
    count += 1
    if request.method!='GET':
        abort(405)
        
    db_categories = client["CC_Categories"]
    categories = db_categories.list_collection_names()
    try:
        categories.remove("test")
    except:
        print("test not found")
	
    if len(categories)==0:
        return('',204)
    
    if category not in categories:
        return('',204)
        
    acts_list = list(db_categories[category].find({},{'_id':0}))
    
    ret = []
    ret.append(len(acts_list))
   
    return jsonify(ret),200
    
    

@app.route('/api/v1/acts/upvote',methods=['POST'])
def upvote_act():

    if crash==1:
        return jsonify({}),500
    global count
    count += 1
    if request.method!='POST':
        abort(405)
    if not request.get_data() or len(request.get_data())==0:
        abort(400)
        
    db_categories = client["CC_Categories"]
    categories = db_categories.list_collection_names()
    try:
        categories.remove("test")
    except:
        print("test not found")
	
    if len(categories)==0:
        abort(400)
    
    #actIds = [act["actId"] for L in [list(db_categories[category].find({},{'actId':1})) for category in categories] for act in L] 
    #print(actIds)
    
    token = request.get_data().decode('utf-8')
    match = re.search("[0-9]+",token)
    if match is None:
        abort(400)
    token = int(match.group(0))
    
    #if token in actIds:
    #    abort(400)
        
    try:
    
        query = {"actId": token}
        act = []
        act_cat = ""
        
        for category in categories:
            act = list(db_categories[category].find(query))
            if len(act) > 0:
                act_cat = category
                break
        
        if len(act)==0:
            abort(400)
        else:
            db_categories[act_cat].update_one({"actId":token},{"$inc":{"upvotes":1}})
            return jsonify({}), 200
    except:
        abort(400)


@app.route('/api/v1/acts/<actId>', methods=['DELETE'])
def delete_act(actId):

    if crash==1:
        return jsonify({}),500
    global count
    count += 1
    if request.method!='DELETE':
        abort(405)
    if request.get_data():
        abort(405) #Takes care if data is passed as parameters
        
    actId = int(actId)
    #print(actId)
    db_categories = client["CC_Categories"]
    categories = db_categories.list_collection_names()
    try:
        categories.remove("test")
    except:
        print("test not found")
	
    if len(categories)==0:
        abort(400)
	
    actIds = [act["actId"] for L in [list(db_categories[category].find({},{'actId':1})) for category in categories] for act in L]
    if actId not in actIds:
        abort(400)
        
    try:
    
        query = {"actId": actId}
        act = []
        act_cat = ""
        
        for category in categories:
            act = list(db_categories[category].find(query))
            if len(act) > 0:
                act_cat = category
                break
        
        if len(act) is 0:
            abort(400)
        else:
            db_categories[act_cat].delete_one(query)
            return jsonify({}), 200
    except:
        abort(400)
        

@app.route('/api/v1/acts', methods=['POST'])
def create_act():

    if crash==1:
        return jsonify({}),500
    global count
    global acts_count
    count += 1
    if request.method!='POST':
        abort(405)

    data_request = request.get_json()	
	
    print(data_request)
    if not data_request:
        print("empty data")
        abort(400)
        
    if 'upvotes' in data_request:
        print("upvotes error")
        abort(400)
    
    if 'actId' not in data_request or 'username' not in data_request or 'timestamp' not in data_request or 'caption' not in data_request or 'categoryName' not in data_request or 'imgB64' not in data_request:
        print("username actid")
        abort(400)
        
    #Validating actId :
    db_categories = client["CC_Categories"]
    categories = db_categories.list_collection_names()
    try:
        categories.remove("test")
    except:
        print("test not found")
    actIds = [act["actId"] for L in [list(db_categories[category].find({},{'actId':1})) for category in categories] for act in L]
    if data_request["actId"] in actIds:
        print("actid error")
        abort(400)
        
    #Validating username :
    #db_users = client["CC_Users"]
    #coll_users = db_users["Users"]
    #L = [doc['username'] for doc in list(coll_users.find({},{'_id':0,'username': 1}))]
    if not check_user_exists(data_request["username"]):
        print("username error")
        abort(400)
        
    #Validating timestamp :
    try:
        datetime.datetime.strptime(data_request["timestamp"], '%d-%m-%Y:%S-%M-%H')
    except:
        print("datetime error")
        abort(400)
        
    #Validating categoryName :
    if data_request["categoryName"] not in categories:
        print("categoryname")
        abort(400)
        
    #Validating imgB64 :
    #pre = "data:image/jpeg;base64,"
    #img = data_request["imgB64"].replace(pre,'')
    if not (re.search("[A-Za-z0-9+/=]", img) and len(img)%4==0):
        print("image encoded")
        abort(400)
        
    #Creating the json data for act to be stored
    act_data = {
                    "actId": data_request["actId"],
                    "username": data_request["username"],
                    "timestamp": data_request["timestamp"],
                    "categoryName": data_request["categoryName"],
                    "caption": data_request["caption"],
                    "upvotes": 0,
                    "imgB64": data_request["imgB64"]
                }
                
    #Adding to respective collection in database :
    try:
        x = db_categories[data_request["categoryName"]].insert_one(act_data)
        acts_count += 1
        return jsonify({}), 201
    except pymongo.errors.PyMongoError as e:
        abort(405)
        
    


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=80)
