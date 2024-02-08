from PyIAC import PyIAC

app = PyIAC()
app._alarm_manager.load_alarms_from_db()

if app.load_default_db:

    if app.config_file_location:

        app.define_alarm_from_config_file(app.config_file_location)