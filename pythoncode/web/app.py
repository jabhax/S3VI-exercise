from flask import Flask, jsonify, request, render_template
from flask_restful import Api, Resource
from pymongo import MongoClient
import feedparser
import json
import pprint
import os


app = Flask(__name__)
api = Api(app)


# Create and setup MongoDB client, collections, and global data flags.
client = MongoClient('mongodb://db:27017')
db = client.aNewDB
UserNum = db['UserNum']
my_SSC_col = db['SSC']
my_SSD_col = db['SSD']
UserNum.insert_one({'num_of_users': 0})
DATA_TITLE = ''
SSC_FLAG = False
SSD_FLAG = False


# Sets the flags for what type of data should be displayed on index.html
def set_data_flags(data_type):
    if data_type == 'SSC':
        SSC_FLAG = True
        SSD_FLAG = False
        DATA_TITLE = 'SmallSat Conference'
    elif data_type == 'SSD':
        SSC_FLAG = False
        SSD_FLAG = True
        DATA_TITLE = 'SmallSat Data'
    elif data_type == 'ALL':
        SSC_FLAG = True
        SSD_FLAG = True
        DATA_TITLE = 'SmallSat Conference & Data'
    else:
        SSC_FLAG = False
        SSD_FLAG = False
        DATA_TITLE = ''
    return (SSC_FLAG, SSD_FLAG, DATA_TITLE)


# Main parser that pulls data from the SSC links from 2017-2019, and from
# the SSD data file. It parses the data into Attributes of Title, Date,
# Description, Author/Organization.
# 
# Returns data object that can be filtered by the above attributes.
def parse_data(data_type=None, start_year='2017', end_year='2019'):
    """ Main parser for SSC and SSD data """
    if not data_type:
        raise ValueError("Must provide data_type.")

    data_type = data_type.upper()
    if data_type.upper() not in ['SSC', 'SSD', 'ALL']:
        raise ValueError("data_type can only be 'SSC', 'SSD', or 'ALL' for both.")
        
    SSC_FLAG, SSD_FLAG, DATA_TITLE = set_data_flags(data_type)

    urls = {
        'SSC': {
            '2017': ('https://digitalcommons.usu.edu/smallsat/2017/all2017/'
                     'recent-events.rss'),
            '2018': ('https://digitalcommons.usu.edu/smallsat/2018/all2018/'
                     'recent-events.rss'),
            '2019': ('https://digitalcommons.usu.edu/smallsat/2019/all2019/'
                     'recent-events.rss')
        },
        'SSD': {
            'paths': ['SmallSat_JSON_6_26.txt']
        }
    }

    data = {}
    if SSC_FLAG:
        data['SSC'] = {}
        for year in range(int(start_year), int(end_year)+1):
            data['SSC'][year] = {}
            data['SSC'][year]['entries'] = feedparser.parse(urls['SSC'][str(year)]).entries

    if SSD_FLAG:
        data['SSD'] = {}
        for path in urls['SSD']['paths']:
            f = open(path, 'r')
            d = json.load(f)
            f.close()
            data['SSD'][path] = d['data']
    return data


# Resource class for SSC (Small Sat Conference) documents stored into the
# SSC collection
class SmallSatConference(Resource):
    def get(self):
        data = parse_data(data_type='SSC')
        entries = []
        for year in range(2017, 2020):
            entries.append(data['SSC'][year]['entries'])
        display_str = ''
        for entry in entries:
            my_dict = {
                'title': entry[0].title,
                'date': entry[0].published,
                'description': entry[0].description,
                'author': entry[0].author
            }
            ssc = my_SSC_col.insert_one(my_dict)
            display_str += ('Inserted id: {} into DB'.format(ssc.inserted_id))
        display_str += 'Processed all SmallSat Conference Data.'

        return display_str


# Resource class for SSD (Small Sat Data) documents stored into the
# SSD collection
class SmallSatData(Resource):
    def get(self):
        data = parse_data(data_type='SSD')
        entries = []
        for path in data['SSD']:
            entries.append(data['SSD'][path])

        display_str = ''
        for entry in entries:
            for key in entry:
                print("SSD ENTRY: {}".format(json.dumps(entry[key], indent=4)))
                my_dict = {
                    'title': entry[key]['title'],
                    'date': entry[key]['lastUpdated'],
                    'description': entry[key]['description'],
                    'author': entry[key]['leadOrganization']
                }
                ssd = my_SSD_col.insert_one(my_dict)
                display_str += ('Inserted id: {} into DB'.format(ssd.inserted_id))
        return display_str


# Class for handling of how many times the '/' page is visited. It is also used
# to test that the MonngoDB Colletions and Documents are updating correctly.
class Visit(Resource):
    def get(self):
        prev_num = UserNum.find({})[0]['num_of_users']
        new_num = prev_num + 1
        UserNum.update({}, {"$set": {'num_of_users': new_num}})
        return str("Hello user " + str(new_num))


@app.route('/')
def hello_world():
    return "Hello World!"

@app.route('/search', methods=['GET', 'POST'])
def search():
    data_type = None
    if request.method == 'POST':
        req = request.form
        text = req['data_field']
        data_type = text.upper()
    SSC_FLAG, SSD_FLAG, DATA_TITLE = set_data_flags(data_type)
    display_items = {'SSC': [], 'SSD': []}
    # build SSC data to be stored into MongoDB Collection
    for i in range(my_SSC_col.find({}).count()):
        item = {
            'title': my_SSC_col.find({})[i]['title'],
            'date': my_SSC_col.find({})[i]['date'],
            'description': my_SSC_col.find({})[i]['description'],
            'author': my_SSC_col.find({})[i]['author']
        }
        display_items['SSC'].append(item)
    # build SSD data to be stored into MongoDB Collection
    for i in range(my_SSD_col.find({}).count()):
        item = {
            'title': my_SSD_col.find({})[i]['title'],
            'date': my_SSD_col.find({})[i]['date'],
            'description': my_SSD_col.find({})[i]['description'],
            'author': my_SSD_col.find({})[i]['author']
        }
        display_items['SSD'].append(item)
    return render_template('index.html', ssc_items=display_items['SSC'], ssd_items=display_items['SSD'], ssc=SSC_FLAG, ssd=SSD_FLAG, data_title=DATA_TITLE)


# Add resource access for the user visit page, SSC, and SSD datas.
api.add_resource(Visit, "/hello")
api.add_resource(SmallSatConference, "/SSC")
api.add_resource(SmallSatData, "/SSD")


if __name__ == '__main__':
    app.run(host='0.0.0.0')
