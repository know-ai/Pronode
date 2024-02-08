from flask_restx import Namespace, Resource, fields
from PyIAC import PyIAC
import json, csv
from opcua.ua.uatypes import datatype_to_varianttype
from app.extensions.api import api
from app.extensions import _api as Api
from app import app
from ..models import Client
from ..subscription import SubHandler
import psutil
from app import APP_AUTH
from opcua import ua


def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False

def return_attrs_value_jsonable(attrs):
    r"""
    Documentation here
    """

    value = attrs['Value']

    new_value = {
        'tag': value.tag,
        'state': value.state,
        'enabled': value.enabled,
        'process': value.process,
        'triggered': value.triggered,
        'trigger_value': value.trigger_value,
        'acknowledged': value.acknowledged,
        'value': value.value,
        'type': value.type,
        'audible': value.audible,
        'priority': value.priority,
        'is_process_alarm': value.is_process_alarm,
    }

    attrs['Value'] = new_value

    return attrs


api_security = None
if APP_AUTH:
    api_security = 'apikey'

ns = Namespace('OPCUA client', description='OPCUA Client')

connect_to_server_model = api.model("connect_to_server_model", {
    'url': fields.String(required=True, description='OPCUA Server URL')
})

get_endpoints_model = api.model("get_endpoints_model", {
    'hostname': fields.String(required=True, description='hostname'),
    'port': fields.String(required=True, description='port')
})

servers_on_network_model = api.model("servers_on_network_model", {
    'hostname': fields.String(required=True, description='hostname')
})

get_node_attrs_model = api.model("get_node_attrs_model", {
    'namespace': fields.String(required=True, description='node namespace'),
    'client_id': fields.String(required=True, description='Client ID')
})

subscription_model = api.model("subscription_model", {
    'namespace': fields.String(required=True, description='node namespace'),
    'client_id': fields.String(required=True, description='Client ID')
})

subscribe_all_model = api.model("subscribe_all_model", {
    'client_id': fields.String(required=True, description='Client ID')
})

get_nodes_attrs_model = api.model("get_nodes_attrs_model", {
    'namespaces': fields.List(fields.String),
    'client_id': fields.String(required=True, description='Client ID')
})

core_app = PyIAC()
db_manager = core_app.get_db_manager()

# Read Current Value Table Binding
daq_machine = core_app.get_machine('DAQ')

@ns.route('/connect_to_server')
class ConnectToServerResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(connect_to_server_model)
    def post(self):
        """
        Connect to a OPC UA Server
        """
        url = api.payload['url']
        _client = Client(url)
        result = _client.connect()
        app.opcua_client_manager.append_client(_client)
        return result

@ns.route('/is_connected/<client_id>')
class IsConnectedResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def get(self, client_id):
        """
        Connect to a OPC UA Server
        """
        _client = app.opcua_client_manager.get_client_by_id(client_id)
        if _client == None:
            
            return {'is_connected': False}, 200
        
        result = _client.is_connected()
        
        return result


@ns.route('/disconnect/<client_id>')
class DisconnectToServerResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def get(self, client_id):
        """
        Disconnect client from server
        """
        try:
            _client = app.opcua_client_manager.get_client_by_id(client_id)
            result = _client.disconnect()
            app.opcua_client_manager.remove_client(_client.get_id())
            return result
        except Exception as err:

            return {'message': ''}, 202

@ns.route('/get_opc_tree/<client_id>')
class GetOPCTreeResource(Resource):
    
    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def get(self, client_id):
        """Get OPC Tree"""
        _client = app.opcua_client_manager.get_client_by_id(client_id)
        tree = _client.get_opc_ua_tree()
        return tree

