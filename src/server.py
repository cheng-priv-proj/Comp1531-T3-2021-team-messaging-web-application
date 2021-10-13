import sys
import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.error import InputError
from src import config
from src.auth import auth_register_v1
from src.data_store import data_store

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

# Auth register 
# Change to dictionary?
# Return errors?
@APP.route('auth/register/v2', methods = ['POST'])
def register_ep():
    register_details = request.get_json(force = True)

    email = register_details.get('email')
    password = register_details.get('password')
    name_first = register_details.get('name_first')
    name_last = register_details.get('name_last')

    auth_id = auth_register_v1(email, password, name_first, name_last)
    token = str(auth_id) # Change to jwt later

    data_store.insert_token(token, auth_id)

    return {'token': token, 'auth_user_id': auth_id}

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
