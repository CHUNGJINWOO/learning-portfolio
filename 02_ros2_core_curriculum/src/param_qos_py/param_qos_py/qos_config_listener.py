"""
Late-Joining Robot Configuration Listener with Transient Local QoS.

Demonstrates reception of historical latched samples:
- When durability_mode is 'transient_local': Late-joining node immediately receives
  the previously published hardware configuration upon connection.
- When durability_mode is 'volatile': Late-joining node connects successfully but
  receives ZERO past messages, waiting only for future publications.

Official References:
- ROS 2 Humble Documentation: About Quality of Service Settings
- Apache License, Version 2.0
"""

from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
import rclpy
from std_msgs.msg import String


class QoSConfigListener(Node):
    """Late-joining subscriber demonstrating Transient Local historical sample delivery."""

    def __init__(self) -> None:
        super().__init__('qos_config_listener')

        self.declare_parameter('durability_mode', 'transient_local')
        mode = str(self.get_parameter('durability_mode').value).strip().lower()

        if mode == 'volatile':
            durability = DurabilityPolicy.VOLATILE
            self.get_logger().warn(
                'Requested Durability: VOLATILE. Will NOT receive historical latched samples!'
            )
        else:
            durability = DurabilityPolicy.TRANSIENT_LOCAL
            self.get_logger().info(
                'Requested Durability: TRANSIENT_LOCAL. Expecting latched sample immediately.'
            )

        self._qos_profile = QoSProfile(
            depth=1,
            durability=durability,
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST
        )

        self._received_configuration: bool = False
        self._subscription = self.create_subscription(
            String,
            'system/robot_configuration',
            self._config_callback,
            self._qos_profile
        )

        self.get_logger().info(
            'QoSConfigListener started (Late-joiner). Subscribed to "system/robot_configuration"...'
        )

    def _config_callback(self, msg: String) -> None:
        self._received_configuration = True
        self.get_logger().info(
            f'SUCCESS: Latched configuration received from publisher: "{msg.data}"'
        )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = QoSConfigListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
