# 📚 ROS 2 대화형 학습 노트북 (Turtlesim Interactive Notebooks)

본 디렉터리는 ROS 2 Humble 환경에서 Python(`rclpy`)을 이용한 노드 생성, 토픽 발행/구독, 서비스 클라이언트 통신을 대화형 환경(Jupyter Notebook)에서 시각적으로 검증하기 위해 작성된 실습 노트북 모음입니다.

---

## 🗂️ 실습 노트북 목록

| 순서 | 노트북 파일명 | 핵심 주제 | 주요 사용 인터페이스 | 학습 내용 요약 |
| :---: | :--- | :--- | :--- | :--- |
| **03** | [`03_topic_publisher_turtlesim.ipynb`](03_topic_publisher_turtlesim.ipynb) | ROS 2 토픽 발행 | `rclpy`, `geometry_msgs/msg/Twist` | `create_node`, `create_publisher`, 타이머 콜백을 이용한 거북이 속도 제어(`/turtle1/cmd_vel`) |
| **04** | [`04_topic_subscriber_turtlesim.ipynb`](04_topic_subscriber_turtlesim.ipynb) | ROS 2 토픽 수신 | `rclpy`, `turtlesim/msg/Pose` | `create_subscription`, 콜백 기반 좌표 수신 및 출력(`/turtle1/pose`), spin 제어 |
| **05** | [`05_service_client_turtlesim.ipynb`](05_service_client_turtlesim.ipynb) | ROS 2 서비스 클라이언트 | `rclpy`, `turtlesim/srv/TeleportAbsolute` | `create_client`, 요청 객체(`Request`) 작성, `call_async`, `wait_for_service` 호출 및 대기 기록 |

---

## 🔄 학습 노트북과 정규 패키지(`my_package_rclcpy`)의 유기적 관계

대화형 환경에서 검증된 단편 코드는 [`../exercises/my_package_rclcpy/`](../exercises/my_package_rclcpy/)를 통해 정식 ROS 2 패키지로 승격되었습니다:

1. **대화형 프로토타이핑 $\rightarrow$ 표준 패키지화:**
   - `03_topic_publisher_turtlesim.ipynb` 및 `04_topic_subscriber_turtlesim.ipynb`의 단편적인 발행/구독 코드는 `my_package_rclcpy`의 `talker.py`와 `listener.py`로 정형화되어 예외 처리(`KeyboardInterrupt`), 로거(`get_logger().info()`), 정상 종료 라이프사이클을 갖춘 패키지 노드로 발전했습니다.
2. **서비스 호출 $\rightarrow$ 서버/클라이언트 양방향 구현:**
   - `05_service_client_turtlesim.ipynb`에서 클라이언트 측면만 다루었던 서비스 통신을 `my_package_rclcpy`에서는 `add_two_ints_server.py`와 `add_two_ints_client.py`를 통해 서버와 클라이언트 양방향 전체 메커니즘으로 완성했습니다.
3. **실전 응용 (LIMO 및 OCI 연계):**
   - 토픽 발행 실습에서 익힌 `Twist` 메시지 구조는 [`../../src/remote_teleop_node.py`](../../src/remote_teleop_node.py)로 확장되어 실제 OCI 클라우드 시뮬레이션 로봇을 원격 조향하는 실전 코드로 활용됩니다.

---

## 🛠️ 실행 환경 및 주의사항 (실습 기록 분석)

### 1. 필수 의존 패키지
```bash
sudo apt update
sudo apt install -y ros-humble-rclpy ros-humble-geometry-msgs ros-humble-turtlesim
```

### 2. Turtlesim 노드 사전 실행 필요
노트북 03, 04, 05는 Turtlesim을 대상으로 합니다. 원활한 실습을 위해서는 별도의 GUI/터미널 환경에서 먼저 다음 노드가 실행 중이어야 합니다:
```bash
ros2 run turtlesim turtlesim_node
```

### 3. Jupyter 환경의 강제 예외 발생(`raise Exception`)과 표준 ROS 2 종료 패턴 구분
- **노트북 실습 코드의 제어 흐름:** `03_topic_publisher_turtlesim.ipynb`와 `04_topic_subscriber_turtlesim.ipynb`에서는 카운터가 3을 초과할 때(`cnt > 3`) `raise Exception("Publisher Stop")` 또는 `raise Exception("Subscription Stop !")`을 의도적으로 발생시켜 실행을 중단합니다.
- **배경 및 한계:** `rclpy.spin()`은 메시지가 들어오는 한 무한 루프로 블로킹되므로, 단일 스레드로 동작하는 Jupyter Notebook 커널이 영구 대기(Busy) 상태에 빠지는 것을 막기 위한 **대화형 환경 전용 우회 탈출 방식**입니다. 이를 일반적인 ROS 2 노드의 표준 종료 패턴으로 오해해서는 안 됩니다.
- **패키지 소스 코드(`my_package_rclcpy`)의 실제 종료 처리 비교:**
  - `talker.py`, `listener.py`, `add_two_ints_server.py`: 소스 코드에서 `try ... rclpy.spin(node) except KeyboardInterrupt: pass finally: node.destroy_node(); rclpy.shutdown()` 구문을 사용하여 터미널의 `Ctrl+C` 인터럽트를 정상 수신하고 노드 파괴 및 클라이언트 종료 루틴을 명시적으로 거칩니다.
  - `my_first_node.py`: 최소 구조 학습용으로 작성되어 별도의 `try...except` 없이 순차적으로 `rclpy.spin(node)` 후 `destroy_node()`, `shutdown()`을 호출합니다.
  - `add_two_ints_client.py`: 비동기 요청 후 `rclpy.spin_until_future_complete(node, future)`를 통해 서비스 응답 수신 시 자동으로 스핀 루프를 종료합니다.

### 4. `05_service_client_turtlesim.ipynb`의 서비스 대기(`Waiting for service`) 기록 분석
- **실제 저장된 출력 현황:** 05번 노트북의 마지막 셀 출력에는 `Waiting for service`가 10회 연속 출력된 상태로 남아 있습니다.
- **현상 원인:** 해당 셀 실행 당시 대상 노드인 `turtlesim_node`가 백그라운드나 다른 터미널에서 실행되어 있지 않아, 클라이언트의 `while not cli.wait_for_service(timeout_sec=1.0): print('Waiting for service')` 루프가 서비스를 발견하지 못하고 계속 대기한 실제 트러블슈팅 사례입니다.
- **주의 사항:** 저장된 출력 기록만으로 서비스 호출 및 응답이 정상 완료되었다고 단정할 수 없으며, 서비스 서버 미기동으로 인한 대기 상태가 보존된 기록입니다.
- **정상 호출 재현 및 검증 절차:**
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
