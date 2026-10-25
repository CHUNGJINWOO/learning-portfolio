# ROS 2 & Python 개념 중심 학습 포트폴리오 (Learning Portfolio)

본 저장소는 단순한 코드 모음이나 튜토리얼 복제가 아닌, **Python 객체지향 프로그래밍(OOP) 사고와 ROS 2 분산 로보틱스 통신 철학을 깊이 있게 이해하고 장기적으로 축적·응용**하기 위해 체계적으로 구축된 통합 학습 포트폴리오입니다.

---

## 📚 1. 학습 철학 및 핵심 운영 원칙

1. **원리와 설계 이유 중심 (First-Principles Thinking)**
   - 코드가 단순히 "동작하는가"에 머무르지 않고, *왜 이 아키텍처를 선택했는지*, *어떤 대안이 존재하는지*, *동시성 및 스레드 안전성 문제는 어떻게 해결했는지*를 구조적으로 분석합니다.
2. **독립적 청정 구현 (Clean-room Implementation)**
   - 특정 비공개 상용 교재나 외부 자료의 코드를 무단 복제하지 않고, ROS 2 Humble 및 Python 3.10 공식 표준 문서에 기반해 자체 설계한 예제만을 다룹니다.
3. **엄격한 검증과 기술적 정직성 (Transparency)**
   - 실제로 빌드·실행·검증한 항목과 실행 환경의 제약으로 미검증된 항목을 명확히 분리합니다. 미검증된 내용을 추정으로 통과 처리하지 않습니다.
4. **코드 빌드 성공과 개념 이해의 엄격한 구분**
   - 코드가 빌드되고 에러 없이 실행되었다고 해서 학습자가 개념을 완전히 이해한 것은 아닙니다. 다른 사람에게 동작 원리를 설명하고, 예상치 못한 오류를 해결하며, 응용 문제를 풀 수 있을 때 비로소 '이해 완료'로 간주합니다.
5. **실제 오류와 해결 과정의 자산화 (Troubleshooting as an Asset)**
   - 개발 및 실습 중 마주친 실제 오류 메시지, 원인 분석, 디버깅 과정을 상세히 기록하여 향후 문제 해결의 레퍼런스로 활용합니다.
6. **학교 원본 자료 보존 및 선별 통합 원칙**
   - 학교 원본 자료(`school/`)는 별도의 로컬 공간에 영구 보존하며 포트폴리오로 일괄 복사하지 않습니다. 학습자가 직접 소화하고 자신의 언어로 재구성한 지식만을 선별하여 포트폴리오에 수용합니다.

---

## 🗂️ 2. 포트폴리오 구조

