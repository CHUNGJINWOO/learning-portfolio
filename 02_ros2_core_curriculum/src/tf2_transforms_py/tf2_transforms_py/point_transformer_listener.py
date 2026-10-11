"""
Coordinate Point Transformation Listener Node using tf2_ros and tf2_geometry_msgs.

Listens to spatial transforms across the chain (odom -> base_link -> laser_frame)
and projects a sensor-detected local point (laser_frame) into global odom coordinates.
"""

from geometry_msgs.msg import PointStamped
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.time import Time
import tf2_geometry_msgs
from tf2_ros import (
    ConnectivityException,
    ExtrapolationException,
    LookupException
)
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener


class PointTransformerListener(Node):
    """Listens to transforms and transforms 3D point data across coordinate frames."""

    def __init__(self) -> None:
        super().__init__('point_transformer_listener')

        # 1. Initialize TF buffer and TransformListener
        self._buffer = Buffer()
        self._listener = TransformListener(self._buffer, self)

        # 2. Timer to periodically lookup transform and transform point (1 Hz)
        self._timer = self.create_timer(1.0, self._timer_callback)

        self.get_logger().info(
            'PointTransformerListener initialized. Transforming laser_frame point to odom.'
        )

    def _timer_callback(self) -> None:
        # Define obstacle detected 1.0m directly in front of the LiDAR
        point_in_laser = PointStamped()
        point_in_laser.header.frame_id = 'laser_frame'
        point_in_laser.header.stamp = self.get_clock().now().to_msg()
        point_in_laser.point.x = 1.0
        point_in_laser.point.y = 0.0
        point_in_laser.point.z = 0.0

        try:
            # Lookup transform to express laser_frame data in odom frame at latest time (Time 0)
            transform = self._buffer.lookup_transform(
                'odom',
                'laser_frame',
                Time()
            )

            # Apply coordinate transformation using tf2_geometry_msgs
            point_in_odom = tf2_geometry_msgs.do_transform_point(point_in_laser, transform)

            self.get_logger().info(
                f'Transformed: [{point_in_laser.header.frame_id}] '
                f'({point_in_laser.point.x:.3f}, {point_in_laser.point.y:.3f}, '
                f'{point_in_laser.point.z:.3f}) -> '
                f'[{point_in_odom.header.frame_id}] '
                f'({point_in_odom.point.x:.3f}, {point_in_odom.point.y:.3f}, '
                f'{point_in_odom.point.z:.3f})'
            )

        except (LookupException, ConnectivityException, ExtrapolationException) as ex:
            self.get_logger().warn(
                f'Waiting for valid odom -> laser_frame transform: {ex}'
            )


def main(args=None) -> None:
    """Entry point for point_transformer_listener node."""
    rclpy.init(args=args)
    try:
        node = PointTransformerListener()
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if 'node' in locals() and rclpy.ok():
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
