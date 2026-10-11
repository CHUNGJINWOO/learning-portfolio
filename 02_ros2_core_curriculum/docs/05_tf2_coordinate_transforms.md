# ROS 2 Learning Portfolio — Phase 5: TF2 Coordinate Transforms

본 문서는 ROS 2 Humble Hawksbill 환경에서 로봇 좌표계 변환 프레임워크인 **TF2 (Transform Library 2)**의 핵심 아키텍처, 오일러-쿼터니언 수학적 변환 원리, 정적(Static) 및 동적(Dynamic) 브로드캐스터 구현, 리스너 기반 3D 포인트 변환(`do_transform_point`), 그리고 3대 변환 예외(`LookupException`, `ConnectivityException`, `ExtrapolationException`) 진단 및 CLI 도구 활용법을 다루는 종합 기술 가이드입니다.

---

## 1. TF2 좌표 변환의 목적과 아키텍처

### 1.1 왜 TF2 좌표 변환 프레임워크가 필요한가?
실제 이동 로봇(AMR, Manipulator, Drone 등)은 수많은 센서와 링크로 구성됩니다:
- 전방 LiDAR (`laser_frame`)
- 심도 카메라 (`camera_link`)
- 로봇 중심점 (`base_link`)
- 바퀴 오도메트리 기준 좌표계 (`odom`)
- 전역 지도 좌표계 (`map`)

LiDAR 센서가 센서 전방 1.0m 지점에서 장애물을 감지했다면, 이 장애물의 위치는 `laser_frame` 기준 $(1.0, 0.0, 0.0)$입니다. 그러나 로봇이 회피 경로를 계획하려면 **전역 오도메트리 좌표계(`odom`)** 또는 **지도 좌표계(`map`)**에서의 위치를 알아야 합니다.

만약 개발자가 매번 삼각함수와 4x4 동차 변환 행렬(Homogeneous Transformation Matrix)을 수동으로 계산한다면:
1. 로봇 링크 간 체인 계산이 복잡해집니다.
2. 각 센서 데이터와 로봇 위치의 취득 시점(Timestamp) 불일치로 인한 오차가 발생합니다.
3. 여러 노드 간 좌표계 이름 불일치와 변환 방향 혼선이 발생합니다.

**TF2는 시간 축을 따라 분산 시스템 전체의 좌표계 관계를 버퍼링하고, 요청된 시점의 좌표 변환을 스레드 안전하게 제공하는 프레임워크**입니다.

---

### 1.2 TF 트리의 기본 법칙: 단일 부모와 사이클 금지
TF2의 모든 프레임은 **단방향 트리(Directed Tree)** 구조를 형성해야 합니다.
- **규칙 1: 각 프레임은 오직 하나의 부모(Single Parent)만 가질 수 있습니다.**
  - 예: `laser_frame`의 부모는 `base_link`여야 하며, 동시에 `camera_link`를 부모로 둘 수 없습니다.
- **규칙 2: 순환 경로(Cycle)는 엄격히 금지됩니다.**
  - $A \to B \to C \to A$ 형태의 폐루프가 존재하면 좌표 변환 루프가 무한 재귀에 빠지므로 TF2 데몬이 에러를 발생시킵니다.
- **규칙 3: 정적 프레임 vs 동적 프레임 분리**
  - **정적 변환 (`/tf_static`)**: 로봇 섀시에 물리적으로 고정된 센서 장착 위치. `TransientLocal` 내구성 QoS로 래칭(Latched)되어 주기적 재발행 없이 1회만 발행.
  - **동적 변환 (`/tf`)**: 바퀴 주행, 관성 측정 등으로 실시간 변화하는 위치/자세. `Volatile` QoS로 높은 주기(10~100Hz)로 스트리밍.

---

