from app import CreateApp
from PyIAC import PyIAC
from app.utils.utils import load_protocols_from_config, init_logging

init_logging()
core_app = PyIAC()
application = CreateApp()

# Serve App
app = application()

# Import variables defined when CreateApp
from app.extensions import sio
from app import port, CERTFILE, KEYFILE

core_app.set_socketio(sio=sio.app)

# Run hades safe way
core_app.safe_start(create_tables=True, alarm_worker=True)
load_protocols_from_config()

if __name__=="__main__":
    
    if CERTFILE and KEYFILE:
        
        sio.app.run(app, host="0.0.0.0", port=port, ssl_context=(CERTFILE, KEYFILE))

    else:
        
        sio.app.run(app, host="0.0.0.0", port=port)