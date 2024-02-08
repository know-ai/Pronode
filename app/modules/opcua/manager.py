class OPCUAClientManager:
    r"""
    Documentation here
    """

    def __init__(self):
        r"""
        Documentation here
        """
        self._clients = list()

    def append_client(self, client):
        r"""
        Documentation here
        """
        self._clients.append(client)

    def remove_client(self, client_id):
        r"""
        Documentation here
        """
        index = 0
        for _client in self._clients:

            if client_id == _client.get_id():

                del self._clients[index]

                return {'message': 'successfully'}, 200

            index += 1


    def get_client_by_id(self, client_id):
        r"""
        Documentation here
        """
        for _client in self._clients:

            if client_id == _client.get_id():

                return _client

    def get_clients(self):
        r"""
        Documentation here
        """
        return [_client.serialize() for _client in self._clients]