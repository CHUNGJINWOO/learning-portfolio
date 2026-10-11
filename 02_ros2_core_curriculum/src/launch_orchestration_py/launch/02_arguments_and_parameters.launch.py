"""
Launch script for Exercise 02: Launch Arguments and Parameter Overrides.

Demonstrates:
1. Declaring launch arguments (rate_hz, bot_id) with defaults matching YAML.
2. Locating package configuration files via PathJoinSubstitution and FindPackageShare.
3. Loading a base YAML configuration into a Node.
4. Overriding YAML parameters dynamically using a subsequent parameter dictionary.
   (In ROS 2 Humble launch_ros, the parameter list is evaluated sequentially;
    the subsequent dictionary overrides matching keys previously loaded from YAML.)
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    """Generate launch description with arguments and parameter overriding."""
    # Declare launch arguments
    rate_hz_arg = DeclareLaunchArgument(
        'rate_hz',
        default_value='2.0',
        description='Telemetry publishing frequency in Hz (overrides YAML)'
    )

    bot_id_arg = DeclareLaunchArgument(
        'bot_id',
        default_value='telemetry_bot_orchestrated',
        description='Device ID for telemetry tracking (overrides YAML)'
    )

    # Resolve YAML configuration file path
    params_file = PathJoinSubstitution([
        FindPackageShare('launch_orchestration_py'),
        'config',
        'orchestration_params.yaml'
    ])

    # Declare Node with YAML base parameters followed by LaunchConfiguration overrides
    telemetry_node = Node(
        package='param_qos_py',
        executable='dynamic_telemetry_publisher',
        name='dynamic_telemetry_publisher',
        output='screen',
        parameters=[
            params_file,
            {
                'publish_rate_hz': LaunchConfiguration('rate_hz'),
                'device_id': LaunchConfiguration('bot_id'),
            }
        ]
    )

    return LaunchDescription([
        rate_hz_arg,
        bot_id_arg,
        telemetry_node
    ])
