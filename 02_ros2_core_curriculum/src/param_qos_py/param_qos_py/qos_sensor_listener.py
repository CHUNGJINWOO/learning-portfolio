"""
Configurable QoS Sensor Listener Node.

Demonstrates DDS QoS compatibility matching:
- When reliability_mode is 'best_effort': Compatible with SensorDataQoS publisher.
- When reliability_mode is 'reliable': Incompatible with Best Effort publisher,
  resulting in endpoint mismatch and communication failure.

Official References:
- ROS 2 Humble Documentation: About Quality of Service Settings
- Apache License, Version 2.0
"""

from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy, qos_profile_sensor_data
import rclpy
from std_msgs.msg import String


class QoSSensorListener(Node):
    """Subscribes to sensor telemetry with configurable QoS reliability."""

    def __init__(self) -> None:
        super().__init__('qos_sensor_listener')

        # Declare parameter allowing dynamic selection of requested reliability
        self.declare_parameter('reliability_mode', 'best_effort')
        mode = str(self.get_parameter('reliability_mode').value).strip().lower()

        if mode == 'reliable':
            self._qos_profile = QoSProfile(
                depth=10,
                reliability=ReliabilityPolicy.RELIABLE,
                durability=DurabilityPolicy.VOLATILE,
                history=HistoryPolicy.KEEP_LAST
            )
            self.get_logger().warn(
                'Requested QoS: RELIABLE. Note: Incompatible if publisher offers BEST_EFFORT!'
            )
        else:
            self._qos_profile = qos_profile_sensor_data
            self.get_logger().info('Requested QoS: BEST_EFFORT (SensorDataQoS). Compatible.')

        self._subscription = self.create_subscription(
            String,
            'sensor/imu_stream',
            self._listener_callback,
            self._qos_profile
        )

        self._received_count: int = 0
        self.get_logger().info('QoSSensorListener ready. Listening to "sensor/imu_stream"...')

    def _listener_callback(self, msg: String) -> None:
        self._received_count += 1
        if self._received_count % 10 == 0 or self._received_count <= 3:
            self.get_logger().info(f'Received sample (#{self._received_count}): "{msg.data}"')


def main(args=None) -> None:
    rclpy.init(args=args)
    node = QoSSensorListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
