from app.extensions.api import api


def init_app():

    from .alarms import ns as ns_alarms
    from .summary import ns as ns_summary
    from .logging import ns as ns_logging

    api.add_namespace(ns_alarms, path="/alarms")
    api.add_namespace(ns_summary, path="/alarms/summary")
    api.add_namespace(ns_logging, path="/alarms/logging")