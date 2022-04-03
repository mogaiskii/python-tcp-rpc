from client import TcpRpcClient
from core.connection import TcpJRpcConnectionHelper
from example.contract_example import MathContract, MathOperations


class ExampleClient(TcpRpcClient):
    def concat(self, item_a, item_b):
        return self.make_request(
            self.generate_id(),
            'concat',
            item_a=item_a, item_b=item_b
        )

    def math(self, operation, item_a, item_b):
        return self.make_request(
            self.generate_id(),
            'math',
            operation=operation, item_a=item_a, item_b=item_b
        )

    def whoami(self):
        return self.make_request(
            self.generate_id(),
            'whoami'
        )


if __name__ == '__main__':
    client = ExampleClient()
    connection = TcpJRpcConnectionHelper.connect()

    print('--> Concat("abc","def")')
    print(client.concat('abc', 'def'))

    c1 = MathContract.make_request(connection, operation=MathOperations.add, item_a=3, item_b=5)
    print('\n--> MathContract(add, 3, 5)')
    print(c1)

    c2 = client.perform(MathContract(operation=MathOperations.add, item_a=3, item_b=5))
    print('\n--> MathContract(add, 3, 5)')
    print(c2)

    print('\n--> Math(*, 3, 5)')
    print(client.math('*', 3, 5))

    print('\n--> whoami')
    print(client.whoami())
