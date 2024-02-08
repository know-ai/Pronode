from flask_restx import Namespace, Resource, fields
from PyIAC import PyIAC
from app.extensions.api import api
from app.extensions import _api as Api
from ..models import Channels, Protocols
from app import APP_AUTH

api_security = None
if APP_AUTH:
    api_security = 'apikey'


ns = Namespace('Channels', description='Communication Industrial Protocols Channels')

channel_model = api.model("channel_model",{
    'protocol': fields.String(required=True, description='Industrial Protocol Name [opcua - modbus rtu - modbus tcp ...]'),
    'hostname': fields.String(required=True, description='Server hostname'),
    'port': fields.Integer(required=True, description='Server port'),
})

update_channel_model = api.model("update_channel_model",{
    'protocol': fields.String(required=False, description='Industrial Protocol Name [opcua - modbus rtu - modbus tcp ...]'),
    'hostname': fields.String(required=True, description='Server hostname'),
    'port': fields.Integer(required=False, description='Server port address'),
})


core_app = PyIAC()

@ns.route('/')
class ChannelsCollection(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def get(self)->tuple[dict, int]:
        """
        Select all records

        You can use this endpoint to retrieve all instances matching in the database. 

        This endpoint is a shortcut that calls Channels.select() with the given query.

        ## Python code with requests Library
        ```
        import requests
        url = 'http://hostname:port/api/DAQ/channels'
        requests.get(url).json()
        ```

        ## JavaScript code qith Axios Library
        ```
        axios({
            method: 'get',
            url: 'http://hostname:port/api/DAQ/channels',
        });
        ```
        """
        
        return Channels.read_all(), 200

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(channel_model)
    def post(self)->tuple[dict, int]:
        """
        Create a new model instance

        You can create a new model instance. This method accepts keyword arguments, where the keys correspond 
        to the names of the model's fields. A new instance is returned and a row is added to the table.

        ## Python code with requests Library
        ```
        import requests
        url = 'http://hostname:port/api/DAQ/channels'
        payload = {'name': 'opcua'}
        requests.post(url, json=payload).json()
        ```

        ## JavaScript code qith Axios Library
        ```
        axios({
            method: 'post',
            url: 'http://hostname:port/api/DAQ/channels',
            data: {
                'name': 'opcua'
            }
        });
        ```
        
        This will INSERT a new row into the database. The primary key will automatically be retrieved and stored on the model instance.
        """
        
        return Channels.create(**api.payload), 200

@ns.route("/<id>")
class ChannelResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def get(self, id:int)->tuple[dict, int]:
        r"""
        Select a single record

        You can use this endpoint to retrieve a single instance matching the given query. 

        This endpoint is a shortcut that calls Channels.select() with the given query, but limits the result set to a single row. 
        Additionally, if no model matches the given query, a DoesNotExist exception will be raised.

        ## Python code with requests Library
        ```
        import requests
        url = 'http://hostname:port/api/DAQ/channels/<id>'
        requests.get(url).json()
        ```

        ## JavaScript code qith Axios Library
        ```
        axios({
            method: 'get',
            url: 'http://hostname:port/api/DAQ/channels/<id>',
        });
        ```
        """
        return Channels.read(id), 200

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(update_channel_model)
    def put(self, id:int)->tuple[dict, int]:
        """
        Update a single record

        Once a model instance has a primary key, you UPDATE a field by its id. 
        The model's primary key will not change:

        ## Python code with requests Library
        ```
        import requests
        url = 'http://hostname:port/api/DAQ/channels/<id>'
        payload = {'name': 'opc-ua'}
        requests.put(url, json=payload).json()
        ```

        ## JavaScript code qith Axios Library
        ```
        axios({
            method: 'put',
            url: 'http://hostname:port/api/DAQ/channels/<id>',
            data: {
                'name': 'opc-ua'
            }
        });
        ```
        """
        if 'protocol' in api.payload:

            protocol_name = api.payload.pop('protocol')

            protocol = Protocols.read_by_name(protocol_name)

            if 'id' in protocol['data']:

                protocol_id = protocol['data']['id']

                api.payload.update({'protocol_id': protocol_id})

            else:

                return {'message': f'protocol {protocol_name} not exist into database'}, 200
        
        return Channels.put(id, **api.payload), 200


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
        
        return Channels.delete(id), 200