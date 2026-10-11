# ROS 2 Learning Portfolio — Phase 4: Launch and System Orchestration

본 문서는 ROS 2 Humble Hawksbill 환경에서 다중 노드 오케스트레이션(Launch System), 파라미터 주입 및 우선순위, 네임스페이스 격리와 토픽 리매핑, 그리고 수명주기 이벤트 핸들링(`OnProcessExit`)을 심층적으로 다루는 기술 가이드입니다.

---

## 1. ROS 2 Launch의 목적과 아키텍처

### 1.1 왜 Launch 시스템이 필요한가?
로봇 시스템은 단일 노드로 동작하지 않습니다. 센서 드라이버, 원격 측정기, 제어기, 상태 추정기 등 수십 개의 노드가 동시에 유기적으로 실행되어야 합니다.
- **수동 실행의 한계**: 노드마다 터미널을 열고 파라미터를 입력하는 방식은 재현성이 없고 환경 설정 오류에 취약합니다.
- **Launch 시스템의 역할**:
  1. **선언적 다중 노드 기동**: 단 하나의 명령(`ros2 launch`)으로 시스템 전체를 기동.
  2. **환경 구성 및 파라미터 주입**: YAML 파일 및 CLI 인수(`DeclareLaunchArgument`)를 통한 동적 설정.
  3. **네임스페이스 및 통신 격리**: 동일한 노드 바이너리를 다중 로봇(Multi-Robot) 환경에서 충돌 없이 인스턴스화.
  4. **프로세스 수명주기 관리**: 일회성 태스크(Client) 종료 시 백그라운드 데몬(Server)을 자동으로 회수(`OnProcessExit` + `Shutdown`).

### 1.2 패키지 구조 (`launch_orchestration_py`)
```
src/launch_orchestration_py/
├── package.xml                                     # launch, launch_ros 및 Phase 1~3 의존성 선언
├── setup.py                                        # launch 및 config 데이터 파일 install 매핑
├── setup.cfg                                       # 패키지 빌드 디렉터리 설정
├── resource/launch_orchestration_py                # ament 인덱스 마커
├── launch_orchestration_py/__init__.py             # Python 모듈 초기화
├── config/
│   └── orchestration_params.yaml                   # 텔레메트리 파라미터 YAML 기본 설정
└── launch/
    ├── 01_basic_two_nodes.launch.py                # 기초: 2개 노드 동시 실행
    ├── 02_arguments_and_parameters.launch.py       # 파라미터: YAML 로딩 및 CLI 인수 오버라이드
    ├── 03_namespaces_and_remappings.launch.py      # 네임스페이스: PushRosNamespace 및 토픽 리매핑
    ├── 04_event_handler_on_exit.launch.py          # 이벤트: OnProcessExit 기반 정상/오류 감지 및 자동 셧다운
    └── 05_integrated_system.launch.py              # 통합: 4개 서브시스템 통합 브링업
```

---

## 2. Launch 실습 가이드 및 실제 검증 결과

### 실습 1. 다중 노드 동시 실행 (`01_basic_two_nodes.launch.py`)
- **목표**: Phase 1의 `minimal_publisher`와 `minimal_subscriber`를 단일 Launch 파일로 묶어 동시 기동하고 통신을 확인합니다.
- **실행 명령**:
  ```bash
  ros2 launch launch_orchestration_py 01_basic_two_nodes.launch.py
  ```
- **실제 검증 출력**:
  ```text
  [INFO] [launch]: Default logging verbosity is set to INFO
  [INFO] [minimal_publisher-1]: process started with pid [131922]
  [INFO] [minimal_subscriber-2]: process started with pid [131924]
  [minimal_publisher-1] [INFO] [minimal_publisher]: MinimalPublisher node initialized. Publishing to "heartbeat" at 1.0s interval.
  [minimal_subscriber-2] [INFO] [minimal_subscriber]: MinimalSubscriber node initialized. Listening to "heartbeat" topic...
  [minimal_publisher-1] [INFO] [minimal_publisher]: Published: "Heartbeat seq=0 status=ACTIVE"
  [minimal_subscriber-2] [INFO] [minimal_subscriber]: Received: "Heartbeat seq=0 status=ACTIVE"
  [minimal_publisher-1] [INFO] [minimal_publisher]: Published: "Heartbeat seq=1 status=ACTIVE"
  [minimal_subscriber-2] [INFO] [minimal_subscriber]: Received: "Heartbeat seq=1 status=ACTIVE"
  ```
- **기술적 핵심**:
  - `LaunchDescription`에 리스트 형태로 노드를 등록하면 ROS 2 데몬이 비동기적으로 각 프로세스를 포크합니다.
  - 두 노드는 동일한 DDS 도메인 상에서 `/heartbeat` 토픽을 자동으로 탐색하여 정상 바인딩됩니다.

