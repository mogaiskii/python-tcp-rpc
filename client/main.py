from core.connection import TcpJRpcConnectionHelper
from core.utils import generate_id, TEST_ROUTE


class TcpRpcClient(object):
    def __init__(self, host='127.0.0.1', port=5445):
        self._host = host
        self._port = port

    def _get_connection(self):
        return TcpJRpcConnectionHelper.connect(self._host, self._port)

    @classmethod
    def generate_id(cls):
        return generate_id()

    def make_request(self, id, method, **params):
        connection = self._get_connection()
        connection.send_request(id, method, params)
        response_data = connection.recv_response()
        connection.close()
        return response_data

    def perform(self, contract_request):
        id = self.generate_id()
        method = contract_request.__method__
        params = contract_request.get_params()
        response = self.make_request(id, method, **params)
        return contract_request.parse_response(response.result)

    def check(self):
        return self.make_request(self.generate_id(), TEST_ROUTE)
