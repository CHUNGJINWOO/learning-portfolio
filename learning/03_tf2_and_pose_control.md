# 🧭 TF2 좌표 변환 및 목표 자세 제어 (TF2 & Pose Control)

> 📖 **교재 참고**: `[WeGo] Limo_ROS2_교재.pdf` (제7장 ROS 2 TF2, pp. 260~318)<br>
> 💻 **코드 출처**: 교재 수록 예제 코드 (`limo_ros2_application` 패키지)<br>
> 🏷️ **실습 상태**: `[개념 학습 완료]`, `[시뮬레이터 개념 검증 완료]`, `[교재 코드 분석 완료]`, `[로컬 소스 미구현 (교재 분석 완료)]`, `[미검증 (실제 하드웨어 미주행)]`

---

## 1. 개요 및 학습 목표

로봇 공학에서 센서 데이터(카메라, LiDAR 등)는 로봇의 특정 부착 위치를 기준으로 측정되며, 액추에이터는 차체 중심을 기준으로 제어되고, 주행 목표는 전체 맵(또는 시작 위치)을 기준으로 정의됩니다. 이처럼 서로 다른 기준 좌표계들을 실시간으로 일치시키고 상호 변환을 관리하는 핵심 프레임워크가 바로 **TF2 (Transform Library 2)**입니다.

본 문서에서는 TF2의 수학적 배경(동차 변환 행렬, 쿼터니언), 브로드캐스터와 리스너의 동작 메커니즘, AgileX LIMO의 표준 TF 트리 및 URDF/Xacro 구조, 그리고 TF2 리스너를 기반으로 목표 좌표를 추종하는 극좌표 피드백 제어기(`move_to_pose.py`)를 정리합니다.

---

## 2. 좌표 변환 이론과 TF2 기초

> 📖 **교재 참고**: 제7장 7.1절~7.2절 (pp. 262~295)<br>
> 🏷️ **상태**: `[개념 학습 완료]`, `[시뮬레이터 개념 검증 완료]`

### 2.1. 동차 변환 행렬 (Homogeneous Transformation Matrix)
평행 이동($x, y, z$)과 회전(Rotation)을 $4 \times 4$ 단일 행렬 곱으로 통합하여 표현합니다:

$$T = \begin{bmatrix} R_{3 \times 3} & \mathbf{t}_{3 \times 1} \\ \mathbf{0}_{1 \times 3} & 1 \end{bmatrix}$$

- **회전 표현**: 오일러 각(Roll, Pitch, Yaw)은 짐벌 락(Gimbal Lock) 문제가 발생하므로, ROS 2 내부적으로는 4개의 실수 성분을 갖는 **사원수(Quaternion, $x, y, z, w$)**를 사용하여 3차원 회전을 특이점 없이 표현합니다.

### 2.2. Transform Broadcaster & Listener
- **Broadcaster**: 특정 프레임 간의 상대적 위치 및 회전 관계($T_{parent \to child}$)를 주기적으로 `/tf` 또는 `/tf_static` 토픽에 전송합니다.
  - `TransformBroadcaster`: 시간에 따라 동적으로 변하는 변환 (`odom \to base_link` 등).
  - `StaticTransformPublisher`: 로봇 구조상 고정된 변환 (`base_link \to laser_link` 등).
- **Listener**: 수신된 변환 정보들을 시간 축 버퍼(`tf2_ros.Buffer`)에 캐싱해두고, 사용자가 원하는 두 프레임 간의 최신 변환을 역방향 추적 및 합성하여 계산합니다.

### 2.3. Turtlesim TF 예제 구조
교재 7.2절(pp. 270~294)에서는 다음과 같은 트리 구조를 통해 TF 합성의 원리를 검증합니다:
- `world` (월드 절대 좌표계)
  - $\rightarrow$ `turtle1` (1번 거북이) $\rightarrow$ `carrot` (1번 거북이의 상대적 오프셋 가상 프레임)
  - $\rightarrow$ `turtle2` (2번 거북이: `turtle2` 기준에서 `carrot` 프레임을 `lookup_transform`하여 추종)

