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
  - 지정한 월드 좌표 `(x, y)`에 대응하는 2D 격자 인덱스 및 셀 경계 좌표 정밀 계산

### 3. `map_change_monitor.py` (점유격자 델타 모니터링)
- **기능:**
  - 주기적으로 발행되는 `/map` 토픽의 변화량을 추적
  - 이전 맵과 최신 맵 간의 셀 점유 상태 변화(Free ↔ Occupied ↔ Unknown)를 비교하여 맵 업데이트 빈도 및 안정성 진단

### 4. `map_visualizer.py` (터미널 및 Matplotlib 맵 시각화)
- **기능:** 점유격자 1D 직렬화 배열(`int8[]`)을 2D 2차원 넘파이 행렬로 재구성하여 콘솔 ASCII 및 그래픽 플롯 렌더링

---

## 🛠️ 실행 및 테스트 방법

```bash
# ROS 2 환경 로드
source /opt/ros/humble/setup.bash

# 1. 독립 레이 트레이싱 수학 시뮬레이션 (순수 파이썬)
python3 03_robotics_algorithms/ray_trace.py

# 2. 실시간 맵 인스펙터 노드 실행 (/map 토픽 수신 대기)
python3 03_robotics_algorithms/map_inspector.py
```
