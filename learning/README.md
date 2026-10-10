# 📚 ROS 2 Python 학습 기록 (Learning Records)

이 디렉터리는 ROS 2 Humble 환경에서 Python(`rclpy`)을 기반으로 진행한 단계별 학습 코드와 실습 기록을 관리합니다.

수학적 신호 모델링과 Python 객체지향(OOP) 기초부터 시작하여, 대화형 환경(Jupyter Notebook)에서의 Turtlesim 제어 실습, 그리고 정식 ROS 2 패키지(`my_package_rclcpy`) 구축까지의 학습 과정을 다룹니다.

---

## 1. 디렉터리 구조

```text
learning/
├── README.md                      # [본 문서] ROS 2 학습 로드맵 및 통합 안내
├── notebooks/                     # 단계별 대화형 학습 노트북 (Jupyter Notebook)
│   ├── 01_sin_modeling.ipynb             # 1단계: NumPy 기반 사인파 신호 모델링
│   ├── 02_python_oop_class.ipynb         # 2단계: 객체지향(OOP) 클래스 상속 및 super()
│   ├── 03_topic_publisher_turtlesim.ipynb # 3단계: rclpy Topic Publisher (/turtle1/cmd_vel)
│   ├── 04_topic_subscriber_turtlesim.ipynb# 4단계: rclpy Topic Subscriber (/turtle1/pose)
│   └── 05_service_client_turtlesim.ipynb  # 5단계: rclpy Service Client (/turtle1/teleport_absolute)
└── my_package_rclcpy/             # ROS 2 Python 공식 빌드 패키지
    ├── README.md                  # 패키지 빌드/실행 상세 가이드
    ├── package.xml                # 의존성 및 패키지 메타데이터
    ├── setup.py                   # console_scripts 엔트리포인트 설정
    ├── my_package_rclcpy/
    │   ├── my_first_node.py       # 기본 Node 클래스 상속 예제
    │   ├── talker.py              # String 메시지 발행 노드
    │   ├── listener.py            # String 메시지 수신 노드
    │   ├── add_two_ints_server.py # 정수 덧셈 서비스 서버
    │   └── add_two_ints_client.py # 정수 덧셈 서비스 클라이언트
    └── test/                      # flake8, pep257, copyright 단위 테스트
```

---

## 2. 단계별 학습 순서 및 노트북 상세

실습은 아래 순서로 진행되었으며, 각 단계는 후속 개념의 필수 전제조건으로 연결됩니다.

| 순서 | 노트북 파일명 | 핵심 주제 | 주요 사용 라이브러리 / ROS 2 인터페이스 | 학습 내용 요약 |
| :---: | :--- | :--- | :--- | :--- |
| **01** | `01_sin_modeling.ipynb` | 기초 신호 모델링 | `numpy`, `matplotlib` | 시간 축(`arange`) 생성, 사인파 수식($y = A \sin(2\pi ft) + b$) 계산 및 시각화 절차형 함수 구현 |
| **02** | `02_python_oop_class.ipynb` | 객체지향 프로그래밍 (OOP) | Python 기본 문법 | `DrawSin` 기본 클래스 선언, 인스턴스화, 단일 상속, 메서드 오버라이딩, `super().__init__()` 활용 |
| **03** | `03_topic_publisher_turtlesim.ipynb` | ROS 2 토픽 발행 | `rclpy`, `geometry_msgs/msg/Twist` | `create_node`, `create_publisher`, 타이머 콜백을 이용한 거북이 속도 제어(`/turtle1/cmd_vel`) |
| **04** | `04_topic_subscriber_turtlesim.ipynb` | ROS 2 토픽 수신 | `rclpy`, `turtlesim/msg/Pose` | `create_subscription`, 콜백 기반 좌표 수신 및 출력(`/turtle1/pose`), spin 제어 |
| **05** | `05_service_client_turtlesim.ipynb` | ROS 2 서비스 클라이언트 | `rclpy`, `turtlesim/srv/TeleportAbsolute` | `create_client`, 요청 객체(`Request`) 작성, `call_async`, `wait_for_service` 호출 및 대기 기록 |

