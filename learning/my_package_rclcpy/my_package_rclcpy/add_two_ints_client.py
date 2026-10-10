
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class AddTwoIntsClient(Node):
    def __init__(self):
        super().__init__('add_two_ints_client')
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')

        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for add_two_ints service...')

    def send_request(self, a, b):
        request = AddTwoInts.Request()
        request.a = a
        request.b = b
        return self.cli.call_async(request)


def main(args=None):
    rclpy.init(args=args)
    node = AddTwoIntsClient()

    future = node.send_request(12, 34)
    rclpy.spin_until_future_complete(node, future)

    if future.result() is not None:
        response = future.result()
        node.get_logger().info(f'Result: {12} + {34} = {response.sum}')
    else:
        node.get_logger().error('Service call failed.')

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
