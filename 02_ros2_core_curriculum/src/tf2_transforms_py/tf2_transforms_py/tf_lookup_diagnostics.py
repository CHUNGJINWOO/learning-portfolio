"""
TF2 Lookup Diagnostics and Defensive Exception Demonstration Node.

Demonstrates deterministic detection and graceful handling of the three core
TF2 lookup exceptions: LookupException, ConnectivityException, and ExtrapolationException.
Uses an isolated in-memory TF buffer to guarantee 100% deterministic verification.
"""

from geometry_msgs.msg import TransformStamped
import rclpy
from rclpy.duration import Duration
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.time import Time
from tf2_ros import (
    ConnectivityException,
    ExtrapolationException,
    LookupException
)
from tf2_ros.buffer import Buffer


class TfLookupDiagnostics(Node):
    """Executes deterministic diagnostics on TF2 exception handling semantics."""

    def __init__(self) -> None:
        super().__init__('tf_lookup_diagnostics')
        self.get_logger().info('TfLookupDiagnostics initializing diagnostic test suite...')

        # Run the self-contained in-memory buffer exception verification
        all_passed = self.run_diagnostic_suite()

        if all_passed:
            self.get_logger().info(
                'All 3 TF2 exceptions (Lookup, Connectivity, Extrapolation) '
                'verified successfully!'
            )
        else:
            self.get_logger().error('One or more TF2 exception diagnostic tests failed.')

    def run_diagnostic_suite(self) -> bool:
        """
        Execute deterministic exception tests on an isolated in-memory Buffer.

        Note: Uses isolated Buffer and set_transform APIs to eliminate DDS timing races.
        """
        buf = Buffer()
        results = []

        # -------------------------------------------------------------
        # 1. LookupException Test: Querying a non-existent frame
        # -------------------------------------------------------------
        try:
            buf.lookup_transform('odom', 'unknown_frame_99', Time())
            self.get_logger().error('Test 1 FAILED: LookupException was not raised.')
            results.append(False)
        except LookupException as ex:
            self.get_logger().info(
                f'[DIAGNOSTIC PASS] 1. LookupException correctly caught: {ex}'
            )
            results.append(True)
        except Exception as ex:  # pylint: disable=broad-except
            err_msg = f'Test 1 FAILED: Unexpected exception type: {type(ex).__name__}'
            self.get_logger().error(err_msg)
            results.append(False)

        # -------------------------------------------------------------
        # 2. ConnectivityException Test: Querying disconnected sub-trees
        # -------------------------------------------------------------
        # Populate Tree A: world_a -> robot_a
        t1 = TransformStamped()
        t1.header.frame_id = 'world_a'
        t1.header.stamp = Time(seconds=10).to_msg()
        t1.child_frame_id = 'robot_a'
        t1.transform.rotation.w = 1.0
        buf.set_transform_static(t1, 'authority')

        # Populate Tree B: world_b -> robot_b
        t2 = TransformStamped()
        t2.header.frame_id = 'world_b'
        t2.header.stamp = Time(seconds=10).to_msg()
        t2.child_frame_id = 'robot_b'
        t2.transform.rotation.w = 1.0
        buf.set_transform_static(t2, 'authority')

        try:
            buf.lookup_transform('robot_a', 'robot_b', Time())
            self.get_logger().error('Test 2 FAILED: ConnectivityException was not raised.')
            results.append(False)
        except ConnectivityException as ex:
            self.get_logger().info(
                f'[DIAGNOSTIC PASS] 2. ConnectivityException correctly caught: {ex}'
            )
            results.append(True)
        except Exception as ex:  # pylint: disable=broad-except
            err_msg = f'Test 2 FAILED: Unexpected exception type: {type(ex).__name__}'
            self.get_logger().error(err_msg)
            results.append(False)

        # -------------------------------------------------------------
        # 3. ExtrapolationException Test: Querying a future timestamp
        # -------------------------------------------------------------
        # Populate dynamic transform at t = 100.0s
        t3 = TransformStamped()
        t3.header.frame_id = 'odom'
        t3.header.stamp = Time(seconds=100).to_msg()
        t3.child_frame_id = 'base_link'
        t3.transform.rotation.w = 1.0
        buf.set_transform(t3, 'authority')

        # Query future time t = 110.0s (exceeds buffer timeline)
        try:
            buf.lookup_transform(
                'odom',
                'base_link',
                Time(seconds=110),
                timeout=Duration(seconds=0.0)
            )
            self.get_logger().error('Test 3 FAILED: ExtrapolationException was not raised.')
            results.append(False)
        except ExtrapolationException as ex:
            self.get_logger().info(
                f'[DIAGNOSTIC PASS] 3. ExtrapolationException correctly caught: {ex}'
            )
            results.append(True)
        except Exception as ex:  # pylint: disable=broad-except
            err_msg = f'Test 3 FAILED: Unexpected exception type: {type(ex).__name__}'
            self.get_logger().error(err_msg)
            results.append(False)

        return all(results)


def main(args=None) -> None:
    """Entry point for tf_lookup_diagnostics node."""
    rclpy.init(args=args)
    try:
        node = TfLookupDiagnostics()
        # Brief spin to flush logs cleanly
        rclpy.spin_once(node, timeout_sec=0.5)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if 'node' in locals() and rclpy.ok():
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
