import unittest
from app.tests import client, AlarmsDB, tag_engine, alarm_manager, headers


class TestAlarmsApi(unittest.TestCase):
        

    def setUp(self) -> None:
        
        return super().setUp()

    def tearDown(self) -> None:

        return super().tearDown()
    
    def test_01_add_alarm_resource(self):
        r"""
        Dcoumentation here
        """
        # First define a tag
        tag = {
            'tag_name': 'PT-100',
            'data_type': 'float',
            'unit': 'kPa',
            'description': 'Pressure transmissor at KP 100',
            'min_value': 10.132,
            'max_value': 101.325,
            'tcp_source_address': 'opc.tcp://127.0.0.1:53530/OPCUA/SimulationServer',
            'node_namespace': 'ns=3;i=1001'
        }
        response = client.post('api/tags/add', headers=headers, json=tag)

        with self.subTest("Testing Status Code"):

            self.assertEqual(response.status_code, 200)

        # Define Alarm
        alarm = {
            'name': 'PT-100-HH',
            'tag': tag['tag_name'],
            'description': 'Pressure transmissor Alarm at KP 100',
            'type': 'HIGH-HIGH',
            'trigger_value': 101.325
        }
        response = client.post('api/alarms/append', headers=headers, json=alarm)

        with self.subTest("Testing Status Code"):

            self.assertEqual(response.status_code, 200)

        with self.subTest("Testing Response"):

            data = response.get_json()
            alarm_from_db = AlarmsDB.read_by_name(alarm['name']).serialize()
            expected_data = {
                'id': data['id'],
                'name': data['name'],
                'tag': data['tag'],
                'description': data['description'],
                'alarm_type': data['type'],
                'trigger': data['trigger_value']
            }

            self.assertEqual(alarm_from_db, expected_data)

    def test_02_alarm_resource(self):
        r"""
        Documentation here
        """
        response = client.get('api/alarms/', headers=headers, query_string='1')

        with self.subTest("Testing Status Code"):

            self.assertEqual(response.status_code, 200)

        data = response.get_json()['1']

        expected_data = {
            'id': 1, 
            'timestamp': None, 
            'name': 'PT-100-HH', 
            'tag': 'PT-100', 
            'tag_alarm': None, 
            'state': 'Normal', 
            'mnemonic': 'NORM', 
            'enabled': True, 
            'process': 'Normal', 
            'triggered': False, 
            'trigger_value': 101.325, 
            'acknowledged': True, 
            'acknowledged_timestamp': None, 
            'value': False, 
            'type': 'HIGH-HIGH', 
            'audible': False, 
            'description':'Pressure transmissor Alarm at KP 100', 
            'operations': {
                'acknowledge': 'not active', 
                'enable': 'not active', 
                'disable': 'active', 
                'silence': 'not active', 
                'shelve': 'active', 
                'suppress by design': 'active', 
                'unsuppressed': 'not active', 
                'out of service': 'active', 
                'return to service': 'not active', 
                'reset': 'active'
                },
            'priority': 0
            }
        
        self.assertDictEqual(data, expected_data)

    def test_03_alarms_resource(self):
        r"""
        Documentation here
        """
        response = client.get('api/tags/', headers=headers)

        # Define Alarm
        alarm = {
            'name': 'PT-100-LL',
            'tag': 'PT-100',
            'description': 'Pressure transmissor Low-Low Alarm at KP 100',
            'type': 'LOW',
            'trigger_value': 20.5
        }

        response = client.post('api/alarms/append', headers=headers, json=alarm)
        
        with self.subTest("Testing Status Code"):

            self.assertEqual(response.status_code, 200)

        response = client.get('api/alarms/', headers=headers)

        with self.subTest("Testing Status Code"):

            self.assertEqual(response.status_code, 200)

        expected_data = {
            '1': {
                'id': 1, 
                'timestamp': None, 
                'name': 'PT-100-HH', 
                'tag': 'PT-100', 
                'tag_alarm': None, 
                'state': 'Normal', 
                'mnemonic': 'NORM', 
                'enabled': True, 
                'process': 'Normal', 
                'triggered': False, 
                'trigger_value': 101.325, 
                'acknowledged': True, 
                'acknowledged_timestamp': None, 
                'value': False, 
                'type': 'HIGH-HIGH', 
                'audible': False, 
                'description': 'Pressure transmissor Alarm at KP 100', 
                'operations': {
                    'acknowledge': 'not active', 
                    'enable': 'not active', 
                    'disable': 'active', 
                    'silence': 'not active', 
                    'shelve': 'active', 
                    'suppress by design': 'active', 
                    'unsuppressed': 'not active', 
                    'out of service': 'active', 
                    'return to service': 'not active', 
                    'reset': 'active'
                    },
                'priority': 0
                }, 
            '2': {
                'id': 2, 
                'timestamp': None, 
                'name': 'PT-100-LL', 
                'tag': 'PT-100', 
                'tag_alarm': None, 
                'state': 'Normal', 
                'mnemonic': 'NORM', 
                'enabled': True, 
                'process': 'Normal', 
                'triggered': False, 
                'trigger_value': 20.5, 
                'acknowledged': True, 
                'acknowledged_timestamp': None, 
                'value': False, 
                'type': 'LOW', 
                'audible': False, 
                'description': 'Pressure transmissor Low-Low Alarm at KP 100', 
                'operations': {
                    'acknowledge': 'not active', 
                    'enable': 'not active', 
                    'disable': 'active', 
                    'silence': 'not active', 
                    'shelve': 'active', 
                    'suppress by design': 'active', 
                    'unsuppressed': 'not active', 
                    'out of service': 'active', 
                    'return to service': 'not active', 
                    'reset': 'active'
                    },
                'priority': 0
                }
            }

        self.assertDictEqual(response.get_json(), expected_data)

    def test_04_triggered_alarm_resource(self):
        r"""
        Documentation here
        """
        # Write vaue to tag in cvt
        tag_engine.write_tag('PT-100', 102.0)
        # Update alarm value
        alarm_manager.execute('PT-100')
        alarm = alarm_manager.get_alarms_by_tag('PT-100')
        response = client.get('api/alarms/triggered', headers=headers)

        with self.subTest("Testing Status Code"):

            self.assertEqual(response.status_code, 200)

        self.assertEqual(response.get_json()[0], alarm['1'].serialize())
        
    def test_05_acknowledge_alarm_resource(self):
        r"""
        Documentation here
        """
        payload = {
            'alarm_id': 1
        }
        response = client.post('api/alarms/acknowledge', headers=headers, json=payload)

        with self.subTest("Testing Status Code"):

            self.assertEqual(response.status_code, 200)

        response = client.get('api/alarms/1', headers=headers)

        with self.subTest("Testing Status Code"):

            self.assertEqual(response.status_code, 200)

        alarm = response.get_json()

        with self.subTest("Testing Status Code"):

            self.assertIsNotNone(alarm['timestamp'])
            self.assertIsNotNone(alarm['acknowledged_timestamp'])
            self.assertEqual(alarm['state'], 'Acknowledged')
            self.assertEqual(alarm['name'], 'PT-100-HH')
            self.assertEqual(alarm['tag'], 'PT-100')
            self.assertEqual(alarm['mnemonic'], 'ACKED')
            self.assertEqual(alarm['enabled'], True)
            self.assertEqual(alarm['process'], 'Abnormal')
            self.assertEqual(alarm['triggered'], True)
            self.assertEqual(alarm['acknowledged'], True)
            self.assertEqual(alarm['value'], 102)
            self.assertEqual(alarm['type'], 'HIGH-HIGH')
            self.assertEqual(alarm['audible'], False)
            expected_operations = {
                'acknowledge': 'not active', 
                'enable': 'not active', 
                'disable': 'active', 
                'silence': 'not active', 
                'shelve': 'not active', 
                'suppress by design': 'not active', 
                'unsuppressed': 'not active', 
                'out of service': 'not active', 
                'return to service': 'not active', 
                'reset': 'active'
            }
            self.assertEqual(alarm['operations'], expected_operations)

    def test_06_lasts_alarms_resource(self):
        r"""
        Documentation here
        """
        response = client.get('api/alarms/lasts/1', headers=headers, query_string='1')

        with self.subTest("Testing Status Code"):

            self.assertEqual(response.status_code, 200)

        self.assertIsNotNone(response.get_json())

    def test_07_reset_alarm_resource(self):
        r"""
        Documentation here
        """
        payload = {
            'alarm_id': 1
        }
        response = client.post('api/alarms/reset', headers=headers, json=payload)

        with self.subTest("Testing Status Code"):

            self.assertEqual(response.status_code, 200)

        response = client.get('api/alarms/1', headers=headers)

        with self.subTest("Testing Status Code"):

            self.assertEqual(response.status_code, 200)

        alarm = response.get_json()

        with self.subTest("Testing Response"):

            self.assertIsNone(alarm['timestamp'])
            self.assertIsNone(alarm['acknowledged_timestamp'])
            self.assertEqual(alarm['state'], 'Normal')
            self.assertEqual(alarm['name'], 'PT-100-HH')
            self.assertEqual(alarm['tag'], 'PT-100')
            self.assertEqual(alarm['mnemonic'], 'NORM')
            self.assertEqual(alarm['enabled'], True)
            self.assertEqual(alarm['process'], 'Normal')
            self.assertEqual(alarm['triggered'], False)
            self.assertEqual(alarm['acknowledged'], True)
            self.assertEqual(alarm['value'], 102)
            self.assertEqual(alarm['type'], 'HIGH-HIGH')
            self.assertEqual(alarm['audible'], False)
            expected_operations = {
                'acknowledge': 'not active', 
                'enable': 'not active', 
                'disable': 'active', 
                'silence': 'not active', 
                'shelve': 'active', 
                'suppress by design': 'active', 
                'unsuppressed': 'not active', 
                'out of service': 'active', 
                'return to service': 'not active', 
                'reset': 'active'
            }
            self.assertEqual(alarm['operations'], expected_operations)

    def test_08_alarm_logging_collection(self):
        r"""
        Documentation here
        """
        response = client.get('api/alarms/logging/', headers=headers)
        with self.subTest("Testing Status Code"):

            self.assertEqual(response.status_code, 200)


    def test_09_alarm_logging_filter_by_alarm_name_resource(self):
        r"""
        Documentation here
        """
        payload = {
            'name': 'PT-100-HH'
        }
        response = client.post('api/alarms/logging/filter_by', headers=headers, json=payload)

        with self.subTest("Testing Status Code"):

            self.assertEqual(response.status_code, 200)

    def test_10_alarm_logging_filter_by_alarm_name_resource(self):
        r"""
        Documentation here
        """
        payload = {
            'name': 'PT-100-HH'
        }
        response = client.post('api/alarms/logging/filter_by', headers=headers, json=payload)

        with self.subTest("Testing Status Code"):

            self.assertEqual(response.status_code, 200)

    def test_11_alarm_logging_filter_by_alarm_state_resource(self):
        r"""
        Documentation here
        """
        payload = {
            'state': 'Unacknowledged'
        }
        response = client.post('api/alarms/logging/filter_by', headers=headers, json=payload)

        with self.subTest("Testing Status Code"):

            self.assertEqual(response.status_code, 200)

    def test_12_alarm_logging_filter_by_alarm_priority_resource(self):
        r"""
        Documentation here
        """
        payload = {
            'priority': 0
        }
        response = client.post('api/alarms/logging/filter_by', headers=headers, json=payload)

        with self.subTest("Testing Status Code"):

            self.assertEqual(response.status_code, 200)

    def test_13_alarm_logging_filter_by_alarm_timestamp_resource(self):
        r"""
        Documentation here
        """
        payload = {
            'greater_than_timestamp': '2022-09-20 10:18:03'
        }
        response = client.post('api/alarms/logging/filter_by', headers=headers, json=payload)

        with self.subTest("Testing Status Code"):

            self.assertEqual(response.status_code, 200)


if __name__=='__main__':

    unittest.main()