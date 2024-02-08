from peewee import CharField
from PyIAC.dbmodels import BaseModel
from PyIAC import PyIAC

core_app = PyIAC()


@core_app.define_table
class Protocols(BaseModel):

    name = CharField(unique=True)

    @classmethod
    def create(cls, name:str)-> dict:
        r"""
        You can use Model.create() to create a new model instance. This method accepts keyword arguments, where the keys correspond 
        to the names of the model's fields. A new instance is returned and a row is added to the table.

        ```python
        >>> Protocols.create(name='opc-ua')
        {
            'message': (str)
            'data': (dict) {
                'name': 'opc-ua'
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

        name = name.lower()

        if not cls.name_exist(name):
            
            query = cls(name=name)
            query.save()
            message = f"{name} protocol created successfully"
            data.update(query.serialize())

            result.update(
                {
                    'message': message, 
                    'data': data
                }
            )
            return result

        message = f'{name} protocol is already exist'        
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
        url = 'http://hostname:port/api/DAS/protocols'
        requests.get(url).json()
        ```

        ## JavaScript code qith Axios Library
        ```
        axios({
            method: 'get',
            url: 'http://hostname:port/api/DAS/protocols',
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
    def read_by_name(cls, name:str) -> dict:
        r"""
        Select a single record

        You can use this method to retrieve a single instance matching the given query. 

        This method is a shortcut that calls Model.select() with the given query, but limits the result set to a single row. 
        Additionally, if no model matches the given query, a DoesNotExist exception will be raised.

        ## Python code with requests Library
        ```
        import requests
        url = 'http://hostname:port/api/DAS/protocols'
        requests.get(url).json()
        ```

        ## JavaScript code qith Axios Library
        ```
        axios({
            method: 'get',
            url: 'http://hostname:port/api/DAS/protocols',
        });
        ```

        **Parameters**

        * **id:** (int), Record ID

        **Returns**

        * **result:** (dict) --> {'message': (str), 'data': (list) row serialized}

        """
        result = dict()
        data = dict()
        query = cls.select().where(cls.name == name).get_or_none()

        if query:
            
            message = f"You have got protocol {name} successfully"
            data.update(query.serialize())

            result.update(
                {
                    'message': message, 
                    'data': data
                }
            )
            return result

        message = f'Protocol {name} not exist into database'       
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

        This endpoint is a shortcut that calls Protocol.select() with the given query.

        ## Python code with requests Library
        ```
        import requests
        url = 'http://hostname:port/api/DAS/protocols'
        requests.get(url).json()
        ```

        ## JavaScript code qith Axios Library
        ```
        axios({
            method: 'get',
            url: 'http://hostname:port/api/DAS/protocols',
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
        url = 'http://hostname:port/api/DAS/protocols/<id>'
        payload = {'name': 'opc-ua'}
        requests.put(url, json=payload).json()
        ```

        ## JavaScript code qith Axios Library
        ```
        axios({
            method: 'put',
            url: 'http://hostname:port/api/DAS/protocols/<id>',
            data: {
                'name': 'opc-ua'
            }
        });
        ```
        """
        result = dict()
        data = dict()
        
        if cls.check_record(id):

            if 'name' in fields:

                name = fields['name']

                if cls.name_exist(name):

                    message = f"You cannot update ID {id} to name: {name} because that name is already exist into database"
                    query = cls.select().where(cls.id == id).get_or_none()
                    result.update(
                        {
                            'message': message,
                            'data': query.serialize()
                        }
                    )

                    return result

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

            return {'message': f"You have deleted id {id} from Protocols table"}

        return {'message': f"id {id} not exist into Protocols table"}

    @classmethod
    def name_exist(cls, name:str)->bool:
        r"""
        Verify is a protocol name exist into database

        **Parameters**

        * **name:** (str) Protocol name

        **Returns**

        * **bool:** If True, name exist into database 
        """
        query = cls.get_or_none(name=name)
        
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

    def serialize(self)-> dict:
        r"""
        Serialize database record to a jsonable object
        """

        return {
            "id": self.id,
            "name": self.name
        }
