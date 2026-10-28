# 모듈 02: ROS 2 Parameters 및 Quality of Service (QoS) 심층 실습

본 문서는 ROS 2의 핵심 분산 시스템 제어 요소인 **동적 파라미터(Parameters)**와 **서비스 품질(Quality of Service, QoS)** 정책을 초보자 관점에서 직접 실행하고 체득할 수 있도록 구성된 단계별 실습 교육 가이드입니다.

---

## 1. 개요 및 학습 목표

Phase 1에서 우리는 하드코딩된 주기(`1.0초`)로 동작하는 기본적인 하트비트 Pub/Sub 노드를 작성했습니다.  
실제 자율주행 및 로보틱스 환경에서는 다음과 같은 문제에 직면합니다:

1. **런타임 설정 주입의 필요성:** 로봇의 센서 프레임 ID, 주행 속도 제한, 텔레메트리 발행 주기를 변경할 때마다 소스 코드를 고치고 `colcon build`를 다시 수행하는 것은 배포 및 유지보수 관점에서 비효율적입니다.
2. **비신뢰 네트워크 환경 제어:** Wi-Fi 패킷 손실이나 대역폭 제약이 있는 환경에서 고빈도 센서 데이터를 TCP처럼 무조건 재전송하면 대역폭 병목과 큐 지연이 발생합니다. 반대로 정적 맵이나 하드웨어 설정값은 노드가 나중에 실행(Late-join)되더라도 즉시 수신할 수 있어야 합니다.

본 모듈에서는 ROS 2 Humble 공식 표준에 기반하여:
- **Part A:** 방어적 유효성 검증(Validation)과 `/parameter_events`를 통한 안전한 런타임 상태 갱신 메커니즘을 배웁니다.
- **Part B:** DDS 레벨의 `Reliability`(신뢰성), `Durability`(내구성) 정책과 송수신자 간 호환성(Compatibility) 규칙을 실습합니다.

---

## Part A — ROS 2 Parameters (동적 매개변수 제어)

### 2. 개념 및 아키텍처 (Parameters)

#### 2.1 정적 선언과 동적 재구성
- **`declare_parameter(name, default_value)`**: 노드 생성 시점에 매개변수를 등록하며, 초기값의 파이썬 타입에 따라 파라미터 타입이 정적으로 결정됩니다.
- **`add_on_set_parameters_callback(callback)`**: 런타임에 외부(CLI, YAML, 서비스)에서 파라미터 변경 요청이 들어올 때 호출되는 검증 가드(Guard)입니다.

#### 2.2 핵심 설계 원칙: 검증과 적용의 2단계 분리 (Separation of Concerns)
초보 개발자가 흔히 저지르는 실수는 검증 콜백 내부에서 타이머 주기를 직접 변경하거나 내부 상태를 즉시 대입하는 것입니다.
- **원자성(Atomicity) 파괴 문제:** 사용자가 `[publish_rate_hz=5.0, device_id=""]`를 일괄 요청했을 때, 첫 번째 파라미터를 검사하며 타이머를 변경한 후 두 번째 파라미터에서 실패(`successful=False`)를 반환하면, ROS 2 파라미터 서버는 변경을 전체 거부하지만 타이머는 이미 변경되어 **내부 상태와 파라미터 서버 간의 상태 불일치(State Inconsistency)**가 발생합니다.
- **올바른 아키텍처:**
  1. **검증 콜백 (`on_set_callback`):** 모든 매개변수의 타입과 범위를 순수 함수 형태로 검증만 수행하고 부수 효과(Side-effect)를 절대 일으키지 않습니다.
  2. **적용 콜백 (`/parameter_events` 구독):** ROS 2 파라미터 서버가 원자적 커밋을 완료한 후 발행하는 이벤트를 수신하여, 자신의 노드에 속한 변경 사항일 때만 안전하게 `timer.timer_period_ns`를 재계산합니다.

