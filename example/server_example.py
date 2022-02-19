from operator import add, mul, sub

from server import TcpRpcServer


app = TcpRpcServer()


@app.function_method('concat')
def example_concat(item_a, item_b):
    return str(item_a) + str(item_b)


@app.function_method('math')
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


# @MathContract.implement(app)
# def example_math_handler(operation, item_a, item_b):
#     pass


if __name__ == '__main__':
    app.serve()
