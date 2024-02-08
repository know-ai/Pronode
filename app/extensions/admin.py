from flask_admin import Admin as admin
from  app.utils import Singleton


class Admin(Singleton):

    def __init__(self):
        
        self.app = None

    def init_app(self, app):
        r"""
        Documentation here
        """
        # set optional bootswatch theme
        app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
        self.app = admin(app, name='microblog', template_mode='bootstrap3')
        # Add administrative views here

        return app