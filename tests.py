from unittest import TestLoader, TestSuite, TextTestRunner
from app.tests.test_tags_api import TestTagsApi
from app.tests.test_alarms_api import TestAlarmsApi
from app.tests.test_daq_protocols import TestDAQProtocolsApi
from app.tests.test_daq_channels import TestDAQChannelsApi
# from app.tests.test_daq_api import TestDAQApi
# from app.tests.test_daq_addresses import TestDAQAddressesApi
# from app.tests.test_opcua_api import TestOPCUAApi

def suite():
    r"""
    Documentation here
    """
    tests = list()
    suite = TestSuite()
    tests.append(TestLoader().loadTestsFromTestCase(TestTagsApi))
    tests.append(TestLoader().loadTestsFromTestCase(TestAlarmsApi))
    # tests.append(TestLoader().loadTestsFromTestCase(TestDAQProtocolsApi))
    # tests.append(TestLoader().loadTestsFromTestCase(TestDAQChannelsApi))
    # tests.append(TestLoader().loadTestsFromTestCase(TestDAQApi))
    # tests.append(TestLoader().loadTestsFromTestCase(TestDAQAddressesApi))
    # tests.append(TestLoader().loadTestsFromTestCase(TestOPCUAApi))
    suite = TestSuite(tests)
    return suite

if __name__=='__main__':
    
    runner = TextTestRunner()
    runner.run(suite())