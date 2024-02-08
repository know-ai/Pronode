from flask_restx import Namespace, Resource, fields
from PyIAC import PyIAC
from ..models.channels import Channels
from app.extensions.api import api
from app.extensions import _api as Api
from app import APP_AUTH, APP_EVENT_LOG

api_security = None
if APP_AUTH:
    api_security = 'apikey'


ns = Namespace('DAQ', description='Data Acquisition Service By Query')

class DictItem(fields.Raw):
    def output(self, key, obj, *args, **kwargs):
        try:
            dct = getattr(obj, self.attribute)
        except AttributeError:
            return {}
        return dct or {}

channel_model = api.model("channel_model",{
    'protocol': fields.String(required=True, description='Industrial Protocol Name [opcua - modbus rtu - modbus tcp ...]'),
    'hostname': fields.String(required=True, description='Server hostname'),
    'port': fields.Integer(required=True, description='Server port'),
})

read_tags_model = api.model("read_tags_model",{
    'tags':  DictItem(attribute="'name': 'unit'")
})

core_app = PyIAC()

# Read Current Value Table Binding
daq_machine = core_app.get_machine('DAQ')


@ns.route('/')
class DAQCollection(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def get(self):
        """
        Get DAQ serialized
        """
        
        return daq_machine.serialize(), 200 


@ns.route('/states_for_users')
class DAQStatesForUSersCollection(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def get(self):
        """
        Get all states allowed to change by users
        """
        
        return daq_machine.get_allowed_transitions(), 200 


@ns.route('/reset')
class ResetResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def post(self):
        """
        Reset DAQ Service
        """
        daq_machine.transition(to='reset')
        result = daq_machine.serialize()
        result.update({
            'message': "Service waiting for reset confirmation"
        })
        if APP_EVENT_LOG:
            Api.log_alarm_operation(
                message="DAQ Query System changed state",
                description="Reset operation pressed",
                classification="User Request",
                priority=3,
                criticity=3
            )

        return result, 200


@ns.route('/confirm_reset')
class ConfirmResetResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def post(self):
        """
        Confirm reset DAQ Service
        """
        daq_machine.transition(to='start')
        result = daq_machine.serialize()
        result.update({
            'message': "Service resetted successfully"
        })
        if APP_EVENT_LOG:
            Api.log_alarm_operation(
                message="DAQ Query System changed state",
                description="Reset operation was confirmed",
                classification="User Request",
                priority=3,
                criticity=3
            )

        return result, 200


@ns.route('/restart')
class RestartResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def post(self):
        """
        Restart DAQ Service
        """
        daq_machine.transition(to='restart')
        result = daq_machine.serialize()
        result.update({
            'message': "Service waiting for restart confirmation"
        })
        if APP_EVENT_LOG:
            Api.log_alarm_operation(
                message="DAQ Query System changed state",
                description="Restart operation pressed",
                classification="User Request",
                priority=3,
                criticity=3
            )

        return result, 200


@ns.route('/sleep')
class SleepResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def post(self):
        """
        Sleep DAQ Service
        """
        daq_machine.transition(to='sleep')
        result = daq_machine.serialize()
        result.update({
            'message': "Service switched to sleep state successfully"
        })
        if APP_EVENT_LOG:
            Api.log_alarm_operation(
                message="DAQ Query System changed state",
                description="Sleep operation pressed",
                classification="User Request",
                priority=3,
                criticity=3
            )

        return result, 200


@ns.route('/test')
class TestResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def post(self):
        """
        Test DAQ Service
        """
        daq_machine.transition(to='test')
        result = daq_machine.serialize()
        result.update({
            'message': "Service switched to test state successfully"
        })
        if APP_EVENT_LOG:
            Api.log_alarm_operation(
                message="DAQ Query System changed state",
                description="Test operation pressed",
                classification="User Request",
                priority=3,
                criticity=3
            )

        return result, 200


@ns.route('/confirm_restart')
class ConfirmRestartResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def post(self):
        """
        Confirm restart DAQ Service
        """
        daq_machine.transition(to='wait')
        result = daq_machine.serialize()
        result.update({
            'message': "Service restarted successfully"
        })
        if APP_EVENT_LOG:
            Api.log_alarm_operation(
                message="DAQ Query System changed state",
                description="Restart operation was confirmed",
                priority=3,
                criticity=3
            )

        return result, 200


@ns.route('/create_channel')
class OPCUAChannelCollection(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(channel_model)
    def post(self)->tuple[dict, int]:
        """
        Create a new model instance

        You can create a new model instance. This method accepts keyword arguments, where the keys correspond 
        to the names of the model's fields. A new instance is returned and a row is added to the table.

        ## Python code with requests Library
        ```
        import requests
        url = 'http://hostname:port/api/DAS/channels'
        payload = {'name': 'opcua'}
        requests.post(url, json=payload).json()
        ```

        ## JavaScript code qith Axios Library
        ```
        axios({
            method: 'post',
            url: 'http://hostname:port/api/DAS/channels',
            data: {
                'name': 'opcua'
            }
        });
        ```
        
        This will INSERT a new row into the database. The primary key will automatically be retrieved and stored on the model instance.
        """
        channel = Channels.create(**api.payload)

        if channel['data']:

            daq_machine.set_channel(**channel['data'])

        return Channels.create(**api.payload), 200


@ns.route('/read_tags')
class ReadTagsResource(Resource):

    @api.doc()
    @ns.expect(read_tags_model)
    def post(self):
        """
        Read current tags
        """
        tags = api.payload['tags']
        result = daq_machine.read_tags(**tags)
        
        if result:

            return result, 200

        return result, 204
