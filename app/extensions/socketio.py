from flask_socketio import SocketIO as sio
from  app.utils import Singleton


class SocketIO(Singleton):

    def __init__(self):

        self.app = None

    def init_app(self, app):
        r"""
        Documentation here
        """
        self.app = sio(app, cors_allowed_origins='*')
        
        return app
