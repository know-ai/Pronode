import unittest
from PyIAC import PyIAC
from PyIAC.dbmodels import AlarmsDB
from PyIAC.tags import CVTEngine
from app.tests import client


class TestDAQApi(unittest.TestCase):
        

    def setUp(self) -> None:

        # Init DB
        self.dbfile = "app.db"
        self.core_app = PyIAC()
        self.core_app.set_mode('Development')
        self.core_app.drop_db(dbfile=self.dbfile)
        self.core_app.set_db(dbfile=self.dbfile)
        self.hades_db_worker = self.core_app.init_db()
        self.tag_engine = CVTEngine()
        
        return super().setUp()

    def tearDown(self) -> None:

        return super().tearDown()
    
    def test_daq_resource(self):
        r"""
        Dcoumentation here
        """
        pass

    def test_states_for_user_resource(self):
        r"""
        Documentation here
        """
        pass

    def test_daq_reset_resource(self):
        r"""
        Documentation here
        """
        pass

    def test_daq_confirm_reset_resource(self):
        r"""
        Documentation here
        """
        pass

    def test_daq_restart_resource(self):
        r"""
        Documentation here
        """
        pass

    def test_daq_confirm_restart_resource(self):
        r"""
        Documentation here
        """
        pass


if __name__=='__main__':

    unittest.main()