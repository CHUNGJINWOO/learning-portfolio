"""
Minimal Publisher Node implementation in ROS 2.

This module demonstrates the fundamental mapping between Python Object-Oriented
Programming (OOP) principles and ROS 2 Node architecture.

Key Concepts Demonstrated:
1. Inheritance: MinimalPublisher inherits lifecycle, logging, and middleware
   interfaces from rclpy.node.Node.
2. Encapsulation: State variables (such as sequence_number) are safely encapsulated
   within the class instance rather than scattered in global scope.
3. Asynchronous Timer Callbacks: Uses ROS 2 executor-driven timer callbacks instead
   of procedural blocking sleep loops (time.sleep), ensuring the process remains
   responsive to system signals and executor scheduling.

Official References:
- ROS 2 Humble Documentation: Writing a simple publisher and subscriber (Python)
- Apache License, Version 2.0
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MinimalPublisher(Node):
    """
    Periodic telemetry publisher node.

    Publishes heartbeat status messages to the 'heartbeat' topic at a fixed
    frequency using a non-blocking timer callback.
    """

    def __init__(self) -> None:
        """Initialize the MinimalPublisher node, publisher, and periodic timer."""
        # Register the unique node name in the ROS 2 computation graph
        super().__init__('minimal_publisher')

        # Create a publisher on topic 'heartbeat' with QoS queue depth of 10
        self.publisher_ = self.create_publisher(String, 'heartbeat', 10)

        # Define periodic timer interval (1.0 second = 1 Hz)
        self.timer_period_sec: float = 1.0
        self.timer = self.create_timer(self.timer_period_sec, self.timer_callback)

        # Encapsulated state variable tracking message sequence
        self.sequence_number: int = 0

        self.get_logger().info(
            f'MinimalPublisher node initialized. Publishing to "heartbeat" at {self.timer_period_sec}s interval.'
        )

    def timer_callback(self) -> None:
        """
        Timer event handler executed periodically by the ROS 2 executor.

        Constructs a structured status payload, publishes it to the DDS topic,
        logs the dispatch event, and increments the internal sequence counter.
        """
        msg = String()
        msg.data = f'Heartbeat seq={self.sequence_number} status=ACTIVE'

        self.publisher_.publish(msg)
        self.get_logger().info(f'Published: "{msg.data}"')

        self.sequence_number += 1


def main(args=None) -> None:
    """
    Main entry point for node execution.

    Initializes the rclpy client library, instantiates the node, spins the
    event loop until interrupted, and performs deterministic resource cleanup.
    """
    rclpy.init(args=args)
    node = MinimalPublisher()

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
