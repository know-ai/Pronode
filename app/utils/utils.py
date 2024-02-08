import ipaddress, json, os
import requests
import urllib3
import logging
from PyIAC.utils import parse_config
from app import AUTH_SERVICE_URL as url
from app import core_app
from logging.handlers import TimedRotatingFileHandler
from .decorators import decorator

opcua_server_machine = core_app.get_machine("OPCUAServer")

def init_logging():
    r"""
    Documentation here
    """
    requests.urllib3.disable_warnings()
    urllib3.disable_warnings()

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger('peewee').setLevel(logging.WARNING)
    logging.getLogger('opcua').setLevel(logging.WARNING)
    handler = TimedRotatingFileHandler('logs/app.log', when='midnight', backupCount=365)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)

def validate_ip_address(address):
    try:
        
        ip = ipaddress.ip_address(address)
        
        return ip._ip
    
    except ValueError:
        
        return None

def load_socketio_clients_info_from_config_file():

    if hasattr(core_app, 'config_file_location'):

        config = parse_config(core_app.config_file_location)

        if 'modules' in config and config['modules'] is not None:

            if 'socketIO_Clients' in config['modules'] and config['modules']['socketIO_Clients'] is not None:

                clients = config['modules']['socketIO_Clients']

                return clients

def load_protocols_from_config():
    r"""
    Documentation here
    """
    from app.modules.daq.models.protocols import Protocols
    
    filename = os.path.join("app/config/protocols.json")
    protocols = []
    
    with open(filename, 'r') as f:

        protocols = json.load(f)

    for protocol in protocols:

        Protocols.create(name=protocol)

def get_headers():
    r"""
    Documentation here
    """
    key = None
    try:
        response = requests.get(f'{url}/api/healthcheck/key', verify=False)   
        if response:
            
            response = response.json()
            key = response['message']
        
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "X-API-KEY": key
        }

        return headers
    
    except requests.ConnectionError as ex:

        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        msg = str({
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        })
        logging.warning(msg=msg)

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "X-API-KEY": key
        }

        return headers

@decorator
def create_opcua_folder_struct(func, args, kwargs):
    """

    :param args:
    :return:
    """
    result = func(*args, **kwargs)
    state_machine = args[0]
    current_transition = func.__name__.replace('on_','')
    current_destination = current_transition.split('_to_')[-1]
    active_transitions = state_machine._get_active_transitions()

    for transition in active_transitions:

        if transition.identifier==current_transition:
            
            for destination in transition.destinations:
                
                if destination.name==current_destination:

                    engine_state = destination.value


                    machine = state_machine.serialize()
                    machine['state']['value'] = engine_state

                    if "pipeline" in machine.keys():

                        payload = {
                            'folder_struct': [machine['pipeline']['value'], "Engines", machine['name']['value']],
                            'engine': machine
                        }

                    else:

                        payload = {
                            'folder_struct': ["Engines", machine['name']['value']],
                            'engine': machine
                        }

                    # Notify to OPCUA Server
                    opcua_server_machine.set_engine_into_server(folder_struct=payload['folder_struct'], **machine)

    return result

class Container:

    def __init__(self):
        r"""
        Documentation here
        """
        self.__detach = False
        self.__name = None
        self.__host = '127.0.0.1'
        self.__external_port = 5050
        self.__interlnal_port = None
        self.__image = None

    @property
    def detach(self):
        r"""
        Documentation here
        """
        return self.__detach

    @detach.setter
    def detach(self, value:bool):
        r""""
        Documentation here
        """
        if isinstance(value, bool):

            self.__detach = value

        else:

            raise ValueError(f'{value} value must be a boolean field')

    @property
    def name(self):
        r"""
        Documentation here
        """
        return self.__name

    @name.setter
    def name(self, value:str):
        r""""
        Documentation here
        """
        if isinstance(value, str):

            self.__name = value

        else:

            raise ValueError(f'{value} value must be a string field')


    @property
    def host(self):
        r"""
        Documentation here
        """
        return self.__host

    @host.setter
    def host(self, value:str):
        r""""
        Documentation here
        """
        if isinstance(value, str):

            self.__host = value

        else:

            raise ValueError(f'{value} value must be a string field')
    
    @property
    def ext_port(self):
        r"""
        Documentation here
        """
        return self.__external_port

    @ext_port.setter
    def ext_port(self, value:str):
        r""""
        Documentation here
        """
        if isinstance(value, str):

            self.__external_port = value

        else:

            raise ValueError(f'{value} value must be a string field')



    def run(self):
        r"""
        Docunaion here
        """
        pass