from flask_restx import Namespace, Resource
from PyIAC import PyIAC
from app.extensions.api import api
from app.extensions import _api as Api
from ..models import Addresses
from app import APP_AUTH

api_security = None
if APP_AUTH:
    api_security = 'apikey'


ns = Namespace('Addresses', description='Communication Industrial Protocols Addresses')


core_app = PyIAC()

@ns.route('/')
class AddressesCollection(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def get(self)->tuple[dict, int]:
        """
        Select all records

        You can use this endpoint to retrieve all instances matching in the database. 

        This endpoint is a shortcut that calls Addresses.select() with the given query.

        ## Python code with requests Library
        ```
        import requests
        url = 'http://hostname:port/api/DAQ/addresses'
        requests.get(url).json()
        ```

        ## JavaScript code qith Axios Library
        ```
        axios({
            method: 'get',
            url: 'http://hostname:port/api/DAQ/addresses',
        });
        ```
        """
        
        return Addresses.read_all(), 200

@ns.route("/<id>")
class AddressResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def get(self, id:int)->tuple[dict, int]:
        r"""
        Select a single record

        You can use this endpoint to retrieve a single instance matching the given query. 

        This endpoint is a shortcut that calls Protocol.select() with the given query, but limits the result set to a single row. 
        Additionally, if no model matches the given query, a DoesNotExist exception will be raised.

        ## Python code with requests Library
        ```
        import requests
        url = 'http://hostname:port/api/DAQ/addresses/<id>'
        requests.get(url).json()
        ```

        ## JavaScript code qith Axios Library
        ```
        axios({
            method: 'get',
            url: 'http://hostname:port/api/DAQ/addresses/<id>',
        });
        ```
        """
        return Addresses.read(id), 200