@ns.route('/export_opcua_tree_to_csv/<client_id>')
class ExportOPCTreeToCSVResource(Resource):
    
    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def get(self, client_id):
        """Export OPC UA Tree to CSV"""
        _client = app.opcua_client_manager.get_client_by_id(client_id)
        root = _client.get_objects_node()
        node = _client.get_node(root)
        self.tag_name = list()
        self.to_csv = list()
        self.browse_recursive(node, _client)
        keys = self.to_csv[0].keys()

        with open('daq_opcua_server_nodes.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.to_csv)

        return {'message': True}, 200

    def browse_recursive(self, node, client):
        
        for childId in node.get_children():
            ch = client.get_node(childId)

            if ch.get_browse_name().Name not in ('Aliases', 'MyObjects', 'Server', 'StaticData'):

                if ch.get_node_class() == ua.NodeClass.Object:
                    
                    self.tag_name.append(ch.get_display_name().Text)
                    self.browse_recursive(ch, client)

                elif ch.get_node_class() == ua.NodeClass.Variable:
                    
                    self.tag_name.append(ch.get_display_name().Text)
                    namespace = ch.nodeid.to_string()
                    unit = ch.get_browse_name().Name
                    data_type = datatype_to_varianttype(ch.get_data_type()).name
                    _to_csv = {
                        'tag_name': '.'.join(self.tag_name),
                        'namespace': namespace,
                        'unit': unit,
                        'data_type': data_type
                    }
                    self.to_csv.append(_to_csv)

                    props = ch.get_properties()
                    if props:

                        for prop in props:

                            self.tag_name.append(prop.get_display_name().Text)
                            namespace = prop.nodeid.to_string()
                            unit = prop.get_browse_name().Name
                            data_type = datatype_to_varianttype(prop.get_data_type()).name
                            _to_csv = {
                                'tag_name': '.'.join(self.tag_name),
                                'namespace': namespace,
                                'unit': unit,
                                'data_type': data_type
                            }
                            self.to_csv.append(_to_csv)

                            self.tag_name.pop()

                    self.tag_name.pop()

        if self.tag_name:
            self.tag_name.pop()


@ns.route('/get_endpoints')
class GetEndpointsResources(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(get_endpoints_model)
    def post(self):
        """
        Get Endpoints given a hostname and port
        """
        hostname = api.payload['hostname']
        port = api.payload['port']
        endpoints = Client.get_endpoints(hostname, port)

        return endpoints

@ns.route('/find_servers_on_network')
class FindServersOnNetworkResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def get(self):
        """
        Find Servers on Network
        """
        connections = psutil.net_connections()
        opcua_servers = list()
        for connection in connections:
            
            hostname = connection[3].ip
            port = connection[3].port
            status = connection[5]
            if status.lower()=='listen':
                
                result, status_code = Client.get_endpoints(hostname, port)
            
                if status_code==200:

                    opcua_servers.extend(result['endpoints'])

        return opcua_servers, 200

@ns.route('/node_attributes')
class NodeAttributesResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(get_node_attrs_model)
    def post(self):
        r"""
        Get node attributes by node namespace
        """
        client_id = api.payload['client_id']
        _client = app.opcua_client_manager.get_client_by_id(client_id)
        node_namespace = api.payload['namespace']
        attrs, status_code = _client.get_node_attributes(node_namespace)
        if is_jsonable(attrs):

            return attrs, status_code

        return return_attrs_value_jsonable(attrs), status_code

@ns.route('/nodes_values')
class NodesValuesCollection(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(get_nodes_attrs_model)
    def post(self):
        r"""
        Get node attributes by node namespace
        """
        client_id = api.payload['client_id']
        _client = app.opcua_client_manager.get_client_by_id(client_id)
        namespaces = api.payload['namespaces']
        attrs, status_code = _client.get_nodes_values(namespaces)
        if is_jsonable(attrs):

            return attrs, status_code

        return return_attrs_value_jsonable(attrs), status_code

@ns.route('/referenced_nodes')
class ReferencedNodesCollection(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(get_node_attrs_model)
    def post(self):
        r"""
        Get node attributes by node namespace
        """
        node_namespace = api.payload['namespace']
        client_id = api.payload['client_id']
        _client = app.opcua_client_manager.get_client_by_id(client_id)
        
        referenced_nodes, status_code = _client.get_referenced_nodes(node_namespace)

        return referenced_nodes, status_code

@ns.route('/get_clients')
class ClientCollection(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def get(self):
        r"""
        Get All Clients
        """

        return app.opcua_client_manager.get_clients(), 200

@ns.route('/create_subscription')
class CreateSubscriptionResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(subscription_model)
    def post(self):
        """
        Subscribe client node ID to server to monitor variables when it changes
        """
        namespace = api.payload['namespace']

        if namespace in daq_machine.handles_subscribed.keys():

            return {"message": f"{namespace} is already subscribed"}, 400

        handler = SubHandler()
        client_id = api.payload['client_id']
        _client = app.opcua_client_manager.get_client_by_id(client_id)
        subscriber = _client.create_subscription(500, handler)
        
        myvar = _client.get_node(namespace)
        daq_machine.handles_subscribed.update(
                {f"{namespace}": subscriber.subscribe_data_change(myvar)}
            )

        return {"message": f"{namespace} subscribed successfully"}, 200

@ns.route('/subscribe_all')
class SubscribeAllResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(subscribe_all_model)
    def post(self):
        """
        Tags must have *address* and *node_namespace* attributes defined, if they have a valid OPCUA address and node_namespace,
        this request allows to you subscribe these tags to OPCUA Server to update values every time tha tags in OPCUA server change.
        """
        query = db_manager.get_tags()
        handler = SubHandler()
        client_id = api.payload['client_id']
        _client = app.opcua_client_manager.get_client_by_id(client_id)
        subscriber = _client.create_subscription(500, handler)
        tags_subscribed = list()

        for tag, value in query.items():

            namespace = value['node_namespace']
            if namespace in daq_machine.handles_subscribed.keys() or not namespace:
                
                continue

            myvar = _client.get_node(namespace)
            daq_machine.handles_subscribed.update(
                    {f"{namespace}": subscriber.subscribe_data_change(myvar)}
                )
            tags_subscribed.append(tag)

        return {"message": f"{tags_subscribed} subscribed successfully"}, 200

