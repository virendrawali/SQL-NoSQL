from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

app = Flask(__name__)
CORS(app, support_credentials=True)

app.config['MONGO_DBNAME'] = 'credit-service'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/credit-service'

mongo = PyMongo(app)

@app.route('/add', methods=['POST'])

def add_user():
    _json = request.json
    _firstname = _json['firstName']
    _email = _json['email']
    _password = _json['pwd']
    _lastname = _json['lastName']
    _contact = _json['contactNumber']
    _creditscore = _json['creditScore']
    _income = _json['income']
    _withdraw = 0
    _creditlimit = 100000
    print(_password)
    user = mongo.db.users.find_one({"email": _email})
    if user is None and _firstname and _email and _password and request.method == 'POST':
        #do not save password as a plain text
        _hashed_password = generate_password_hash(_password)
        # save details
        id = mongo.db.users.insert({'email': _email, 'pwd': _password, 'firstname': _firstname,
                                    'lastname': _lastname, 'contact': _contact, 'creditscore': _creditscore,
                                    'income': _income,"withdraw":_withdraw,"creditlimit": _creditlimit})
        resp = jsonify('User added successfully!')
        resp.status_code = 200
        return "success"
    elif user is not None:
        return "User Already Present"
    else:
        "Not Found"

@app.route('/addTransaction', methods=['POST'])
def add_transaction():
  _newjson = request.json
  print("function is called")
  print(_newjson)
  '''
  _firstname = _json['firstname']
  _email = _json['email']
  _lastname = _json['lastname']
  _action = _json['action']
  _amount = _json['amount']

  if _firstname and _email and request.method == 'POST':
    id = mongo.db.transactions.insert({'email': _email, 'firstname': _firstname, "lastname":_lastname, "action": _action, "amount": _amount})
    resp = jsonify('User added successfully!')
    resp.status_code = 200
    return resp
  else:
    return "Not found"
'''

@app.route('/getUserData', methods=['POST'])
def getuserdata():
  _json = request.json
  _email = _json['email']
  _password = _json['pwd']
  _hashed_password = generate_password_hash(_password)
  user = mongo.db.users.find_one({"email":_email})
  print("login",_password)
  if user is None:
      return "Incorrect Username"
  elif _password != user['pwd']:
      return "Incorrect Password"
  resp = dumps(user)
  return "Login Success"


@app.route('/getData', methods=['POST'])
def getdata():
  _json = request.json
  _email = _json['email']
  user = mongo.db.users.find_one({"email":_email})
  print(user['email'])
  return {'email':user['email'], 'withdraw':user['withdraw'], 'creditlimit':user['creditlimit'], 'balance':user['creditlimit'] - user['withdraw']}


@app.route('/getPersonalData', methods=['POST'])
def getPersonalData():
  _json = request.json
  _email = _json['email']
  user = mongo.db.users.find_one({"email":_email})
  return {'firstname':user['firstname'], 'lastname':user['lastname']}


@app.route('/updateData', methods=['POST'])
def update_user():
  _json = request.json
  _email = _json['email']
  _amount = int(_json['amount'])
  user = mongo.db.users.find_one({"email": _email})
  if user is not None and _email and request.method == 'PUT':
    if user['creditlimit'] - user['withdraw'] - _amount > 0:
        _total_amount = user['withdraw']+ _amount
        user['withdraw'] = _total_amount
        print(_total_amount)
        # mongo.db.users.update_one({'email': _email},
        #                          {'$set': {"withdraw":_total_amount}}, upsert=False)
        mongo.db.users.update_one(user)
    else:
        return "Limit Exceed"
    resp = jsonify('User updated successfully!')
    resp.status_code = 200
    print(resp)
    return resp
  else:
    return not_found()


@app.route('/payAmount', methods=['PUT'])
def payAmount():
  _json = request.json
  _email = _json['email']
  _amount = int(_json['amount'])
  user = mongo.db.users.find_one({"email": _email})
  if user is not None and user['withdraw'] > 0:
    if user['withdraw'] - _amount >= 0:
        _total_amount = user['withdraw']- _amount
        mongo.db.users.update_one({'email': _email},
                                 {'$set': {"withdraw":_total_amount}}, upsert=False)
    else:
        return "Limit Exceed"
    resp = jsonify('User updated successfully!')
    resp.status_code = 200
    return resp
  else:
    return "Hello"


@app.route('/delete/<id>', methods=['DELETE'])
def delete_user(id):
  mongo.db.users.delete_one({'_id': ObjectId(id)})
  resp = jsonify('User deleted successfully!')
  resp.status_code = 200
  return resp


@app.errorhandler(404)
def not_found\
                (error=None):
  message = {
    'status': 404,
    'message': 'Not Found: ' + request.url,
  }
  resp = jsonify(message)
  resp.status_code = 404

  return resp

@app.route('/getdata', methods=['GET'])
def get_data():
    return "Yes"


if __name__ == "__main__":
    app.run()