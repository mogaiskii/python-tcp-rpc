import sys
import traceback

from core.connection import TcpJRpcConnectionHelper

import socket
import signal
import threading

from core.logging import get_logger


logger = get_logger()


def test_handler(*args, **kwargs):
    return 'OK'


class TcpRpcServer(object):
    def __init__(self):
        self._routes = {'test': test_handler}
        self._listener = None
        self._should_stop = False
        self._chunk = 1024

    def add_route(self, route, handler):
        self._routes[route] = handler

    def _handle(self, raw_connection, address):
        id_ = None
        connection = TcpJRpcConnectionHelper(raw_connection)
        try:
            logger.info("start processing request from {}".format(address))
            request = connection.recv_request()
            id_ = request.id
            route = request.method
            handler = self._routes.get(route)
            logger.info("start handling request {}".format(str(request)))
            response = handler(request)
            connection.send_response(id_, response)
            logger.info("request #{} successfully finished".format(request.id))
            return True

        except Exception as e:
            logger.error("request #{} caught an exception {}".format(id_, traceback.format_exc()))
            connection.send_response_error(id_, e)
            return False
        finally:
            connection.close()
            logger.info("connection with {} closed".format(address))

    def stop(self, *args, **kwargs):
        logger.error('stop signal caught')
        if self._should_stop is True:
            logger.fatal('immediate stop')
            self._listener.close()
            sys.exit(1)
        self._should_stop = True

    def _listen(self):
        while not self._should_stop:
            try:
                connection, addr = self._listener.accept()
            except OSError:
                if self._should_stop:
                    break
                else:
                    raise

            if self._should_stop:
                connection.close()
                continue

            # TODO: wait until end
            # TODO: mb keep-connection
            worker = threading.Thread(
                target=self._handle,
                args=(connection, addr)
            ).start()

    def serve(self, host='127.0.0.1', port=5445, pool=5):
        logger.info('server ignition...')

        self._listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._listener.bind((host, port))
        self._listener.listen(pool)

        signal.signal(signal.SIGINT, self.stop)

        logger.info('server is ready {}:{}'.format(host, port))

        listener = threading.Thread(
            target=self._listen
        )
        listener.start()
        while not self._should_stop:
            pass
        listener.join(5)
        self._listener.close()

    def method(self, route):
        def wrapper(func):
            self.add_route(route, func)
            return func
        return wrapper

    def function_method(self, route):
        """
        позволяет использовать плоские/чистые функции без завязки на реквест. то есть, реализует прямой RPC
        добавляет метод в роуты
        """
        def wrapper(func):
            def inner(request):
                return func(**request.params)
            self.add_route(route, inner)
            return func
        return wrapper
