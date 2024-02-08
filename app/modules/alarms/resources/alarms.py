from flask_restx import Namespace, Resource, fields
from PyIAC.alarms import Alarm, TriggerType, AlarmState
from PyIAC.dbmodels import AlarmSummary
from PyIAC import PyIAC
from app.extensions.api import api
from app.extensions import _api as Api
from app import AUTH_SERVICE_URL, EVENT_LOGGER_SERVICE_URL, APP_AUTH, APP_EVENT_LOG
from flask import request
import os, requests

api_security = None
if APP_AUTH:
    api_security = 'apikey'



ns = Namespace('Alarms', description='Alarms Management System (AMS)')

alarm_resource_model = api.model("alarm_resource_model",{
    'alarm_id': fields.Integer(required=True, description='Alarm ID')
})

alarm_resource_by_name_model = api.model("alarm_resource_by_name_model",{
    'alarm_name': fields.String(required=True, description='Alarm Name')
})

shelve_alarm_resource_by_name_model = api.model("shelve_alarm_resource_by_name_model",{
    'alarm_name': fields.String(required=True, description='Alarm Name'),
    'seconds': fields.Integer(required=False, description='Shelve time'),
    'minutes': fields.Integer(required=False, description='Shelve time'),
    'hours': fields.Integer(required=False, description='Shelve time'),
    'days': fields.Integer(required=False, description='Shelve time'),
    'weeks': fields.Integer(required=False, description='Shelve time')
})

append_alarm_resource_model = api.model("append_alarm_resource_model",{
    'name': fields.String(required=True, description='Alarm Name'),
    'tag': fields.String(required=True, description='Tag to whom the alarm will be subscribed'),
    'description': fields.String(required=True, description='Alarm description'),
    'type': fields.String(required=True, description='Alarm Type - Allowed ["HIGH-HIGH", "HIGH", "BOOL", "LOW", "LOW-LOW"]'),
    'trigger_value': fields.Float(required=True, description="Alarm trigger value")
})

update_alarm_resource_model = api.model("update_alarm_resource_model",{
    'name': fields.String(required=False, description='Alarm Name'),
    'tag': fields.String(required=False, description='Tag to whom the alarm will be subscribed'),
    'description': fields.String(required=False, description='Alarm description'),
    'type': fields.String(required=False, description='Alarm Type - Allowed ["HIGH-HIGH", "HIGH", "BOOL", "LOW", "LOW-LOW"]'),
    'trigger_value': fields.Float(required=False, description="Alarm trigger value")
})

trigger_alarm_resource_model = api.model("trigger_alarm_resource_model",{
    'name': fields.String(required=False, description='Alarm Name'),
    'value': fields.Float(required=False, description="Alarm value")
})


app = PyIAC()
# Read Current Value Table Binding
alarm_manager = app.get_alarm_manager()
db_manager = app.get_db_manager()

