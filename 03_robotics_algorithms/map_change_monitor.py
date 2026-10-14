# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 CHUNGJINWOO
"""
ROS 2 OccupancyGrid Map Change Monitor Node.

Subscribes to '/map' (nav_msgs/OccupancyGrid) and tracks map changes by
computing SHA-256 hashes of the grid data buffer to detect update cycles.
"""

import hashlib

import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid


class MapChangeMonitor(Node):
    def __init__(self):
        super().__init__('map_change_monitor')
        self.previous_hash = None
        self.count = 0

        self.subscription = self.create_subscription(
            OccupancyGrid,
            '/map',
            self.callback,
            10
        )

        self.get_logger().info('Monitoring /map data...')

    def callback(self, msg):
        data = bytes((value & 0xff) for value in msg.data)
        current_hash = hashlib.sha256(data).hexdigest()[:16]
        self.count += 1

        if self.previous_hash is None:
            state = 'FIRST MAP'
        elif current_hash != self.previous_hash:
            state = 'MAP DATA CHANGED'
        else:
            state = 'MAP DATA UNCHANGED'

        self.get_logger().info(
            f'#{self.count} {state} | '
            f'{msg.info.width}x{msg.info.height} | '
            f'hash={current_hash} | '
            f'stamp={msg.header.stamp.sec}.'
            f'{msg.header.stamp.nanosec:09d}'
        )

        self.previous_hash = current_hash


def main():
    rclpy.init()
    node = MapChangeMonitor()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