---

## 3. LIMO TF 트리 및 URDF/Xacro

> 📖 **교재 참고**: 제7장 7.3절 (pp. 295~305)<br>
> 🏷️ **상태**: `[개념 학습 완료]`, `[교재 코드 분석 완료]`, `[미검증 (실제 하드웨어)]`

### 3.1. LIMO의 표준 TF 트리 계층 (교재 p. 295 그림 7-25 기준)
교재 분석에 따른 AgileX LIMO의 기본 좌표 프레임 트리는 다음과 같이 구성됩니다:

```text
odom (주행 기록 고정 프레임)
 └── base_link (로봇 제자리 회전 중심점)
      ├── inertial_link (질량 및 관성 모멘트 중심)
      ├── laser_link (LiDAR 광학 중심점)
      ├── imu_link (IMU 센서 중심점)
      ├── front_left / rear_right_wheel_link 등 (바퀴 링크)
      └── camera_mount ~ camera_link (카메라 센서 링크군)
```

- **`odom`**: 시작 지점을 기준으로 한 상대 위치. 휠 엔코더와 IMU 데이터를 융합한 EKF 노드(`robot_localization`, 교재 p. 297)에 의해 `odom \to base_link` 변환이 동적으로 발행됩니다.
- **`base_link`**: 차체 회전의 중심축.
- 💡 **보충 설명 (`base_footprint`)**: 일반적인 ROS 모바일 로봇(REP-105 표준)에서는 지면 투영 기준면으로 `odom \to base_footprint \to base_link` 계층을 널리 사용하지만, 교재 7.3.1절의 LIMO 기본 패키지 구성에서는 `odom \to base_link`가 직접 연결된 트리를 사용합니다.

### 3.2. 링크(Link)와 조인트(Joint), URDF와 Xacro
- **Link**: 센서, 바퀴, 차체 등 물리적인 강체(Rigid Body)의 질량, 형상(Collision/Visual)을 정의.
- **Joint**: 두 링크 간의 연결 관계와 자유도(Fixed, Continuous, Revolute)를 정의.
- **URDF & Xacro**: XML 기반 로봇 기술 포맷. Xacro는 매크로 및 변수를 지원하여 복잡한 URDF를 간결하게 모듈화합니다.
- **`robot_state_publisher`**: 로봇의 조인트 상태(`joint_states`)와 URDF 모델을 결합하여 로봇의 모든 부품 간 정적/동적 TF 변환을 자동 브로드캐스팅합니다.

### 3.3. 카메라 마운트 틸트(Camera Tilt)와 각도 단위 변환
- 교재 7.3.3절(pp. 301~303)에 따르면, LIMO는 바닥면 차선을 보기 위해 카메라가 아래로 기울어져 마운트됩니다.
- `camera_tilt_launch.py`는 사용자로부터 도(Degree, 예: 15도) 단위 인자를 입력받지만, ROS 2 내부 static transform은 **라디안(Radian)** 단위로 변환($\text{rad} = \text{deg} \times \frac{\pi}{180}$)되어 적용되어야 올바른 좌표 투영이 이루어집니다.

---

## 4. 목표 자세 추종 제어기 (`move_to_pose.py`)

> 📖 **교재 참고**: 제7장 7.4절 (pp. 306~318)<br>
> 🏷️ **상태**: `[개념 학습 완료]`, `[교재 코드 분석 완료]`, `[미검증 (실제 하드웨어)]`

