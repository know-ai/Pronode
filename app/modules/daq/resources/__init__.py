from app.extensions.api import api


def init_app():

    from .daq import ns as ns_daq
    from .protocols import ns as ns_protocols
    from .channels import ns as ns_channels
    from .addresses import ns as ns_addresses

    api.add_namespace(ns_daq, path="/DAQ")
    api.add_namespace(ns_protocols, path="/DAQ/protocols")
    api.add_namespace(ns_channels, path="/DAQ/channels")
    api.add_namespace(ns_addresses, path="/DAQ/addresses")


    
