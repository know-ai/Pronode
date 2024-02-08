from flask_restx import Namespace, Resource, fields
from flask import request
from datetime import datetime, timedelta
from PyIAC.dbmodels import AlarmSummary, AlarmsDB, AlarmStates, AlarmPriorities
import logging, requests
from app.extensions.api import api
from app.extensions import _api as Api
from app import APP_AUTH, EVENT_LOGGER_SERVICE_URL

api_security = None
if APP_AUTH:
    api_security = 'apikey'

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

ns = Namespace('Alarms Summary', description='Alarms Management System (AMS)')


alarms_summary_filter_model = api.model("alarms_summary_filter_model",{
    'name': fields.String(required=False, description='Alarm name'),
    'state': fields.String(required=False, description='Alarm state ["Normal", "Unacknowledged", "Acknowledged", "RTN Unacknowledged", "Shelved", "Suppressed By Design", "Out Of Service"]'),
    'priority': fields.Integer(required=False, description='Alarm priority [0-5]'),
    'greater_than_timestamp': fields.DateTime(required=False, default=datetime.now() - timedelta(minutes=2), description=f'Greater than timestamp - DateTime Format: {DATETIME_FORMAT}'),
    'less_than_timestamp': fields.DateTime(required=False, default=datetime.now(), description=f'Less than timestamp - DateTime Format: {DATETIME_FORMAT}')
})


add_user_log_model = api.model("add_user_log_model",{
    'comment': fields.String(required=True, description='User log comment')
})



@ns.route('/')
class AlarmsSummaryCollection(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def get(self):
        """
        Gets all alarm names defined
        """
        alarms = AlarmSummary.read_all()
        
        return alarms, 200


@ns.route('/<id>')
class AlarmsSummaryResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def get(self, id):
        """
        Gets alarm summary by id
        """
        alarm = AlarmSummary.read(id=id)

        if alarm['data']:
        
            return alarm['data'], 200

        return {'message': f"{id} not exist into Alarm Summary table"}, 400


@ns.route('/filter_by')
class AlarmsSummarygFilterByResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(alarms_summary_filter_model)
    def post(self):
        r"""
        Alarms Summary Filter By
        """
        payload = api.payload
        
        _query = ''

        # PRIORITY
        if 'priority' in payload.keys():
            priority = payload["priority"]

            _priority = AlarmPriorities.read_by_value(priority)

            if _priority:

                priority_id = [_priority.id]
                _query = f'AlarmSummary.priority_id.in_({priority_id})'

        # State
        if 'state' in payload.keys():
            
            state = payload["state"]
            _state = AlarmStates.read_by_name(state)

            if _state:

                state_id = [_state.id]

                if _query:
                
                    _query += ' & ' + f'AlarmSummary.state_id.in_({state_id})'

                else:

                    _query = f'AlarmSummary.state_id.in_({state_id})'

            else:
            
                return {'message': f'State {state} not exist'}, 400

        if 'name' in payload.keys():
            
            name = payload["name"]
            
            _alarm = AlarmsDB.read_by_name(name)
            
            if _alarm:
                
                alarm_id = [_alarm.id]

                if _query:

                    _query += ' & ' + f'AlarmSummary.alarm_id.in_({alarm_id})'

                else:
                    
                    _query = f'AlarmSummary.alarm_id.in_({alarm_id})'

            else:

                return {'message': f'Alarm {name} not exist'}, 400

        try:

            separator = '.'
            # GREATER THAN TIMESTAMP
            if 'greater_than_timestamp' in payload.keys():

                greater_than_timestamp = payload.pop('greater_than_timestamp')
                greater_than_timestamp = datetime.strptime(greater_than_timestamp.replace("T", " ").split(separator, 1)[0], DATETIME_FORMAT)

                if _query:

                    _query += ' & ' + f'(AlarmSummary.alarm_time >= greater_than_timestamp)'

                else:

                    _query = f'(AlarmSummary.alarm_time >= greater_than_timestamp)'

            # LESS THAN TIMESTAMP
            if 'less_than_timestamp' in payload.keys():

                less_than_timestamp = payload.pop('less_than_timestamp')
                less_than_timestamp = datetime.strptime(less_than_timestamp.replace("T", " ").split(separator, 1)[0], DATETIME_FORMAT)
                
                if _query:

                    _query += ' & ' + f'(AlarmSummary.alarm_time <= less_than_timestamp)'

                else:
                
                    _query = f'(AlarmSummary.alarm_time <= less_than_timestamp)'


            if _query:
               
                alarms = AlarmSummary.select().where(eval(_query)).order_by(AlarmSummary.id.desc())

            else: 

                return {'message': f"Please provide a valid key"}, 400

            result = [alarm.serialize() for alarm in alarms]

            return result, 200

        except Exception as ex:

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
            return {'message': msg}, 400


@ns.route('/<id>/comments')
class CommentsResource(Resource):

    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    def get(self, id):
        """
        Get User log comments 
        """
        summary = AlarmSummary.select().where(AlarmSummary.id == id).get_or_none()
        summary = summary.serialize()

        return summary['comments'], 200

    
    @api.doc(security=api_security)
    @Api.token_required(auth=APP_AUTH)
    @ns.expect(add_user_log_model)
    def post(self, id):
        """
        Add User log to event
        """
        query = AlarmSummary.read(id=id)
        
        if query:
            if APP_AUTH:
                token = request.headers['X-API-KEY']
                headers = {
                    "Content-Type": "application/json; charset=utf-8",
                    "X-API-KEY": token
                }
                api.payload.update({
                    'table_id': id,
                    'classification': 'Alarm',
                    'alarm_time': query['data']['alarm_time'],
                    'alarm_message': query['data']['name'],
                    'alarm_description': query['data']['description']
                })
                query = requests.post(f"{EVENT_LOGGER_SERVICE_URL}/api/logs/add", json=api.payload, headers=headers, verify=False)
                return query.json(), 200

            return {
                'message': f'Must activate Authorization service'
            }, 401

        return {
                'message': f"{id} ID Alarm Summary not exist",
                'data': []
            }, 400