import unittest
from app.tests import client, AlarmsDB, tag_engine, alarm_manager


class TestDAQChannelsApi(unittest.TestCase):
        

    def setUp(self) -> None:
        
        return super().setUp()

    def tearDown(self) -> None:

        return super().tearDown()
    
    def test_01_daq_channels_add_resource(self):
        r"""
        Dcoumentation here
        """
        payload = {
            'protocol': 'opcua',
            'hostname': '127.0.0.1',
            'port': '4840'
        }

        response = client.post('api/daq/channels/', json=payload)

        with self.subTest("Testing Status Code"):

            self.assertEqual(response.status_code, 200)

    def test_02_daq_channel_resource(self):
        r"""
        Documentation here
        """
        pass



if __name__=='__main__':

    unittest.main()