```text
portfolio/
├── .gitignore                                 # 빌드 산출물 및 캐시 제외 규칙
├── LICENSE                                    # Apache-2.0 라이선스
├── README.md                                  # [본 문서] 학습 포트폴리오 대시보드 및 기준선
├── docs/                                      # Phase별 심층 개념 교육 가이드 (총 5개)
│   ├── 01_python_oop_and_ros2_node.md         # [Phase 1] Python OOP와 ROS 2 Node 수명주기
│   ├── 02_parameters_and_qos.md               # [Phase 2] 동적 매개변수 및 QoS 심층 실습
│   ├── 03_services_and_actions.md             # [Phase 3] Services 및 Actions 통신 패러다임
│   ├── 04_launch_and_system_orchestration.md  # [Phase 4] Launch 시스템 및 오케스트레이션
│   ├── 05_tf2_coordinate_transforms.md        # [Phase 5] TF2 공간 좌표 변환 및 진단
│   └── SYSTEM_GUIDE.md                        # 통합 실행 및 검증 가이드
├── exercises/                                 # 복습 및 실습 과제 공간
│   ├── my_package_rclcpy/                     # [입문 실습] Turtlesim 기반 첫 ROS 2 Python 패키지
│   └── README.md                              # 복습 질문 및 과제 운영 안내
├── inbox/                                     # 신규 학습 자료 대기소
├── notebooks/                                 # 대화형 주피터 실습 노트북 (Turtlesim 3종)
│   ├── 03_topic_publisher_turtlesim.ipynb     # [대화형] Topic Publisher 실습
│   ├── 04_topic_subscriber_turtlesim.ipynb    # [대화형] Topic Subscriber 실습
│   ├── 05_service_client_turtlesim.ipynb      # [대화형] Service Client 실습
│   └── README.md                              # 대화형 실습 및 주의사항 안내
├── notes/                                     # 심층 개념 및 이론 학습 노트 (교재 분석 4종)
│   ├── 01_ros2_core_and_interfaces.md         # [이론] Topic/Service/Action 통신 패턴
│   ├── 02_limo_application_programming.md     # [이론] LIMO 복합 센서 제어 파이프라인
│   ├── 03_tf2_and_pose_control.md             # [이론] TF2 수학 및 move_to_pose 제어
│   ├── 04_local_state_estimation.md           # [이론] 지역 위치 추정 및 센서 융합
│   └── README.md                              # 이론 노트 색인 및 검증 범위
└── src/                                       # 정규 독립 패키지 공간 (총 5개)
    ├── core_pubsub_py/                        # [Phase 1] 최소 Pub/Sub 패키지 (ament_python)
    │   ├── package.xml
    │   ├── setup.py
    │   ├── setup.cfg
    │   └── core_pubsub_py/
    │       ├── __init__.py
    │       ├── minimal_publisher.py           # 하트비트 텔레메트리 퍼블리셔 (타이머 기반)
    │       └── minimal_subscriber.py          # 비동기 이벤트 주도 서브스크라이버
    ├── param_qos_py/                          # [Phase 2] 동적 파라미터 및 QoS 패키지
    │   ├── package.xml
    │   ├── setup.py
    │   ├── setup.cfg
    │   ├── config/
    │   │   └── default_params.yaml            # YAML 파라미터 설정 파일
    │   └── param_qos_py/
    │       ├── __init__.py
    │       ├── dynamic_telemetry_publisher.py # 원자적 검증 가드 및 비동기 타이머 갱신 노드
    │       ├── qos_sensor_streamer.py         # Best Effort 고빈도 센서 스트리머
    │       ├── qos_sensor_listener.py         # 신뢰성 모드 선택형 센서 수신자
    │       ├── qos_config_publisher.py        # Transient Local 정적 설정 래칭 퍼블리셔
    │       └── qos_config_listener.py         # 늦은 구독자 (Late-joiner) 설정 수신자
    ├── service_action_py/                     # [Phase 3] 서비스 및 액션 패키지
    │   ├── package.xml
    │   ├── setup.py
    │   ├── setup.cfg
    │   └── service_action_py/
    │       ├── __init__.py
    │       ├── add_two_ints_server.py         # 정수 덧셈 서비스 서버 (RPC)
    │       ├── add_two_ints_client.py         # 비동기 Future 기반 서비스 클라이언트
    │       ├── fibonacci_action_server.py     # 피보나치 액션 서버 (취소 및 선점 제어)
    │       └── fibonacci_action_client.py     # 피보나치 액션 클라이언트 (피드백 수신 및 취소)
    ├── launch_orchestration_py/               # [Phase 4] 런치 시스템 오케스트레이션 패키지
    │   ├── package.xml
    │   ├── setup.py
    │   ├── setup.cfg
    │   ├── config/
    │   │   └── orchestration_params.yaml      # 오케스트레이션 YAML 파라미터 설정
    │   └── launch/
    │       ├── 01_basic_two_nodes.launch.py   # 다중 노드 동시 실행
    │       ├── 02_arguments_and_parameters.launch.py # YAML 로딩 및 CLI 인수 오버라이드
    │       ├── 03_namespaces_and_remappings.launch.py# PushRosNamespace 및 토픽 리매핑
    │       ├── 04_event_handler_on_exit.launch.py    # OnProcessExit 이벤트 감지 및 셧다운
    │       └── 05_integrated_system.launch.py # 4개 서브시스템 통합 브링업
    └── tf2_transforms_py/                     # [Phase 5] TF2 좌표 변환 프레임워크 패키지
        ├── package.xml
        ├── setup.py
        ├── setup.cfg
        ├── resource/tf2_transforms_py
        ├── tf2_transforms_py/
        │   ├── __init__.py
        │   ├── quaternion_utils.py            # 순수 Python math 기반 ZYX 오일러-쿼터니언 변환
        │   ├── static_frame_broadcaster.py    # 파라미터 기반 정적 센서 프레임 브로드캐스터
        │   ├── dynamic_frame_broadcaster.py   # 10Hz 원형 궤적 오도메트리 동적 브로드캐스터
        │   ├── point_transformer_listener.py  # Buffer/Listener 기반 3D LiDAR 포인트 변환
        │   └── tf_lookup_diagnostics.py       # 3대 TF2 예외 결정론적 메모리 진단 노드
        └── launch/
            └── tf2_demo.launch.py             # 2개 정적 + 1개 동적 + 1개 리스너 통합 런치
```

---

## 🚀 3. 학습 모듈 상세 현황 (Curriculum Modules)

