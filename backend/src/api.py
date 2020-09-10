import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

AUTH0_DOMAIN = 'dvcoffee.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'http://localhost:5000'

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES



@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()

    return jsonify({
    'success':True,
    'drinks': [drink.short() for drink in drinks]
    }), 200




@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-datail')
def get_drinks_detail(payload):       #pass in payload
    drinks = Drink.query.all()

    return jsonify({
    'success': True,
    'drinks-detail':[drink.long() for drink in drinks]
    }), 200





'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):          #pass in payload
    data = request.get_json()
    if 'title ' and 'recipe' not in data:
        abort(422)

    recipe_data = data['recipe']


    recipe_data = [recipe_data]

    drink = Drink()
    drink.title = data['title']
    drink.recipe = json.dumps(recipe_data)
    drink.insert()

    return jsonify({
        'success': True,
        'drink': Drink.long(drink)
    })



@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def modify_drink(payload, id):
    drink=Drink.query.get(id)
    if drink is None:
        abort(404)

    data = request.get_json()
    if 'title' in data:
        drink.title = data['title']

    if 'recipe' in data:
        drink.recipe = data['recipe']

    drink.update()

    return jsonify({
        'success' : True,
        'drinks' : [drink.long()]
    })

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink=Drink.query.get(id)
    if drink is None:
        abort(404)

    drink.delete()

    return jsonify({
        'success' : True,
        'drinks' : drink.id
    })




'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": 'Bad Request'
    }), 400

@app.errorhandler(401)
def unauthorised(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Unauthorised'
    }), 401

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": 'Not Found'
    }), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": 'Internal Server Error'
    }), 500

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code
