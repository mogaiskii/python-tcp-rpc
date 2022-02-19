class TcpJRpcResponse(object):
    def __init__(self, id, result):
        self.id = id
        self.result = result

    @classmethod
    def parse(cls, data):
        id = data.get('id')
        error = data.get('error')
        if error:
            raise error
        result = data.get('result')
        return cls(id, result)

    def __repr__(self):
        return "<-- {{id: {}, result: {}}}".format(self.id, str(self.result))
