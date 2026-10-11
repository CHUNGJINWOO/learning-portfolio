"""
Dynamic Telemetry Publisher Node with Defensive Parameter Validation.

Demonstrates:
1. Pure validation callback via add_on_set_parameters_callback (Zero side-effects).
2. Runtime state & timer period adjustment via /parameter_events subscription.
3. Use of timer_period_ns and reset() for atomic timer recalculation.

Official References:
- ROS 2 Humble Documentation: Understanding Parameters, About Parameters
- Apache License, Version 2.0
"""

from typing import List

from rcl_interfaces.msg import ParameterEvent, SetParametersResult
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from std_msgs.msg import String


class DynamicTelemetryPublisher(Node):
    """
    Telemetry publisher supporting dynamic parameter reconfiguration.

    Enforces defensive validation in on_set callback and applies runtime
    timer updates asynchronously via the /parameter_events topic.
    """

    def __init__(self) -> None:
        super().__init__('dynamic_telemetry_publisher')

        # 1. Parameter declaration with explicit defaults and types
        self.declare_parameter('publish_rate_hz', 1.0)
        self.declare_parameter('device_id', 'telemetry_bot_01')

        # 2. Local state initialization
        self._publish_rate_hz: float = float(self.get_parameter('publish_rate_hz').value)
        self._device_id: str = str(self.get_parameter('device_id').value)
        self._sequence_number: int = 0

        # 3. Telemetry publisher and periodic timer
        self._publisher = self.create_publisher(String, 'telemetry/status', 10)
        period_sec = 1.0 / self._publish_rate_hz
        self._timer = self.create_timer(period_sec, self._timer_callback)

        # 4. Pure validation callback (guard clause only, zero side-effects)
        self.add_on_set_parameters_callback(self._validate_parameters_callback)

        # 5. Parameter event listener for applying committed runtime changes
        self._param_event_sub = self.create_subscription(
            ParameterEvent,
            '/parameter_events',
            self._on_parameter_event_callback,
            10
        )

        self.get_logger().info(
            f'DynamicTelemetryPublisher initialized. ID="{self._device_id}", Rate={self._publish_rate_hz:.1f}Hz'
        )

    def _validate_parameters_callback(self, params: List[Parameter]) -> SetParametersResult:
        """
        Pure validation callback.

        Validates all candidate parameters atomically.
        CRITICAL: Never mutates internal state, timers, or parameters here.
        """
        for param in params:
            if param.name == 'publish_rate_hz':
                if param.type_ not in (Parameter.Type.DOUBLE, Parameter.Type.INTEGER):
                    return SetParametersResult(
                        successful=False,
                        reason=f'publish_rate_hz must be numeric, got {param.type_}'
                    )
                val = float(param.value)
                if val <= 0.0 or val > 50.0:
                    return SetParametersResult(
                        successful=False,
                        reason=f'publish_rate_hz must be in (0.0, 50.0] Hz, got {val}'
                    )

            elif param.name == 'device_id':
                if param.type_ != Parameter.Type.STRING:
                    return SetParametersResult(
                        successful=False,
                        reason=f'device_id must be a string, got {param.type_}'
                    )
                val_str = str(param.value).strip()
                if not val_str:
                    return SetParametersResult(
                        successful=False,
                        reason='device_id cannot be empty or whitespace only'
                    )

        return SetParametersResult(successful=True)

    def _on_parameter_event_callback(self, event: ParameterEvent) -> None:
        """
        Applies committed parameter changes upon receiving confirmed /parameter_events.

        Triggered asynchronously by the executor after ROS 2 commits the parameters.
        """
        # Filter events targeting this specific node
        if event.node != self.get_fully_qualified_name():
            return

        all_params = event.changed_parameters + event.new_parameters
        for param_msg in all_params:
            if param_msg.name == 'publish_rate_hz':
                if param_msg.value.type == Parameter.Type.DOUBLE.value:
                    new_rate = float(param_msg.value.double_value)
                elif param_msg.value.type == Parameter.Type.INTEGER.value:
                    new_rate = float(param_msg.value.integer_value)
                else:
                    continue

                if new_rate > 0.0:
                    self._publish_rate_hz = new_rate
                    new_period_ns = int((1.0 / new_rate) * 1e9)
                    self._timer.timer_period_ns = new_period_ns
                    self._timer.reset()
                    self.get_logger().info(
                        f'Parameter event applied: publish_rate_hz={new_rate:.1f}Hz (period={new_period_ns}ns)'
                    )

            elif param_msg.name == 'device_id':
                if param_msg.value.type == Parameter.Type.STRING.value:
                    self._device_id = str(param_msg.value.string_value)
                    self.get_logger().info(
                        f'Parameter event applied: device_id="{self._device_id}"'
                    )

    def _timer_callback(self) -> None:
        """Periodic telemetry dispatch handler."""
        msg = String()
        msg.data = f'[{self._device_id}] seq={self._sequence_number} rate={self._publish_rate_hz:.1f}Hz'
        self._publisher.publish(msg)
        self.get_logger().info(f'Published: "{msg.data}"')
        self._sequence_number += 1


def main(args=None) -> None:
    rclpy.init(args=args)
    node = DynamicTelemetryPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
