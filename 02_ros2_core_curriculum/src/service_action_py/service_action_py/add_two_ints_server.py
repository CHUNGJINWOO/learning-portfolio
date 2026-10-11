"""
AddTwoInts Service Server Node.

Demonstrates the synchronous request-response Service pattern in ROS 2.
Unlike continuous streaming Topics, Services provide two-way remote procedure calls (RPC).

Official References:
- ROS 2 Humble Documentation: Writing a simple service and client (Python)
- Apache License, Version 2.0
"""

from example_interfaces.srv import AddTwoInts
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
import rclpy


class AddTwoIntsServer(Node):
    """Service server that calculates the sum of two 64-bit integers."""

    def __init__(self) -> None:
        super().__init__('add_two_ints_server')

        # Create service with name 'add_two_ints'
        self._srv = self.create_service(
            AddTwoInts,
            'add_two_ints',
            self._add_two_ints_callback
        )

        self.get_logger().info('AddTwoIntsServer ready. Service "add_two_ints" is advertising.')

    def _add_two_ints_callback(
        self,
        request: AddTwoInts.Request,
        response: AddTwoInts.Response
    ) -> AddTwoInts.Response:
        """
        Processes incoming service requests and computes the sum.

        :param request: AddTwoInts.Request containing int64 fields a and b.
        :param response: AddTwoInts.Response containing int64 field sum.
        :return: Completed AddTwoInts.Response.
        """
        self.get_logger().info(f'Incoming request: a={request.a}, b={request.b}')

        # Input calculation (int64 addition)
        response.sum = request.a + request.b

        self.get_logger().info(f'Sending response: sum={response.sum}')
        return response


def main(args=None) -> None:
    rclpy.init(args=args)
    node = AddTwoIntsServer()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