### 1.3 패키지 구조 (`tf2_transforms_py`)
```
src/tf2_transforms_py/
├── package.xml                                     # rclpy, tf2_ros, tf2_geometry_msgs, tf2_tools 의존성 선언
├── setup.py                                        # 4개 실행 노드 entry_points 및 launch data_files 매핑
├── setup.cfg                                       # lib/tf2_transforms_py 설치 경로 설정
├── resource/tf2_transforms_py                      # ament 인덱스 마커
├── tf2_transforms_py/
│   ├── __init__.py                                 # Python 모듈 초기화
│   ├── quaternion_utils.py                         # 순수 Python 표준 라이브러리 기반 오일러-쿼터니언 변환 모듈
│   ├── static_frame_broadcaster.py                 # 파라미터 기반 정적 센서 프레임 브로드캐스터
│   ├── dynamic_frame_broadcaster.py                # 10Hz 원형 궤적 오도메트리 동적 브로드캐스터
│   ├── point_transformer_listener.py               # Buffer/Listener 기반 LiDAR 포인트 좌표 변환 노드
│   └── tf_lookup_diagnostics.py                    # TF2 3대 예외 결정론적 진단 노드
└── launch/
    └── tf2_demo.launch.py                          # 2개 정적 프레임 + 1개 동적 프레임 + 1개 리스너 통합 Launch
```

---

## 2. 쿼터니언 수학적 기초 및 순수 Python 구현

### 2.1 짐벌 락(Gimbal Lock)과 쿼터니언 사용 이유
3차원 회전을 표현하는 데 오일러 각(Euler angles: Roll, Pitch, Yaw)은 직관적이지만 다음과 같은 치명적인 한계를 가집니다:
1. **짐벌 락**: 피치 각도가 $\pm 90^\circ$가 될 때 롤 축과 요 축이 동일 평면에 정렬되어 1개의 자유도를 상실합니다.
2. **보간의 비선형성**: 오일러 각 사이를 선형 보간하면 부자연스러운 왜곡과 속도 불균일이 발생합니다.
3. **표현의 다의성**: 동일한 회전 상태를 나타내는 오일러 각 표현이 무한히 존재합니다.

반면 **단위 쿼터니언(Unit Quaternion)** $q = (x, y, z, w)$는 4차원 복소수 벡터로 회전을 표현하여 짐벌 락이 전혀 없으며, 구면 선형 보간(SLERP)을 통해 매끄러운 회전 보간이 가능합니다.

---

### 2.2 ZYX 내재적 오일러 각 $\to$ 해밀턴 쿼터니언 수식
ROS 2에서 널리 사용하는 표준 축 회전 규약은 **내재적 Z-Y-X(Intrinsic Yaw-Pitch-Roll)** 순서입니다.
- $\psi$ (Yaw, $Z$축 회전)
- $\theta$ (Pitch, $Y$축 회전)
- $\phi$ (Roll, $X$축 회전)

반각(Half-angles) 삼각함수:
$$c_r = \cos(\phi/2), \quad s_r = \sin(\phi/2)$$
$$c_p = \cos(\theta/2), \quad s_p = \sin(\theta/2)$$
$$c_y = \cos(\psi/2), \quad s_y = \sin(\psi/2)$$

해밀턴 쿼터니언 원소 $(q_x, q_y, q_z, q_w)$:
$$\begin{aligned}
q_x &= s_r c_p c_y - c_r s_p s_y \\
q_y &= c_r s_p c_y + s_r c_p s_y \\
q_z &= c_r c_p s_y - s_r s_p c_y \\
q_w &= c_r c_p c_y + s_r s_p s_y
\end{aligned}$$

---

### 2.3 `quaternion_utils.py` 구현 및 표준 라이브러리 채택 배경
ROS 2 Humble 최소 설치 환경에서는 외부 의존성인 `tf_transformations` 또는 `transforms3d`가 설치되어 있지 않으며, 바이너리 환경에 따라 C 확장 모듈의 ABI 충돌이 발생할 수 있습니다.
따라서 본 포트폴리오는 **Python 표준 라이브러리 `math` 모듈만을 사용하여 제로 외부 의존성(Zero External Dependency)**으로 완전 무결한 쿼터니언 변환 모듈을 직접 구현했습니다.

