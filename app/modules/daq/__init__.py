from PyIAC.utils import parse_config
from PyIAC import PyIAC, AutomationStateMachine
from PyIAC.tags import CVTEngine
from PyIAC.logger import QueryLogger
from PyIAC.models import IntegerType, StringType
from PyIAC.dbmodels import Units
from PyIAC.utils import notify_state, logging_error_handler
from .models.channels import Channels
from PyIAC.dbmodels import Units
import socketio, requests
from app import (
    IDETECT_OPCUA_SERVICE_URL,
    app,
    port,
    CERTFILE,
    KEYFILE,
    APP_AUTH
)
from app.utils.utils import get_headers
from app.modules.opcua.models import Client
from PyIAC.models import IntegerType, StringType
import os

core_app = PyIAC()
query = QueryLogger()
db_manager = core_app.get_db_manager()
alarm_manager = core_app.get_alarm_manager()
tag_engine = CVTEngine()
# opcua_server_machine = core_app.get_machine("OPCUAServer")

def get_state_machine_interval():

    if hasattr(core_app, 'config_file_location'):

        config = parse_config(core_app.config_file_location)

        if 'modules' in config and config['modules'] is not None:

            if 'daq' in config['modules'] and config['modules']['daq'] is not None:

                if 'interval' in config['modules']['daq'] and config['modules']['daq']['interval'] is not None:

                    try:

                        interval = float(config['modules']['daq']['interval'])

                    except:

                        interval = 1.0
    return interval

def get_opcua_channel_config():

    r"""
    Documentation here
    """
    host = os.environ.get('OPCUA_SERVER_HOST') or "127.0.0.1"
    port = os.environ.get('OPCUA_SERVER_PORT') or 4840

    return {
        "protocol": "opcua",
        "hostname": host,
        "port": port
    }

def get_conversions_config():

    r"""
    Documentation here
    """
    if hasattr(core_app, 'config_file_location'):

        config = parse_config(core_app.config_file_location)

        if 'modules' in config and config['modules'] is not None:

            if 'tags' in config['modules'] and config['modules']['tags'] is not None:

                if 'conversions' in config['modules']['tags'] and config['modules']['tags']['conversions'] is not None:

                    return config['modules']['tags']['conversions']

                else:

                    return {}


@core_app.define_automation_machine(
    name='DAQ', 
    period=get_state_machine_interval()
    )
