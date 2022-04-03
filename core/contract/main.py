import inspect

from core.contract.fields import Field


class ContractPartition(object):
    def __init__(self, proto):
        self._proto = proto
        self._fields = self.get_fields()

    def get_fields(self):
        fields = dict()
        for name, value in self._proto.__dict__.items():
            if name[:1] == '_':
                continue
            if not isinstance(value, Field):
                continue
            fields[name] = value
        return fields

    def is_plain(self):
        if getattr(self._proto, 'plain', False):
            if len(self._fields) != 1:
                raise RuntimeError('Incorrect partition - `plain` was used with multiple fields')
            return True
        return False

    def clean_data(self, data):
        validated = dict()
        plain = self.is_plain()

        for field_name, field in self._fields.items():
            if plain:
                value = data
            else:
                value = data.get(field_name)

            if field.required and not value:
                raise ValueError('{} is required but not provided'.format(field_name))

            field.clean(value)
            validated[field_name] = field.clean(value)

            if plain:
                break

        return validated

    def make_object(self, data):
        # TODO: wrap on metaclass Request and Response so it would be easier
        #   and add repr to them
        if getattr(self._proto, 'plain', False):
            return next(iter(data.values()))

        obj = self._proto()
        for name, value in data.items():
            setattr(obj, name, value)
        return obj

    def check_fields(self, args, varargs, varkw):
        if self.is_plain():
            return bool(varargs)

        used_args = set()

        for field_name, _ in self._fields.items():
            if field_name in args:
                used_args.add(field_name)
                continue
            if bool(varkw):
                continue
            return False

        if set(args) - used_args:
            return False

        return True


class Contract(object):
    __method__ = None

    class Request:
        pass

    class Response:
        pass

    def __init__(self, **data):
        clean_data = self._prepare_data(data, self.Request)
        for k, v in clean_data.items():
            setattr(self, k, v)
        self._data = clean_data

    def get_params(self):
        return self._data

    @classmethod
    def make_request(cls, connection, **data):
        if not cls.__method__:
            raise RuntimeError('Incorrect contract - __method__ was not provided')

        request_data = cls._prepare_data(data, cls.Request)
        connection.send_request(connection.generate_id(), cls.__method__, request_data)
        response = connection.recv_response()
        return cls.parse_response(response.result)

    @classmethod
    def parse_response(cls, result):
        partition = ContractPartition(cls.Response)
        data = partition.clean_data(result)
        return partition.make_object(data)

    @classmethod
    def _prepare_data(cls, data, partition):
        return ContractPartition(partition).clean_data(data)

    @classmethod
    def implement(cls, app):
        def wrapper(func):
            # TODO: mb validation errors, both, req and resp, in wrapper
            arg_spec = inspect.getfullargspec(func)
            partition = ContractPartition(cls.Request)
            if not partition.check_fields(arg_spec.args, arg_spec.varargs, arg_spec.varkw):
                raise RuntimeError(
                    'Incorrect contract implementation - check args {}'.format(func.__name__)
                )

            app.function_method(cls.__method__)(func)
            return func
        return wrapper
