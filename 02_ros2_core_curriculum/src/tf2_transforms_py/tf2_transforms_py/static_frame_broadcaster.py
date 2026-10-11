"""
Static Transform Broadcaster Node with ROS 2 Parameter Configuration.

Broadcasts fixed geometric frame relationships (e.g. sensor mount offsets)
to /tf_static using tf2_ros.StaticTransformBroadcaster with Transient Local QoS.
"""

from geometry_msgs.msg import TransformStamped
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from tf2_ros.static_transform_broadcaster import StaticTransformBroadcaster

from tf2_transforms_py.quaternion_utils import euler_to_quaternion


class StaticFrameBroadcaster(Node):
    """Broadcasts a static coordinate frame transform using ROS parameters."""

    def __init__(self) -> None:
        super().__init__('static_frame_broadcaster')

        # 1. Declare configurable ROS parameters with default mount offsets
        self.declare_parameter('parent_frame', 'base_link')
        self.declare_parameter('child_frame', 'laser_frame')
        self.declare_parameter('x', 0.20)
        self.declare_parameter('y', 0.0)
        self.declare_parameter('z', 0.15)
        self.declare_parameter('roll', 0.0)
        self.declare_parameter('pitch', 0.0)
        self.declare_parameter('yaw', 0.0)

        # 2. Retrieve parameters
        self._parent_frame: str = str(self.get_parameter('parent_frame').value).strip()
        self._child_frame: str = str(self.get_parameter('child_frame').value).strip()
        self._x: float = float(self.get_parameter('x').value)
        self._y: float = float(self.get_parameter('y').value)
        self._z: float = float(self.get_parameter('z').value)
        self._roll: float = float(self.get_parameter('roll').value)
        self._pitch: float = float(self.get_parameter('pitch').value)
        self._yaw: float = float(self.get_parameter('yaw').value)

        # 3. Defensive validation guard
        if not self._parent_frame or not self._child_frame:
            self.get_logger().error('parent_frame and child_frame must not be empty.')
            raise ValueError('parent_frame and child_frame cannot be empty')
        if self._parent_frame == self._child_frame:
            self.get_logger().error(
                f'Cyclic frame self-reference detected: "{self._parent_frame}"'
            )
            raise ValueError(
                f'parent_frame and child_frame cannot be identical: {self._parent_frame}'
            )

        # 4. Instantiate broadcaster and construct TransformStamped message
        self._broadcaster = StaticTransformBroadcaster(self)

        qx, qy, qz, qw = euler_to_quaternion(self._roll, self._pitch, self._yaw)

        transform_msg = TransformStamped()
        transform_msg.header.stamp = self.get_clock().now().to_msg()
        transform_msg.header.frame_id = self._parent_frame
        transform_msg.child_frame_id = self._child_frame
        transform_msg.transform.translation.x = self._x
        transform_msg.transform.translation.y = self._y
        transform_msg.transform.translation.z = self._z
        transform_msg.transform.rotation.x = qx
        transform_msg.transform.rotation.y = qy
        transform_msg.transform.rotation.z = qz
        transform_msg.transform.rotation.w = qw

        # 5. Broadcast to /tf_static (latched by DDS Transient Local durability)
        self._broadcaster.sendTransform(transform_msg)

        self.get_logger().info(
            f'Static transform published: "{self._parent_frame}" -> "{self._child_frame}" '
            f'translation=({self._x:.2f}, {self._y:.2f}, {self._z:.2f}) '
            f'rotation_rpy=({self._roll:.2f}, {self._pitch:.2f}, {self._yaw:.2f})'
        )


def main(args=None) -> None:
    """Entry point for static_frame_broadcaster node."""
    rclpy.init(args=args)
    try:
        node = StaticFrameBroadcaster()
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if 'node' in locals() and rclpy.ok():
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
