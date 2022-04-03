from operator import add, mul, sub

from example.contract_example import MathContract
from server import TcpRpcServer


app = TcpRpcServer()


@app.function_method('concat')
def example_concat(item_a, item_b):
    return str(item_a) + str(item_b)


@MathContract.implement(app)
def example_math_handler(operation, item_a, item_b):
    ops = {
        '+': add,
        '*': mul,
        '-': sub
    }
    c_op = ops[operation]
    return c_op(item_a, item_b)


@app.method('whoami')
def example_whoami(request):
    return request.addr


if __name__ == '__main__':
    app.serve()