---

## 3. 학습 노트북과 `my_package_rclcpy`의 유기적 관계

1. **사전 기초 -> 노드 구조화**:
   - `02_python_oop_class.ipynb`에서 다룬 클래스 상속과 `super()` 패턴은 `my_first_node.py` 및 이후 모든 노드가 `rclpy.node.Node`를 상속받아 구현되는 기본 뼈대가 됩니다.
2. **대화형 프로토타이핑 -> 표준 패키지화**:
   - `03_topic_publisher_turtlesim.ipynb` 및 `04_topic_subscriber_turtlesim.ipynb`의 단편적인 발행/구독 코드는 `my_package_rclcpy`의 `talker.py`와 `listener.py`로 정형화되어 예외 처리(`KeyboardInterrupt`), 로거(`get_logger().info()`), 정상 종료 라이프사이클을 갖춘 패키지 노드로 승격되었습니다.
3. **서비스 호출 -> 서버/클라이언트 양방향 구현**:
   - `05_service_client_turtlesim.ipynb`에서 클라이언트 측면만 다루었던 서비스 통신을 `my_package_rclcpy`에서는 `add_two_ints_server.py`와 `add_two_ints_client.py`를 통해 서버와 클라이언트 양방향 전체 메커니즘으로 완성했습니다.