---

### 실습 2. Launch 인자와 파라미터 오버라이드 (`02_arguments_and_parameters.launch.py`)
- **목표**: YAML 파일의 기본값을 로드하고, CLI 인수로 전달된 `rate_hz` 및 `bot_id`가 노드 파라미터를 재정의하는 동작 원리를 체득합니다.
- **파라미터 우선순위 메커니즘**:
  ```python
  Node(
      package='param_qos_py',
      executable='dynamic_telemetry_publisher',
      parameters=[
          params_file,  # 1. orchestration_params.yaml (publish_rate_hz: 2.0)
          {
              'publish_rate_hz': LaunchConfiguration('rate_hz'),  # 2. Launch 인수 딕셔너리
              'device_id': LaunchConfiguration('bot_id'),
          }
      ]
  )
  ```
  > [!IMPORTANT]
  > ROS 2 Humble의 `launch_ros`는 `parameters` 리스트를 **좌측에서 우측으로 순차 평가**합니다.
  > YAML의 `publish_rate_hz: 2.0`과 Launch 인자의 기본값 `'2.0'`이 같더라도, **실제 노드에 적용되는 값의 출처는 뒤이어 평가된 LaunchConfiguration 딕셔너리**입니다. 즉, Launch argument 딕셔너리가 항상 YAML 값을 덮어씁니다.

#### 1) 기본값 실행 (CLI 인수 미지정)
- **실행 명령**:
  ```bash
  ros2 launch launch_orchestration_py 02_arguments_and_parameters.launch.py
  ```
- **실제 검증 출력**:
  ```text
  [INFO] [dynamic_telemetry_publisher-1]: process started with pid [132124]
  [dynamic_telemetry_publisher-1] [INFO] [dynamic_telemetry_publisher]: DynamicTelemetryPublisher initialized. ID="telemetry_bot_orchestrated", Rate=2.0Hz
  [dynamic_telemetry_publisher-1] [INFO] [dynamic_telemetry_publisher]: Published: "[telemetry_bot_orchestrated] seq=0 rate=2.0Hz"
  [dynamic_telemetry_publisher-1] [INFO] [dynamic_telemetry_publisher]: Published: "[telemetry_bot_orchestrated] seq=1 rate=2.0Hz"
  ```
  - 주기: `0.5s` (2.0Hz) 간격으로 정확히 발행.

#### 2) CLI 인수 명시 (재정의 실행)
- **실행 명령**:
  ```bash
  ros2 launch launch_orchestration_py 02_arguments_and_parameters.launch.py rate_hz:=8.0 bot_id:=limo_patrol_99
  ```
- **실제 검증 출력**:
  ```text
  [INFO] [dynamic_telemetry_publisher-1]: process started with pid [132219]
  [dynamic_telemetry_publisher-1] [INFO] [dynamic_telemetry_publisher]: DynamicTelemetryPublisher initialized. ID="limo_patrol_99", Rate=8.0Hz
  [dynamic_telemetry_publisher-1] [INFO] [dynamic_telemetry_publisher]: Published: "[limo_patrol_99] seq=0 rate=8.0Hz"
  [dynamic_telemetry_publisher-1] [INFO] [dynamic_telemetry_publisher]: Published: "[limo_patrol_99] seq=1 rate=8.0Hz"
  [dynamic_telemetry_publisher-1] [INFO] [dynamic_telemetry_publisher]: Published: "[limo_patrol_99] seq=2 rate=8.0Hz"
  ```
  - 주기: `0.125s` (8.0Hz) 간격으로 고속 발행. CLI 전달값이 YAML 기본값을 성공적으로 오버라이드했음을 입증.

---

### 실습 3. 네임스페이스 격리와 토픽 리매핑 (`03_namespaces_and_remappings.launch.py`)
- **목표**: 단일 실행 파일(`qos_sensor_streamer`)을 2개 인스턴스로 실행하되, 네임스페이스(`limo_01`, `limo_02`)와 토픽 리매핑(`sensor/imu_stream` $\to$ `imu/data_raw`)을 적용하여 충돌 없이 독립 동작하도록 구성합니다.
- **실행 명령**:
  ```bash
  ros2 launch launch_orchestration_py 03_namespaces_and_remappings.launch.py
  ```
- **실제 검증 결과 (노드 및 토픽 실측)**:
  - **활성 노드 목록 (`ros2 node list`)**:
    ```text
    /limo_01/qos_sensor_streamer
    /limo_02/qos_sensor_streamer
    ```
  - **활성 토픽 목록 (`ros2 topic list`)**:
    ```text
    /limo_01/imu/data_raw
    /limo_02/sensor/imu_stream
    /parameter_events
    /rosout
    ```
