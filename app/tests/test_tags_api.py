import unittest
from app.tests import client, tag_engine, Tags, headers


class TestTagsApi(unittest.TestCase):
        

    def setUp(self) -> None:
        
        return super().setUp()

    def tearDown(self) -> None:

        return super().tearDown()
    
    def test_01_add_tag_resource(self):
        r"""
        Dcoumentation here
        """
        add_tag_model = {
            'tag_name': 'PT-100',
            'data_type': 'float',
            'unit': 'kPa',
            'description': 'Pressure transmissor at KP 100',
            'min_value': 10.132,
            'max_value': 101.325,
            'tcp_source_address': 'opc.tcp://127.0.0.1:53530/OPCUA/SimulationServer',
            'node_namespace': 'ns=3;i=1001'
        }

        response = client.post('api/tags/add', headers=headers, json=add_tag_model)
        tag_from_db = Tags.read_by_name(add_tag_model['tag_name'])

        with self.subTest("Testing Status Code"):

            self.assertEqual(response.status_code, 200)

        with self.subTest("Testing Response"):

            self.assertEqual(response.get_json(), tag_from_db.serialize())

    def test_02_tag_resource(self):
        r"""
        Documentation here
        """
        add_tag_model = {
            'tag_name': 'PT-100',
            'data_type': 'float',
            'unit': 'kPa',
            'description': 'Pressure transmissor at KP 100',
            'min_value': 10.132,
            'max_value': 101.325,
            'tcp_source_address': 'opc.tcp://127.0.0.1:53530/OPCUA/SimulationServer',
            'node_namespace': 'ns=3;i=1001'
        }
        client.post('api/tags/add', headers=headers, json=add_tag_model)

        # Testing Get Resource
        with self.subTest("Testing Get Resource"):
        
            response = client.get('api/tags/', headers=headers, query_string='1')

            self.assertEqual(response.status_code, 200)
            data = response.get_json()['1']
            min_data_expected = {
                'tag_name': data['name'],
                'data_type': data['data_type'],
                'unit': data['unit'],
                'description': data['description'],
                'min_value': data['min_value'],
                'max_value': data['max_value'],
                'tcp_source_address': data['tcp_source_address'],
                'node_namespace': data['node_namespace']
            }
            self.assertDictEqual(add_tag_model, min_data_expected)

        # Testing Update Resource
        with self.subTest("Testing Update Resource"):

            update_tag_model = {
                'min_value': 0.0,
                'max_value': 100.0
            }

            response = client.put('api/tags/1', headers=headers, json=update_tag_model)
            self.assertEqual(response.status_code, 200)
            data = response.get_json()['data']
            min_data_expected = {
                'tag_name': data['name'],
                'data_type': data['data_type'],
                'unit': data['unit'],
                'description': data['description'],
                'min_value': data['min_value'],
                'max_value': data['max_value'],
                'tcp_source_address': data['tcp_source_address'],
                'node_namespace': data['node_namespace']
            }
            add_tag_model['min_value'] = update_tag_model['min_value']
            add_tag_model['max_value'] = update_tag_model['max_value']

            self.assertEqual(add_tag_model, min_data_expected)

        # Testing Delete Resource
        with self.subTest("Testing Update Resource"):

            response = client.delete('api/tags/1', headers=headers)

            self.assertEqual(response.status_code, 200)
            
            self.assertFalse(tag_engine.tag_defined(add_tag_model['tag_name']))

    def test_03_tag_collection(self):
        r"""
        Documentation here
        """
        tags = list()
        tags.append({
            'tag_name': 'PT-100',
            'data_type': 'float',
            'unit': 'kPa',
            'description': 'Pressure transmissor at KP 100',
            'min_value': 10.132,
            'max_value': 101.325,
            'tcp_source_address': 'opc.tcp://127.0.0.1:53530/OPCUA/SimulationServer',
            'node_namespace': 'ns=3;i=1001'
        })

        tags.append({
            'tag_name': 'PT-200',
            'data_type': 'float',
            'unit': 'kPa',
            'description': 'Pressure transmissor at KP 200',
            'min_value': 1.013,
            'max_value': 10.132,
            'tcp_source_address': 'opc.tcp://127.0.0.1:53530/OPCUA/SimulationServer',
            'node_namespace': 'ns=3;i=1002'
        })

        for i, tag in enumerate(tags):

            client.post('api/tags/add', headers=headers, json=tag)

            response = client.get('api/tags/', headers=headers)

            self.assertEqual(response.status_code, 200)
        
            response = client.get('api/tags/', headers=headers, query_string=f'{i+1}')

            self.assertEqual(response.status_code, 200)
            data = response.get_json()[f'{i+1}']
            min_data_expected = {
                'tag_name': data['name'],
                'data_type': data['data_type'],
                'unit': data['unit'],
                'description': data['description'],
                'min_value': data['min_value'],
                'max_value': data['max_value'],
                'tcp_source_address': data['tcp_source_address'],
                'node_namespace': data['node_namespace']
            }
            self.assertEqual(tag, min_data_expected)

    def test_04_tag_min_max(self):
        r"""
        Documentation here
        """
        tags = list()
        tags.append({
            'tag_name': 'PT-100',
            'data_type': 'float',
            'unit': 'kPa',
            'description': 'Pressure transmissor at KP 100',
            'min_value': 10.132,
            'max_value': 101.325,
            'tcp_source_address': 'opc.tcp://127.0.0.1:53530/OPCUA/SimulationServer',
            'node_namespace': 'ns=3;i=1001'
        })

        tags.append({
            'tag_name': 'PT-200',
            'data_type': 'float',
            'unit': 'kPa',
            'description': 'Pressure transmissor at KP 200',
            'min_value': 1.013,
            'max_value': 10.132,
            'tcp_source_address': 'opc.tcp://127.0.0.1:53530/OPCUA/SimulationServer',
            'node_namespace': 'ns=3;i=1002'
        })

        expected_data = dict()
        for i, tag in enumerate(tags):

            client.post('api/tags/add', headers=headers, json=tag)
            expected_data[f'{i+1}'] = {
                'min_value': tag['min_value'],
                'max_value': tag['max_value'],
            }

        response = client.get('api/tags/min_max', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data, expected_data)

if __name__=='__main__':

    unittest.main()