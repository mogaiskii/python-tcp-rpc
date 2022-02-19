import sys

if sys.version_info > (3, 0):
    import pickle
else:
    import cPickle as pickle


class NullObject(object):
    pass


null = NullObject


class TcpJsonRpcProto(object):
    CONTENT_LENGTH_LENGTH = 32

    @classmethod
    def encode_request(cls, id, method, params):
        request_data = {
            'method': method,
            'params': params,
            'id': id
        }
        return cls.encode(request_data)

    @classmethod
    def encode_response(cls, id, result=null, error=null):
        response_data = {'id': id}
        if result is not null:
            response_data['result'] = result
        else:
            response_data['error'] = error
        return cls.encode(response_data)

    @classmethod
    def encode(cls, data):
        data = pickle.dumps(data, 1)
        content_length = len(data)
        content_length_header = str(content_length).zfill(cls.CONTENT_LENGTH_LENGTH).encode()
        return content_length_header + data

    @classmethod
    def decode_length(cls, raw_header_data):
        assert raw_header_data, 'empty data'

        content_length = int(raw_header_data)
        return content_length

    @classmethod
    def decode_data(cls, raw_data):
        data = pickle.loads(raw_data)
        return data
