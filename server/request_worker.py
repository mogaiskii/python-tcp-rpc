class RequestWorker(object):
    def __init__(self, request, handler):
        self._request = request
        self._handler = handler
        self.request_id = request.get('id')

    def not_found(self):
        pass

    def perform(self):
        if self._handler is None:
            return self.not_found()
