# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 CHUNGJINWOO
"""
2D Occupancy Grid Ray Tracing Simulation.

This module implements 2D ray casting and grid occupancy calculation
based on Bresenham's line algorithm (Jack E. Bresenham, 1962).
The algorithm casts virtual laser beams across a 2D grid map to compute
traversed (free) cells and endpoint (occupied) cells.
"""

import math

# 지도 설정
MAP_WIDTH = 12
MAP_HEIGHT = 10
RESOLUTION = 1.0

MIN_PASS_THROUGH = 2
OCCUPANCY_THRESHOLD = 0.1

# 스캔마다 로봇이 이동하는 위치 (미터)
robot_positions = [
    (5.0, 4.0),
    (5.5, 4.0),
    (6.0, 4.0),
]

# LaserScan 형태의 가상 데이터
angle_min = -1.57
angle_increment = 0.39

ranges = [
    3.0, float("inf"), 3.0,
    float("nan"), 3.0, 2.0,
    3.0, float("inf"), 3.0,
]

range_min = 0.12
range_max = 3.5


def trace_line(x0, y0, x1, y1):
    """시작 셀부터 끝 셀까지 지나가는 격자 좌표를 반환한다."""
    cells = []

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    error = dx - dy

    while True:
        cells.append((x0, y0))

        if x0 == x1 and y0 == y1:
            break

        error2 = 2 * error

        if error2 > -dy:
            error -= dy
            x0 += sx

        if error2 < dx:
            error += dx
            y0 += sy

    return cells


def world_to_grid(x, y):
    """미터 좌표를 격자 인덱스로 변환한다."""
    return (
        math.floor(x / RESOLUTION),
        math.floor(y / RESOLUTION),
    )


def calculate_endpoint(robot, angle, distance):
    """각도와 거리로 센서 빔의 끝점 좌표를 계산한다."""
    x = robot[0] + distance * math.cos(angle)
    y = robot[1] + distance * math.sin(angle)
    return x, y


def record_free(cell):
    """셀을 자유 공간 관측으로 기록한다."""
    pass_count[cell] = pass_count.get(cell, 0) + 1
    hit_count.setdefault(cell, 0)


def record_hit(cell):
    """셀을 장애물 끝점 관측으로 기록한다."""
    pass_count[cell] = pass_count.get(cell, 0) + 1
    hit_count[cell] = hit_count.get(cell, 0) + 1


def classify_cell(passes, hits):
    """통과 횟수와 장애물 비율로 셀 상태를 결정한다."""
    if passes <= MIN_PASS_THROUGH:
        return "Unknown"

    if hits / passes > OCCUPANCY_THRESHOLD:
        return "Occupied"

    return "Free"


def print_map(width, height, robot, states):
    """점유 격자 지도를 문자로 출력한다."""
    symbols = {
        "Unknown": "?",
        "Free": ".",
        "Occupied": "#",
    }

    for y in reversed(range(height)):
        row = []

        for x in range(width):
            cell = (x, y)

            if cell == robot:
                row.append("R")
            elif cell in states:
                row.append(symbols[states[cell]])
            else:
                row.append("?")

        print(" ".join(row))


# 모든 스캔에서 공유하는 누적 카운트
pass_count = {}
hit_count = {}

NUM_SCANS = len(robot_positions)

print("LaserScan 빔 처리:")

for scan_num, robot in enumerate(robot_positions):
    robot_grid = world_to_grid(*robot)

    print(
        f"\n===== 스캔 {scan_num + 1}/{NUM_SCANS} "
        f"| 로봇 위치={robot} "
        f"| 격자={robot_grid} ====="
    )

    for i, distance in enumerate(ranges):
        angle = angle_min + i * angle_increment

        # NaN은 유효하지 않은 측정값으로 건너뛴다.
        if math.isnan(distance):
            print(f"빔 {i}: NaN - 건너뜀")
            continue

        if distance < range_min:
            print(f"빔 {i}: 최소 거리 미만 - 건너뜀")
            continue

        if math.isinf(distance):
            if distance < 0:
                print(f"빔 {i}: 음의 무한대 - 건너뜀")
                continue

            # 학습용 가정: +inf는 최대 거리까지 자유 공간
            distance = range_max
            has_hit = False

            print(
                f"빔 {i}: +inf - "
                f"최대 거리 {range_max}m까지 자유 공간"
            )

        elif distance > range_max:
            print(f"빔 {i}: 최대 거리 초과 - 건너뜀")
            continue

        else:
            has_hit = True

        endpoint = calculate_endpoint(robot, angle, distance)
        endpoint_grid = world_to_grid(*endpoint)

        print(
            f"빔 {i}: 끝점=({endpoint[0]:.2f}, "
            f"{endpoint[1]:.2f}), 격자={endpoint_grid}"
        )

        # 로봇에서 끝점까지 격자 셀을 추적한다.
        cells = trace_line(*robot_grid, *endpoint_grid)

        # 끝점 이전 셀은 자유 공간으로 기록한다.
        for cell in cells[:-1]:
            record_free(cell)

        # 유한 거리의 끝점은 장애물, +inf 끝점은 자유 공간이다.
        if has_hit:
            record_hit(endpoint_grid)
            print(f"  -> 장애물 끝점 기록: {endpoint_grid}")
        else:
            record_free(endpoint_grid)
            print(f"  -> 자유 공간 끝점 기록: {endpoint_grid}")


# 모든 스캔이 끝난 후 셀 상태를 분류한다.
states = {
    cell: classify_cell(pass_count[cell], hit_count[cell])
    for cell in pass_count
}


print("\n셀별 상태 분류 과정:")

for cell in sorted(pass_count, key=lambda c: (c[1], c[0])):
    passes = pass_count[cell]
    hits = hit_count[cell]

    if passes <= MIN_PASS_THROUGH:
        ratio_text = "계산 안 함 (관측 부족)"
    else:
        ratio = hits / passes
        ratio_text = f"{ratio:.3f}"

    print(
        f"셀={cell}, "
        f"통과={passes}, "
        f"장애물={hits}, "
        f"장애물 비율={ratio_text}, "
        f"최종 상태={states[cell]}"
    )


print("\n2D 점유 격자 지도:")

# 마지막 스캔에서 로봇이 위치한 격자 셀
final_robot_grid = world_to_grid(*robot_positions[-1])

print_map(
    MAP_WIDTH,
    MAP_HEIGHT,
    final_robot_grid,
    states,
)
