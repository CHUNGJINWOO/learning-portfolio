"""
Fibonacci Action Client Node with Feedback Monitoring and Cancellation Testing.

Demonstrates:
1. Sending an asynchronous action goal to the ActionServer.
2. Confirming goal acceptance or rejection.
3. Receiving continuous feedback during long-running execution.
4. Sending cooperative cancellation requests via the --cancel command-line flag.
5. Differentiating final states (SUCCEEDED vs CANCELED vs REJECTED).

Official References:
- ROS 2 Humble Documentation: Writing an action server and client (Python)
- Apache License, Version 2.0
"""

import sys
import time
from typing import Optional, Tuple

from action_msgs.msg import GoalStatus
from example_interfaces.action import Fibonacci
from rclpy.action import ActionClient
from rclpy.action.client import ClientGoalHandle
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
import rclpy


class FibonacciActionClient(Node):
    """Action client interacting with the fibonacci ActionServer."""

    def __init__(self) -> None:
        super().__init__('fibonacci_action_client')

        self._action_client = ActionClient(self, Fibonacci, 'fibonacci')
        self._feedback_count: int = 0

    def _feedback_callback(self, feedback_msg) -> None:
        """Callback executed whenever server publishes progress feedback."""
        self._feedback_count += 1
        sequence = feedback_msg.feedback.sequence
        self.get_logger().info(f'Feedback received (#{self._feedback_count}): {sequence}')

    def execute_goal(self, order: int, request_cancel: bool = False) -> Tuple[Optional[int], list]:
        """
        Sends goal, monitors execution, handles optional cancellation, and retrieves result.

        :param order: Desired Fibonacci sequence order.
        :param request_cancel: If True, dispatches cancel request after receiving initial feedback.
        :return: Tuple of (GoalStatus int or None if rejected, final sequence list).
        """
        # 1. Wait for Action Server discovery
        self.get_logger().info('Waiting for "fibonacci" action server...')
        if not self._action_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error(
                'Action server "fibonacci" not available after 5 seconds. '
                'Ensure "ros2 run service_action_py fibonacci_action_server" is running.'
            )
            return GoalStatus.STATUS_UNKNOWN, []

        # 2. Build and dispatch goal request
        goal_msg = Fibonacci.Goal()
        goal_msg.order = order

        self.get_logger().info(f'Sending goal request: order={order} (request_cancel={request_cancel})')
        send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self._feedback_callback
        )

        rclpy.spin_until_future_complete(self, send_goal_future)
        goal_handle: Optional[ClientGoalHandle] = send_goal_future.result()

        if goal_handle is None or not goal_handle.accepted:
            self.get_logger().warn(f'Goal REJECTED by server: order={order}')
            return None, []

        self.get_logger().info(f'Goal ACCEPTED by server. Processing execution (order={order})...')

        # 3. Retrieve result future
        result_future = goal_handle.get_result_async()

        # 4. If cancellation requested, wait for 2 feedback steps then trigger cancel
        if request_cancel:
            self.get_logger().info('Cancellation test active. Waiting for progress before sending cancel...')
            timeout_start = time.time()
            while self._feedback_count < 2 and (time.time() - timeout_start) < 4.0:
                rclpy.spin_once(self, timeout_sec=0.1)

            self.get_logger().warn('Sending cancellation request to action server now...')
            cancel_future = goal_handle.cancel_goal_async()
            rclpy.spin_until_future_complete(self, cancel_future)
            cancel_response = cancel_future.result()
            self.get_logger().info(
                f'Cancel response received: return_code={cancel_response.return_code}'
            )

        # 5. Wait until final result arrives
        rclpy.spin_until_future_complete(self, result_future)
        result_response = result_future.result()

        status = result_response.status
        sequence = result_response.result.sequence

        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(f'SUCCESS: Action succeeded! Result sequence: {sequence}')
        elif status == GoalStatus.STATUS_CANCELED:
            self.get_logger().warn(f'CANCELED: Action successfully canceled! Partial sequence: {sequence}')
        else:
            self.get_logger().error(f'FAILED: Action finished with status={status}')

        return status, sequence


def parse_cli_args(args: list) -> Tuple[Optional[int], bool]:
    """
    Parses CLI order integer and --cancel flag.
    Example: ['10'] or ['10', '--cancel'] or ['--cancel', '10']
    """
    request_cancel = '--cancel' in args
    clean_args = [arg for arg in args if not arg.startswith('--') and not arg.startswith('__')]

    if not clean_args:
        return None, request_cancel

    try:
        order = int(clean_args[0])
        return order, request_cancel
    except ValueError:
        return None, request_cancel


def main(args=None) -> None:
    rclpy.init(args=args)

    order, request_cancel = parse_cli_args(sys.argv[1:])
    if order is None:
        print(
            'Error: Missing or invalid sequence order argument.\n'
            'Usage: ros2 run service_action_py fibonacci_action_client -- <order> [--cancel]\n'
            'Examples:\n'
            '  Normal execution:  ros2 run service_action_py fibonacci_action_client -- 10\n'
            '  Cancellation test: ros2 run service_action_py fibonacci_action_client -- 10 --cancel',
            file=sys.stderr
        )
        rclpy.try_shutdown()
        sys.exit(1)

    node = FibonacciActionClient()
    try:
        status, sequence = node.execute_goal(order, request_cancel)
        if status is None:
            print('STATUS: REJECTED (no action result status)')
        else:
            print(f'STATUS: {status}')
        print(f'SEQUENCE: {sequence}')
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
