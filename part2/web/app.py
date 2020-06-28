from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import requests


app = Flask(__name__)
api = Api(app)


client = MongoClient('mongodb://db:27017')
db = client.aNewDB
UserNum = db['UserNum']
UserNum.insert_one({'num_of_users': 0})

class Data(Resource):
    def get(self):
        url = 'https://digitalcommons.usu.edu/smallsat/2017/all2017/recent-events.rss'
        response = requests.get(url)
        data = response.text
        if response.status_code != 200:
            print('Failed to get data:', response.status_code)
        else:
            print('First 100 characters of data are')
            print(data[:100])
        print('[*] Parsing response text')
        data = data.split('\n')
        data_list = list()
        for value in data:
            if 'title,author' not in value:
                if value:
                    value = value.split(',')
                    data_list.append({'title': int(value[0]), 'author': float(value[1])})
        print(data_list)
        return str(data_list)


class Visit(Resource):
    def get(self):
        prev_num = UserNum.find({})[0]['num_of_users']
        new_num = prev_num + 1
        UserNum.update({}, {"$set": {'num_of_users': new_num}})
        return str("Hello user " + str(new_num))

def check_posted_data(posted_data, func_name):
    if func_name == 'add' or func_name == 'subtract' or func_name == 'multiply':
        if 'x' not in posted_data or 'y' not in posted_data:
            return 301 # missing parameters
        else:
            return 200
    elif func_name == 'division':
        if 'x' not in posted_data or 'y' not in posted_data:
            return 301 # missing parameters
        elif int(posted_data['y']) == 0:
            return 302
        else:
            return 200


class Add(Resource):
    def post(self):
        # If I am here, then the resouce Add was requested using the method POST
        # Step 1: Get posted data:
        posted_data = request.get_json()
        # Steb 1b: Verify validity of posted data
        status_code = check_posted_data(posted_data, "add")
        if (status_code!=200):
            ret_json = {
                "Message": "An error happened",
                "Status Code":status_code
            }
            return jsonify(ret_json)
        # If i am here, then status_code == 200
        x = int(posted_data["x"])
        y = int(posted_data["y"])
        # Step 2: Add the posted data
        ret = x+y
        ret_map = {
            'Message': ret,
            'Status Code': 200
        }
        return jsonify(ret_map)


class Subtract(Resource):
    def post(self):
        # If I am here, then the resouce Subtract was requested using the method POST
        # Step 1: Get posted data:
        posted_data = request.get_json()
        # Steb 1b: Verify validity of posted data
        status_code = check_posted_data(posted_data, "subtract")
        if (status_code!=200):
            ret_json = {
                "Message": "An error happened",
                "Status Code":status_code
            }
            return jsonify(ret_json)
        # If i am here, then status_code == 200
        x = int(posted_data["x"])
        y = int(posted_data["y"])
        # Step 2: Subtract the posted data
        ret = x-y
        ret_map = {
            'Message': ret,
            'Status Code': 200
        }
        return jsonify(ret_map)


class Multiply(Resource):
    def post(self):
        # If I am here, then the resouce Multiply was requested using the method POST
        # Step 1: Get posted data:
        posted_data = request.get_json()
        # Steb 1b: Verify validity of posted data
        status_code = check_posted_data(posted_data, "multiply")
        if (status_code!=200):
            ret_json = {
                "Message": "An error happened",
                "Status Code":status_code
            }
            return jsonify(ret_json)
        # If i am here, then status_code == 200
        x = int(posted_data["x"])
        y = int(posted_data["y"])
        # Step 2: Multiply the posted data
        ret = x*y
        ret_map = {
            'Message': ret,
            'Status Code': 200
        }
        return jsonify(ret_map)


class Divide(Resource):
    def post(self):
        #If I am here, then the resouce Divide was requested using the method POST
        #Step 1: Get posted data:
        posted_data = request.get_json()
        #Steb 1b: Verify validity of posted data
        status_code = check_posted_data(posted_data, "division")
        if (status_code!=200):
            ret_json = {
                "Message": "An error happened",
                "Status Code":status_code
            }
            return jsonify(ret_json)
        #If i am here, then status_code == 200
        x = int(posted_data["x"])
        y = int(posted_data["y"])
        #Step 2: Multiply the posted data
        ret = (x*1.0)/y
        ret_map = {
            'Message': ret,
            'Status Code': 200
        }
        return jsonify(ret_map)


api.add_resource(Add, "/add")
api.add_resource(Subtract, "/subtract")
api.add_resource(Multiply, "/multiply")
api.add_resource(Divide, "/division")
api.add_resource(Visit, "/hello")
api.add_resource(Data, "/data")


@app.route('/')
def hello_world():
    return "Hello World!"


if __name__=='__main__':
    app.run(host='0.0.0.0')
