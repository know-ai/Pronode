import os
from flask import Flask
from PyIAC import PyIAC
from dotenv import load_dotenv
import requests
import urllib3

urllib3.disable_warnings()

CERT_FILE = os.environ.get('CERT_FILE') or "idetect.crt"
KEY_FILE = os.environ.get('KEY_FILE') or "idetect.key"

CERTFILE = os.path.join("app", "ssl", CERT_FILE)
KEYFILE = os.path.join("app", "ssl", KEY_FILE)
if not os.path.exists(CERTFILE):

    CERTFILE = None

if not os.path.exists(KEYFILE):

    KEYFILE = None


EVENT_LOGGER_SERVICE_HOST = os.environ.get('EVENT_LOGGER_SERVICE_HOST') or "127.0.0.1"
EVENT_LOGGER_SERVICE_PORT = os.environ.get('EVENT_LOGGER_SERVICE_PORT') or "5004"
EVENT_LOGGER_SERVICE_URL = f"https://{EVENT_LOGGER_SERVICE_HOST}:{EVENT_LOGGER_SERVICE_PORT}"
try:
    response = requests.get(f'{EVENT_LOGGER_SERVICE_URL}/api/healthcheck/', timeout=(3, 5), verify=False)

except:

    EVENT_LOGGER_SERVICE_URL = f"http://{EVENT_LOGGER_SERVICE_HOST}:{EVENT_LOGGER_SERVICE_PORT}"

AUTH_SERVICE_HOST = os.environ.get('AUTH_SERVICE_HOST') or "127.0.0.1"
AUTH_SERVICE_PORT = os.environ.get('AUTH_SERVICE_PORT') or "5000"
AUTH_SERVICE_URL = f"https://{AUTH_SERVICE_HOST}:{AUTH_SERVICE_PORT}"
try:
    response = requests.get(f'{AUTH_SERVICE_URL}/api/healthcheck/', timeout=(3, 5), verify=False)

except:

    AUTH_SERVICE_URL = f"http://{AUTH_SERVICE_HOST}:{AUTH_SERVICE_PORT}"


IDETECT_OPCUA_SERVICE_HOST = os.environ.get('IDETECT_OPCUA_SERVICE_HOST') or "127.0.0.1"
IDETECT_OPCUA_SERVICE_PORT = os.environ.get('IDETECT_OPCUA_SERVICE_PORT') or "53531"
IDETECT_OPCUA_SERVICE_URL = f"https://{IDETECT_OPCUA_SERVICE_HOST}:{IDETECT_OPCUA_SERVICE_PORT}"
try:
    response = requests.get(f'{IDETECT_OPCUA_SERVICE_URL}/api/healthcheck/', timeout=(3, 5), verify=False)

except:

    IDETECT_OPCUA_SERVICE_URL = f"http://{IDETECT_OPCUA_SERVICE_HOST}:{IDETECT_OPCUA_SERVICE_PORT}"


OPCUA_SERVER_HOST = os.environ.get('OPCUA_SERVER_HOST') or "127.0.0.1"
OPCUA_SERVER_PORT = os.environ.get('OPCUA_SERVER_PORT') or "4840"

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

app = Flask(__name__, instance_relative_config=False)

def load_env_var():
    r"""
    Documentation here
    """
    load_dotenv()
    mode = os.environ.get('APP_MODE') or 'Development'
    port = int(os.environ.get('APP_PORT') or '5001')
    config_file_location = os.environ.get('APP_CONFIG_FILE') or 'app/config.yml'

    default_db = True
    if os.environ.get('APP_LOAD_DEFAULT_DB'):

        default_db = bool(int(os.environ.get('APP_LOAD_DEFAULT_DB')))

    core_app = PyIAC()
    setattr(core_app, 'config_file_location', config_file_location)
    setattr(core_app, 'load_default_db', default_db)
    setattr(core_app, 'port',port)

    core_app.set_mode(mode)

    return core_app, mode, port

core_app, mode, port = load_env_var()

APP_AUTH = bool(int(os.environ.get('APP_AUTH') or "0"))
APP_EVENT_LOG = bool(int(os.environ.get('APP_EVENT_LOG') or "0"))
APP_THREADS = int(os.environ.get('APP_THREADS') or "2")


class CreateApp():
    """Initialize the core application."""


    def __call__(self):
        """
        Documentation here
        """
        app.client = None
        self.application = app
        
        with app.app_context():

            from . import extensions
            _app = extensions.init_app(app)

            from . import modules
            _app = modules.init_app(app)
            
            return _app