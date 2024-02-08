from peewee import CharField, ForeignKeyField, IntegerField
from PyIAC.dbmodels import BaseModel
from PyIAC import PyIAC
from . import Protocols
from app.modules.opcua.models import Client

core_app = PyIAC()


@core_app.define_table
class Channels(BaseModel):

    protocol_id = ForeignKeyField(Protocols, backref='channels', on_delete='CASCADE')
    hostname = CharField()
    port = IntegerField()

    @classmethod
    def create(cls, protocol:str, hostname:str, port:int)-> dict:
        r"""
        You can use Model.create() to create a new model instance. This method accepts keyword arguments, where the keys correspond 
        to the names of the model's fields. A new instance is returned and a row is added to the table.

        ```python
        >>> Channels.create(protocol='opc-ua', hostname="0.0.0.0", port=53530)
        {
            'message': (str)
            'data': (dict) {
                'protocol': 'opcu-ua',
                'hostname': '0.0.0.0',
                'port': 53530
            }
        }
        ```
        
        This will INSERT a new row into the database. The primary key will automatically be retrieved and stored on the model instance.

        **Parameters**

        * **name:** (str), Industrial protocol name

        **Returns**

        * **result:** (dict) --> {'message': (str), 'data': (dict) row serialized}

        """
        result = dict()
        data = dict()

        _protocol = Protocols.read_by_name(name=protocol)
        if 'id' in _protocol['data']:
            protocol_id = _protocol['data']['id']

            if cls.check_endpoint(hostname, port):

                query = cls(protocol_id=protocol_id, hostname=hostname, port=port)
                query.save()
                
                if protocol.lower() in ['opcua', 'ua', 'opc-ua', 'opc_ua']:
                    
                    query.opcua_endpoints()

                    message = f"{protocol} protocol created successfully"
                    data.update(query.serialize())

                    result.update(
                        {
                            'message': message, 
                            'data': data
                        }
                    )
                    return result

                message = f"{protocol} protocol is not a valid protocol name"
                result.update(
                    {
                        'message': message, 
                        'data': data
                    }
                )
                return result

            message = f"{protocol} server is not running in Host: {hostname} and Port: {port}"
            result.update(
                {
                    'message': message, 
                    'data': data
                }
            )
            return result

        message = f"{protocol} protocol is not a valid protocol name"
        result.update(
            {
                'message': message, 
                'data': data
            }
        )
        return result

    @classmethod
    def read(cls, id:int) -> dict:
        r"""
        Select a single record

        You can use this method to retrieve a single instance matching the given query. 

        This method is a shortcut that calls Model.select() with the given query, but limits the result set to a single row. 
        Additionally, if no model matches the given query, a DoesNotExist exception will be raised.

        ## Python code with requests Library
        ```
        import requests
        url = 'http://hostname:port/api/DAS/channels'
        requests.get(url).json()
        ```

        ## JavaScript code qith Axios Library
        ```
        axios({
            method: 'get',
            url: 'http://hostname:port/api/DAS/channels',
        });
        ```

        **Parameters**

        * **id:** (int), Record ID

        **Returns**

        * **result:** (dict) --> {'message': (str), 'data': (list) row serialized}

        """
        result = dict()
        data = dict()
        query = cls.select().where(cls.id == id).get_or_none()

        if query:
            
            message = f"You have got id {id} successfully"
            data.update(query.serialize())

            result.update(
                {
                    'message': message, 
                    'data': data
                }
            )
            return result

        message = f'ID {id} not exist into database'       
        result.update(
                {
                    'message': message, 
                    'data': data
                }
            )

        return result

    @classmethod
    def read_all(cls):
        r"""
        Select all records

        You can use this method to retrieve all instances matching in the database. 

        This endpoint is a shortcut that calls Channels.select() with the given query.

        ## Python code with requests Library
        ```
        import requests
        url = 'http://hostname:port/api/DAS/channels'
        requests.get(url).json()
        ```

        ## JavaScript code qith Axios Library
        ```
        axios({
            method: 'get',
            url: 'http://hostname:port/api/DAS/channels',
        });
        ```

        **Parameters**

        **Returns**

        * **result:** (dict) --> {'message': (str), 'data': (list) row serialized}
        """

        result = dict()
        data = list()
        
        try:
            data = [query.serialize() for query in cls.select()]
            message = f"You have got all records successfully"

            result.update(
                {
                    'message': message, 
                    'data': data
                }
            )
            return result

        except Exception as _err:

            message = f"{_err}"
            result.update(
                {
                    'message': message, 
                    'data': data
                }
            )
            return result

    @classmethod
    def put(cls, id:int, **fields)-> dict:
        r""""
        Update a single record

        Once a model instance has a primary key, you UPDATE a field by its id. 
        The model's primary key will not change:

        ## Python code with requests Library
        ```
        import requests
        url = 'http://hostname:port/api/DAS/channels/<id>'
        payload = {'name': 'opc-ua'}
        requests.put(url, json=payload).json()
        ```

        ## JavaScript code qith Axios Library
        ```
        axios({
            method: 'put',
            url: 'http://hostname:port/api/DAS/channels/<id>',
            data: {
                'name': 'opc-ua'
            }
        });
        ```
        """
        result = dict()
        data = dict()
        
        if cls.check_record(id):

            query = cls.update(**fields).where(cls.id == id)
            query.execute()
            message = f"You updated ID {id} successfuly"
            query = cls.select().where(cls.id == id).get_or_none()
            result.update(
                {
                    'message': message,
                    'data': query.serialize()
                }
            )

            return result

        message = f"ID {id} not exist into database"

        result.update(
            {
                'message': message,
                'data': data
            }
        )

        return result

    @classmethod
    def delete(cls, id:int):
        r"""
        Documentation here
        """
        if cls.check_record(id):
        
            super().delete(id)

            return {'message': f"You have deleted id {id} from Channels table"}

        return {'message': f"id {id} not exist into Channels table"}

    @classmethod
    def protocol_exist(cls, protocol:str)->bool:
        r"""
        Verify is a protocol name exist into database

        **Parameters**

        * **protocol:** (str) Protocol name

        **Returns**

        * **bool:** If True, name exist into database 
        """
        query = cls.get_or_none(protocol=protocol)
        
        if query is not None:

            return True
        
        return False

    @classmethod
    def check_record(cls, id:int)->bool:
        r"""
        Verify if a record exist by its id

        **Parameters**

        * **id:** (int) Record ID

        **Returns**

        * **bool:** If True, so id record exist into database
        """
        query = cls.get_or_none(id=id)
        if query is not None:

            return True
        
        return False
        
    def opcua_endpoints(self):
        r"""
        Documentation here
        """ 
        from .addresses import Addresses

        result, _ = Client.get_endpoints(self.hostname, self.port)

        for address in result['endpoints']:

            endpoint = address.split(f"{self.hostname}:{self.port}/")[-1]

            Addresses.create(self.id, endpoint=endpoint, address=address)

    @classmethod
    def check_endpoint(cls, hostname:str, port:int):
        r"""
        Documentation here
        """
        _, status_code = Client.get_endpoints(hostname, port)
        if status_code == 200:

            return True

        return False


    def serialize(self)-> dict:
        r"""
        Serialize database record to a jsonable object
        """

        return {
            "id": self.id,
            "protocol": self.protocol_id.name,
            "hostname": self.hostname,
            "port": self.port,
            "addresses": [addr.address for addr in self.addresses]
        }
