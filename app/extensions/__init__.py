from .db import DB
from .api import Api
from .cors import Cors
from .socketio import SocketIO

_db = DB()
_api = Api()
_cors = Cors()
sio = SocketIO()

def init_app(app):
    """
    Application extensions initialization.
    """
    extensions = (_db, _api, _cors, sio )

    for extension in extensions:
        
        extension.init_app(app)