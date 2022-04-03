import sys
import traceback

from core.connection import TcpJRpcConnectionHelper

import socket
import signal
import threading

from core.logging import get_logger
from core.utils import TEST_ROUTE


logger = get_logger()


def test_handler(*args, **kwargs):
    return 'OK'


class TcpRpcServer(object):
    def __init__(self):
        self._routes = {TEST_ROUTE: test_handler}
        self._listener = None
        self._should_stop = False
        self._chunk = 1024
        self._before_start = set()
        self._after_finish = set()

    def add_route(self, route, handler):
        """
        Registers the handler function as a route for the application

        route: str
        handler: callable
        """
        if not callable(handler):
            raise ValueError('handler should be a callable')

        if not isinstance(route, str):
            raise ValueError('route should be a string')

        self._routes[route] = handler

    def hook_before_start(self, hook):
        """
        Registers the hook that would be called before the listening

        hook: callable
        """
        if not callable(hook):
            raise ValueError('hook should be a callable')

        self._before_start.add(hook)

    def hook_after_finish(self, hook):
        """
        Registers the hook that would be called on exit (would be skipped on an immediate exit)

        hook: callable
        """
        if not callable(hook):
            raise ValueError('hook should be callable')

        self._after_finish.add(hook)

    def serve(self, host='127.0.0.1', port=5445, pool=5):
        """
        Starts the app.
        """
        logger.info('server ignition...')

        self._run_hooks_before_start()

        self._listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._listener.bind((host, port))
        self._listener.listen(pool)

        signal.signal(signal.SIGINT, self.stop)

        logger.info('The server is ready {}:{}'.format(host, port))

        listener = threading.Thread(
            target=self._listen
        )
        listener.start()
        while not self._should_stop:
            listener.join(5)
        listener.join(5)
        self._listener.close()

        self._run_hooks_after_finish()

    def method(self, route):
        """
        Returns a decorator that makes routes from controller functions.
        A controller function is the function that takes 'request' as an only argument.
        """
        def wrapper(func):
            self.add_route(route, func)
            return func
        return wrapper

    def function_method(self, route):
        """
        Returns a decorator that makes routes from "plain" functions.
        A plain function is the function that doesn't take 'request' as an argument.
        However, it could take any other arguments.
        In that case, the request parameters will be provided as function arguments.

        NB: all routes should be imported to the scope of entry point.

        Example:
            @app.function_method('add')
            def add(item_a, item_b):
                return item_a + item_b

            class AddContract(Contract):
            __method__ = 'add'
            class Request:
                item_a = IntField(required=True)
                item_b = IntField(required=True)
        """
        def wrapper(func):
            def inner(request):
                return func(**request.params)
            self.add_route(route, inner)
            return func
        return wrapper

    def stop(self, *args, **kwargs):
        """
        Stops the app. The first call initiates a graceful stop
        (no new connections/request allowed, waits for current requests to be finished).
        The second call stops the server immediately (skipping any hooks).

        Handles SIGINT by default.
        """
        logger.error('the stop signal caught')
        if self._should_stop is True:
            logger.fatal('immediate stop')
            self._listener.close()
            sys.exit(1)
        self._should_stop = True

    def _handle_request(self, connection):
        id_ = None
        logger.info("start processing the request")
        try:
            request = connection.recv_request()

            id_ = request.id
            route = request.method
            handler = self._routes.get(route)
            logger.info("start handling the request {}".format(str(request)))

            response = handler(request)
            connection.send_response(id_, response)

            logger.info("request #{} is finished successfully".format(request.id))

        except ValueError as e:
            logger.warning("request #{} - invalid data".format(id_))
            connection.send_response_error(id_, e)

        except (EOFError, TimeoutError, ConnectionAbortedError, ConnectionResetError):
            logger.error("broken request #{}".format(id_))
            connection.close()

        except Exception as e:
            logger.error(
                "an exception was caught while handling the request #{} ({})".format(id_, traceback.format_exc())
            )
            connection.send_response_error(id_, e)
            connection.close()

    def _send_connection_error(self, connection, error, address):
        try:
            connection.send_response_error(None, error)
        except Exception as e:
            logger.error("unable to send an error to {} ({})".format(address, e))

    def _handle_connection(self, raw_connection, address):
        connection = TcpJRpcConnectionHelper(raw_connection)
        try:
            while connection.keep_alive() and not self._should_stop:
                self._handle_request(connection)

        except TimeoutError:
            logger.warning("connection with {} is closed (timeout)".format(address))

        except (ConnectionResetError, ConnectionAbortedError):
            logger.warning("connection with {} is closed".format(address))

        except Exception as e:
            logger.error("connection with {} caught an exception {}".format(address, traceback.format_exc()))
            self._send_connection_error(connection, e, address)

        finally:
            connection.close()
            logger.info("connection with {} is closed".format(address))

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

            threading.Thread(
                target=self._handle_connection,
                args=(connection, addr)
            ).start()

    def _run_hooks_before_start(self):
        for hook in self._before_start:
            hook(self)

    def _run_hooks_after_finish(self):
        for hook in self._after_finish:
            hook(self)
