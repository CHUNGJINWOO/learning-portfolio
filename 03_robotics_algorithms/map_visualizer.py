
import numpy as np
import matplotlib.pyplot as plt

import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid


class MapVisualizer(Node):
    def __init__(self):
        super().__init__('map_visualizer')

        self.subscription = self.create_subscription(
            OccupancyGrid,
            '/map',
            self.map_callback,
            10
        )

        self.map_count = 0

        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(9, 7))
        self.get_logger().info('Waiting for /map ...')

    def map_callback(self, msg):
        width = msg.info.width
        height = msg.info.height
        resolution = msg.info.resolution

        origin_x = msg.info.origin.position.x
        origin_y = msg.info.origin.position.y

        grid = np.asarray(msg.data, dtype=np.int16)
        grid = grid.reshape((height, width))

        # Unknown=회색, Free=흰색, Occupied=검정
        display = np.full((height, width), 0.5, dtype=np.float32)
        display[grid == 0] = 1.0
        display[grid == 100] = 0.0

        extent = [
            origin_x,
            origin_x + width * resolution,
            origin_y,
            origin_y + height * resolution
        ]

        self.ax.clear()
        self.ax.imshow(
            display,
            cmap='gray',
            vmin=0.0,
            vmax=1.0,
            origin='lower',
            extent=extent,
            interpolation='nearest'
        )

        self.ax.plot(0.0, 0.0, 'r+', markersize=12)
        self.ax.set_title('Live ROS 2 OccupancyGrid (/map)')
        self.ax.set_xlabel('World X (m)')
        self.ax.set_ylabel('World Y (m)')
        self.ax.set_aspect('equal')
        self.fig.tight_layout()

        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        plt.pause(0.001)

        self.map_count += 1
        unknown = int(np.count_nonzero(grid == -1))
        free = int(np.count_nonzero(grid == 0))
        occupied = int(np.count_nonzero(grid == 100))

        self.get_logger().info(
            f'Map #{self.map_count}: {width}x{height}, '
            f'Unknown={unknown}, Free={free}, Occupied={occupied}'
        )

    def destroy_node(self):
        plt.close('all')
        super().destroy_node()


def main():
    rclpy.init()
    node = MapVisualizer()

    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.1)
            plt.pause(0.01)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
