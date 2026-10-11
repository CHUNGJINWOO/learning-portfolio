"""
Minimal Subscriber Node implementation in ROS 2.

This module demonstrates reactive, event-driven message handling in ROS 2
using Python class-based subscriptions.

Key Concepts Demonstrated:
1. Event-Driven Execution: The node does not actively poll the network; the ROS 2
   executor invokes listener_callback automatically whenever new DDS data arrives.
2. Inversion of Control (IoC): Control flow is ceded to rclpy.spin(), which dispatches
   incoming middleware events to registered callback methods.
3. Decoupling: MinimalSubscriber operates with complete decoupling from the publisher;
   it requires only the topic name ('heartbeat') and message interface (std_msgs/msg/String).

Official References:
- ROS 2 Humble Documentation: Writing a simple publisher and subscriber (Python)
- Apache License, Version 2.0
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MinimalSubscriber(Node):
    """
    Heartbeat telemetry subscriber node.

    Subscribes to the 'heartbeat' topic and processes status updates
    asynchronously via a registered callback method.
    """

    def __init__(self) -> None:
        """Initialize the MinimalSubscriber node and subscribe to the heartbeat topic."""
        # Register the unique node name in the ROS 2 computation graph
        super().__init__('minimal_subscriber')

        # Create a subscription to topic 'heartbeat' with QoS queue depth of 10
        self.subscription = self.create_subscription(
            String,
            'heartbeat',
            self.listener_callback,
            10
        )

        self.get_logger().info(
            'MinimalSubscriber node initialized. Listening to "heartbeat" topic...'
        )

    def listener_callback(self, msg: String) -> None:
        """
        Message event handler executed upon receiving data from the middleware.

        Extracts the message payload and logs the received telemetry string.
        """
        self.get_logger().info(f'Received: "{msg.data}"')


def main(args=None) -> None:
    """
    Main entry point for subscriber node execution.

    Initializes rclpy, instantiates the subscriber node, spins the event loop
    to process incoming messages, and performs deterministic cleanup upon termination.
    """
    rclpy.init(args=args)
    node = MinimalSubscriber()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        # Graceful exit upon SIGINT (Ctrl+C)
        pass
    finally:
        # Deterministic resource deallocation
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
