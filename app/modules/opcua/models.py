from opcua import Client as OPCClient
from opcua import ua
from opcua.ua.uatypes import NodeId, datatype_to_varianttype
import re
import uuid

DATETIME_FORMAT = "%m/%d/%Y, %H:%M:%S.%f"

class Client(OPCClient):
    r"""
    Documentation here
    """
    def __init__(self, url, timeout=4):
        r"""
        Documentation here
        """
        self._id = None
        self._server_url = url
        self._timeout = timeout
        self._client = None
        self._is_open = False
        self._opc_ua_tree = dict()
        super(Client, self).__init__(url, timeout)

    def get_id(self):
        r"""
        Documentation here
        """
        return self._id

    def connect(self):
        r"""
        Documentation here
        """
        try:

            super(Client, self).connect()
            self._is_open = True
            self._id = str(uuid.uuid4())
            result = {
                'message': 'Successful connection',
                'url': self._server_url,
                'is_connected': self._is_open,
                'id': self.get_id()
                }
            return result, 200

        except Exception as _err:
            
            self._is_open = False
            result = {
                'message': 'Connection could not be established',
                'url': self._server_url,
                'is_connected': self._is_open,
                'id': self.get_id()
                }
            return result, 404

    def __reset_object_attributes(self):
        r"""
        Documentation here
        """
        self._server_url = None
        self._client = None
        self._opc_ua_tree = dict()

    def disconnect(self):
        r"""
        Documentation here
        """
        try:
            super(Client, self).disconnect()
            self.__reset_object_attributes()
            result = {
                'message': 'Successful disconnection',
                'is_connected': False
                }
            return result, 200

        except Exception as _err:
            result = {'message': 'Disconnect could not be performed'}
            return result, 404

    def get_opc_ua_tree(self):
        r"""
        Documentation here
        """
        try:
            root = self.get_objects_node()
            node = self.get_node(root)
            tree = self.__walk_into_nodes(node)
            return tree, 200

        except Exception as _err:
            self.disconnect()
            result = { 'message': str(_err)}
            return result, 500

    def __walk_into_nodes(self, node, tree=None):
        r"""
        Documentation here
        """
        if tree is None:

            tree = dict()

        _object = list()

        for ref in node.get_children_descriptions():

            _node = self.get_node(ref.NodeId)
            # ('Aliases', 'MyObjects', 'Server', 'StaticData')

            if _node.get_browse_name().Name not in ('Aliases', 'MyObjects', 'Server', 'StaticData'):

                result = self.__opc_ua_tree(ref.NodeId)

                if _node.get_children():

                    _children = self.__get_children_node_recursively(_node)

                    result['children'] = _children
                
                _object.append(result)

        tree[f"{node.get_browse_name().Name}"] = _object

        return tree

    def __get_children_node_recursively(self, node, children=None):
        r"""
        Documentation here
        """

        if children is None:

            children = list()

        for child in node.get_children():

            result = self.__opc_ua_tree(child.nodeid)

            if child.get_children():

                _children = self.__get_children_node_recursively(child)

                result['children'] = _children

            children.append(result)            

        return children

    def __opc_ua_tree(self, namespace_node):
        r"""
        Documentation here
        """
        _node = self.get_node(namespace_node)

        result = {
            "title": _node.get_browse_name().Name,
            "key": _node.nodeid.to_string(),
            "children": [],
            "NodeClass": _node.get_node_class().name,
        }

        return result

    def get_values(self, nodes:list):
        r"""
        Documentation here
        """
            
        results = self.uaclient.get_attributes(nodes, ua.AttributeIds.Value)
        result = [{"Namespace": nodes[id].to_string(), "Value": result.Value.Value, "Timestamp": result.SourceTimestamp} for id, result in enumerate(results)]
        
        return result, 200

    def get_nodes_id_by_namespaces(self, namespaces:list):
        r"""
        Documentar here
        """
        nodes = list()

        for namespace in namespaces:

            _node = self.get_node(NodeId.from_string(namespace))
            nodes.append(_node)

        return nodes

    def get_nodes_values(self, namespaces):
        r"""
        Documentation here
        """
        result = list()
        nodes = list()

        for namespace in namespaces:

            _node = self.get_node(NodeId.from_string(namespace))
            nodes.append(_node)
                
            if _node.get_node_class().name.lower()=='variable':
                node = {
                    "Namespace": namespace,
                    "Value": _node.get_value()
                    }
                result.append(node)

        return result, 200

    @staticmethod
    def find_servers(hostname, port):
        r"""
        Documentation here
        """
        
        _client = OPCClient(f'opc.tcp://{hostname}:{port}')
        servers = _client.connect_and_find_servers()
        _servers = list()
        for server in servers:
            _server = dict()
            _server['ApplicationUri'] = server.ApplicationUri
            _server['ProductUri'] = server.ProductUri
            _server['ApplicationName'] = server.ApplicationName.Text
            _server['ApplicationType'] = server.ApplicationType.Server
            _server['GatewayServerUri'] = server.GatewayServerUri
            _server['DiscoveryProfileUri'] = server.DiscoveryProfileUri
            _server['DiscoveryUrls'] = server.DiscoveryUrls
            _servers.append(_server)

        return _servers

    @staticmethod
    def get_endpoints(hostname, port):
        r"""
        Documentation here
        """
        try:
            _client = OPCClient(f'opc.tcp://{hostname}:{port}')
            endpoints = _client.connect_and_get_server_endpoints()
            _endpoints = list()
            for ep in endpoints:

                if isinstance(ep.Server.DiscoveryUrls, list):
                    
                    _endpoints.extend(ep.Server.DiscoveryUrls)
                
                else:

                    _endpoints.append(ep.Server.DiscoveryUrls)

            _endpoints = list(set(_endpoints))

            for ep in _endpoints:
                if not ep.startswith('opc.tcp'):
                    _endpoints.remove(ep)

            result = [re.sub('//.*?/',f'//{hostname}:{port}/', __ep) for __ep in _endpoints]
            result = {
                'message': 'Successful search',
                'endpoints': result
            }

            return result, 200
            
        except Exception as err:

            result = {
                'message': 'Unsuccessful search',
                'endpoints': []
            }
            return result, 400

    def is_connected(self):
        r"""
        Documentation here
        """
        try:

            return self.uaclient._uasocket._connection.is_open()
        
        except Exception as _err:

            return False

    def get_node_attributes(self, node_namespace):
        r"""
        Documentation here
        """
        _node = self.get_node(NodeId.from_string(node_namespace))

        node_class = _node.get_node_class().name.lower()

        if node_class=='variable':

            result = {
                "NamespaceIndex": _node.nodeid.NamespaceIndex,
                "NamespaceUri": _node.nodeid.NamespaceUri,
                "Identifier": _node.nodeid.Identifier,
                "Namespace": _node.nodeid.to_string(),
                "NodeClass": _node.get_node_class().name,
                "BrowseName": _node.get_browse_name().Name,
                "DisplayName": _node.get_display_name().Text,
                "DataType": datatype_to_varianttype(_node.get_data_type()).name,
                "AccesLevel": [access_lvl.name for access_lvl in _node.get_access_level()],
                "UserAccessLevel": [user_access_lvl.name for user_access_lvl in _node.get_user_access_level()],
                "Description": _node.get_description().Text if _node.get_description() else None,
                "Value": _node.get_value(),
                "ArrayDimensions": _node.get_array_dimensions(),
                "ValueRank": _node.get_value_rank().name
            }

        else:

            result = {
                "NamespaceIndex": _node.nodeid.NamespaceIndex,
                "NamespaceUri": _node.nodeid.NamespaceUri,
                "Identifier": _node.nodeid.Identifier,
                "Namespace": _node.nodeid.to_string(),
                "NodeClass": _node.get_node_class().name,
                "BrowseName": _node.get_browse_name().Name,
                "DisplayName": _node.get_display_name().Text,
                "Description": _node.get_description().Text if _node.get_description() else ''
            }

        return result, 200

    def get_referenced_nodes(self, node_id):
        r"""
        Documentation here
        """
        _node = self.get_node(NodeId.from_string(node_id))
        referenced_nodes = _node.get_referenced_nodes()
        result = list()
        for count, node in  enumerate(referenced_nodes):

            node_name = node.get_browse_name().Name
            if count==0:
                result.append(('OrganizedBy', node_name))
            elif count==1:
                result.append(('HasTypeDefinition', node_name))
            else:
                result.append(('Organizes', node_name))

        return result, 200

    def serialize(self):
        r"""
        Documentation here
        """
        return {
            'client_id': self.get_id(),
            'server_url': self._server_url,
            'timeout': self._timeout,
            'is_opened': self._is_open
        }