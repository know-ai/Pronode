from PyIAC import PyIAC
from  app.utils import Singleton

core_app = PyIAC()

class DB(Singleton):

    def __init__(self):
        
        self.app = None

    def init_app(self, app):
        r"""
        Documentation here
        """
        if core_app.config_file_location:
            
            core_app.set_db_from_config_file(core_app.config_file_location)

        return app