```python
def euler_to_quaternion(roll: float, pitch: float, yaw: float) -> tuple[float, float, float, float]:
    """Convert Euler angles (roll, pitch, yaw in radians) to a Hamilton unit quaternion."""
    # 방어적 타입 및 유효성 검사
    for name, val in [('roll', roll), ('pitch', pitch), ('yaw', yaw)]:
        if not isinstance(val, (int, float)):
            raise TypeError(f"Angle {name} must be a float or int, got {type(val).__name__}")
        if math.isnan(val) or math.isinf(val):
            raise ValueError(f"Angle {name} must be a finite number, got {val}")

    half_r = roll * 0.5
    half_p = pitch * 0.5
    half_y = yaw * 0.5

    cr = math.cos(half_r)
    sr = math.sin(half_r)
    cp = math.cos(half_p)
    sp = math.sin(half_p)
    cy = math.cos(half_y)
    sy = math.sin(half_y)

    qx = sr * cp * cy - cr * sp * sy
    qy = cr * sp * cy + sr * cp * sy
    qz = cr * cp * sy - sr * sp * cy
    qw = cr * cp * cy + sr * sp * sy

    # 수치 안정성을 위한 단위 정규화
    norm = math.sqrt(qx * qx + qy * qy + qz * qz + qw * qw)
    if norm > 1e-12:
        qx /= norm
        qy /= norm
        qz /= norm
        qw /= norm

    return (qx, qy, qz, qw)
```

#### 단위 검증 결과 (`quaternion_utils.py`)
- **실행 명령**:
  ```bash
  python3 /home/cjinw/learning/portfolio/src/tf2_transforms_py/tf2_transforms_py/quaternion_utils.py
  ```
- **실제 검증 출력**:
  ```text
  [QUATERNION_TEST] 1. Identity rotation (0, 0, 0) -> (0.0, 0.0, 0.0, 1.0): PASS
  [QUATERNION_TEST] 2. Yaw +90 deg (0, 0, pi/2) -> (0.0, 0.0, 0.7071, 0.7071): PASS
  [QUATERNION_TEST] 3. Pitch +90 deg (0, pi/2, 0) -> (0.0, 0.7071, 0.0, 0.7071): PASS
  [QUATERNION_TEST] 4. Roll +90 deg (pi/2, 0, 0) -> (0.7071, 0.0, 0.0, 0.7071): PASS
  [QUATERNION_TEST] 5. Yaw 180 deg (0, 0, pi) -> (0.0, 0.0, 1.0, 0.0): PASS
  [QUATERNION_TEST] 6. Defensive validation check (TypeError, NaN): PASS
  [QUATERNION_TEST] All 6 quaternion self-tests passed successfully!
  ```

---

## 3. 정적 및 동적 브로드캐스터 구현

### 3.1 정적 브로드캐스터 (`static_frame_broadcaster.py`)
- **역할**: 로봇 섀시에 장착된 센서(LiDAR, 카메라)의 고정 상대 위치를 `/tf_static` 토픽으로 1회 브로드캐스트합니다.
- **파라미터 지원**: 단일 노드 소스코드로 여러 센서를 유연하게 기동할 수 있도록 ROS 파라미터를 지원합니다.
  - `parent_frame`: 부모 좌표계 이름 (기본값: `'base_link'`)
  - `child_frame`: 자식 좌표계 이름 (기본값: `'laser_frame'`)
  - `x`, `y`, `z`: 위치 오프셋(m)
  - `roll`, `pitch`, `yaw`: 회전 각도(rad)
- **방어적 유효성 검사**: 동일한 프레임 이름 지정 시 발생하는 순환 사이클($A \to A$)을 사전에 차단합니다:
  ```python
  if not parent_frame or not child_frame:
      raise ValueError("Frame names cannot be empty")
  if parent_frame == child_frame:
      raise ValueError(f"Parent and child frames cannot be identical: {parent_frame}")
  ```
- **핵심 API**: `tf2_ros.StaticTransformBroadcaster(self)` 및 `sendTransform(transform_stamped)`

---

### 3.2 동적 브로드캐스터 (`dynamic_frame_broadcaster.py`)
- **역할**: 로봇이 반경 $R=1.0\text{ m}$의 원 궤적을 각속도 $\omega = 0.3\text{ rad/s}$로 주행하는 오도메트리(`odom` $\to$ `base_link`) 좌표 변환을 10Hz 주기로 `/tf`에 브로드캐스트합니다.
- **원형 궤적 운동학 (Planar Kinematics)**:
  $$\begin{aligned}
  x(t) &= R \cdot \cos(\omega \cdot t) \\
  y(t) &= R \cdot \sin(\omega \cdot t) \\
  z(t) &= 0.0 \\
  \text{yaw}(t) &= \omega \cdot t + \frac{\pi}{2} \quad (\text{궤적의 접선 방향을 향함})
  \end{aligned}$$
