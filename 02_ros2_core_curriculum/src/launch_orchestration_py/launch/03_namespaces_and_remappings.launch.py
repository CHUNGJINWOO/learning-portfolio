"""
Launch script for Exercise 03: Namespaces and Topic Remappings.

Demonstrates:
1. Running multiple instances of the same node executable concurrently without conflict.
2. GroupAction and PushRosNamespace for multi-robot namespace scoping (limo_01, limo_02).
3. Relative topic resolution ('sensor/imu_stream' -> '/limo_02/sensor/imu_stream').
4. Topic remapping ('sensor/imu_stream' -> 'imu/data_raw' -> '/limo_01/imu/data_raw').
"""

from launch import LaunchDescription
from launch.actions import GroupAction
from launch_ros.actions import Node, PushRosNamespace


def generate_launch_description() -> LaunchDescription:
    """Generate launch description with namespaces and topic remapping."""
    # Robot 1 Group: Namespace 'limo_01' with topic remapping to 'imu/data_raw'
    limo_01_group = GroupAction([
        PushRosNamespace('limo_01'),
        Node(
            package='param_qos_py',
            executable='qos_sensor_streamer',
            name='qos_sensor_streamer',
            output='screen',
            remappings=[
                ('sensor/imu_stream', 'imu/data_raw')
            ]
        )
    ])

    # Robot 2 Group: Namespace 'limo_02' with standard relative topic resolution
    limo_02_group = GroupAction([
        PushRosNamespace('limo_02'),
        Node(
            package='param_qos_py',
            executable='qos_sensor_streamer',
            name='qos_sensor_streamer',
            output='screen'
        )
    ])

    return LaunchDescription([
        limo_01_group,
        limo_02_group
    ])