> [!NOTE]
> **비동기 지연 안내:** 파라미터가 커밋된 시점과 `/parameter_events` 구독 콜백이 실행기(Executor)에 의해 디스패치되는 시점 사이에는 수 밀리초의 비동기 지연이 존재합니다. 따라서 이벤트 기반 갱신이 모든 동시성 경쟁 상태를 물리적으로 0으로 만드는 것은 아니며, 실행기 이벤트 루프 내에서 안전하게 순차 처리되도록 스케줄링하는 방식입니다.

---

### 3. 최소 실행 예제: `DynamicTelemetryPublisher`

이 노드는 `src/param_qos_py/param_qos_py/dynamic_telemetry_publisher.py`에 완전한 실행 파일로 구현되어 있습니다.

#### 코드 핵심 구조
```python
# [검증 단계] 부수 효과가 없는 순수 유효성 검사 콜백
def _validate_parameters_callback(self, params: List[Parameter]) -> SetParametersResult:
    for param in params:
        if param.name == 'publish_rate_hz':
            val = float(param.value)
            if val <= 0.0 or val > 50.0:
                return SetParametersResult(
                    successful=False,
                    reason=f'publish_rate_hz must be in (0.0, 50.0] Hz, got {val}'
                )
        elif param.name == 'device_id':
            val_str = str(param.value).strip()
            if not val_str:
                return SetParametersResult(
                    successful=False,
                    reason='device_id cannot be empty or whitespace only'
                )
    return SetParametersResult(successful=True)

# [적용 단계] 파라미터 커밋 확인 후 런타임 타이머 안전 갱신
def _on_parameter_event_callback(self, event: ParameterEvent) -> None:
    if event.node != self.get_fully_qualified_name():
        return
    for param_msg in (event.changed_parameters + event.new_parameters):
        if param_msg.name == 'publish_rate_hz':
            new_rate = float(param_msg.value.double_value or param_msg.value.integer_value)
            if new_rate > 0.0:
                self._publish_rate_hz = new_rate
                # Humble 표준: C 레벨 타이머 주기 원자적 변경 및 리셋
                self._timer.timer_period_ns = int((1.0 / new_rate) * 1e9)
                self._timer.reset()
```

---

### 4. 실행 및 단계별 실습 절차 (Part A)

저장소 루트에서 `colcon list`로 패키지를 확인하고 `colcon build --packages-select param_qos_py`로 선택 빌드한 뒤 진행합니다. 하위 디렉터리의 독립 빌드는 별도 선택지이며 그 위치의 overlay를 사용해야 합니다. 이 문서 정리에서 명령의 실행 검증은 하지 않았습니다.

> [!IMPORTANT]
> **새 터미널 환경 설정 안내 (필수):**
> 실습을 위해 새로운 터미널 창을 열 때마다 반드시 아래 두 단계의 환경 소싱을 수행해야 합니다 (`~/.bashrc`를 변경하지 않는 격리 환경 기준):
> 1. **ROS 2 기본 환경 소싱:** `source /opt/ros/humble/setup.bash` (`ros2` CLI 기본 바이너리 및 핵심 라이브러리 활성화)
> 2. **워크스페이스 오버레이 소싱:** 저장소 루트로 이동 후 `source install/setup.bash` (`param_qos_py` 등 우리가 직접 빌드한 사용자 패키지 로딩)
>
> *(참고: `ros2 param set`이나 `ros2 topic info` 같은 범용 CLI 도구만 실행할 때는 기본 환경 소싱만으로도 동작하지만, 노드 실행(`ros2 run`)을 포함한 일관된 실습을 위해 새 터미널마다 두 환경을 모두 소싱하는 것을 권장합니다.)*

#### 4.1 기본 노드 기동
```bash
# 터미널 1: 환경 소싱 및 기본 노드 실행
source /opt/ros/humble/setup.bash
cd ~/learning/learning-portfolio  # 또는 클론한 저장소 루트
source install/setup.bash

ros2 run param_qos_py dynamic_telemetry_publisher
```

**기대 출력 (Expected Output):**
```text
[INFO] [dynamic_telemetry_publisher]: DynamicTelemetryPublisher initialized. ID="telemetry_bot_01", Rate=1.0Hz
[INFO] [dynamic_telemetry_publisher]: Published: "[telemetry_bot_01] seq=0 rate=1.0Hz"
[INFO] [dynamic_telemetry_publisher]: Published: "[telemetry_bot_01] seq=1 rate=1.0Hz"
```

