import math

import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid


class MapInspector(Node):
    def __init__(self):
        super().__init__('map_inspector')

        self.subscription = self.create_subscription(
            OccupancyGrid,
            '/map',
            self.map_callback,
            10
        )

    def map_callback(self, msg):
        info = msg.info

        width = info.width
        height = info.height
        resolution = info.resolution
        origin_x = info.origin.position.x
        origin_y = info.origin.position.y

        # 검사할 월드 좌표
        world_x = -2.0
        world_y = -2.0

        # 월드 좌표 -> 격자 좌표
        grid_x = math.floor(
            (world_x - origin_x) / resolution
        )
        grid_y = math.floor(
            (world_y - origin_y) / resolution
        )

        print('\n===== ROS 2 Map Inspector =====')
        print(f'Frame: {msg.header.frame_id}')
        print(f'Map size: {width} x {height}')
        print(f'Resolution: {resolution:.3f} m/cell')
        print(f'Origin: ({origin_x:.3f}, {origin_y:.3f})')
        print(f'World coordinate: ({world_x}, {world_y})')
        print(f'Grid coordinate: ({grid_x}, {grid_y})')

                # 격자 셀의 실제 월드 좌표 계산
        cell_x = origin_x + grid_x * resolution
        cell_y = origin_y + grid_y * resolution

        center_x = cell_x + resolution / 2
        center_y = cell_y + resolution / 2

        print(
            f'Cell lower-left corner: '
            f'({cell_x:.3f}, {cell_y:.3f})'
        )
        print(
            f'Cell center: '
            f'({center_x:.3f}, {center_y:.3f})'
        )
        
        if not (0 <= grid_x < width and 0 <= grid_y < height):
            print('검사 좌표가 지도 범위를 벗어났습니다.')
            self.finish()
            return

        index = grid_y * width + grid_x
        value = msg.data[index]

        states = {
            -1: 'Unknown',
            0: 'Free',
            100: 'Occupied'
        }

        print(f'Array index: {index}')
        print(f'Cell value: {value}')
        print(f'Cell state: {states.get(value, "Other")}')

        # 중심 셀 주변 11 x 11 격자 출력
        print('\n===== Neighborhood (11 x 11) =====')
        print('Legend: ? = Unknown, . = Free, # = Occupied, R = Center')

        symbols = {
            -1: '?',
            0: '.',
            100: '#'
        }

        radius = 5

        for y in range(grid_y + radius, grid_y - radius - 1, -1):
            row = ''

            for x in range(grid_x - radius, grid_x + radius + 1):
                if x == grid_x and y == grid_y:
                    row += 'R'
                elif 0 <= x < width and 0 <= y < height:
                    cell_value = msg.data[y * width + x]
                    row += symbols.get(cell_value, '?')
                else:
                    row += ' '

            print(row)

        # 주변 셀의 실제 OccupancyGrid 값 출력
        print('\\n===== Numeric Neighborhood (11 x 11) =====')

        for y in range(grid_y + radius, grid_y - radius - 1, -1):
            row = []

            for x in range(grid_x - radius, grid_x + radius + 1):
                if 0 <= x < width and 0 <= y < height:
                    cell_value = msg.data[y * width + x]
                    row.append(f'{cell_value:4d}')
                else:
                    row.append('   -')

            print(' '.join(row))

        self.finish()

    def finish(self):
        self.subscription.destroy()
        rclpy.shutdown()


def main():
    rclpy.init()
    node = MapInspector()

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
