from peewee import CharField, ForeignKeyField
from PyIAC.dbmodels import BaseModel
from PyIAC import PyIAC
from .channels import Channels

core_app = PyIAC()


@core_app.define_table
class Addresses(BaseModel):

    channel_id = ForeignKeyField(Channels, backref='addresses', on_delete='CASCADE')
    endpoint = CharField()
    address = CharField()

    @classmethod
    def create(cls, channel_id:int, endpoint:str, address:str)-> dict:
        r"""
        You can use Model.create() to create a new model instance. This method accepts keyword arguments, where the keys correspond 
        to the names of the model's fields. A new instance is returned and a row is added to the table.
        
        This will INSERT a new row into the database. The primary key will automatically be retrieved and stored on the model instance.

        **Parameters**

        * **name:** (str), Industrial protocol name

        **Returns**

        * **result:** (dict) --> {'message': (str), 'data': (dict) row serialized}

        """
            
        query = cls(channel_id=channel_id, endpoint=endpoint, address=address)
        query.save()
        message = f"{address} address created successfully"
        data = query.serialize()

        result = {
                'message': message, 
                'data': data
            }

        return result


    @classmethod
    def read(cls, id:int) -> dict:
        r"""
        Select a single record

        You can use this method to retrieve a single instance matching the given query. 

        This method is a shortcut that calls Model.select() with the given query, but limits the result set to a single row. 
        Additionally, if no model matches the given query, a DoesNotExist exception will be raised.

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

        This endpoint is a shortcut that calls Addresses.select() with the given query.

        ## Python code with requests Library
        ```
        import requests
        url = 'http://hostname:port/api/DAS/addresses'
        requests.get(url).json()
        ```

        ## JavaScript code qith Axios Library
        ```
        axios({
            method: 'get',
            url: 'http://hostname:port/api/DAS/addresses',
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
    def delete(cls, id:int):
        r"""
        Documentation here
        """
        if cls.check_record(id):
        
            super().delete(id)

            return {'message': f"You have deleted id {id} from Channels table"}

        return {'message': f"id {id} not exist into Channels table"}

    
    def serialize(self)-> dict: 
        r"""
        Serialize database record to a jsonable object
        """

        return {
            "id": self.id,
            "protocol": self.channel_id.protocol_id.name,
            "endpoint": self.endpoint,
            "address": self.address
        }