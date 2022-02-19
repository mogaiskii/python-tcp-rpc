class Field(object):
    def __init__(self, required=False, default=None):
        self.required = required
        self.default = default

    def clean(self, value):
        if self.required and not value:
            raise ValueError('value is required but not provided, {}'.format(value))
        if self.default and not value:
            value = self.default
        if not self._type_validation(value):
            raise ValueError('invalid value given for {} (given {})'.format(str(type(self)), value))
        return value

    def _type_validation(self, value):
        return True

    def __repr__(self):
        return '{}'.format(type(self))


class IntField(Field):
    def _type_validation(self, value):
        return isinstance(value, int)


class StrField(Field):
    def _type_validation(self, value):
        return isinstance(value, str)


class PythonicField(Field):
    def __init__(self, required=False, default=None, type_=object):
        self.type_ = type_
        super(PythonicField, self).__init__(required, default)

    def _type_validation(self, value):
        return isinstance(value, self.type_)


class EnumField(Field):
    def __init__(self, required=False, default=None, options=None):
        if isinstance(options, ContractEnum):
            options = options.get_options()
        elif isinstance(options, list):
            pass
        else:
            raise ValueError('`options` must be either `list` or `ContractEnum`')

        self.options = options
        super(EnumField, self).__init__(required, default)

    def _type_validation(self, value):
        return value in self.options


class ContractEnum(object):
    @classmethod
    def get_options(cls):
        result = []
        for name, value in cls.__dict__.items():
            if name[:1] == '_':
                continue
            result.append(value)
        return result
