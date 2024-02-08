from PyIAC import PyIAC
from PyIAC.dbmodels import AlarmsDB, Tags
from PyIAC.tags import CVTEngine
from app import CreateApp
from app.utils.utils import get_headers

application = CreateApp()
app = application()
app.config['TESTING'] = True
client = app.test_client()

# Hades instantiation
dbfile = "app.db"
PyIAC.drop_db(dbfile=dbfile)
core_app = PyIAC()
core_app.set_mode('Development')
core_app.set_db(dbfile=dbfile)
hades_db_worker = core_app.init_db()
tag_engine = CVTEngine()
alarm_manager = core_app.get_alarm_manager()
headers = get_headers()
