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


class ConcatContract(Contract):
    __method__ = 'concat'

    class Request:
        item_a = StrField(required=True)
        item_b = StrField(required=True)

    class Response:
        result = StrField()
    Response.plain = True
```


### Contract-based client implementation

```python
from client import TcpRpcClient


client = TcpRpcClient()

client.perform(ConcatContract(item_a='abc', item_b='def'))  # == 'abcdef'
```


### See more examples in `example/`


## TODO:

- listener thread (non-main one)
- refactoring
  + contracts
  + MathContract.implement
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
