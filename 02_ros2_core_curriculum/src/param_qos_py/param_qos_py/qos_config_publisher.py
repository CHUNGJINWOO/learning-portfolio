"""
Robot Configuration Publisher with Transient Local QoS (Latched State).

Publishes static hardware configuration using Transient Local durability.
The DDS middleware caches the sample locally so late-joining subscribers receive
the configuration immediately upon connecting, without needing re-transmission.

Official References:
- ROS 2 Humble Documentation: About Quality of Service Settings
- Apache License, Version 2.0
"""

from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
import rclpy
from std_msgs.msg import String


class QoSConfigPublisher(Node):
    """Publishes static robot hardware configuration with Transient Local QoS."""

    def __init__(self) -> None:
        super().__init__('qos_config_publisher')

        # Latched QoS profile: Transient Local, Reliable, Depth=1
        self._latched_qos = QoSProfile(
            depth=1,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST
        )

        self._publisher = self.create_publisher(
            String,
            'system/robot_configuration',
            self._latched_qos
        )

        # Publish the static hardware configuration once upon initialization
        self._config_payload = 'hardware_rev=2.1 wheelbase_m=0.35 max_payload_kg=15.0 lidar=2D_360'
        msg = String()
        msg.data = self._config_payload
        self._publisher.publish(msg)

        self.get_logger().info(
            f'QoSConfigPublisher initialized. Latched configuration published: "{msg.data}"'
        )
        self.get_logger().info(
            'Publisher remains active with Transient Local memory cache. Waiting for late-joining subscribers...'
        )

        # Optional slow heartbeat timer keeping node spin active
        self._heartbeat_timer = self.create_timer(10.0, self._heartbeat_callback)

    def _heartbeat_callback(self) -> None:
        self.get_logger().info(
            'Config publisher heartbeat: Latched message remains preserved in DDS publisher cache.'
        )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = QoSConfigPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
