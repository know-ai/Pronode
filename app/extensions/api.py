import requests
from flask import request
from functools import wraps
from app import AUTH_SERVICE_URL as url
from app import EVENT_LOGGER_SERVICE_URL
from flask import Blueprint
from flask_restx import Api as API
from  app.utils import Singleton
import os
from app import core_app


authorizations = {
    'apikey' : {
        'type' : 'apiKey',
        'in' : 'header',
        'name' : 'X-API-KEY'
    }
}

alarm_manager = core_app.get_alarm_manager()
blueprint = Blueprint('api', __name__, url_prefix='/api')

api = API(blueprint, version='1.0', 
        title='DAQ Service API',
        description="""
        This API groups all namespaces defined in every module's resources for Data Acquisition Service (DAQ).

        Basically, the roadmap suggested to interact or configure your DAQ is the following:

        1.- Create Tags: In Tags namespace you can do CRUD actions for tags.
        2.- Define Communication Channels: If you need get data from plant, here you define your communication channel.
        So far, you can only define OPCUA channels.
        3.- Bind Tags-Plant: You can bind communication nodes with any defined tag. With OPCUA Client you can explore your channel
        to get all node namespace in your OPCUA Server.
        3.1.- Update Address and Node in Tags: Once you know the node namespace for tags in OPCUA Server, you should update
        tcp_source_address and node_namespace, according to OPCUA Server information.
        4.- Get Tag Value by Exception: Once you update *tcp_source_address* and *node_namespace* in Tags, you must subscribe all tags
        to OPCUA Server to get values when they change. This is done in OPCUA Client.

        **Note:** At this moment, you can logging data read from OPCUA Server into DAQ Database.

        5.- Define Alarms: You can define new alarms in **Alarms** namespace.
        """, 
        doc='/docs',
        authorizations=authorizations
    )

class Api(Singleton):

    def __init__(self):

        self.app = None

    def init_app(self, app):
        r"""
        Documentation here
        """
        self.app = self.create_api(app)

        return app

    def create_api(self, app):
        r"""
        Documentation here
        """
        app.register_blueprint(blueprint)

        return api

    @staticmethod
    def log_alarm_operation(
        message:str,
        description:str,
        classification:str,
        priority:int,
        criticity:int
        ):
        """Documentation here
        """
        response = requests.get(f'{url}/api/users/is_a_valid_token', headers=request.headers, verify=False)
        status_code = response.status_code
        response = response.json()
        
        if status_code!=200:

            return response, status_code

        event_url = f"{EVENT_LOGGER_SERVICE_URL}/api/events/add"

        payload = {
            'user': response['username'],
            'message': message,
            'description': description,
            'classification': classification,
            'priority': priority,
            'criticity': criticity
        }
        requests.post(event_url, headers=request.headers, json=payload, verify=False)

    @staticmethod
    def token_required(auth:bool=False):
        def _token_required(f):
            @wraps(f)
            def decorated(*args, **kwargs):

                if auth:

                    token = None

                    if 'X-API-KEY' in request.headers:
                        
                        token = request.headers['X-API-KEY']

                    elif 'Authorization' in request.headers:
                        
                        token = request.headers['Authorization'].split('Token ')[-1]

                    if not token:
                        
                        return {'message' : 'Key is missing.'}, 401

                    headers = {
                        "Content-Type": "application/json; charset=utf-8",
                        "X-API-KEY": token
                        }
                    try:

                        if "sys_token" in os.environ.keys():

                            if token!=os.environ["sys_token"]:

                                response = requests.get(f'{url}/api/users/is_a_valid_token', headers=headers, verify=False)
                                status_code = response.status_code
                                response = response.json()
                            
                            else:
  
                                status_code = 200
                                response = {'message': True, 'username': "SYS.KNOWAI"}
                        else:

                            response = requests.get(f'{url}/api/users/is_a_valid_token', headers=headers, verify=False)
                            status_code = response.status_code
                            response = response.json()
                        
                        if status_code!=200:

                            return response, status_code

                        return f(*args, **kwargs)
                    
                    except requests.ConnectionError:

                        return {'message' : 'Authentication service is not active'}, 401

                else:

                    return f(*args, **kwargs)

            return decorated

        return _token_required
        

    @staticmethod
    def verify_credentials(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            payload = {
                'username': kwargs['username'],
                'password': kwargs['password']
            }

            response = requests.post(f'{url}/api/users/credentials_are_valid', json=payload, verify=False)

            if response:

                response = response.json()

                if not response['message']:

                    return {'message' : 'Invalid username or password'}, 401

            else:

                return {'message' : 'Authentication service is not active'}, 401

            return func(*args, **kwargs)

        return wrapper