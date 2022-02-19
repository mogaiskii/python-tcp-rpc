from core.contract.fields import Field


class ContractPartition(object):
    def __init__(self, proto):
        self._proto = proto

    def get_fields(self):
        fields = dict()
        for name, value in self._proto.__dict__.items():
            if name[:1] == '_':
                continue
            if not isinstance(value, Field):
                continue
            fields[name] = value
        return fields

    def clean_data(self, data):
        validated = dict()
        fields = self.get_fields()
        plain = False
        if getattr(self._proto, 'plain', False):
            assert len(fields) == 1
            plain = True

        for field_name, field in fields.items():
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
        assert cls.__method__
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
