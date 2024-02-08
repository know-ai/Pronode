from app.extensions.api import api


def init_app():

    from .client import ns as ns_opcua_client

    api.add_namespace(ns_opcua_client, path="/opcua_client")