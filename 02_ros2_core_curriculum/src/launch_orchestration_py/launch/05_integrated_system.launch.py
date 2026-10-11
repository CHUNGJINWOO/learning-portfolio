"""
Launch script for Exercise 05: Integrated Multi-Subsystem System Bringup.

Demonstrates:
1. Orchestrating multiple disparate subsystems from Phase 1 and Phase 2 into a unified robot stack.
2. Composing four independent nodes:
   - MinimalPublisher (Phase 1 core comms): /heartbeat
   - DynamicTelemetryPublisher (Phase 2 telemetry): /telemetry/status with YAML parameter injection
   - QoSSensorStreamer (Phase 2 sensor stream): /sensor/imu_stream with SensorDataQoS (10Hz)
   - QoSConfigPublisher (Phase 2 state latching):
     /system/robot_configuration with TransientLocal QoS
3. Mimicking a real-world mobile robot bringup architecture (e.g. AgileX LIMO bringup).
"""

from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    """Generate launch description for integrated system bringup."""
    # Resolve YAML configuration file path for telemetry publisher
    params_file = PathJoinSubstitution([
        FindPackageShare('launch_orchestration_py'),
        'config',
        'orchestration_params.yaml'
    ])

    # 1. Heartbeat Subsystem (Phase 1)
    heartbeat_node = Node(
        package='core_pubsub_py',
        executable='minimal_publisher',
        name='minimal_publisher',
        output='screen'
    )

    # 2. Dynamic Telemetry Subsystem (Phase 2)
    telemetry_node = Node(
        package='param_qos_py',
        executable='dynamic_telemetry_publisher',
        name='dynamic_telemetry_publisher',
        output='screen',
        parameters=[params_file]
    )

    # 3. High-Rate IMU Sensor Subsystem (Phase 2, Best Effort QoS)
    sensor_node = Node(
        package='param_qos_py',
        executable='qos_sensor_streamer',
        name='qos_sensor_streamer',
        output='screen'
    )

    # 4. Robot System Configuration Subsystem (Phase 2, Transient Local QoS)
    config_node = Node(
        package='param_qos_py',
        executable='qos_config_publisher',
        name='qos_config_publisher',
        output='screen'
    )

    return LaunchDescription([
        heartbeat_node,
        telemetry_node,
        sensor_node,
        config_node
    ])
