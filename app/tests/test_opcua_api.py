import unittest
from app.tests import client, AlarmsDB, tag_engine, alarm_manager


class TestOPCUAApi(unittest.TestCase):
        

    def setUp(self) -> None:
        
        return super().setUp()

    def tearDown(self) -> None:

        return super().tearDown()
    
    def test_opcua_connect_to_server_resource(self):
        r"""
        Dcoumentation here
        """
        pass

    def test_opcua_is_connected_resource(self):
        r"""
        Documentation here
        """
        pass

    def test_opcua_disconnect_resource(self):
        r"""
        Documentation here
        """
        pass

    def test_opcua_tree_resource(self):
        r"""
        Documentation here
        """
        pass

    def test_opcua_endpoints_resource(self):
        r"""
        Documentation here
        """
        pass

    def test_opcua_server_network_resource(self):
        r"""
        Documentation here
        """
        pass

    def test_opcua_node_attributes_resource(self):
        r"""
        Documentation here
        """
        pass

    def test_opcua_node_values_resource(self):
        r"""
        Documentation here
        """
        pass

    def test_opcua_referenced_nodes_resource(self):
        r"""
        Documentation here
        """
        pass

    def test_opcua_clients_resource(self):
        r"""
        Documentation here
        """
        pass

    def test_opcua_create_subscription_resource(self):
        r"""
        Documentation here
        """
        pass

    def test_opcua_subscribe_all_resource(self):
        r"""
        Documentation here
        """
        pass


if __name__=='__main__':

    unittest.main()