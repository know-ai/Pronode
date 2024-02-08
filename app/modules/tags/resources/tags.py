from flask_restx import Namespace, Resource, fields
from flask import send_file
from PyIAC import PyIAC
from PyIAC.logger import QueryLogger
from PyIAC.tags import CVTEngine
from app.extensions.api import api
from app.extensions import _api as Api
from PyIAC.dbmodels import Tags, TagValue
from app import APP_AUTH, APP_EVENT_LOG
from datetime import datetime, timedelta
from io import BytesIO, StringIO
import csv
import codecs

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

api_security = None
if APP_AUTH:
    api_security = 'apikey' 

class DictItem(fields.Raw):
    def output(self, key, obj, *args, **kwargs):
        try:
            dct = getattr(obj, self.attribute)
        except AttributeError:
            return {}
        return dct or {}


ns = Namespace('Tags', description='CVT Tags Repository')

query = QueryLogger()

query_last_model = api.model("query_last_model",{
    'tag_name': fields.String(required=True, description='Tag Name'),
    'seconds': fields.Integer(required=True, description='Last seconds to query')
})

query_current_model = api.model("query_current_model",{
    'tags':  DictItem()
})

query_model = api.model("query_model",{
    'tag_name': fields.String(required=True, description='Tag Name'),
    'greater_than_timestamp': fields.DateTime(required=True, default=datetime.now() - timedelta(minutes=2), description='Greater than DateTime'),
    'less_than_timestamp': fields.DateTime(required=True, default=datetime.now(), description='Less than DateTime')
})

query_trends_model = api.model("query_trends_model",{
    'tags':  fields.List(fields.String(), required=True),
    'greater_than_timestamp': fields.DateTime(required=True, default=datetime.now() - timedelta(minutes=2), description='Greater than DateTime'),
    'less_than_timestamp': fields.DateTime(required=True, default=datetime.now(), description='Less than DateTime')
})

query_values_model = api.model("query_values_model",{
    'tags':  fields.List(fields.String(), required=True),
    'timestamp': fields.DateTime(required=True, default=datetime.now(), description='DateTime')
})

add_tag_model = api.model("add_tag_model",{
    'tag_name': fields.String(required=True, description='Tag Name'),
    'data_type': fields.String(required=True, description='Datatype [float - int - bool - string]'),
    'unit': fields.String(required=True, description='Tag Unit'),
    'description': fields.String(required=True, description='Tag description'),
    'display_name': fields.String(required=False, description='Tag display name'),
    'min_value': fields.Float(required=False, description='Lower range for variable'),
    'max_value': fields.Float(required=False, description='Higher range for variable'),
    'tcp_source_address': fields.String(required=False, description="OPC UA Server URL to bind tag"),
    'node_namespace': fields.String(required=False, description="Node namespace to bind tag in OPCUA Server"),
    # 'sample_time': fields.Float(required=False, description="Period to log into database")
})


update_tag_model = api.model("update_tag_model",{
    'name': fields.String(required=False, description='Tag Name'),
    'data_type': fields.String(required=False, description='Datatype [float - int - bool - string]'),
    'unit': fields.String(required=False, description='Tag Unit'),
    'description': fields.String(required=False, description='Tag description'),
    'display_name': fields.String(required=False, description='Tag display name'),
    'min_value': fields.Float(required=False, description='Lower range for variable'),
    'max_value': fields.Float(required=False, description='Higher range for variable'),
    'tcp_source_address': fields.String(required=False, description="OPC UA Server URL to bind tag"),
    'node_namespace': fields.String(required=False, description="Node namespace to bind tag in OPCUA Server")
})

write_tag_model = api.model("write_tag_model",{
    'name': fields.String(required=False, description='Tag Name'),
    'value': fields.Float(required=False, description='Tag Value')
})

str_write_tag_model = api.model("str_write_tag_model",{
    'name': fields.String(required=False, description='Tag Name'),
    'value': fields.String(required=False, description='Tag Value')
})

read_tag_id_model = api.model("read_tag_id_model",{
    'tags':  fields.List(fields.String(), required=True)
})

write_tags_model = api.model("write_tags_model",{
    'tags':  fields.List(DictItem(attribute="'tag_name': 'tag_id', 'value': 0.0"), required=True)
})

convert_unit_model = api.model("convert_unit_model",{
    'tags':  DictItem(attribute="'tag_name': dict(value, unit)")
})