class DAQ(AutomationStateMachine):
    r"""
    Documentation here
    """
    priority = IntegerType(default=1)
    criticity = IntegerType(default=1)
    classification = StringType(default='Communication')
    description = StringType(default='Data Acquisition System By Query')
    channel_url = None
    client = None

    @logging_error_handler
    def while_starting(self):
        r"""
        Documentation here
        """
        self._sio = None
        self.sio = core_app.get_socketio()
        self.headers = None

        if APP_AUTH:
            self.headers = get_headers()
            os.environ["sys_token"] = self.headers["X-API-KEY"]
        payload_for_daq_create_channel = get_opcua_channel_config()
        self.conversions = get_conversions_config()

        if payload_for_daq_create_channel:

            channel = Channels.create(**payload_for_daq_create_channel)

            if channel['data']:

                self.set_channel(**channel['data'])

        if self.channel_url:

            if self.client is None:

                self.client = Client(self.channel_url)

                if not self.client.is_connected():

                    self.client.connect()

            else:

                if self.client.is_connected():

                    app.opcua_client_manager.append_client(self.client)
                    self.opcua_client_id = self.client.get_id()
                    self.define_socket_io_watch_events()
                    self.create_opcua_structure()
                    
                    super(DAQ, self).while_starting()

    @logging_error_handler
    def while_waiting(self):
        r"""
        Documentation here
        """
        
        self.refresh_namespaces()
        
        if len(self.opcua_namespaces)>0:

            self.wait_to_run()

    @logging_error_handler
    def while_running(self):
        r"""
        Documentation here
        """
        data, _ = self.read_current_data()
        self.write_data(data)
        self.emit_daq(data)
        self.emit_das()

    @logging_error_handler
    def while_testing(self):
        r"""
        Documentation here
        """
        # self.write_data(data)
        self.emit_daq(self.data)
        # self.emit_das()

    @logging_error_handler
    def while_sleeping(self):
        r"""
        Documentation here
        """
        # self.write_data(data)
        self.emit_daq(self.data)
        self.criticity.value = 4
        # self.emit_das()

    @logging_error_handler
    def while_con_reset(self):
        r"""
        ## **confirm_reset** state

        Only set priority and classification to notify in the front end
        """
        self.criticity.value = 3
        self.confirm_reset_to_start()

    @logging_error_handler
    def while_con_restart(self):
        r"""
        ## **confirm_restart** state

        Only set priority and classification to notify in the front end
        """
        self.criticity.value = 3
        self.confirm_restart_to_wait()

    # Transitions Methods
    @notify_state
    def on_confirm_restart_to_wait(self):
        """
        ## **Transition**

        * **from: *confirm_restart* ** state
        * **to: *waiting* ** state

        ### **Settings**

        * **priority:** 1 (low priority) machine to waiting state, warning
        * **classification:** user (Transition triggered by the operator)

        This method is decorated by @notify_transition to register this event in the database.
        """
        self.last_state = "wait"
        self.criticity.value = 1

    @notify_state
    def on_confirm_reset_to_start(self):
        """
        ## **Transition**

        * **from: *confirm_restart* ** state
        * **to: *waiting* ** state

        ### **Settings**

        * **priority:** 1 (low priority) machine to waiting state, warning
        * **classification:** user (Transition triggered by the operator)

        This method is decorated by @notify_transition to register this event in the database.
        """
        self.last_state = "start"
        self.criticity.value = 1

    # Auxiliary Methods
    @logging_error_handler
    def write_data(self, data):
        r"""
        Documentation here
        """
        tags = list()

        for _data in data:

            tag_id = tag_engine.get_tag_id_by_node_namespace(_data['Namespace'])
            
            if tag_id is not None:
                
                value = _data['Value']
                tags.append({
                    'tag': tag_id,
                    'value': value
                })                

        tag_engine.write_tags(tags)        

    @logging_error_handler
    def emit_daq(self, data):

        """Documentation here
        """
        tags_sio = dict()
        for _data in data:

            tag_id = tag_engine.get_tag_id_by_node_namespace(_data['Namespace'])
            
            tag_name = tag_engine.get_tagname_by_node_namespace(_data['Namespace'])
            
            if tag_id is not None:
                
                value = _data['Value']

                display_name = tag_engine.read_display_name(tag_name)

                # Unit Conversion
                value, to_unit = self.unit_conversion(value=value, tag_name=tag_name)
                variable = Units.read_by_unit(unit=to_unit)['variable']

                tags_sio[tag_name] = {
                    'y': value,
                    'unit': to_unit,
                    'variable': variable,
                    'display_name': display_name
                }

        self.sio.emit('DAQ', tags_sio)

    @logging_error_handler
    def emit_das(self):
        """Documentation here
        """
        tags = dict()
        for tag in tag_engine.get_tags():

            tag_name = tag["name"]
            tag_value = tag_engine.read_tag(name=tag_name)
            tag_display_name = tag["display_name"]
            tag_unit = tag["unit"]

            tags[tag_name] = {
                'y': tag_value,
                'unit': tag_unit,
                'display_name': tag_display_name
            }
        self.sio.emit('DAQ-DAS', tags)

    def unit_conversion(self, value:float, tag_name:str)->float:
        r"""
        Documentation here
        """
        _unit = tag_engine.read_unit(tag_name)
        to_unit = _unit
        if _unit is not None and _unit!='Adim':

            variable = tag_engine.read_variable(tag_name)

            if variable in self.conversions:
                
                to_unit = self.conversions[variable]
                
                if to_unit!=_unit:
                    
                    value = tag_engine.read_tag(tag_name, unit=to_unit)

        return value, to_unit

    @logging_error_handler
    def get_opcua_namespaces(self):
        r"""
        Documentation here
        """
        tags = tag_engine.serialize()
        namespaces = [tag['node_namespace'] for tag in tags if tag['node_namespace']]
        return namespaces

    @logging_error_handler
    def get_node_values(self, nodes:list):
        r"""
        Documentation here
        """
        attrs, status_code = self.client.get_values(nodes)
        return attrs, status_code

    @logging_error_handler
    def read_current_data(self):
        r"""
        Documentation here
        """
        self.data, status_code = self.get_node_values(self.nodes_id)
        return self.data, status_code

    @logging_error_handler
    def set_channel(self, **info):
        r"""
        Documentation here
        """
        self.channel_url = info['addresses'][0]

    @logging_error_handler
    def connect_to_opcua_server(self, url:str):
        r"""
        Documentation here
        """
        self.client = Client(url)

    @logging_error_handler
    def refresh_namespaces(self):
        r"""
        Documentation here
        """
        self.opcua_namespaces = self.get_opcua_namespaces()
        nodes = self.client.get_nodes_id_by_namespaces(self.opcua_namespaces)
        self.nodes_id = [node.nodeid for node in nodes]

    @logging_error_handler
    def define_socket_io_watch_events(self):
        r"""
        Documentation here
        """
        if self._sio is None:
            http_session = requests.Session()
            http_session.verify = False

            if CERTFILE and KEYFILE:
                
                http_session.cert = (CERTFILE, KEYFILE)
                self._sio = socketio.Client(http_session=http_session)
                self._sio.connect(f'https://127.0.0.1:{port}')
        
            else:
                
                self._sio = socketio.Client()
                self._sio.connect(f'http://127.0.0.1:{port}')

            @self._sio.on('notify_state')
            def notify_state(data):
                r"""
                Documentation here
                """
                folder_struct = ["Engines", data['name']['value']]
                payload = {
                    'folder_struct': folder_struct,
                    'engine': data
                }
                if APP_AUTH:
                    
                    requests.put(f'{IDETECT_OPCUA_SERVICE_URL}/api/opcua_server/engine', json=payload, headers=self.headers, timeout=(3, 5), verify=False)
                
                else:
                    
                    requests.put(f'{IDETECT_OPCUA_SERVICE_URL}/api/opcua_server/engine', json=payload, timeout=(3, 5), verify=False)

            
            @self._sio.on('notify_alarm')
            def notify_alarm(data):
            
                payload = {
                    'alarm': data
                }
                if APP_AUTH:
                    
                    requests.put(f'{IDETECT_OPCUA_SERVICE_URL}/api/opcua_server/alarm', json=payload, headers=self.headers, timeout=(3, 5), verify=False)
                
                else:
                    
                    requests.put(f'{IDETECT_OPCUA_SERVICE_URL}/api/opcua_server/alarm', json=payload, timeout=(3, 5), verify=False)

            @self._sio.on('notify_machine_attr')
            def notify_machine_attr(data):
                r"""
                Documentation here
                """
                folder_struct = ['Engines', data['name']['value']]

                payload = {
                    "folder_struct": folder_struct,
                    "engine": data
                }
                
                if APP_AUTH:

                    requests.put(f"{IDETECT_OPCUA_SERVICE_URL}/api/opcua_server/engine", json=payload, headers=self.headers, verify=False)
                else:

                    requests.put(f"{IDETECT_OPCUA_SERVICE_URL}/api/opcua_server/engine", json=payload, verify=False)  

    @logging_error_handler
    def create_opcua_structure(self):
        r"""
        Documentation here
        """
        payload = {
            'tags': tag_engine.get_tags()
        }
        alarms = dict()

        for key, alarm in alarm_manager.get_alarms().items():

            alarms[key] = alarm.serialize()
        
        alarms_payload = {
            'alarms': alarms
        }

        engine_payload = {
            'folder_struct': ['Engines'],
            'engine': self.serialize()
        }

        if APP_AUTH:
            requests.post(f'{IDETECT_OPCUA_SERVICE_URL}/api/opcua_server/tags', json=payload, headers=self.headers, timeout=(3, 5), verify=False)
            requests.post(f'{IDETECT_OPCUA_SERVICE_URL}/api/opcua_server/alarms', json=alarms_payload, headers=self.headers, timeout=(3, 5), verify=False)
            requests.post(f'{IDETECT_OPCUA_SERVICE_URL}/api/opcua_server/engine', json=engine_payload, headers=self.headers, timeout=(3, 5), verify=False)
            requests.post(f'{IDETECT_OPCUA_SERVICE_URL}/api/opcua_server/start', json=payload, headers=self.headers, timeout=(3, 5), verify=False)
        else:
            
            requests.post(f'{IDETECT_OPCUA_SERVICE_URL}/api/opcua_server/tags', json=payload, timeout=(3, 5), verify=False)
            requests.post(f'{IDETECT_OPCUA_SERVICE_URL}/api/opcua_server/alarms', json=alarms_payload, timeout=(3, 5), verify=False)
            requests.post(f'{IDETECT_OPCUA_SERVICE_URL}/api/opcua_server/engine', json=engine_payload, timeout=(3, 5), verify=False)
            requests.post(f'{IDETECT_OPCUA_SERVICE_URL}/api/opcua_server/start', json=payload, timeout=(3, 5), verify=False)
    
    @logging_error_handler
    def read_tags(self, **tags):
        r"""
        Documentation here
        """
        data = dict()
        for name, unit in tags.items():
            value = tag_engine.read_tag(name=name, unit=unit)
            if value:
                data[name] = {
                    'y': value
                }

        return data
    