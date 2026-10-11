"""
Dynamic Transform Broadcaster Node Simulating Circular Odometry Motion.

Broadcasts continuously evolving spatial relationships (odom -> base_link)
at 10Hz using tf2_ros.TransformBroadcaster on topic /tf.
"""

import math

from geometry_msgs.msg import TransformStamped
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from tf2_ros.transform_broadcaster import TransformBroadcaster

from tf2_transforms_py.quaternion_utils import euler_to_quaternion


class DynamicFrameBroadcaster(Node):
    """Broadcasts dynamic odom -> base_link transform along a circular path."""

    def __init__(self) -> None:
        super().__init__('dynamic_frame_broadcaster')

        self._broadcaster = TransformBroadcaster(self)

        # Trajectory parameters: radius R=1.0m, angular velocity omega=0.3 rad/s
        self._radius: float = 1.0
        self._omega: float = 0.3
        self._start_time_sec = self.get_clock().now().nanoseconds * 1e-9

        # Periodic timer at 10 Hz (0.1s period)
        self._timer_period_sec: float = 0.1
        self._timer = self.create_timer(self._timer_period_sec, self._timer_callback)

        self.get_logger().info(
            'DynamicFrameBroadcaster initialized. Broadcasting odom -> base_link at 10Hz.'
        )

    def _timer_callback(self) -> None:
        now_time_sec = self.get_clock().now().nanoseconds * 1e-9
        elapsed_sec = now_time_sec - self._start_time_sec

        # Circular trajectory: x = R*cos(omega*t), y = R*sin(omega*t)
        angle = self._omega * elapsed_sec
        x = self._radius * math.cos(angle)
        y = self._radius * math.sin(angle)
        z = 0.0

        # Heading tangential to the circle: yaw = angle + pi/2
        yaw = angle + (math.pi / 2.0)
        # Normalize yaw to [-pi, pi]
        yaw = math.atan2(math.sin(yaw), math.cos(yaw))

        qx, qy, qz, qw = euler_to_quaternion(0.0, 0.0, yaw)

        msg = TransformStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'odom'
        msg.child_frame_id = 'base_link'
        msg.transform.translation.x = x
        msg.transform.translation.y = y
        msg.transform.translation.z = z
        msg.transform.rotation.x = qx
        msg.transform.rotation.y = qy
        msg.transform.rotation.z = qz
        msg.transform.rotation.w = qw

        self._broadcaster.sendTransform(msg)


def main(args=None) -> None:
    """Entry point for dynamic_frame_broadcaster node."""
    rclpy.init(args=args)
    try:
        node = DynamicFrameBroadcaster()
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if 'node' in locals() and rclpy.ok():
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
