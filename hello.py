from flask import Flask, render_template, request, jsonify
import atexit
import os
import json
import pymongo

app = Flask(__name__, static_url_path='')

client = None
db = None

if 'MONGODB_URL' in os.environ:
    client = pymongo.MongoClient(os.environ['MONGODB_URL'])
    db = client[os.environ['MONGODB_DATABASE']]
elif os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        print('Found local VCAP_SERVICES')
        client = pymongo.MongoClient(vcap['services']['mongoDB']['uri'])
        db = client[vcap['services']['mongoDB']['database']]

# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))

@app.route('/')
def root():
    return app.send_static_file('index.html')

# /* Endpoint to greet and add a new visitor to database.
# * Send a POST request to localhost:8000/api/visitors with body
# * {
# *     "name": "Bob"
# * }
# */
@app.route('/api/visitors', methods=['GET'])
def get_visitor():
    if client:
        return jsonify(list(map(lambda doc: doc['name'], db.visitors.find())))
    else:
        print('No database')
        return jsonify([])

# /**
#  * Endpoint to get a JSON array of all the visitors in the database
#  * REST API example:
#  * <code>
#  * GET http://localhost:8000/api/visitors
#  * </code>
#  *
#  * Response:
#  * [ "Bob", "Jane" ]
#  * @return An array of all the visitor names
#  */
@app.route('/api/visitors', methods=['POST'])
def put_visitor():
    user = request.json['name']
    data = {'name':user}
    if client:
        data['_id'] = format(db.visitors.insert_one(data).inserted_id)
        return jsonify(data)
    else:
        print('No database')
        return jsonify(data)

@atexit.register
def shutdown():
    if client:
        client.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
