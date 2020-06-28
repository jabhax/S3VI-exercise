from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import feedparser
import json
import pprint


app = Flask(__name__)
api = Api(app)


client = MongoClient('mongodb://db:27017')
db = client.aNewDB
UserNum = db['UserNum']
UserNum.insert_one({'num_of_users': 0})


"""
def check_posted_data(posted_data, func_name):
    if (func_name == 'add' or func_name == 'subtract'
            or func_name == 'multiply'):
        if 'x' not in posted_data or 'y' not in posted_data:
            return 301  # missing parameters
        else:
            return 200
    elif func_name == 'division':
        if 'x' not in posted_data or 'y' not in posted_data:
            return 301  # missing parameters
        elif int(posted_data['y']) == 0:
            return 302
        else:
            return 200
"""

class Data(Resource):
    def get(self):
        data = self.parse_data()
        entries = []
        for year in range(2017, 2020):
            entries.append(data[year]['entries'])
        pprint.pprint(json.dumps(entries, indent=4))
        return json.dumps(entries, indent=4)

    def parse_data(self, start_year='2017', end_year='2019'):
        urls = {
            '2017': ('https://digitalcommons.usu.edu/smallsat/2017/all2017/'
                     'recent-events.rss'),
            '2018': ('https://digitalcommons.usu.edu/smallsat/2018/all2018/'
                     'recent-events.rss'),
            '2019': ('https://digitalcommons.usu.edu/smallsat/2019/all2019/'
                     'recent-events.rss')
        }
        data = {}
        for year in range(int(start_year), int(end_year)+1):
            data[year] = {}
            data[year]['entries'] = feedparser.parse(urls[str(year)]).entries

        """
        for year in data:
            entries = data[year]['entries']
            for entry in entries:
                print('Title: {}'.format(entry.title))
                print('Date: {}'.format(entry.published))
                print('Description: {}'.format(entry.description))
                print('Author/Organization: {}'.format(entry.author))
        """
        return data


class Visit(Resource):
    def get(self):
        prev_num = UserNum.find({})[0]['num_of_users']
        new_num = prev_num + 1
        UserNum.update({}, {"$set": {'num_of_users': new_num}})
        return str("Hello user " + str(new_num))


"""
class Add(Resource):
    def post(self):
        # If here, then the resouce Add was requested using POST
        # Step 1: Get posted data:
        posted_data = request.get_json()
        # Steb 1b: Verify validity of posted data
        status_code = check_posted_data(posted_data, "add")
        if status_code != 200:
            ret_json = {
                "Message": "An error happened",
                "Status Code": status_code
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
        # If here, then the resouce Subtract was requested using POST
        # Step 1: Get posted data:
        posted_data = request.get_json()
        # Steb 1b: Verify validity of posted data
        status_code = check_posted_data(posted_data, "subtract")
        if status_code != 200:
            ret_json = {
                "Message": "An error happened",
                "Status Code": status_code
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
        # If here, then the resouce Multiply was requested using POST
        # Step 1: Get posted data:
        posted_data = request.get_json()
        # Steb 1b: Verify validity of posted data
        status_code = check_posted_data(posted_data, "multiply")
        if status_code != 200:
            ret_json = {
                "Message": "An error happened",
                "Status Code": status_code
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
        # If here, then the resouce Divide was requested using POST
        # Step 1: Get posted data:
        posted_data = request.get_json()
        # Steb 1b: Verify validity of posted data
        status_code = check_posted_data(posted_data, "division")
        if status_code != 200:
            ret_json = {
                "Message": "An error happened",
                "Status Code": status_code
            }
            return jsonify(ret_json)
        # If i am here, then status_code == 200
        x = int(posted_data["x"])
        y = int(posted_data["y"])
        # Step 2: Multiply the posted data
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
"""
api.add_resource(Visit, "/hello")
api.add_resource(Data, "/data")


@app.route('/')
def hello_world():
    return "Hello World!"


if __name__ == '__main__':
    app.run(host='0.0.0.0')