### [Phase 1] 핵심 통신 및 객체지향 기초
- **상세 문서:** [01_python_oop_and_ros2_node.md](docs/01_python_oop_and_ros2_node.md)
- **대상 패키지:** `src/core_pubsub_py`
- **핵심 학습 내용:**
  - 절차적 무한 루프(`while True + sleep`)의 자원 독점 문제와 이벤트 주도(Event-Driven) 아키텍처의 필요성
  - `rclpy.node.Node` 클래스 상속 및 `super().__init__()` 수명주기
  - 비차단 타이머(`create_timer`) 콜백과 상태 캡슐화
- **검증 상태:**
  - 패키지 빌드 및 `ament_flake8` 린트: **PASS**
  - 노드 간 하트비트 토픽 송수신 런타임: **PASS**

### [Phase 2] 동적 매개변수 및 서비스 품질 (QoS)
- **상세 문서:** [02_parameters_and_qos.md](docs/02_parameters_and_qos.md)
- **대상 패키지:** `src/param_qos_py`
- **핵심 학습 내용:**
  - `add_on_set_parameters_callback`을 통한 원자적(All-or-Nothing) 매개변수 유효성 검증
  - `/parameter_events` 구독 기반의 2단계 비동기 타이머 주기 갱신
  - `SensorDataQoS` (Best Effort) 고주파 스트리밍과 송수신자 간 비호환(`Incompatibility`) 진단
  - `Transient Local` 래칭을 통한 늦게 참여하는 구독자(Late-joiner) 정적 설정 수신
- **검증 상태:**
  - 패키지 빌드 및 `ament_flake8` 린트: **PASS**
  - 파라미터 동적 오버라이드 및 QoS 호환/비호환 런타임: **PASS**

### [Phase 3] 서비스(Services) 및 액션(Actions)
- **상세 문서:** [03_services_and_actions.md](docs/03_services_and_actions.md)
- **대상 패키지:** `src/service_action_py`
- **핵심 학습 내용:**
  - Topic vs Service vs Action 통신 패러다임 비교 및 최적 설계 선정 기준
  - `call_async()` 기반 비차단 RPC 통신과 데드락 방지
  - Action Goal-Feedback-Result-Cancel 4단계 수명주기 및 상태 전이
  - `MultiThreadedExecutor` 및 `ReentrantCallbackGroup`을 통한 장기 연산 중 취소(Cancel) 동시성 보장
- **검증 상태:**
  - 패키지 빌드 및 `ament_flake8` 린트: **PASS**
  - AddTwoInts RPC 호출, Fibonacci 정상 완료 / 중도 취소 / Goal 거부 런타임: **PASS**

### [Phase 4] 런치 시스템 및 시스템 오케스트레이션
- **상세 문서:** [04_launch_and_system_orchestration.md](docs/04_launch_and_system_orchestration.md)
- **대상 패키지:** `src/launch_orchestration_py`
- **핵심 학습 내용:**
  - 다중 노드 선언적 동시 기동 및 프로세스 수명주기 관리
  - YAML 설정 파일 로딩과 Launch Argument 우선순위 오버라이드 메커니즘
  - `PushRosNamespace` 및 토픽 리매핑을 통한 다중 로봇 통신 격리
  - `OnProcessExit` 이벤트 핸들러를 통한 클라이언트 종료 감지 및 데몬 자동 회수
  - Phase 1~3 노드를 유기적으로 연결한 통합 시스템 브링업
- **검증 상태:**
  - 패키지 빌드 및 `ament_flake8` 린트: **PASS**
  - 5개 Launch 스크립트 실행, CLI 인수 오버라이드, 이벤트 전이 런타임: **PASS**

### [Phase 5] TF2 좌표 변환 및 공간 프레임워크
- **상세 문서:** [05_tf2_coordinate_transforms.md](docs/05_tf2_coordinate_transforms.md)
- **대상 패키지:** `src/tf2_transforms_py`
- **핵심 학습 내용:**
  - TF 트리의 단방향 규칙(단일 부모, 사이클 금지)과 정적(`/tf_static`) vs 동적(`/tf`) 분리
  - ZYX 내재적 오일러 각 $\leftrightarrow$ 해밀턴 쿼터니언 변환 수식 (외부 의존성 제로 순수 `math` 구현)
  - 파라미터 기반 정적 브로드캐스터(LiDAR, Camera) 및 10Hz 원형 주행 오도메트리 동적 브로드캐스터
  - Buffer / Listener 및 `do_transform_point` 기반 LiDAR 관측점 3D 변환 ($z=0.150$ 불변성 확인)
  - TF2 3대 예외(`LookupException`, `ConnectivityException`, `ExtrapolationException`) 결정론적 메모리 진단
  - Python API(`lookup_transform`)와 CLI(`tf2_echo`) 간 인자 순서 및 변환 방향 매핑
