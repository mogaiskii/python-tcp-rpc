class TcpJRpcRequest(object):
    def __init__(self, id, method, params, addr=None):
        self.id = id
        self.method = method
        self.params = params
        self.addr = addr

    @classmethod
    def parse(cls, request, addr=None):
        id = request.get('id')
        method = request.get('method')
        params = request.get('params')
        return cls(id, method, params, addr)

    def __repr__(self):
        return "--> {{id: {}, method: {}, params: {}}}".format(self.id, self.method, str(self.params))
