from PyIAC import PyIAC
from PyIAC.tags import CVTEngine

app = PyIAC()
engine = CVTEngine()

if app.load_default_db:

    if app.config_file_location:

        engine.set_config(app.config_file_location)

    engine.load_tag_from_db_to_cvt()