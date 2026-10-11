"""
High-rate Sensor Data Streamer with SensorDataQoS (Best Effort).

Simulates high-frequency IMU sensor telemetry using Best Effort reliability
and Volatile durability, optimal for lossy wireless robotic networks.

Official References:
- ROS 2 Humble Documentation: About Quality of Service Settings
- Apache License, Version 2.0
"""

from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
import rclpy
from std_msgs.msg import String


class QoSSensorStreamer(Node):
    """Publishes high-frequency sensor telemetry using SensorDataQoS profile."""

    def __init__(self) -> None:
        super().__init__('qos_sensor_streamer')

        # Using standard SensorDataQoS: Best Effort, Volatile, Depth=5
        self._publisher = self.create_publisher(
            String,
            'sensor/imu_stream',
            qos_profile_sensor_data
        )

        self._seq: int = 0
        self._timer_period_sec: float = 0.1  # 10 Hz
        self._timer = self.create_timer(self._timer_period_sec, self._timer_callback)

        self.get_logger().info(
            'QoSSensorStreamer initialized. Publishing to "sensor/imu_stream" with Best Effort QoS at 10Hz.'
        )

    def _timer_callback(self) -> None:
        msg = String()
        # Simulated sensor pitch/roll payload
        msg.data = f'IMU roll=0.012 pitch=-0.005 seq={self._seq}'
        self._publisher.publish(msg)

        # Log every 10th sample to prevent terminal clutter while verifying activity
        if self._seq % 10 == 0:
            self.get_logger().info(f'Streamed sample: "{msg.data}"')

        self._seq += 1


def main(args=None) -> None:
    rclpy.init(args=args)
    node = QoSSensorStreamer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
