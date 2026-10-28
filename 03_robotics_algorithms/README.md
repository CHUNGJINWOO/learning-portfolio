# 03. 로보틱스 공간 수학 및 매핑 알고리즘

이 디렉터리는 2D LiDAR 센서 데이터가 점유격자 지도(OccupancyGrid Map)로 변환되는 **수학적 기하 연산**과 **격자 지도 모니터링/시각화 도구**를 다룹니다.

---

## 📌 주요 모듈 및 구현 원리

### 1. `ray_trace.py` (브레젠험 레이 트레이싱 기반 빔 투영)
- **알고리즘:** Bresenham's Line Algorithm 정수 연산 최적화 구현
- **기능:**
  - 이동 로봇의 현재 위치 `(x0, y0)`로부터 센서 반사점 `(x1, y1)`까지 가상 레이를 방사하여 경유하는 모든 2D 격자 셀 `(grid_x, grid_y)`을 산출
  - 관통 셀(Free Space, 통과 횟수 누적)과 반사 셀(Occupied Space)을 구분하여 점유 확률을 계산
  - `NaN`, `Inf` 등의 센서 이상치(Out-of-range) 필터링 처리 포함

### 2. `map_inspector.py` (월드 ↔ 격자 좌표 변환기)
- **변환 수식:**
  $$grid\_x = \lfloor \frac{world\_x - origin\_x}{resolution} \rfloor$$
  $$grid\_y = \lfloor \frac{world\_y - origin\_y}{resolution} \rfloor$$
- **기능:**
  - ROS 2 `nav_msgs/msg/OccupancyGrid` 메시지를 실시간 수신하여 해상도(`resolution`), 원점 오프셋(`origin`), 격자 인덱스를 분석
  - 코드에 고정된 월드 좌표 `(-2.0, -2.0)`의 격자 인덱스 및 셀 경계 계산
  - 원점 위치와 해상도만 사용하며 원점 회전은 처리하지 않음

### 3. `map_change_monitor.py` (점유격자 변경 감지)
- **기능:**
  - `/map` 메시지의 데이터에 대한 SHA-256 해시를 이전 메시지와 비교해 변경 여부를 기록
  - 셀별 상태 전환이나 변경된 셀 수는 계산하지 않음

### 4. `map_visualizer.py` (터미널 및 Matplotlib 맵 시각화)
- **기능:** 점유격자 배열을 2D NumPy 행렬로 재구성하여 Matplotlib 그래프로 표시하고 셀 상태별 개수를 로깅

---

## 🛠️ 실행 및 테스트 방법

저장소 루트에서 실행합니다. `ray_trace.py`는 Python 표준 라이브러리만 사용하는 독립 시뮬레이션입니다. 나머지 세 도구는 ROS 2의 `rclpy`, `nav_msgs`와 `/map`의 `OccupancyGrid` 발행자가 필요합니다. 시각화에는 NumPy, Matplotlib 및 그래픽 표시 환경도 필요합니다. 아래 명령은 이번 문서 정리에서 실행 검증하지 않았습니다.

```bash
# ROS 2 환경 로드
source /opt/ros/humble/setup.bash

# 1. 독립 레이 트레이싱 수학 시뮬레이션 (순수 파이썬)
python3 03_robotics_algorithms/ray_trace.py

# 2. 실시간 맵 인스펙터 노드 실행 (/map 토픽 수신 대기)
python3 03_robotics_algorithms/map_inspector.py

# 각각 별도 터미널에서 실행 (ROS 2 환경 소싱 필요)
python3 03_robotics_algorithms/map_change_monitor.py
python3 03_robotics_algorithms/map_visualizer.py
```
