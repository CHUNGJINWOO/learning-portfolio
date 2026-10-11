"""
Launch script for Phase 5: TF2 Coordinate Transformation Demonstration.

Orchestrates:
1. Static Laser Broadcaster: base_link -> laser_frame (x=0.20, z=0.15)
2. Static Camera Broadcaster: base_link -> camera_link (x=0.10, z=0.25)
3. Dynamic Odometry Broadcaster: odom -> base_link (10Hz circular path)
4. Point Transformer Listener: converts local laser points to global odom frame
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    """Generate launch description for the integrated TF2 transform demo."""
    # 1. Static LiDAR sensor mount transform (base_link -> laser_frame)
    static_laser_node = Node(
        package='tf2_transforms_py',
        executable='static_frame_broadcaster',
        name='static_laser_broadcaster',
        output='screen',
        parameters=[{
            'parent_frame': 'base_link',
            'child_frame': 'laser_frame',
            'x': 0.20,
            'y': 0.0,
            'z': 0.15,
            'roll': 0.0,
            'pitch': 0.0,
            'yaw': 0.0,
        }]
    )

    # 2. Static front camera mount transform (base_link -> camera_link)
    static_camera_node = Node(
        package='tf2_transforms_py',
        executable='static_frame_broadcaster',
        name='static_camera_broadcaster',
        output='screen',
        parameters=[{
            'parent_frame': 'base_link',
            'child_frame': 'camera_link',
            'x': 0.10,
            'y': 0.0,
            'z': 0.25,
            'roll': 0.0,
            'pitch': 0.0,
            'yaw': 0.0,
        }]
    )

    # 3. Dynamic planar odometry motion broadcaster (odom -> base_link, 10Hz)
    dynamic_odom_node = Node(
        package='tf2_transforms_py',
        executable='dynamic_frame_broadcaster',
        name='dynamic_frame_broadcaster',
        output='screen'
    )

    # 4. Point coordinate transformer listener node
    listener_node = Node(
        package='tf2_transforms_py',
        executable='point_transformer_listener',
        name='point_transformer_listener',
        output='screen'
    )

    return LaunchDescription([
        static_laser_node,
        static_camera_node,
        dynamic_odom_node,
        listener_node
    ])