- **원리 분석**:
  1. `qos_sensor_streamer.py`의 소스코드는 토픽 선두에 `/`가 없는 **상대 토픽(`sensor/imu_stream`)**을 사용합니다.
  2. `PushRosNamespace('limo_02')` 적용 시, 상대 토픽은 자동으로 접두사가 붙어 `/limo_02/sensor/imu_stream`으로 바인딩됩니다.
  3. `limo_01`의 경우 `remappings=[('sensor/imu_stream', 'imu/data_raw')]` 규칙이 추가 적용되어 `/limo_01/imu/data_raw`로 최종 변환됩니다.

---

### 실습 4. OnProcessExit 이벤트 처리 및 자동 셧다운 (`04_event_handler_on_exit.launch.py`)
- **목표**: 영구 실행 서버(`add_two_ints_server`)와 일회성 클라이언트(`add_two_ints_client`)를 연동하고, 클라이언트 종료 시 `event.returncode`를 분석하여 전체 시스템을 정상 또는 비정상 종료 처리합니다.
- **이벤트 핸들러 구현**:
  ```python
  def handle_client_exit(event: ProcessExited, context: LaunchContext):
      if event.returncode == 0:
          return [
              LogInfo(msg=f'[Orchestration] Client task completed successfully (returncode={event.returncode}). Initiating graceful system shutdown.'),
              EmitEvent(event=Shutdown(reason='Service client call finished with success.'))
          ]
      else:
          return [
              LogInfo(msg=f'[Orchestration ERROR] Client task failed (returncode={event.returncode}). Initiating emergency system shutdown.'),
              EmitEvent(event=Shutdown(reason=f'Service client failed with exit code {event.returncode}.'))
          ]
  ```

#### 1) 정상 종료 시나리오 (`returncode == 0`)
- **실행 명령**:
  ```bash
  ros2 launch launch_orchestration_py 04_event_handler_on_exit.launch.py arg_a:=20 arg_b:=30
  ```
- **실제 검증 출력**:
  ```text
  [INFO] [add_two_ints_server-1]: process started with pid [134858]
  [INFO] [add_two_ints_client-2]: process started with pid [134860]
  [add_two_ints_server-1] [INFO] [add_two_ints_server]: AddTwoIntsServer ready. Service "add_two_ints" is advertising.
  [add_two_ints_client-2] [INFO] [add_two_ints_client]: Sending async request: 20 + 30
  [add_two_ints_server-1] [INFO] [add_two_ints_server]: Incoming request: a=20, b=30
  [add_two_ints_server-1] [INFO] [add_two_ints_server]: Sending response: sum=50
  [add_two_ints_client-2] [INFO] [add_two_ints_client]: Received response: 20 + 30 = 50
  [add_two_ints_client-2] RESULT: 50
  [INFO] [add_two_ints_client-2]: process has finished cleanly [pid 134860]
  [INFO] [launch.user]: [Orchestration] Client task completed successfully (returncode=0). Initiating graceful system shutdown.
  [INFO] [add_two_ints_server-1]: sending signal 'SIGINT' to process[add_two_ints_server-1]
  [INFO] [add_two_ints_server-1]: process has finished cleanly [pid 134858]
  ```
- **잔여 프로세스 확인**:
  ```bash
  ps aux | grep -E "add_two_ints_server|add_two_ints_client" | grep -v grep
  # 출력: NO_RESIDUAL_PROCESSES (완전 회수 확인)
  ```

#### 2) 오류 종료 시나리오 (`returncode == 1`)
- **실행 명령**:
  ```bash
  ros2 launch launch_orchestration_py 04_event_handler_on_exit.launch.py arg_a:=invalid_num
  ```
- **실제 검증 출력**:
  ```text
  [INFO] [add_two_ints_server-1]: process started with pid [135421]
  [INFO] [add_two_ints_client-2]: process started with pid [135423]
  [add_two_ints_client-2] Error: Invalid or missing arguments.
  [add_two_ints_client-2] Usage: ros2 run service_action_py add_two_ints_client -- <a> <b>
  [ERROR] [add_two_ints_client-2]: process has died [pid 135423, exit code 1, cmd '...'].
  [INFO] [launch.user]: [Orchestration ERROR] Client task failed (returncode=1). Initiating emergency system shutdown.
  [INFO] [add_two_ints_server-1]: sending signal 'SIGINT' to process[add_two_ints_server-1]
  ```
- **원리 분석**:
  - 클라이언트가 정수 파싱에 실패하여 `sys.exit(1)`로 즉시 종료됨.
  - `OnProcessExit` 핸들러가 `event.returncode`의 1을 포획하여 에러 로그를 출력하고 비상 셧다운을 트리거함.
  - 백그라운드 서버에 `SIGINT`가 즉시 전달되어 방치되지 않고 안전하게 회수됨.

---

