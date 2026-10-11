"""
Fibonacci Action Server Node with Goal Validation and Cooperative Cancellation.

Demonstrates:
1. Long-running preemptable task management via ROS 2 Actions.
2. Goal validation in goal_callback rejecting invalid orders (e.g. order < 1 or order > 45).
3. Cooperative cancellation checking goal_handle.is_cancel_requested during execution.
4. Concurrency management using ReentrantCallbackGroup and MultiThreadedExecutor.

Official References:
- ROS 2 Humble Documentation: Writing an action server and client (Python)
- Apache License, Version 2.0
"""

import time

from example_interfaces.action import Fibonacci
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.action.server import ServerGoalHandle
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from rclpy.node import Node
import rclpy


class FibonacciActionServer(Node):
    """Action server computing Fibonacci sequence with feedback and cancellation support."""

    # Maximum order limit to prevent int32 signed overflow (F_47 exceeds 2^31 - 1)
    MAX_VALID_ORDER = 45

    def __init__(self) -> None:
        super().__init__('fibonacci_action_server')

        # ReentrantCallbackGroup allows cancel_callback to execute concurrently with execute_callback
        self._callback_group = ReentrantCallbackGroup()

        self._action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            execute_callback=self._execute_callback,
            callback_group=self._callback_group,
            goal_callback=self._goal_callback,
            cancel_callback=self._cancel_callback
        )

        self.get_logger().info(
            f'FibonacciActionServer ready. Advertising action "fibonacci" (Valid orders: 1..{self.MAX_VALID_ORDER}).'
        )

    def _goal_callback(self, goal_request: Fibonacci.Goal) -> GoalResponse:
        """
        Validates incoming goal requests before accepting execution.

        Rejects order < 1 (non-positive) or order > MAX_VALID_ORDER (overflow prevention).
        """
        order = goal_request.order
        if order < 1:
            self.get_logger().warn(
                f'REJECTING Goal: order={order} is non-positive. Order must be >= 1.'
            )
            return GoalResponse.REJECT

        if order > self.MAX_VALID_ORDER:
            self.get_logger().warn(
                f'REJECTING Goal: order={order} exceeds maximum limit {self.MAX_VALID_ORDER} '
                '(preventing int32 signed integer overflow).'
            )
            return GoalResponse.REJECT

        self.get_logger().info(f'ACCEPTING Goal: order={order}')
        return GoalResponse.ACCEPT

    def _cancel_callback(self, goal_handle: ServerGoalHandle) -> CancelResponse:
        """Accepts incoming cancellation requests."""
        self.get_logger().info('Received client cancellation request. Accepting cancellation.')
        return CancelResponse.ACCEPT

    def _execute_callback(self, goal_handle: ServerGoalHandle) -> Fibonacci.Result:
        """
        Iteratively computes the Fibonacci sequence with periodic feedback and cancel checks.
        """
        order = goal_handle.request.order
        self.get_logger().info(f'Executing goal order={order}...')

        feedback_msg = Fibonacci.Feedback()
        feedback_msg.sequence = [0, 1]

        for i in range(1, order):
            # 1. Check for cancellation request from client
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().warn(
                    f'Goal canceled by client during step {i}/{order}. '
                    f'Partial sequence: {feedback_msg.sequence}'
                )
                result = Fibonacci.Result()
                result.sequence = feedback_msg.sequence
                return result

            # 2. Compute next term
            next_term = feedback_msg.sequence[i] + feedback_msg.sequence[i - 1]
            feedback_msg.sequence.append(next_term)

            # 3. Simulate work and allow cooperative cancellation window
            time.sleep(0.3)

            # 4. Publish feedback
            self.get_logger().info(f'Publishing feedback: {feedback_msg.sequence}')
            goal_handle.publish_feedback(feedback_msg)

        # 5. Transition to SUCCEEDED state upon full completion
        goal_handle.succeed()
        result = Fibonacci.Result()
        result.sequence = feedback_msg.sequence
        self.get_logger().info(f'Goal succeeded! Final result: {result.sequence}')
        return result


def main(args=None) -> None:
    rclpy.init(args=args)
    node = FibonacciActionServer()

    # MultiThreadedExecutor is necessary so cancel requests can be handled while execute_callback runs
    executor = MultiThreadedExecutor()

    try:
        rclpy.spin(node, executor=executor)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
