from flask_restx import Namespace, Resource
from app.extensions.api import api


ns = Namespace('Healthcheck', description='Healthcheck')

@ns.route('/')
class Health(Resource):
    
    @api.doc()
    def get(self):
        
        return { 'success': True, 'message': "healthy" }