### 실습 5. 통합 시스템 브링업 (`05_integrated_system.launch.py`)
- **목표**: Phase 1~2에서 개별적으로 개발한 4개 핵심 노드를 단일 파일로 엮어, 실제 로봇(LIMO 등)의 전체 탑재 소프트웨어 스택 브링업 환경을 모사합니다.
- **실행 명령**:
  ```bash
  ros2 launch launch_orchestration_py 05_integrated_system.launch.py
  ```
- **실제 검증 결과 (노드 및 토픽 실측)**:
  - **활성 노드 목록 (`ros2 node list`)**:
    ```text
    /dynamic_telemetry_publisher
    /minimal_publisher
    /qos_config_publisher
    /qos_sensor_streamer
    ```
  - **활성 토픽 목록 (`ros2 topic list`)**:
    ```text
    /heartbeat
    /parameter_events
    /rosout
    /sensor/imu_stream
    /system/robot_configuration
    /telemetry/status
    ```
  - **노드 초기화 로그 실측**:
    ```text
    [minimal_publisher-1] [minimal_publisher]: MinimalPublisher node initialized. Publishing to "heartbeat" at 1.0s interval.
    [dynamic_telemetry_publisher-2] [dynamic_telemetry_publisher]: DynamicTelemetryPublisher initialized. ID="telemetry_bot_orchestrated", Rate=2.0Hz
    [qos_sensor_streamer-3] [qos_sensor_streamer]: QoSSensorStreamer initialized. Publishing to "sensor/imu_stream" with Best Effort QoS at 10Hz.
    [qos_config_publisher-4] [qos_config_publisher]: QoSConfigPublisher initialized. Latched configuration published: "hardware_rev=2.1 wheelbase_m=0.35 max_payload_kg=15.0 lidar=2D_360"
    ```

---

## 3. 정적 및 빌드 검증 요약

| 검증 단계 | 사용 도구 / 명령 | 결과 | 비고 |
| :--- | :--- | :---: | :--- |
| **Python 구문 검사** | `python3 -m py_compile` | **`PASS`** | 5개 Launch 파일 및 패키지 스크립트 전수 통과 |
| **YAML 구문 검사** | `yaml.safe_load()` | **`PASS`** | `orchestration_params.yaml` 파싱 무결성 확인 |
| **코드 스타일 린트** | `ament_flake8` | **`PASS`** | 7개 파일 전수 검사, 0 problems found |
| **패키지 빌드** | `colcon build --symlink-install` | **`PASS`** | 4개 패키지 빌드 완료 (2.29s) |
| **Launch 설명 검사** | `ros2 launch <pkg> <file> -p` | **`PASS`** | 5개 LaunchDescription 엔티티 트리 정상 파싱 |
| **인수 목록 검사** | `ros2 launch <pkg> <file> -s` | **`PASS`** | 선언 인자 및 기본값 정확 노출 확인 |

---

## 4. 문제 해결 및 트러블슈팅 (Troubleshooting)

### 4.1 flake8 E501 (Line Too Long) 해결
- **문제**: `04_event_handler_on_exit.launch.py`의 `EmitEvent(event=Shutdown(reason=f'...'))` 구문이 109자로 측정되어 PEP 8 허용치(99자)를 초과함.
- **해결**: 인자를 다중 행으로 분리하여 개행 처리함으로써 `ament_flake8`을 100% 무결점으로 통과시킴.

### 4.2 OnProcessExit 후 좀비 프로세스 방지
- **문제**: 일회성 클라이언트가 종료된 후 백그라운드 서버가 계속 살아있으면 포트와 시스템 메모리를 점유함.
- **해결**: 이벤트 핸들러 내부에서 `EmitEvent(event=Shutdown(...))`를 발행하여 Launch 시스템 전체를 종료시키고, Launch 프레임워크가 자식 프로세스에게 `SIGINT`를 송신하여 `KeyboardInterrupt`를 거쳐 `destroy_node()`를 수행하도록 설계함. `ps aux` 검사 결과 잔여 프로세스 0건 입증.

---

## 5. 알려진 한계 및 다음 Phase 연계

1. **포트폴리오 비-Git 상태 유지**:
   - 본 Phase 4 역시 사용자의 승인 범위에 따라 Git 초기화 없이 순수 로컬 클린룸 환경에서 검증되었습니다.
2. **향후 Phase 5 연계 방안**:
   - **TF2 및 좌표계 변환**: 본 Phase에서 완성된 Launch 시스템을 기반으로 `robot_state_publisher` 및 동적 좌표계 브로드캐스터를 구동할 준비가 완료되었습니다.
   - **LIMO Bringup 실차 연동**: `03`의 네임스페이스 기법과 `05`의 브링업 패턴은 실제 AgileX LIMO 로봇의 다중 로봇 군집 주행 및 통합 런처로 직접 확장 가능합니다.
