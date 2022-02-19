import socket

from core.request import TcpJRpcRequest
from core.response import TcpJRpcResponse
from core.utils import generate_id
from proto.tcpjrpc import TcpJsonRpcProto


class TcpJRpcConnectionHelper(object):
    CHUNK_LENGTH = 1024

    def __init__(self, connection_backend):
        self._connection = connection_backend

    @classmethod
    def generate_id(cls):
        return generate_id()

    @classmethod
    def connect(cls, host='127.0.0.1', port=5445):
        conn = socket.create_connection((host, port))
        return cls(conn)

    def send_request(self, id, method, params):
        encoded_data = TcpJsonRpcProto.encode_request(
            id, method, params
        )
        self._connection.send(encoded_data)

    def send_response(self, id, data):
        encoded = TcpJsonRpcProto.encode_response(id, result=data)
        self._connection.send(encoded)

    def send_response_error(self, id, error):
        encoded = TcpJsonRpcProto.encode_response(id, error=error)
        self._connection.send(encoded)

    def _recv_chunks(self, content_length):
        raw_data = b''
        while len(raw_data) < content_length:
            new_data = self._connection.recv(self.CHUNK_LENGTH)
            if not new_data:
                raise EOFError
            raw_data += new_data

        return raw_data

    def _recv_message(self):
        content_length_raw = self._connection.recv(TcpJsonRpcProto.CONTENT_LENGTH_LENGTH)
        content_length = TcpJsonRpcProto.decode_length(content_length_raw)
        raw_data = self._recv_chunks(content_length)
        data = TcpJsonRpcProto.decode_data(raw_data)
        return data

    def recv_request(self):
        request = self._recv_message()
        return TcpJRpcRequest.parse(request, addr=self._connection.getpeername())

    def recv_response(self):
        response = self._recv_message()
        return TcpJRpcResponse.parse(response)

    def close(self):
        self._connection.close()