- **헤더 타임스탬프**: 반드시 현재 노드 시계인 `self.get_clock().now().to_msg()`를 사용하여 변환 버퍼에 기록합니다.

---

## 4. 좌표 변환 리스너 및 3D 포인트 변환 (`point_transformer_listener.py`)

### 4.1 리스너 아키텍처
리스너 노드는 백그라운드에서 `/tf` 및 `/tf_static` 토픽을 구독하여 내부 링 버퍼에 좌표 변환 이력을 캐싱합니다.
1. `tf2_ros.Buffer(cache_time=Duration(seconds=10.0))`: 좌표 변환 저장 버퍼
2. `tf2_ros.TransformListener(self.tf_buffer, self)`: DDS 토픽으로부터 변환 메시지를 수신하여 버퍼에 자동 기록

---

### 4.2 LiDAR 관측 포인트 변환 (`do_transform_point`)
- **시나리오**: LiDAR 센서(`laser_frame`)가 센서 정면 1.0m 거리에서 장애물 $(x=1.0, y=0.0, z=0.0)$을 탐지함.
- **변환 파이프라인**:
  ```python
  # 1. 원본 포인트 생성 (laser_frame 기준)
  point_in = PointStamped()
  point_in.header.frame_id = 'laser_frame'
  point_in.header.stamp = self.get_clock().now().to_msg()
  point_in.point.x = 1.0
  point_in.point.y = 0.0
  point_in.point.z = 0.0

  # 2. laser_frame -> odom 변환 조회
  transform = self.tf_buffer.lookup_transform(
      'odom',         # target_frame (변환되어 도달할 대상 좌표계)
      'laser_frame',   # source_frame (포인트가 정의된 원본 좌표계)
      Time()          # 최신 가용 시점 (Time(seconds=0))
  )

  # 3. 3D 포인트 변환 수행
  point_out = tf2_geometry_msgs.do_transform_point(point_in, transform)
  ```
- **실제 변환 검증 결과**:
  ```text
  [point_transformer_listener] Transformed: [laser_frame] (1.000, 0.000, 0.000) -> [odom] (0.644, 1.423, 0.150)
  [point_transformer_listener] Transformed: [laser_frame] (1.000, 0.000, 0.000) -> [odom] (0.194, 1.550, 0.150)
  [point_transformer_listener] Transformed: [laser_frame] (1.000, 0.000, 0.000) -> [odom] (-0.273, 1.538, 0.150)
  [point_transformer_listener] Transformed: [laser_frame] (1.000, 0.000, 0.000) -> [odom] (-0.715, 1.389, 0.150)
  ```
  - **$z$ 좌표 불변성**: 센서 오프셋 $z=0.15\text{ m}$가 정확히 반영되어 모든 시점에서 $z=0.150$을 완벽하게 유지합니다.
  - **$x, y$ 궤적 추적**: 로봇이 원 궤적을 회전 주행함에 따라 장애물의 전역 `odom` 좌표가 연속적이고 매끄럽게 갱신됩니다.

---

## 5. TF2 3대 예외 원인과 결정론적 진단 (`tf_lookup_diagnostics.py`)

TF2 변환 조회(`lookup_transform`) 시 발생할 수 있는 핵심 예외 3가지를 명확히 이해하고 예외 처리하는 것은 로봇 소프트웨어의 안정성에 결정적입니다.

| 예외 클래스 | 발생 원인 | 재현 방법 |
| :--- | :--- | :--- |
| **`LookupException`** | 요청된 `target_frame` 또는 `source_frame` 중 하나 이상이 버퍼에 전혀 존재하지 않음 | 빈 버퍼에서 존재하지 않는 프레임 `'odom'` 조회 |
| **`ConnectivityException`** | 두 프레임이 각각 버퍼에 존재하지만 공통 부모가 없어 트리가 연결되지 않음 | 서로 다른 두 독립 트리(`world_a -> robot_a`, `world_b -> robot_b`) 간 조회 |
| **`ExtrapolationException`** | 두 프레임이 연결되어 있으나, 요청한 시각($t$)이 버퍼에 저장된 시간 범위를 벗어남 | $t=100.0\text{s}$ 변환만 버퍼에 넣은 후 $t=110.0\text{s}$ 시각으로 조회 |