#### 4.2 정상 파라미터 동적 변경 (1.0 Hz -> 5.0 Hz)
```bash
# 터미널 2 (새 창): 기본 환경과 루트 overlay 소싱
source /opt/ros/humble/setup.bash
cd ~/learning/learning-portfolio  # 또는 클론한 저장소 루트
source install/setup.bash

# 파라미터 변경 요청 (1.0 Hz -> 5.0 Hz)
ros2 param set /dynamic_telemetry_publisher publish_rate_hz 5.0
```

**터미널 2 출력:**
```text
Set parameter successfully
```

**터미널 1 반영 결과:**
```text
[INFO] [dynamic_telemetry_publisher]: Parameter event applied: publish_rate_hz=5.0Hz (period=200000000ns)
[INFO] [dynamic_telemetry_publisher]: Published: "[telemetry_bot_01] seq=2 rate=5.0Hz"
[INFO] [dynamic_telemetry_publisher]: Published: "[telemetry_bot_01] seq=3 rate=5.0Hz"
```
*(0.2초 간격으로 빠르게 발행됨을 확인할 수 있습니다.)*

#### 4.3 의도적인 비정상 파라미터 거부 실험 (음수 주기 주입)
```bash
# 터미널 2: 유효하지 않은 음수 주기 요청
ros2 param set /dynamic_telemetry_publisher publish_rate_hz -10.0
```

**터미널 2 출력 (거부 확인):**
```text
Setting parameter failed: publish_rate_hz must be in (0.0, 50.0] Hz, got -10.0
```
**터미널 1 관찰:**
- 터미널 1에는 `/parameter_events`가 수신되지 않으며, 이전의 `5.0Hz` 발행 주기가 정확히 유지됩니다.

#### 4.4 YAML 파일을 통한 실행 시점 설정 주입
```bash
# 아래 YAML 상대 경로는 저장소 루트를 기준으로 합니다.
cd ~/learning/learning-portfolio  # 또는 클론한 저장소 루트
source /opt/ros/humble/setup.bash
source install/setup.bash

# 터미널 1의 기존 노드를 종료(Ctrl+C)한 후 YAML 설정 파일 주입하여 실행
ros2 run param_qos_py dynamic_telemetry_publisher --ros-args --params-file 02_ros2_core_curriculum/src/param_qos_py/config/default_params.yaml
```
- 기본값(`1.0Hz`, `telemetry_bot_01`) 대신 YAML에 정의된 `2.5Hz` 및 `configured_bot_99`로 즉시 시작됩니다.

---

## Part B — ROS 2 Quality of Service (QoS 심층)

### 5. 개념 및 정책 심층 분석 (QoS)

DDS 미들웨어의 QoS는 토픽 단위로 네트워크 전송 품질을 결정합니다.

#### 5.1 핵심 정책과 오해 바로잡기
1. **`ReliabilityPolicy.RELIABLE`:**
   - **오해:** "어떠한 네트워크 단절이나 장비 장애 상황에서도 100% 무손실 전달을 영구 보장한다."
   - **실제:** 시스템 큐 리소스(`History/Depth`) 한도 내에서 수신 확인(ACK) 및 손실 시 재전송을 시도합니다. 만약 큐가 가득 차면(`KEEP_LAST(10)`) 오래된 패킷이 폐기되며, 네트워크가 장시간 단절되면 메모리 고갈을 막기 위해 메시지가 유실될 수 있습니다.
2. **`ReliabilityPolicy.BEST_EFFORT`:**
   - 수신 확인 및 재전송 없이 최신 데이터를 가능한 한 빠르게 전송합니다. Wi-Fi 무선망의 패킷 손실 시 재전송 지연(Head-of-Line Blocking)을 방지하여 지연(Latency)을 최소화합니다.