4. **실전 응용 (LIMO 및 OCI 연계)**:
   - 토픽 발행 실습에서 익힌 `Twist` 메시지 구조는 [src/remote_teleop_node.py](file:///home/cjinw/ros2/src/remote_teleop_node.py)로 확장되어 실제 OCI 클라우드 시뮬레이션 로봇을 원격 조향하는 실전 코드로 활용됩니다.

---

## 4. 실행 환경 및 사전 요구사항

### 4.1. 시스템 환경
- **OS**: Ubuntu 22.04 LTS (Jammy Jellyfish)
- **ROS 2 배포판**: ROS 2 Humble Hawksbill
- **Python 버전**: Python 3.10 이상

### 4.2. 필수 의존 패키지
```bash
# ROS 2 필수 패키지 설치
sudo apt update
sudo apt install -y \
  ros-humble-rclpy \
  ros-humble-std-msgs \
  ros-humble-geometry-msgs \
  ros-humble-example-interfaces \
  ros-humble-turtlesim

# Python 과학 계산 및 시각화 라이브러리
pip install numpy matplotlib
```

### 4.3. 대화형 노트북 실행 시 주의사항 및 실습 기록 분석

- **Turtlesim 노드 사전 실행 필요**:
  - `03_topic_publisher_turtlesim.ipynb`, `04_topic_subscriber_turtlesim.ipynb`, `05_service_client_turtlesim.ipynb`는 Turtlesim을 대상으로 합니다. 원활한 실습을 위해서는 별도의 GUI/터미널 환경에서 먼저 다음 노드가 실행 중이어야 합니다:
    ```bash
    ros2 run turtlesim turtlesim_node
    ```

- **Jupyter 환경의 강제 예외 발생(`raise Exception`)과 표준 ROS 2 종료 패턴 구분**:
  - **노트북 실습 코드의 제어 흐름**: `03_topic_publisher_turtlesim.ipynb`와 `04_topic_subscriber_turtlesim.ipynb`에서는 카운터가 3을 초과할 때(`cnt > 3`) `raise Exception("Publisher Stop")` 또는 `raise Exception("Subscription Stop !")`을 의도적으로 발생시켜 실행을 중단합니다.
  - **배경 및 한계**: `rclpy.spin()`은 메시지가 들어오는 한 무한 루프로 블로킹되므로, 단일 스레드로 동작하는 Jupyter Notebook 커널이 영구 대기(Busy) 상태에 빠지는 것을 막기 위한 **대화형 환경 전용 우회 탈출 방식**입니다. 이를 일반적인 ROS 2 노드의 표준 종료 패턴으로 오해해서는 안 됩니다.
  - **패키지 소스 코드(`my_package_rclcpy`)의 실제 종료 처리 비교**:
    - `talker.py`, `listener.py`, `add_two_ints_server.py`: 소스 코드에서 `try ... rclpy.spin(node) except KeyboardInterrupt: pass finally: node.destroy_node(); rclpy.shutdown()` 구문을 사용하여 터미널의 `Ctrl+C` 인터럽트를 정상 수신하고 노드 파괴 및 클라이언트 종료 루틴을 명시적으로 거칩니다.
    - `my_first_node.py`: 최소 구조 학습용으로 작성되어 별도의 `try...except` 없이 순차적으로 `rclpy.spin(node)` 후 `destroy_node()`, `shutdown()`을 호출합니다.
    - `add_two_ints_client.py`: 비동기 요청 후 `rclpy.spin_until_future_complete(node, future)`를 통해 서비스 응답 수신 시 자동으로 스핀 루프를 종료합니다.

- **`05_service_client_turtlesim.ipynb`의 서비스 대기(`Waiting for service`) 기록 분석**:
  - **실제 저장된 출력 현황**: 05번 노트북의 마지막 셀 출력에는 `Waiting for service`가 10회 연속 출력된 상태로 남아 있습니다.
  - **현상 원인**: 해당 셀 실행 당시 대상 노드인 `turtlesim_node`가 백그라운드나 다른 터미널에서 실행되어 있지 않아, 클라이언트의 `while not cli.wait_for_service(timeout_sec=1.0): print('Waiting for service')` 루프가 서비스를 발견하지 못하고 계속 대기한 실제 트러블슈팅 사례입니다.
  - **주의 사항**: 저장된 출력 기록만으로 서비스 호출 및 응답이 정상 완료되었다고 단정할 수 없으며, 서비스 서버 미기동으로 인한 대기 상태가 보존된 기록입니다.
  - **정상 호출 재현 및 검증 절차**:
    1. 터미널 1에서 대상 서비스 노드 실행:
       ```bash
       ros2 run turtlesim turtlesim_node
       ```
    2. 터미널 2에서 서비스 활성화 및 인터페이스 일치 확인:
       ```bash
       ros2 service list | grep teleport_absolute
       # 출력 확인: /turtle1/teleport_absolute
       ros2 service type /turtle1/teleport_absolute
       # 출력 확인: turtlesim/srv/TeleportAbsolute
       ```
    3. 서비스가 정상 감지된 상태에서 노트북 셀을 재실행하거나 CLI로 직접 테스트:
       ```bash
       ros2 service call /turtle1/teleport_absolute turtlesim/srv/TeleportAbsolute "{x: 1.0, y: 1.0, theta: 0.0}"
       ```
    *(참고: 본 감사 단계에서는 GUI/Turtlesim 라이브 구동을 진행하지 않았으므로, 노트북의 기존 실행 출력을 그대로 보존한 상태에서 문서화했습니다.)*

---

## 5. 확인된 실습 범위 및 미확인 항목

- **확인 완료 실습**:
  - Python 기초 신호 모델링 및 OOP 상속
  - Turtlesim 기반 토픽 발행(`cmd_vel`) 및 구독(`pose`) 대화형 실습
  - Turtlesim 기반 서비스 클라이언트 대화형 구현 (단, 실행 기록은 서비스 미기동에 따른 대기 상태로 보존됨)
  - `ament_python` 기반 ROS 2 패키지 빌드 및 5종 콘솔 스크립트 실행 구조
- **미확인 항목 (추가 조사 필요)**:
  - ROS 2 액션(Action, 예: Turtlesim `RotateAbsolute`) 실습 코드: CLI 명령 이력에는 존재하나, 작성된 Python 코드는 확인되지 않음.
  - ROS 2 파라미터(Parameter) 및 Launch 파일: 현재 패키지 내 작성 여부 미확인.
  - 서비스 클라이언트 노트북의 라이브 응답 성공 여부: 저장된 출력이 대기 루프 상태이므로, 차후 라이브 환경에서의 호출 검증 필요.