### 4.1. 시스템 구성 및 TF 관계
1. `static_transform_publisher`가 `odom` 프레임 기준으로 목표 지점(`goal_pose`, 예: $x=1.0, y=1.0, \text{yaw}=3.14$)을 정적 브로드캐스팅합니다 (`move_to_pose_launch.py`).
2. 제어 노드 `move_to_pose`는 `base_link` 프레임을 기준으로 `goal_pose`의 실시간 상대 위치를 리스닝합니다:
   ```python
   t_ = self.tf_buffer.lookup_transform(
       'base_link', 'goal_pose', rclpy.time.Time(),
       timeout=rclpy.duration.Duration(seconds=0.1)
   )
   ```
3. **핵심 원리**: 비록 `goal_pose`가 `odom` 기준으로는 고정되어 있을지라도, 로봇이 전진하고 회전함에 따라 `base_link` 기준에서의 상대 좌표($\Delta x, \Delta y, \Delta\theta$)는 계속해서 변하므로, 별도의 복잡한 전역 경로 계산 없이도 순수 상대 좌표만으로 목표 수렴 제어가 가능합니다.

### 4.2. 극좌표계 제어 변수 도출
상대 평행이동 $\Delta x, \Delta y$와 회전 오차 $\Delta\psi$로부터 다음 3가지 극좌표 변수를 유도합니다:

$$\rho = \sqrt{\Delta x^2 + \Delta y^2} \quad (\text{목표까지의 유클리드 거리})$$
$$\alpha = \text{normalize\_angle}(\text{atan2}(\Delta y, \Delta x)) \quad (\text{목표 지점을 바라보는 지향각 오차})$$
$$\beta = \text{normalize\_angle}(\Delta\psi - \alpha) \quad (\text{목표 방향과 지향각 간의 자세 오차})$$

### 4.3. 3계수 비례 제어 법칙과 후진 주행 처리
1. **선속도 제어**:
   $$v = K_\rho \cdot \rho$$
2. **각속도 제어**:
   - 목표 거리 도달 전 ($\rho > \text{xy\_tolerance}$):
     $$\omega = K_\alpha \cdot \alpha - K_\beta \cdot \beta$$
   - 목표 거리 도달 후 ($\rho \le \text{xy\_tolerance}$): 자세만 정렬
     $$\omega = K_\beta \cdot \text{normalize\_angle}(\Delta\psi)$$
3. **후진 주행 판정 (Reverse Driving)**:
   - 만약 목표 지점이 로봇의 뒤쪽에 위치하여 $|\alpha| > \frac{\pi}{2}$ 인 경우:
     $$v = -v$$
   - 불필요하게 180도 회전하지 않고 후진 주행을 선택하여 이동 효율을 극대화합니다.
4. **포화(Saturation) 제한 및 시각화**:
   - $v \in [-v_{max}, v_{max}]$, $\omega \in [-\omega_{max}, \omega_{max}]$
   - 제어 주기마다 `/cmd_vel`(`Twist`)을 발행하며, `/odometry/filtered`를 수신하여 이동 경로를 `/traj`(`nav_msgs/msg/Path`) 토픽으로 RViz에 시각화합니다.

---

## 5. 학습 검증 및 미확인 사항

| 항목 | 검증 상태 | 상세 설명 |
| :--- | :---: | :--- |
| **TF2 기본 변환 & Turtlesim** | `[시뮬레이터 개념 검증 완료]` | 2D/3D 변환 수학, 쿼터니언, Broadcaster/Listener, Carrot 추종 구조 확인. |
| **LIMO TF 트리 & URDF** | `[교재 코드 분석 완료]` | 교재 7.3절 분석 기반 프레임 계층, Xacro 매크로, 카메라 틸트 라디안 변환 확인. |
| **`move_to_pose.py`** | `[교재 코드 분석 완료]` | 상대 변환 조회, 극좌표 ($\rho, \alpha, \beta$) 유도, 비례 제어 및 후진 로직 분석 완료. |
| **실물 하드웨어 주행 실측** | `[미검증 (하드웨어)]` | 실제 LIMO 로봇에 `move_to_pose_launch.py`를 적용하여 1m 이동 및 RViz 궤적 실측은 미수행. |