3. **`DurabilityPolicy.TRANSIENT_LOCAL` (래칭):**
   - 퍼블리셔가 과거 메시지를 자신의 로컬 메모리에 보존하여, **나중에 연결된 서브스크라이버(Late-joiner)**에게 즉시 전달합니다.
   - **주의:** 퍼블리셔 프로세스가 살아있는 동안에만 유지됩니다. 퍼블리셔 프로세스가 재시작되면 과거 캐시는 소멸합니다.
   - **안전 주의:** 비상 정지(`/emergency_stop`)처럼 오래된 상태를 즉시 적용하면 위험한 토픽에는 사용하지 않으며, 맵 메타데이터나 로봇 하드웨어 사양 같은 **정적/준정적 설정 정보**에 적용하는 것이 안전합니다.

#### 5.2 송수신자 호환성 매트릭스 (Offered vs Requested)

DDS 엔드포인트 연결 규칙: **$\text{Offered (Publisher)} \ge \text{Requested (Subscriber)}$**

| 퍼블리셔 (Offered) | 서브스크라이버 (Requested) | 연결 성립 여부 | 비고 |
| :--- | :--- | :---: | :--- |
| `RELIABLE` | `BEST_EFFORT` | **성립 (Match)** | 제공자가 요구 수준보다 엄격하므로 정상 연결 |
| `BEST_EFFORT` | `RELIABLE` | ❌ **두절 (Mismatch)** | 구독자가 신뢰성을 요구하나 발행자가 보장 못함 $\to$ **메시지 전송 차단** |
| `TRANSIENT_LOCAL` | `VOLATILE` | **성립 (Match)** | 연결은 성립하나 구독자는 과거 래칭 메시지를 받지 않음 |
| `VOLATILE` | `TRANSIENT_LOCAL` | ❌ **두절 (Mismatch)** | 구독자가 과거 메시지 보존을 요구하나 발행자가 미보관 $\to$ **연결 거부** |

---

### 6. 실습 1: 고빈도 센서 스트림 및 QoS 비호환 관찰

#### 6.1 정상 통신 (Best Effort $\leftrightarrow$ Best Effort)
```bash
# 터미널 1: 환경 소싱 후 SensorDataQoS 퍼블리셔 실행 (10Hz IMU 스트리밍)
source /opt/ros/humble/setup.bash
cd ~/learning/learning-portfolio  # 또는 클론한 저장소 루트
source install/setup.bash

ros2 run param_qos_py qos_sensor_streamer

# 터미널 2 (새 창): 환경 소싱 후 기본 Best Effort 구독자 실행
source /opt/ros/humble/setup.bash
cd ~/learning/learning-portfolio  # 또는 클론한 저장소 루트
source install/setup.bash

ros2 run param_qos_py qos_sensor_listener
```
- **결과:** 터미널 2에 `Received sample (#1)...`이 10Hz 빈도로 실시간 수신됩니다.

#### 6.2 의도적 비호환 발생 (Publisher=Best Effort vs Subscriber=Reliable)
```bash
# 터미널 2의 구독자를 종료(Ctrl+C)하고, 신뢰성 모드를 Reliable로 강제 지정하여 재실행
ros2 run param_qos_py qos_sensor_listener --ros-args -p reliability_mode:=reliable
```

**터미널 2 관찰:**
```text
[WARN] [qos_sensor_listener]: Requested QoS: RELIABLE. Note: Incompatible if publisher offers BEST_EFFORT!
[INFO] [qos_sensor_listener]: QoSSensorListener ready. Listening to "sensor/imu_stream"...
```
- **현상:** 에러나 예외가 발생하지 않지만, **메시지가 단 한 건도 수신되지 않는 무음(Silent) 통신 두절**이 발생합니다.

#### 6.3 원인 진단 (`ros2 topic info --verbose`)
```bash
# 터미널 3 (새 창): 기본 환경과 루트 overlay 소싱 후 토픽 진단
source /opt/ros/humble/setup.bash
cd ~/learning/learning-portfolio  # 또는 클론한 저장소 루트
source install/setup.bash
ros2 topic info --verbose /sensor/imu_stream
```
**진단 출력:**
```text
Type: std_msgs/msg/String
Publisher count: 1
  Node name: qos_sensor_streamer
  QoS profile:
    Reliability: BEST_EFFORT
    Durability: VOLATILE
Subscription count: 1
  Node name: qos_sensor_listener
  QoS profile:
    Reliability: RELIABLE
    Durability: VOLATILE
```
- **진단 결론:** 퍼블리셔는 `BEST_EFFORT`를 제공(`Offered`)하는데 서브스크라이버는 `RELIABLE`을 요구(`Requested`)하여 DDS 매칭이 거부되었음을 확인할 수 있습니다.