- **검증 상태:**
  - 패키지 빌드, `ament_flake8` 린트, 쿼터니언 6개 셀프 테스트: **PASS**
  - 예외 진단 노드, `tf2_echo`, `view_frames`, 3D 포인트 변환 수치 런타임: **PASS**
  - **RViz2 GUI 시각 검증**: 헤드리스(Headless) CLI 환경 제약으로 인해 **NOT_VERIFIED**

---

## 🔍 4. 검증 수준 및 상태 표기 체계 (Technical Transparency)

본 포트폴리오는 기술적 정직성을 유지하기 위해 검증 수준을 4가지 범주로 명확히 구분합니다:

| 검증 범주 | 검증 방식 및 판정 기준 | 현재 상태 |
| :--- | :--- | :---: |
| **코드 및 정적 구조** | 파일 존재, `py_compile` 문법 검사, `ament_flake8` (99자 제한) 스타일 감사 | **PASS** (전 패키지 무결성 확인) |
| **빌드 및 런타임 콘솔** | `colcon build`, 노드 실행 로그(`~/.ros/log/`), CLI 도구(`tf2_echo`, `view_frames`) 수치 일치 | **PASS** (전 Phase 터미널 실측 확인) |
| **GUI 시각적 검증** | RViz2 프레임 축(RGB), Gazebo 3D 물리 시뮬레이션, Turtlesim 창 육안 확인 | **NOT_VERIFIED** (헤드리스 서버 환경) |
| **학습자 개념 이해** | 동작 원리 자체 구술 설명, 오류 자율 디버깅, 복습 및 응용 문제 풀이 완료 | **NEEDS_REVIEW** (자가진단 및 복습 진행 단계) |

> [!NOTE]
> - CLI 환경 특성상 디스플레이 서버(X11/Wayland)가 부재하여 GUI 창을 띄우는 시각적 검증은 수행하지 않았으며, 이를 추정으로 PASS 처리하지 않습니다.
> - 코드가 정상 빌드되었다고 해서 '이해 완료'로 단정하지 않으며, 향후 복습 문제 풀이를 통해 학습자 스스로 이해도를 지속 검증합니다.

---

## 🗺️ 5. 장기 확장 계획 (Roadmap — Future Expansion)

본 영역은 **현재 구현된 완료 항목이 아니며**, 향후 학습을 진행함에 따라 검증된 지식만을 단계적으로 추가할 **장기 발전 계획**입니다:

- **Python Core & Data Modeling**
  - 객체지향 심화, 제너레이터/데코레이터, 비동기 I/O, NumPy 수치 모델링
- **C / C++ Systems Programming**
  - 메모리 모델, 포인터 연산, Modern C++ (C++17/20), ROS 2 C++ 클라이언트(`rclcpp`)
- **Embedded & Micro-ROS**
  - 마이크로컨트롤러(Arduino), 디지털/아날로그 센서 회로, 모터 드라이버 제어, Micro-ROS 통신
- **Advanced Robotics & Navigation**
  - 평면 및 공간 기구학, SLAM(지도 작성), Navigation2(Nav2) 자율주행, LIMO 로봇 실전 제어
- **Robotics AI & Sensor Fusion**
  - 센서 융합(Extended Kalman Filter), 로봇 비전, 딥러닝 기반 객체 인식 및 지능 제어

---

## 🛠️ 6. 개발 및 실행 환경 (Prerequisites)

- **운영체제:** Ubuntu 22.04.5 LTS (Jammy Jellyfish)
- **프로그래밍 언어:** Python 3.10.12
- **ROS 배포판:** ROS 2 Humble Hawksbill (`/opt/ros/humble/setup.bash`, 기본 `ROS_DOMAIN_ID=30`)
- **빌드 시스템:** `colcon` (`colcon-core 0.21.3+`), `setuptools`, `ament_python`

---

## 📜 7. 라이선스 및 저작권 고지

- 본 저장소의 모든 신규 교육 문서 및 구현 코드는 [Apache License 2.0](LICENSE) 하에 배포됩니다.
- 참고 공식 표준 문서: [ROS 2 Humble Documentation](https://docs.ros.org/en/humble/) (CC-BY 4.0 / Apache-2.0), [Python 3.10 Documentation](https://docs.python.org/3.10/) (PSFL).
