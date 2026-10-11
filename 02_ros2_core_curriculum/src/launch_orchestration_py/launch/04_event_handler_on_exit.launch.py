"""
Launch script for Exercise 04: Process Lifecycle and OnProcessExit Event Handling.

Demonstrates:
1. Orchestrating a persistent service server alongside a transient client.
2. Passing CLI parameters to a console executable via Launch arguments and Node(arguments=...).
3. Registering an OnProcessExit event handler to monitor process exit status.
4. Inspecting event.returncode:
   - returncode == 0: Logs success and emits Shutdown event to cleanly stop background servers.
   - returncode != 0: Logs failure code and emits Shutdown event with error diagnostic.
"""

from typing import List, Optional

from launch import LaunchContext, LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    EmitEvent,
    LogInfo,
    RegisterEventHandler
)
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch.events.process import ProcessExited
from launch.launch_description_entity import LaunchDescriptionEntity
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    """Generate launch description with OnProcessExit event handler."""
    # Declare launch arguments for client inputs
    arg_a = DeclareLaunchArgument(
        'arg_a',
        default_value='20',
        description='First integer operand for AddTwoInts client'
    )

    arg_b = DeclareLaunchArgument(
        'arg_b',
        default_value='30',
        description='Second integer operand for AddTwoInts client'
    )

    # 1. Background persistent service server
    server_node = Node(
        package='service_action_py',
        executable='add_two_ints_server',
        name='add_two_ints_server',
        output='screen'
    )

    # 2. Transient service client passing arguments through '--'
    client_node = Node(
        package='service_action_py',
        executable='add_two_ints_client',
        name='add_two_ints_client',
        output='screen',
        arguments=[
            '--',
            LaunchConfiguration('arg_a'),
            LaunchConfiguration('arg_b')
        ]
    )

    # 3. Dynamic callback for OnProcessExit inspecting returncode
    def handle_client_exit(
        event: ProcessExited,
        context: LaunchContext
    ) -> Optional[List[LaunchDescriptionEntity]]:
        if event.returncode == 0:
            return [
                LogInfo(msg=(
                    f'[Orchestration] Client task completed successfully '
                    f'(returncode={event.returncode}). Initiating graceful system shutdown.'
                )),
                EmitEvent(event=Shutdown(reason='Service client call finished with success.'))
            ]
        else:
            return [
                LogInfo(msg=(
                    f'[Orchestration ERROR] Client task failed '
                    f'(returncode={event.returncode}). Initiating emergency system shutdown.'
                )),
                EmitEvent(event=Shutdown(
                    reason=f'Service client failed with exit code {event.returncode}.'
                ))
            ]

    # Register OnProcessExit handler specifically targeting client_node
    exit_handler = RegisterEventHandler(
        OnProcessExit(
            target_action=client_node,
            on_exit=handle_client_exit
        )
    )

    return LaunchDescription([
        arg_a,
        arg_b,
        server_node,
        client_node,
        exit_handler
    ])
