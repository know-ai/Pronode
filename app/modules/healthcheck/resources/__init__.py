from app.extensions.api import api


def init_app():

    from .healthcheck import ns as ns_healthcheck

    api.add_namespace(ns_healthcheck, path="/healthcheck")