### 결정론적 진단 실행 결과
`tf_lookup_diagnostics.py`는 네트워크 타이밍이나 통신 지연에 영향받지 않도록 `tf2_ros.Buffer`의 `set_transform` 및 `set_transform_static` API를 사용하여 메모리 상에서 세 가지 예외를 100% 결정론적으로 재현하고 검증합니다.

- **실행 명령**:
  ```bash
  ros2 run tf2_transforms_py tf_lookup_diagnostics
  ```
- **실제 검증 출력**:
  ```text
  [INFO] [tf_lookup_diagnostics]: TfLookupDiagnostics initializing diagnostic test suite...
  [INFO] [tf_lookup_diagnostics]: [DIAGNOSTIC PASS] 1. LookupException correctly caught: "odom" passed to lookupTransform argument target_frame does not exist. 
  [INFO] [tf_lookup_diagnostics]: [DIAGNOSTIC PASS] 2. ConnectivityException correctly caught: Could not find a connection between 'robot_a' and 'robot_b' because they are not part of the same tree.Tf has two or more unconnected trees.
  [INFO] [tf_lookup_diagnostics]: [DIAGNOSTIC PASS] 3. ExtrapolationException correctly caught: Lookup would require extrapolation at time 110.000000, but only time 100.000000 is in the buffer, when looking up transform from frame [base_link] to frame [odom]
  [INFO] [tf_lookup_diagnostics]: All 3 TF2 exceptions (Lookup, Connectivity, Extrapolation) verified successfully!
  ```

---

## 6. API vs CLI 변환 방향 매핑 가이드

ROS 2 초심자가 가장 많이 겪는 혼선은 Python API의 `lookup_transform` 인자 순서와 CLI 도구인 `tf2_echo`의 인자 순서 차이입니다.

### 6.1 인자 의미 비교표
| 구분 | Python API: `lookup_transform(A, B, time)` | CLI 도구: `ros2 run tf2_ros tf2_echo A B` |
| :--- | :--- | :--- |
| **첫 번째 인자 ($A$)** | `target_frame` (도달하고자 하는 목표 프레임) | `source_frame` / `reference_frame` (기준이 되는 부모 좌표계) |
| **두 번째 인자 ($B$)** | `source_frame` (데이터가 측정된 원본 프레임) | `target_frame` (측정하고자 하는 대상/자식 좌표계) |
| **수학적 의미** | $P^A = T_{A \leftarrow B} \cdot P^B$ 변환 행렬 조회 | 좌표계 $A$의 관점에서 바라본 좌표계 $B$의 위치와 자세 |
| **예시 호출** | `lookup_transform('odom', 'laser_frame', Time())` | `ros2 run tf2_ros tf2_echo odom laser_frame` |
| **물리적 결과** | `laser_frame`의 포인트를 `odom` 좌표로 변환 | `odom` 원점에서 `laser_frame`까지의 오프셋 및 회전량 출력 |

> [!IMPORTANT]
> - `base_link` 기준 `laser_frame`의 장착 위치($x=0.20, z=0.15$)를 확인하려면:
>   `ros2 run tf2_ros tf2_echo base_link laser_frame`을 실행합니다.
> - 이 때 출력되는 `Translation: [0.200, 0.000, 0.150]`은 `base_link`를 원점으로 했을 때 `laser_frame`의 위치를 나타냅니다.

---

## 7. 통합 시스템 기동 및 CLI 도구 검증

### 7.1 통합 브링업 (`01_tf2_demo.launch.py`)
통합 Launch 파일은 다음 4개의 노드를 유기적으로 기동합니다:
1. `static_laser_broadcaster`: `base_link` $\to$ `laser_frame` ($x=0.20, z=0.15$)
2. `static_camera_broadcaster`: `base_link` $\to$ `camera_link` ($x=0.10, z=0.25$)
3. `dynamic_frame_broadcaster`: `odom` $\to$ `base_link` ($10\text{Hz}$, 원형 궤적)
4. `point_transformer_listener`: $1\text{Hz}$ 주기로 LiDAR 포인트 변환

- **실행 명령**:
  ```bash
  ros2 launch tf2_transforms_py tf2_demo.launch.py
  ```

---

### 7.2 `tf2_echo` 실행 결과 검증

#### 1) 정적 변환 확인 (`base_link` $\to$ `laser_frame`)
- **실행 명령**:
  ```bash
  ros2 run tf2_ros tf2_echo base_link laser_frame
  ```