export_csv_model = api.model("export_csv_model",{
    'greater_than_timestamp': fields.DateTime(required=True, default=datetime.now() - timedelta(days=1), description='Greater than DateTime'),
    'less_than_timestamp': fields.DateTime(required=True, default=datetime.now(), description='Less than DateTime')
})

export_tags_csv_model = api.model("export_tags_csv_model",{
    'greater_than_timestamp': fields.DateTime(required=True, default=datetime.now() - timedelta(days=1), description='Greater than DateTime'),
    'less_than_timestamp': fields.DateTime(required=True, default=datetime.now(), description='Less than DateTime'),
    'tags': fields.List(fields.String(), required=True)
})

app = PyIAC()
# Read Current Value Table Binding
db_manager = app.get_db_manager()
daq_machine = app.get_machine('DAQ')
alarm_manager = app.get_alarm_manager()
tag_engine = CVTEngine()

@ns.route('/')
class TagsCollection(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def get(self):
        """
        Gets all tags defined
        """
        query = db_manager.get_tags()
        
        return query, 200


@ns.route('/min_max')
class MinMaxTagsResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def get(self):
        """
        Get Min Max values from all defined tags
        """
        # Check tag_name
        tags = db_manager.get_tags()

        result = dict()

        for tag in tags:
            tag_name = tag['name']
            _tag = tag_engine.serialize_tag_by_name(tag_name)
            result[tag_name] = {
                'min_value': _tag['min_value'],
                'max_value': _tag['max_value']
            }
        
        return result, 200 


@ns.route('/<id>')
class TagResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def get(self, id):
        """
        Get tag's definiton
        """
        # Check tag_name
        _tag = Tags.read(id)

        if _tag:
            
            tag = tag_engine.serialize_tag(_tag['data']['id'])
            return tag, 200

        return {'message': f"{tag.name} is not defined"}, 400

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(update_tag_model)
    def put(self, id):
        r"""
        Update tag in database and CVT
        """
        result = tag_engine.update_tag(id, **api.payload)
        
        if 'node_namespace' in api.payload.keys():
            
            daq_machine.refresh_namespaces()
            if APP_EVENT_LOG:
                Api.log_alarm_operation(
                    message=result["name"],
                    description="Update tag in database and CVT",
                    classification="User",
                    priority=1,
                    criticity=3
                )

        return result, 200

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def delete(self, id):
        """
        Delete tag from database and CVT
        """   
        tag = Tags.read(id)
        tag_engine.delete_tag(tag['data']['name'])
        if APP_EVENT_LOG:
            Api.log_alarm_operation(
                message="API Request",
                description="Delete tag from database and CVT",
                classification="User",
                priority=2,
                criticity=4
            )

        return {"message": f"id {id} deleted successfully"}, 200


@ns.route('/add')
class AddTagResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(add_tag_model)
    def post(self):
        """
        Add tag to Current Value Table
        """
        # Checking Tag Name
        tag_name = api.payload['tag_name']
        tags = db_manager.get_tags()
        if tag_name in tags:

            return {'message': f"{tag_name} is already defined"}, 400
        
        # Checking datatype
        datatype = api.payload['data_type'].lower()
        if not datatype in ['float', 'string', 'int', 'bool']:

            return {'message': f"{datatype} is not a valid datatype - try ['float', 'string', 'int', 'bool']"}

        unit = api.payload['unit']

        description = None
        if 'description' in api.payload:
            description = api.payload['description']

        display_name = None
        if 'display_name' in api.payload:
            display_name = api.payload['display_name']

        min_value = None
        if 'min_value' in api.payload:
            min_value = api.payload['min_value']

        max_value = None
        if 'max_value' in api.payload:
            max_value = api.payload['max_value']

        tcp_source_address = None
        if 'tcp_source_address' in api.payload:
            tcp_source_address = api.payload['tcp_source_address']

        node_namespace = None
        if 'node_namespace' in api.payload:
            node_namespace = api.payload['node_namespace']

        # Adding tag to cvt
        tag = (
            tag_name, 
            unit,
            datatype, 
            description, 
            display_name,
            min_value, 
            max_value, 
            tcp_source_address,
            node_namespace)
        tag_engine.set_tag(*tag)

        # Adding to log into Database
        db_manager.set_tag(*tag)
        _tag = Tags.read_by_name(tag_name)
        result = _tag.serialize()
        if APP_EVENT_LOG:
            Api.log_alarm_operation(
                message=tag_name,
                description="Delete tag from database and CVT",
                classification="User",
                priority=2,
                criticity=4
            )
        
        return result, 200

@ns.route('/name/<name>')
class TagResourceByName(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def get(self, name):
        """
        Get tag definitons by tag name
        """
        # Check tag_name
        _tag = Tags.read_by_name(name)

        if _tag:
            
            tag = tag_engine.serialize_tag(_tag.id)
            return tag, 200

        return {'message': f"{tag.name} is not defined"}, 400


@ns.route('/write')
class WriteTagResource(Resource):

    @api.doc()
    @ns.expect(write_tag_model)
    def post(self):
        """
        Add tag to Current Value Table
        """
        # Checking Tag Name
        tag_name = api.payload['name']
        value = api.payload['value']
        _result = tag_engine.write_tag(tag_name, value=value)
        
        return _result, 200


@ns.route('/str/write')
class StrWriteTagResource(Resource):

    @api.doc()
    @ns.expect(str_write_tag_model)
    def post(self):
        """
        Add tag to Current Value Table
        """
        # Checking Tag Name
        tag_name = api.payload['name']
        value = api.payload['value']
        _result = tag_engine.write_tag(tag_name, value=value)
        
        return _result, 200


@ns.route('/write_tags')
class WriteTagsResource(Resource):

    @api.doc()
    @ns.expect(write_tags_model)
    def post(self):
        """
        Write tags to Database
        """
        # Checking Tag Name
        tags = api.payload

        tag_engine.write_tags(tags)
        
        return {'message': True}, 200


@ns.route('/read_tag_id_by_name')
class ReadTagIDResource(Resource):

    @api.doc()
    @ns.expect(read_tag_id_model)
    def post(self):
        """
        Read tag id by tag name
        """
        # Checking Tag Name
        result = dict()
        for tag_name in api.payload:
            
            _tag = Tags.read_by_name(tag_name)
            if _tag:
            
                result[f'{tag_name}'] = _tag.id
        
        return result, 200


@ns.route('/query_last')
class QueryLastResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(query_last_model)
    def post(self):
        """
        Query Last Model 
        """
        tag = api.payload['tag_name']
        seconds = api.payload['seconds']     
        result = query.query_last(tag, seconds=seconds)['values']
        
        return result, 200


@ns.route('/query_current')
class QueryCurrentResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(query_current_model)
    def post(self):
        """
        Query Last Model 
        """
        tags = api.payload['tags']   
        result = daq_machine.read_tags(**tags)
        
        return result, 200


@ns.route('/query')
class QueryResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(query_model)
    def post(self):
        """
        Query tag value filtering by timestamp
        """
        tag_name = api.payload['tag_name']
        separator = '.'
        greater_than_timestamp = api.payload['greater_than_timestamp']
        start = greater_than_timestamp.replace("T", " ").split(separator, 1)[0] + '.00'
        less_than_timestamp = api.payload['less_than_timestamp']
        stop = less_than_timestamp.replace("T", " ").split(separator, 1)[0] + '.00'
    
        result = query.query_trend(tag_name, start, stop)
        
        return result, 200

@ns.route('/query_trend')
class QueryTrendResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(query_trends_model)
    def post(self):
        """
        Query tag value filtering by timestamp
        """
        tags = api.payload['tags']
        separator = '.'
        result = dict()
        greater_than_timestamp = api.payload['greater_than_timestamp']
        start = greater_than_timestamp.replace("T", " ").split(separator, 1)[0] + '.00'
        less_than_timestamp = api.payload['less_than_timestamp']
        stop = less_than_timestamp.replace("T", " ").split(separator, 1)[0] + '.00'
        result = query.query_trend_modified(start, stop, *tags)
        
        return result, 200
    
@ns.route('/query_trend_modified')
class QueryTrendModifiedResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(query_trends_model)
    def post(self):
        """
        Query tag value filtering by timestamp
        """
        tags = api.payload['tags']
        separator = '.'
        result = dict()
        greater_than_timestamp = api.payload['greater_than_timestamp']
        start = greater_than_timestamp.replace("T", " ").split(separator, 1)[0] + '.00'
        less_than_timestamp = api.payload['less_than_timestamp']
        stop = less_than_timestamp.replace("T", " ").split(separator, 1)[0] + '.00'
        result = query.query_trend_modified(start, stop, *tags)
        
        return result, 200

@ns.route('/query_trends')
class QueryTrendsResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(query_trends_model)
    def post(self):
        """
        Query tag value filtering by timestamp
        """
        tags = api.payload['tags']
        separator = '.'
        greater_than_timestamp = api.payload['greater_than_timestamp']
        start = greater_than_timestamp.replace("T", " ").split(separator, 1)[0] + '.00'
        less_than_timestamp = api.payload['less_than_timestamp']
        stop = less_than_timestamp.replace("T", " ").split(separator, 1)[0] + '.00'
        result = query.query_trend_modified(start, stop, *tags)
        
        return result, 200

@ns.route('/query_values')
class QueryValuesResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(query_values_model)
    def post(self):
        """
        Query tag value filtering by timestamp
        """
        tags = api.payload['tags']
        separator = '.'
        timestamp = api.payload['timestamp']
        stop = timestamp.replace("T", " ").split(separator, 1)[0] + '.00'
        values = query.query_values(stop, *tags)
        
        return values, 200


@ns.route('/export_to_csv')
class ExportToCSVResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(export_csv_model)
    def post(self):
        """
        Export Tag Database to CSV
        """
        separator = '.'
        _from = api.payload['greater_than_timestamp']
        _from = _from.replace("T", " ").split(separator, 1)[0] + '.00'
        _from = datetime. strptime(_from, DATETIME_FORMAT)
        _to = api.payload['less_than_timestamp']
        _to = _to.replace("T", " ").split(separator, 1)[0] + '.00'
        _to = datetime. strptime(_to, DATETIME_FORMAT)
    
        TagValue.export_to_csv(start=_from, end=_to)

        #return send_file( TagValue.get_exported_csv(start=_from, end=_to) , as_attachment=True)
        return {'message': True}, 200


@ns.route('/export_tags_to_csv')
class ExportTagsToCSVResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(export_tags_csv_model)
    def post(self):
        """
        Export Tag Database to CSV
        """
        separator = '.'
        _from = api.payload['greater_than_timestamp']
        _from = _from.replace("T", " ").split(separator, 1)[0] + '.00'
        _from = datetime. strptime(_from, DATETIME_FORMAT)
        _to = api.payload['less_than_timestamp']
        _to = _to.replace("T", " ").split(separator, 1)[0] + '.00'
        _to = datetime. strptime(_to, DATETIME_FORMAT)
        tags = api.payload['tags']
    
        TagValue.export_tags_to_csv(start=_from, end=_to, tags=tags)
        
        return {'message': True}, 200
    
@ns.route('/download_exported_csv')
class DownloadExportedToCSVResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(export_csv_model)
    def post(self):
        """
        Export Tag Database to CSV
        """
        separator = '.'
        _from = api.payload['greater_than_timestamp']
        _from = _from.replace("T", " ").split(separator, 1)[0] + '.00'
        _from = datetime. strptime(_from, DATETIME_FORMAT)
        _to = api.payload['less_than_timestamp']
        _to = _to.replace("T", " ").split(separator, 1)[0] + '.00'
        _to = datetime. strptime(_to, DATETIME_FORMAT)

        csv_bytes = StringIO(TagValue.get_exported_csv(start=_from, end=_to))
        
        return send_file(BytesIO(csv_bytes.getvalue().encode()),
                     mimetype='csv',
                     download_name='export.csv',
                     as_attachment=True)


@ns.route('/download_exported_tags_csv')
class DownloadExportedTagsToCSVResource(Resource):

        @api.doc(security=api_security)
        @Api.token_required(auth=APP_AUTH)
        @ns.expect(export_tags_csv_model)
        def post(self):
            """
            Export Tag Database to CSV
            """
            separator = '.'
            _from = api.payload['greater_than_timestamp']
            _from = _from.replace("T", " ").split(separator, 1)[0] + '.00'
            _from = datetime. strptime(_from, DATETIME_FORMAT)
            _to = api.payload['less_than_timestamp']
            _to = _to.replace("T", " ").split(separator, 1)[0] + '.00'
            _to = datetime. strptime(_to, DATETIME_FORMAT)
            tags = api.payload['tags']
        

            csv_bytes = StringIO(TagValue.get_exported_tags_csv(start=_from, end=_to, tags=tags))
            return send_file(BytesIO(csv_bytes.getvalue().encode()),
                        mimetype='csv',
                        download_name='exported_tags.csv',
                        as_attachment=True)
    

@ns.route('/convert_units')
class ConvertUnitResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(convert_unit_model)
    def post(self)->tuple[dict, int]:
        """
        Documentatipon here
        """
        default_units = daq_machine.conversions
        result = tag_engine.convert_units_to_default(default_units=default_units, **api.payload)
        return result, 200