@ns.route('/')
class AlarmsCollection(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def get(self):
        """
        Gets all alarm names defined
        """
        alarms = alarm_manager.get_alarms()

        result = {id: alarm.serialize() for id, alarm in alarms.items()}
        
        return result, 200 


@ns.route('/append')
class AppendAlarmResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(append_alarm_resource_model)
    def post(self):
        """
        Add new alarm definition to Alarm Manager of iDetectFugas
        """
        # Check tag existence
        tag_name = api.payload['tag']
        _tags = db_manager.get_tags()
        tags = [tag['name'] for tag in _tags]
        
        if not tag_name in tags:

            return {'message': f'{tag_name} is not defined in tags'}, 400
        
        # Check alarm name existence
        alarm_name = api.payload['name']
        alarms = alarm_manager.get_alarms()
        alarm_names = [alarm.name for id, alarm in alarms.items()]
        if alarm_name in alarm_names:

            return {'message': f'{alarm_name} is already defined'}, 200

        # Checking Alarm Type
        _type =  api.payload['type'].upper()
        if not _type in ["HIGH-HIGH", "HIGH", "BOOL", "LOW", "LOW-LOW"]:

            return {'message': f'{_type} alarm is not allowed - Try some these values ["HIGH-HIGH", "HIGH", "BOOL", "LOW", "LOW-LOW"]'}, 400

        # Appending alarm
        alarm_description = api.payload['description']
        _type = TriggerType(_type)
        trigger_value = api.payload['trigger_value']

        if _type.value=="BOOL":

            trigger_value = bool(trigger_value)

        alarm = Alarm(alarm_name, tag_name, alarm_description)
        alarm.set_trigger(value=trigger_value, _type=_type.value)

        alarm_manager.append_alarm(alarm)

        result = alarm.serialize()

        result.update({
            'message': f"{alarm_name} added successfully"
        })

        if APP_EVENT_LOG:
            Api.log_alarm_operation(
                message=alarm.name,
                description="New alarm added",
                classification="User",
                priority=1,
                criticity=1
            )
        
        return result, 200 


@ns.route('/states')
class AlarmStatesResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def get(self):
        """
        Gets all alarm states
        """
        
        return [state.state for state in AlarmState._states], 200


@ns.route('/<id>')
class AlarmResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def get(self, id):
        """
        Gets all alarm names defined
        """
        alarm = alarm_manager.get_alarm(id)

        if alarm:
        
            return alarm.serialize(), 200

        return {'message': f"Alarm ID {id} is not exist"}, 400

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(update_alarm_resource_model)
    def put(self, id):
        r"""
        Update Alarm definition in Database and Alarm Manager
        """
        alarm = alarm_manager.get_alarm(id)

        if alarm:

            result = alarm_manager.update_alarm(id, **api.payload)
            if APP_EVENT_LOG:
                Api.log_alarm_operation(
                    message=alarm.name,
                    description="Alarm definition updated",
                    classification="User",
                    priority=2,
                    criticity=3
                )

            return result, 200
        
        return {'message': f"Alarm ID {id} is not exist"}, 400

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def delete(self, id):
        """
        Delete alarm from database and Alarm Manager
        """
        alarm = alarm_manager.get_alarm(id)

        if alarm:
            
            alarm_manager.delete_alarm(id)
            if APP_EVENT_LOG:
                Api.log_alarm_operation(
                    message=alarm.name,
                    description="Alarm deleted",
                    classification="User",
                    priority=3,
                    criticity=5
                )

            return {"message": f"Alarm ID {id} deleted successfully"}, 200

        return {'message': f"Alarm ID {id} is not exist"}, 400


@ns.route('/name/<alarm_name>')
class AlarmByNameResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def get(self, alarm_name):
        """
        Gets all alarm names defined
        """
        alarm = alarm_manager.get_alarm_by_name(alarm_name)

        if alarm:

            return alarm.serialize(), 200 
        
        return {'message': f"Alarm Name {alarm_name} is not exist"}, 400

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(update_alarm_resource_model)
    def put(self, alarm_name):
        r"""
        Update Alarm definition in Database and Alarm Manager
        """
        alarm = alarm_manager.get_alarm_by_name(alarm_name)

        if alarm:

            result = alarm_manager.update_alarm(alarm._id, **api.payload)
            if APP_EVENT_LOG:
                Api.log_alarm_operation(
                    message=alarm.name,
                    description="Alarm definition updated",
                    classification="User",
                    priority=2,
                    criticity=3
                )

            return result, 200

        return {'message': f"Alarm Name {alarm_name} is not exist"}, 400

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def delete(self, alarm_name):
        """
        Delete alarm from database and Alarm Manager
        """
        alarm = alarm_manager.get_alarm_by_name(alarm_name)

        if alarm:

            alarm_manager.delete_alarm(alarm._id)
            if APP_EVENT_LOG:
                Api.log_alarm_operation(
                    message=alarm.name,
                    description="Alarm deleted",
                    classification="User",
                    priority=3,
                    criticity=5
                )

            return {"message": f"Alarm {alarm_name} deleted successfully"}, 200

        return {'message': f"Alarm Name {alarm_name} is not exist"}, 400


@ns.route('/acknowledge_all')
class AckAllAlarmsResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def post(self):
        """
        Acknowledge all alarms triggered
        """
        alarms = alarm_manager.get_alarms()

        for id, alarm in alarms.items():

            if not alarm._is_process_alarm:

                alarm.acknowledge()
        
        result = {
            'message': "Alarms were acknowledged successfully"
        }
        if APP_EVENT_LOG:
            Api.log_alarm_operation(
                message="API Request",
                description="All alarms were acknowledged",
                classification="User",
                priority=1,
                criticity=1
            )
        
        return result, 200

@ns.route('/silence_all')
class SilenceAllAlarmsResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def post(self):
        """
        Silence all alarms triggered
        """
        alarms = alarm_manager.get_alarms()
        result = {
            'message': "None"
        }

        for id, alarm in alarms.items():

            if not alarm._is_process_alarm:

                if alarm.audible:
                    
                    alarm.silence()
                    if APP_EVENT_LOG:
                        Api.log_alarm_operation(
                            message="API Request",
                            description="All alarms were silenced",
                            classification="User",
                            priority=1,
                            criticity=3
                        )
            
                    result = {
                        'message': "Alarms were silenced successfully"
                    }
        
        return result, 200


@ns.route('/acknowledge')
class AckAlarmResource(Resource):
    
    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(alarm_resource_model)
    def post(self):
        """
        Acknowledge alarm
        """
        result = dict()
        alarm_id = api.payload['alarm_id']
        alarm = alarm_manager.get_alarm(str(alarm_id))
        
        if alarm:
            
            if alarm.state in [AlarmState.UNACK, AlarmState.RTNUN]:
                alarm.acknowledge()
                result['message'] = f"{alarm.name} was acknowledged successfully"
                result['data'] = alarm.serialize()
                if APP_EVENT_LOG:
                    Api.log_alarm_operation(
                        message=alarm.name,
                        description="Alarm acknowledged",
                        classification="User",
                        priority=1,
                        criticity=1
                    )
                return result, 200

            return {'message': f"Alarm ID {alarm_id} is not in Unacknowledged state"}, 400

        return {'message': f"Alarm ID {alarm_id} is not exist"}, 400


@ns.route('/silence')
class SilenceAlarmResource(Resource):
    
    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(alarm_resource_model)
    def post(self):
        """
        Silence alarm
        """
        result = dict()
        alarm_id = api.payload['alarm_id']
        alarm = alarm_manager.get_alarm(alarm_id)

        if alarm:
            alarm.silence()
            result['message'] = f"{alarm.name} was silenced successfully"
            result['data'] = alarm.serialize()
            if APP_EVENT_LOG:
                Api.log_alarm_operation(
                    message=alarm.name,
                    description="Alarm silenced",
                    classification="User",
                    priority=1,
                    criticity=1
                )

            return result, 200

        return {'message': f"Alarm ID {alarm_id} is not exist"}, 400


@ns.route('/sound')
class SoundAlarmResource(Resource):
    
    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(alarm_resource_model)
    def post(self):
        """
        Sound alarm
        """
        result = dict()
        alarm_id = api.payload['alarm_id']
        alarm = alarm_manager.get_alarm(alarm_id)
        if alarm:

            alarm.sound()
            result['message'] = f"{alarm.name} was returned to audible successfully"
            result['data'] = alarm.serialize()
            if APP_EVENT_LOG:
                Api.log_alarm_operation(
                    message=alarm.name,
                    description="Alarm return to sound",
                    classification="User",
                    priority=1,
                    criticity=1
                )

            return result, 200 

        return {'message': f"Alarm ID {alarm_id} is not exist"}, 400


@ns.route('/triggered')
class AlarmsTriggeredCollection(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def get(self):
        """
        Gets all triggered alarm
        """
        alarms = alarm_manager.get_alarms()

        result = [alarm.serialize() for id, alarm in alarms.items() if alarm.state.is_triggered]

        result = sorted(result, key=lambda d: d['timestamp'], reverse=True) 
        
        return result, 200


@ns.route('/reset_all')
class ResetAllAlarmsResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def post(self):
        """
        Reset all alarms
        """
        alarms = alarm_manager.get_alarms()

        for id, alarm in alarms.items():

            if not alarm._is_process_alarm:

                alarm.reset()
        
        result = {
            'message': "Alarms were resetted successfully"
        }
        if APP_EVENT_LOG:
            Api.log_alarm_operation(
                message="API Request",
                description="All alarms were resetted",
                classification="User",
                priority=1,
                criticity=1
            )
        
        return result, 200 


@ns.route('/reset')
class ResetAlarmResource(Resource):
    
    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(alarm_resource_model)
    def post(self):
        """
        Reset alarm
        """
        result = dict()
        alarm_id = api.payload['alarm_id']
        alarm = alarm_manager.get_alarm(alarm_id)

        if alarm:

            alarm.reset()

            result['data'] = alarm.serialize()
            result['message'] = f"{alarm.name} was resetted successfully"
            if APP_EVENT_LOG:
                Api.log_alarm_operation(
                    message=alarm.name,
                    description="Alarm resetted",
                    classification="User",
                    priority=1,
                    criticity=1
                )
            
            return result, 200 

        return {'message': f"Alarm ID {alarm_id} is not exist"}, 400


@ns.route('/lasts/<lasts>')
class LastsAlarmsCollection(Resource):
    
    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def get(self, lasts):
        """
        Get lasts alarms triggered
        """
        alarms = AlarmSummary.read_lasts(lasts)
        
        return alarms, 200


@ns.route('/update')
class UpdateAlarmResource(Resource):
    
    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(trigger_alarm_resource_model)
    def post(self):
        """
        Force alarm trigger
        """
        result = dict()
        alarm_name = api.payload['name']
        alarm_value = api.payload['value']
        alarm = alarm_manager.get_alarm_by_name(alarm_name)
        if alarm:
            alarm.update(alarm_value)
            result['message'] = f"{alarm.name} was updated successfully"
            result['data'] = alarm.serialize()

            return result, 200

        return {'message': f"Alarm Name {alarm_name} is not exist"}, 400


@ns.route('/name/acknowledge')
class AckAlarmByNameResource(Resource):
    
    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(alarm_resource_by_name_model)
    def post(self):
        """
        Acknowledge alarm
        """
        result = dict()
        alarm_name = api.payload['alarm_name']
        alarm = alarm_manager.get_alarm_by_name(alarm_name)

        if alarm:

            if alarm.state in [AlarmState.UNACK, AlarmState.RTNUN]:

                alarm.acknowledge()
                result['message'] = f"{alarm.name} was acknowledged successfully"
                result['data'] = alarm.serialize()
                if APP_EVENT_LOG:
                    Api.log_alarm_operation(
                        message=alarm.name,
                        description="Alarm acknowledged",
                        classification="User",
                        priority=1,
                        criticity=1
                    )

                return result, 200

            return {'message': f"Alarm Name {alarm_name} is not in Unacknowledged state"}, 400

        return {'message': f"Alarm Name {alarm_name} is not exist"}, 400


@ns.route('/name/enable')
class EnableAlarmByNameResource(Resource):
    
    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(alarm_resource_by_name_model)
    def post(self):
        """
        Enable alarm
        """
        result = dict()
        alarm_name = api.payload['alarm_name']
        alarm = alarm_manager.get_alarm_by_name(alarm_name)

        if alarm:

            alarm.enable()
            result['message'] = f"{alarm.name} was enabled successfully"
            result['data'] = alarm.serialize()
            if APP_EVENT_LOG:
                Api.log_alarm_operation(
                    message=alarm.name,
                    description="Alarm enabled",
                    classification="User",
                    priority=1,
                    criticity=1
                )

            return result, 200

        return {'message': f"Alarm Name {alarm_name} is not exist"}, 400


@ns.route('/name/disable')
class DisableAlarmByNameResource(Resource):
    
    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(alarm_resource_by_name_model)
    def post(self):
        """
        Disable alarm
        """
        result = dict()
        alarm_name = api.payload['alarm_name']
        alarm = alarm_manager.get_alarm_by_name(alarm_name)

        if alarm:

            if alarm.state in [AlarmState.NORM]:
                alarm.disable()
                result['message'] = f"{alarm.name} was disabled successfully"
                result['data'] = alarm.serialize()
                if APP_EVENT_LOG:
                    Api.log_alarm_operation(
                        message=alarm.name,
                        description="Alarm disabled",
                        classification="User",
                        priority=1,
                        criticity=1
                    )

                return result, 200

            return {'message': f"You cannot disable an alarm if not in Normal state"}, 400

        return {'message': f"Alarm Name {alarm_name} is not exist"}, 400


@ns.route('/name/suppress_by_design')
class SuppressByDesignAlarmByNameResource(Resource):
    
    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(alarm_resource_by_name_model)
    def post(self):
        """
        Suppressed by design alarm
        """
        result = dict()
        alarm_name = api.payload['alarm_name']
        alarm = alarm_manager.get_alarm_by_name(alarm_name)

        if alarm:

            alarm.suppress_by_design()
            result['message'] = f"{alarm.name} was suppressed by design successfully"
            result['data'] = alarm.serialize()
            if APP_EVENT_LOG:
                Api.log_alarm_operation(
                    message=alarm.name,
                    description="Alarm suppressed by design",
                    classification="User",
                    priority=1,
                    criticity=1
                )

            return result, 200

        return {'message': f"Alarm Name {alarm_name} is not exist"}, 400


@ns.route('/name/unsuppress_by_design')
class UnsuppressByDesignAlarmByNameResource(Resource):
    
    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(alarm_resource_by_name_model)
    def post(self):
        """
        Unsuppress by design alarm
        """
        result = dict()
        alarm_name = api.payload['alarm_name']
        alarm = alarm_manager.get_alarm_by_name(alarm_name)

        if alarm:

            if alarm.state in [AlarmState.DSUPR]:
                alarm.unsuppress_by_design()
                result['message'] = f"{alarm.name} was suppressed by design successfully"
                result['data'] = alarm.serialize()
                if APP_EVENT_LOG:
                    Api.log_alarm_operation(
                        message=alarm.name,
                        description="Alarm suppressed by design",
                        classification="User",
                        priority=1,
                        criticity=1
                    )

                return result, 200

            return {'message': f"You cannot unsuppress by design an alarm if not in suppress state"}, 400

        return {'message': f"Alarm Name {alarm_name} is not exist"}, 400


@ns.route('/name/out_of_service')
class OutOfServiceAlarmByNameResource(Resource):
    
    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(alarm_resource_by_name_model)
    def post(self):
        """
        Out Of Service alarm
        """
        result = dict()
        alarm_name = api.payload['alarm_name']
        alarm = alarm_manager.get_alarm_by_name(alarm_name)

        if alarm:

            alarm.out_of_service()
            result['message'] = f"{alarm.name} was pusshed in out of service successfully"
            result['data'] = alarm.serialize()
            if APP_EVENT_LOG:
                Api.log_alarm_operation(
                    message=alarm.name,
                    description="Alarm out of service",
                    classification="User",
                    priority=1,
                    criticity=1
                )

            return result, 200

        return {'message': f"Alarm Name {alarm_name} is not exist"}, 400


@ns.route('/name/shelve')
class ShelveAlarmByNameResource(Resource):
    
    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(shelve_alarm_resource_by_name_model)
    def post(self):
        """
        Shelve alarm
        """
        result = dict()
        alarm_name = api.payload['alarm_name']
        alarm = alarm_manager.get_alarm_by_name(alarm_name)
        seconds = minutes = hours = days = weeks = 0

        if "seconds" in api.payload:

            seconds = api.payload['seconds']

        if "minutes" in api.payload:

            minutes = api.payload['minutes']

        if "hours" in api.payload:

            hours = api.payload['hours']

        if "days" in api.payload:

            days = api.payload['days']

        if "weeks" in api.payload:

            weeks = api.payload['weeks']

        if alarm:

            alarm.shelve(
                seconds=seconds,
                minutes=minutes,
                hours=hours,
                days=days,
                weeks=weeks
            )
            result['message'] = f"{alarm.name} was shelved successfully"
            result['data'] = alarm.serialize()

            if APP_EVENT_LOG:
                Api.log_alarm_operation(
                    message=alarm.name,
                    description="Alarm shelve",
                    classification="User",
                    priority=1,
                    criticity=1
                )

            return result, 200

        return {'message': f"Alarm Name {alarm_name} is not exist"}, 400


@ns.route('/name/return_to_service')
class ReturnToServiceAlarmByNameResource(Resource):
    
    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(alarm_resource_by_name_model)
    def post(self):
        """
        Return to service alarm
        """
        result = dict()
        alarm_name = api.payload['alarm_name']
        alarm = alarm_manager.get_alarm_by_name(alarm_name)

        if alarm:

            if alarm.state in [AlarmState.OOSRV]:
                alarm.return_to_service()
                result['message'] = f"{alarm.name} was returned to service successfully"
                result['data'] = alarm.serialize()
                if APP_EVENT_LOG:
                    Api.log_alarm_operation(
                        message=alarm.name,
                        description="Alarm returned to service",
                        classification="User",
                        priority=1,
                        criticity=1
                    )

                return result, 200

            return {'message': f"You cannot returned to service an alarm if not in out of service state"}, 400

        return {'message': f"Alarm Name {alarm_name} is not exist"}, 400


@ns.route('/name/silence')
class SilenceAlarmByNameResource(Resource):
    
    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(alarm_resource_by_name_model)
    def post(self):
        """
        Silence alarm
        """
        result = dict()
        alarm_name = api.payload['alarm_name']
        alarm = alarm_manager.get_alarm_by_name(alarm_name)
        if alarm:

            if alarm.audible:
                alarm.silence()
                result['message'] = f"{alarm.name} was silenced successfully"
                result['data'] = alarm.serialize()
                if APP_EVENT_LOG:
                    Api.log_alarm_operation(
                        message=alarm.name,
                        description="Alarm silenced",
                        classification="User",
                        priority=1,
                        criticity=1
                    )

                return result, 200

            return {'message': f"Alarm Name {alarm_name} is not sound"}, 400

        return {'message': f"Alarm Name {alarm_name} is not exist"}, 400


@ns.route('/name/sound')
class SoundAlarmByNameResource(Resource):
    
    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(alarm_resource_by_name_model)
    def post(self):
        """
        Sound alarm
        """
        result = dict()
        alarm_name = api.payload['alarm_name']
        alarm = alarm_manager.get_alarm_by_name(alarm_name)

        if alarm:

            if not alarm.audible:
                alarm.sound()
                result['message'] = f"{alarm.name} was returned to audible successfully"
                result['data'] = alarm.serialize()
                if APP_EVENT_LOG:
                    Api.log_alarm_operation(
                        message=alarm.name,
                        description="Alarm return to sound",
                        classification="User",
                        priority=1,
                        criticity=1
                    )

                return result, 200 

            return {'message': f"Alarm Name {alarm_name} is sound"}, 400

        return {'message': f"Alarm Name {alarm_name} is not exist"}, 400


@ns.route('/name/reset')
class ResetAlarmByNameResource(Resource):
    
    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(alarm_resource_by_name_model)
    def post(self):
        """
        Reset alarm
        """
        result = dict()
        alarm_name = api.payload['alarm_name']
        alarm = alarm_manager.get_alarm_by_name(alarm_name)

        if alarm:

            alarm.reset()

            result['data'] = alarm.serialize()
            result['message'] = f"{alarm.name} was resetted successfully"
            if APP_EVENT_LOG:
                Api.log_alarm_operation(
                    message=alarm.name,
                    description="Alarm resetted",
                    classification="User",
                    priority=1,
                    criticity=1
                )
            
            return result, 200 

        return {'message': f"Alarm Name {alarm_name} is not exist"}, 400