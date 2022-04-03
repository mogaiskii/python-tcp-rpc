# Lightweight TCP python-rpc client-server

## Features

### Simple workaround for implementing fast rpc python communication

```python
from server import TcpRpcServer


app = TcpRpcServer()

@app.method('hello')
def example_whoami(request):
    return 'world'

app.serve()
```

### Contracts to keep your life simple

```python
from core.contract import Contract
from core.contract.fields import StrField
from <...> import app


class ConcatContract(Contract):
    __method__ = 'concat'

    class Request:
        item_a = StrField(required=True)
        item_b = StrField(required=True)

    class Response:
        result = StrField()
    Response.plain = True


@ConcatContract.implement(app)
def concat(item_a, item_b):
    return str(item_a) + str(item_b)

```


### Contract-based client implementation

```python
from client import TcpRpcClient
from <...> import ConcatContract


client = TcpRpcClient()

client.perform(ConcatContract(item_a='abc', item_b='def'))  # == 'abcdef'
```


### See more examples in `example/`

Running examples:
1. start example/server_example.py
2. run example/client_example.py


## TODO:

- refactoring
  + contracts
  + ContractPartition.make_object
- graceful stop
- tests
  + +check on different hosts
  + +compatibility
- router
- queue
- another formats of communication
- another formats of data packing
- another connection types (udp, mb other protos)
- socket file connection
- taking port 0 (random free one) and declaring it somehow (tmp file)
- security
