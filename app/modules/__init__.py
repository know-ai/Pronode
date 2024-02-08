# Init Resources
def init_app(app):

    from .tags.resources import init_app as init_tags
    from .healthcheck.resources import init_app as init_healthcheck
    from .daq.resources import init_app as init_daq
    from .opcua.resources import init_app as init_opcua
    from .alarms.resources import init_app as init_alarms
    from .opcua.manager import OPCUAClientManager

    init_tags()
    init_healthcheck()
    init_daq()
    init_opcua()
    init_alarms()

    app.opcua_client_manager = OPCUAClientManager()
    
    return app
