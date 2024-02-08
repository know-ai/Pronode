from flask_restx import Namespace, Resource, fields
from PyIAC import PyIAC
from app.extensions.api import api
from app.extensions import _api as Api
from ..models import Protocols
from app import APP_AUTH

api_security = None
if APP_AUTH:
    api_security = 'apikey'


ns = Namespace('Protocols', description='Communication Industrial Protocols')

protocol_model = api.model("protocol_model",{
    'name': fields.String(required=True, description='Industrial Protocol Name [opcua - modbus rtu - modbus tcp ...]')
})

update_model = api.model("update_model",{
    'name': fields.String(required=False, description='Industrial Protocol Name [opcua - modbus rtu - modbus tcp ...]')
})


core_app = PyIAC()

@ns.route('/')
class ProtocolsCollection(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def get(self)->tuple[dict, int]:
        """
        Select all records

        You can use this endpoint to retrieve all instances matching in the database. 

        This endpoint is a shortcut that calls Protocol.select() with the given query.

        ## Python code with requests Library
        ```
        import requests
        url = 'http://hostname:port/api/DAQ/protocols'
        requests.get(url).json()
        ```

        ## JavaScript code qith Axios Library
        ```
        axios({
            method: 'get',
            url: 'http://hostname:port/api/DAQ/protocols',
        });
        ```
        """
        
        return Protocols.read_all(), 200

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(protocol_model)
    def post(self)->tuple[dict, int]:
        """
        Create a new model instance

        You can create a new model instance. This method accepts keyword arguments, where the keys correspond 
        to the names of the model's fields. A new instance is returned and a row is added to the table.

        ## Python code with requests Library
        ```
        import requests
        url = 'http://hostname:port/api/DAQ/protocols'
        payload = {'name': 'opcua'}
        requests.post(url, json=payload).json()
        ```

        ## JavaScript code qith Axios Library
        ```
        axios({
            method: 'post',
            url: 'http://hostname:port/api/DAQ/protocols',
            data: {
                'name': 'opcua'
            }
        });
        ```
        
        This will INSERT a new row into the database. The primary key will automatically be retrieved and stored on the model instance.
        """
        
        return Protocols.create(**api.payload), 200

@ns.route("/<id>")
class ProtocolResource(Resource):

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
        url = 'http://hostname:port/api/DAQ/protocols/<id>'
        requests.get(url).json()
        ```

        ## JavaScript code qith Axios Library
        ```
        axios({
            method: 'get',
            url: 'http://hostname:port/api/DAQ/protocols/<id>',
        });
        ```
        """
        return Protocols.read(id), 200

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(update_model)
    def put(self, id:int)->tuple[dict, int]:
        """
        Update a single record

        Once a model instance has a primary key, you UPDATE a field by its id. 
        The model's primary key will not change:

        ## Python code with requests Library
        ```
        import requests
        url = 'http://hostname:port/api/DAQ/protocols/<id>'
        payload = {'name': 'opc-ua'}
        requests.put(url, json=payload).json()
        ```

        ## JavaScript code qith Axios Library
        ```
        axios({
            method: 'put',
            url: 'http://hostname:port/api/DAQ/protocols/<id>',
            data: {
                'name': 'opc-ua'
            }
        });
        ```
        """
        payload = {}
        
        if 'name' in api.payload:

            payload.update({'name': api.payload['name']})

            return Protocols.put(id, **payload), 200

        return {}, 200

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def delete(self, id:int)->tuple[dict, int]:
        """
        Delete a single record

        To delete a single model instance, you can use this endpoint. 
        It will delete the given model instance and any dependent objects recursively.

        ## Python code with requests Library
        ```
        import requests
        url = 'http://hostname:port/api/DAQ/protocols/<id>'
        requests.delete(url).json()
        ```

        ## JavaScript code qith Axios Library
        ```
        axios({
            method: 'delete',
            url: 'http://hostname:port/api/DAQ/protocols/<id>',
        });
        ```
        """
        
        return Protocols.delete(id), 200