- **실제 검증 출력**:
  ```text
  At time 0.0
  - Translation: [0.200, 0.000, 0.150]
  - Rotation: in Quaternion (xyzw) [0.000, 0.000, 0.000, 1.000]
  - Rotation: in RPY (radian) [0.000, -0.000, 0.000]
  - Rotation: in RPY (degree) [0.000, -0.000, 0.000]
  - Matrix:
    1.000  0.000  0.000  0.200
    0.000  1.000  0.000  0.000
    0.000  0.000  1.000  0.150
    0.000  0.000  0.000  1.000
  ```

#### 2) 동적 오도메트리 확인 (`odom` $\to$ `base_link`)
- **실행 명령**:
  ```bash
  ros2 run tf2_ros tf2_echo odom base_link
  ```
- **실제 검증 출력**:
  ```text
  At time 1791727214.763611414
  - Translation: [-0.079, 0.997, 0.000]
  - Rotation: in Quaternion (xyzw) [0.000, 0.000, 0.999, -0.040]
  - Rotation: in RPY (radian) [0.000, -0.000, -3.062]
  - Rotation: in RPY (degree) [0.000, -0.000, -175.456]
  - Matrix:
   -0.997  0.079  0.000 -0.079
   -0.079 -0.997  0.000  0.997
    0.000  0.000  1.000  0.000
    0.000  0.000  0.000  1.000
  ```

---

### 7.3 `view_frames` 기반 TF 트리 검증
- **실행 명령**:
  ```bash
  ros2 run tf2_tools view_frames
  ```
- **실제 생성된 Frame Graph 응답 메타데이터**:
  ```yaml
  camera_link: 
    parent: 'base_link'
    broadcaster: 'default_authority'
    rate: 10000.000 (static latch)
    buffer_length: 0.000
  base_link: 
    parent: 'odom'
    broadcaster: 'default_authority'
    rate: 10.200 (dynamic streaming)
    buffer_length: 5.000
  laser_frame: 
    parent: 'base_link'
    broadcaster: 'default_authority'
    rate: 10000.000 (static latch)
    buffer_length: 0.000
  ```
- **트리 시각화 구조**:
  ```text
  [odom]
     │ (dynamic @ 10.2 Hz)
     ▼
  [base_link]
     ├─── (static) ───► [laser_frame]
     │
     └─── (static) ───► [camera_link]
  ```

---

## 8. 최종 종합 검증 매트릭스

| 검증 항목 | 대상 파일 / 명령 | 검증 기준 | 결과 |
| :--- | :--- | :--- | :--- |
| **정적 구문 검사** | `python3 -m py_compile` (전체 5개 Python 파일) | 컴파일 에러 0건 | **PASS** |
| **코드 스타일 감사** | `ament_flake8` (99자 제한) | 스타일 위반 0건 | **PASS** |
| **워크스페이스 빌드** | `colcon build --packages-select tf2_transforms_py` | 빌드 성공 및 4개 실행 파일 설치 | **PASS** |
| **수학 단위 검증** | `quaternion_utils.py` (6개 셀프 테스트) | 단위 쿼터니언 정규화 및 회전축 일치 | **PASS** |
| **예외 진단 노드** | `ros2 run tf2_transforms_py tf_lookup_diagnostics` | 3대 예외 정상 포착 및 종료 코드 0 | **PASS** |
| **정적 브로드캐스터** | `tf2_echo base_link laser_frame` | Translation $[0.20, 0.0, 0.15]$ 확인 | **PASS** |
| **동적 브로드캐스터** | `tf2_echo odom base_link` | 10Hz 원형 궤적 좌표 변환 스트리밍 | **PASS** |
| **포인트 리스너** | `laser_frame` $\to$ `odom` 3D 변환 | 높이 $z=0.15$ 불변 및 동적 $x, y$ 갱신 | **PASS** |
| **TF 트리 구조** | `ros2 run tf2_tools view_frames` | `odom` $\to$ `base_link` $\to$ 센서 단일 부모 트리 | **PASS** |
| **프로세스 잔여 확인** | `ps aux \| grep -E "tf2\|ros2"` | 잔류 프로세스 0건 (`NO_PROCESSES`) | **PASS** |
| **작업 경계 보존** | Phase 1~4, 외부 저장소, `.bashrc`, 비-Git 상태 | 수정 내역 0건 | **PASS** |
