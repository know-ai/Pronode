import unittest
from app.tests import client, AlarmsDB, tag_engine, alarm_manager


class TestDAQProtocolsApi(unittest.TestCase):
        

    def setUp(self) -> None:
        
        return super().setUp()

    def tearDown(self) -> None:

        return super().tearDown()
    
    def test_01_daq_protocols_add_resource(self):
        r"""
        Dcoumentation here
        """
        payloads = [{
            'name': 'opcua'
        },
        {
            'name': 'modbus-tcp'
        },
        {
            'name': 'ethernet-ip'
        }]

        for payload in payloads:

            response = client.post('api/daq/protocols/', json=payload)

            with self.subTest("Testing Status Code"):

                self.assertEqual(response.status_code, 200)

        response = client.get('api/daq/protocols/')

        with self.subTest("Testing Status Code"):

            self.assertEqual(response.status_code, 200)

        data = response.get_json()['data']
        expexted_data = [{
                'id': 1, 
                'name': 'opcua'
            }, 
            {
                'id': 2, 
                'name': 'modbus-tcp'
            }, 
            {
                'id': 3, 
                'name': 'ethernet-ip'
            }]
        self.assertListEqual(data, expexted_data)

    def test_02_daq_protocol_update_resource(self):
        r"""
        Documentation here
        """
        payload = {
            'name': 'modbus-rtu'
        }
        
        id = 2

        response = client.put(f'api/daq/protocols/{id}', json=payload)

        with self.subTest("Testing Status Code"):

            self.assertEqual(response.status_code, 200)

        response = client.get(f'api/daq/protocols/{id}')

        with self.subTest("Testing Status Code"):

            self.assertEqual(response.status_code, 200)

        data = response.get_json()['data']

        expected_data = {
            'id': id,    
            'name': payload['name']
        }

        self.assertDictEqual(data, expected_data)

    def test_03_daq_protocol_delete_resource(self):
        r"""
        Documentation here
        """
        id = 2
        response = client.delete(f'api/daq/protocols/{id}')

        with self.subTest("Testing Status Code"):

            self.assertEqual(response.status_code, 200)

        response = client.get(f'api/daq/protocols/{id}')

        with self.subTest("Testing Status Code"):

            self.assertEqual(response.status_code, 200)

        response = response.get_json()
        expected_response = {
            'message': f'ID {id} not exist into database', 
            'data': {}
            }

        self.assertDictEqual(response, expected_response)

        response = client.get(f'api/daq/protocols/')

        with self.subTest("Testing Status Code"):

            self.assertEqual(response.status_code, 200)

        response = response.get_json()
        expected_response = {
            'message': 'You have got all records successfully', 
            'data': [{
                'id': 1, 
                'name': 'opcua'
                }, 
                {'id': 3, 
                'name': 'ethernet-ip'}
            ]}

        self.assertDictEqual(response, expected_response)


if __name__=='__main__':

    unittest.main()