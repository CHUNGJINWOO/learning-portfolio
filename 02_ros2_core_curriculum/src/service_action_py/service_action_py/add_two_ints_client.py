"""
AddTwoInts Service Asynchronous Client Node.

Demonstrates sending asynchronous requests to a ROS 2 Service,
waiting for service discovery, and safely spinning the executor until completion.

Official References:
- ROS 2 Humble Documentation: Writing a simple service and client (Python)
- Apache License, Version 2.0
"""

import sys
from typing import Optional, Tuple

from example_interfaces.srv import AddTwoInts
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
import rclpy


class AddTwoIntsClient(Node):
    """Asynchronous client invoking the add_two_ints service."""

    def __init__(self) -> None:
        super().__init__('add_two_ints_client')

        # Create service client
        self._client = self.create_client(AddTwoInts, 'add_two_ints')

    def send_request(self, a: int, b: int) -> Optional[int]:
        """
        Wait for service availability, dispatch async request, and spin until complete.

        :param a: First 64-bit integer.
        :param b: Second 64-bit integer.
        :return: Result sum if successful, None otherwise.
        """
        # 1. Verify service availability
        timeout_count = 0
        while not self._client.wait_for_service(timeout_sec=1.0):
            if not rclpy.ok():
                self.get_logger().error('Interrupted while waiting for service.')
                return None
            timeout_count += 1
            self.get_logger().warn(
                f'Service "add_two_ints" not available yet, waiting ({timeout_count}s)...'
            )
            if timeout_count >= 5:
                self.get_logger().error(
                    'Service discovery timed out after 5 seconds. '
                    'Ensure "ros2 run service_action_py add_two_ints_server" is running.'
                )
                return None

        # 2. Construct request payload
        request = AddTwoInts.Request()
        request.a = a
        request.b = b

        self.get_logger().info(f'Sending async request: {a} + {b}')

        # 3. Asynchronous service call returning a Future object
        future = self._client.call_async(request)

        # 4. Spin executor until future resolves
        rclpy.spin_until_future_complete(self, future)

        if future.result() is not None:
            response: AddTwoInts.Response = future.result()
            self.get_logger().info(f'Received response: {a} + {b} = {response.sum}')
            return response.sum
        else:
            self.get_logger().error(f'Service call failed: {future.exception()}')
            return None


def parse_cli_args(args: list) -> Optional[Tuple[int, int]]:
    """Extracts two integer arguments, filtering out ROS specific arguments."""
    clean_args = [arg for arg in args if not arg.startswith('--') and not arg.startswith('__')]
    if len(clean_args) < 2:
        return None
    try:
        a = int(clean_args[0])
        b = int(clean_args[1])
        return a, b
    except ValueError:
        return None


def main(args=None) -> None:
    rclpy.init(args=args)

    # Parse CLI integers (excluding script name)
    cli_inputs = parse_cli_args(sys.argv[1:])
    if cli_inputs is None:
        print(
            'Error: Invalid or missing arguments.\n'
            'Usage: ros2 run service_action_py add_two_ints_client -- <a> <b>\n'
            'Example: ros2 run service_action_py add_two_ints_client -- 10 20',
            file=sys.stderr
        )
        rclpy.try_shutdown()
        sys.exit(1)

    a, b = cli_inputs
    node = AddTwoIntsClient()

    try:
        result = node.send_request(a, b)
        if result is not None:
            print(f'RESULT: {result}')
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