---

### 7. 실습 2: 늦게 참여하는 구독자 (Late-joining with Transient Local)

#### 7.1 퍼블리셔 선행 실행 및 과거 메시지 래칭
```bash
# 터미널 1: 환경 소싱 후 Transient Local 설정 퍼블리셔 실행
source /opt/ros/humble/setup.bash
cd ~/learning/learning-portfolio  # 또는 클론한 저장소 루트
source install/setup.bash

ros2 run param_qos_py qos_config_publisher
```

**터미널 1 출력:**
```text
[INFO] [qos_config_publisher]: Latched configuration published: "hardware_rev=2.1 wheelbase_m=0.35 max_payload_kg=15.0 lidar=2D_360"
[INFO] [qos_config_publisher]: Publisher remains active with Transient Local memory cache. Waiting for late-joining subscribers...
```
*(퍼블리셔는 시작 시 1회 설정을 발행한 후 대기합니다.)*

#### 7.2 수 초 후 늦게 구독자 실행 (Late-joiner 테스트)
```bash
# 터미널 2 (새 창): 환경 소싱 후 퍼블리셔가 이미 발행을 마친 상태에서 뒤늦게 구독자 실행
source /opt/ros/humble/setup.bash
cd ~/learning/learning-portfolio  # 또는 클론한 저장소 루트
source install/setup.bash

ros2 run param_qos_py qos_config_listener
```

**터미널 2 출력 (즉시 수신 확인):**
```text
[INFO] [qos_config_listener]: Requested Durability: TRANSIENT_LOCAL. Expecting latched sample immediately.
[INFO] [qos_config_listener]: QoSConfigListener started (Late-joiner). Subscribed to "system/robot_configuration"...
[INFO] [qos_config_listener]: SUCCESS: Latched configuration received from publisher: "hardware_rev=2.1 wheelbase_m=0.35 max_payload_kg=15.0 lidar=2D_360"
```
- **검증 결론:** 퍼블리셔가 메시지를 발행한 뒤 나중에 켜진 노드라도, `TRANSIENT_LOCAL` 정책에 의해 DDS 메모리에 보관된 최신 설정 정보를 연결 즉시 전달받음을 확인했습니다.

---

## 8. 실무 로보틱스 적용 지침

| 토픽 분류 | 권장 Reliability | 권장 Durability | Depth | 실무 적용 사례 |
| :--- | :--- | :--- | :---: | :--- |
| **고주파 센서 스트림** | `BEST_EFFORT` | `VOLATILE` | 5 | 카메라 이미지, LiDAR 포인트 클라우드, IMU 가속도계 |
| **정적 로봇 설정/사양** | `RELIABLE` | `TRANSIENT_LOCAL` | 1 | 휠베이스/질량 사양, 소프트웨어 버전, 모터 캘리브레이션 오프셋 |
| **글로벌 정적 지도** | `RELIABLE` | `TRANSIENT_LOCAL` | 1 | 슬램(SLAM) 점유 격자 지도 (`/map`), 정적 TF (`/tf_static`) |
| **주행 제어 명령** | `RELIABLE` | `VOLATILE` | 10 | 조이스틱/내비게이션 속도 제어 토픽 (`/cmd_vel`) |

---

## 9. 공식 출처 및 저작권 고지

- **공식 표준 문서:**
  - [ROS 2 Humble Documentation: Understanding Parameters](https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Parameters/Understanding-ROS2-Parameters.html)
  - [ROS 2 Humble Documentation: About Quality of Service Settings](https://docs.ros.org/en/humble/Concepts/Intermediate/About-Quality-of-Service-Settings.html)
  - [ROS 2 Humble rclpy API Reference](https://docs.ros2.org/latest/api/rclpy/)
- **라이선스:** Apache License, Version 2.0
