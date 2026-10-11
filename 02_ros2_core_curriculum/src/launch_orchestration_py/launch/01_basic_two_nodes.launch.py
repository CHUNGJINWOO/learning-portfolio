"""
Launch script for Exercise 01: Basic Multi-Node Orchestration.

Launches minimal_publisher and minimal_subscriber from core_pubsub_py
simultaneously within a single unified process group.
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    """Generate launch description for basic publisher and subscriber nodes."""
    publisher_node = Node(
        package='core_pubsub_py',
        executable='minimal_publisher',
        name='minimal_publisher',
        output='screen'
    )

    subscriber_node = Node(
        package='core_pubsub_py',
        executable='minimal_subscriber',
        name='minimal_subscriber',
        output='screen'
    )

    return LaunchDescription([
        publisher_node,
        subscriber_node
    ])
