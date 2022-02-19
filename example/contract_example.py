from core.contract import Contract
from core.contract.fields import IntField, StrField, PythonicField, EnumField, ContractEnum


class MathOperations(ContractEnum):
    add = '+'
    mul = '*'
    sub = '-'


class MathContract(Contract):
    __method__ = 'math'

    class Request:
        operation = EnumField(required=True, options=MathOperations.get_options())
        item_a = IntField(required=True)
        item_b = IntField(required=True)

    class Response:
        result = IntField()
    Response.plain = True


class ConcatContract(Contract):
    __method__ = 'concat'

    class Request:
        item_a = StrField(required=True)
        item_b = StrField(required=True)

    class Response:
        result = StrField()
    Response.plain = True


class WhoamiContract(Contract):
    __method__ = 'whoami'

    class Response:
        result = PythonicField(type_=tuple)
    Response.plain = True
