# 모듈 01: Python 객체지향(OOP) 설계와 ROS 2 Node의 관계

## 1. 문제 (Problem Statement)
초보 개발자가 로봇 제어 프로그램을 작성할 때 흔히 다음과 같은 절차적(Procedural) 무한 루프 패턴을 사용합니다:

```python
# 절차적 스크립팅 방식의 안티패턴
import time

count = 0
while True:
    print(f"Data: {count}")
    count += 1
    time.sleep(1.0)
```

이러한 절차적 방식은 단일 스크립트에서는 동작하는 것처럼 보이지만, 다중 센서와 액추에이터가 동시에 동작하는 로봇 소프트웨어 시스템에서는 심각한 결함을 초래합니다:
1. **스레드 블로킹(Thread Blocking) 문제:** `time.sleep(1.0)`은 프로세스 전체가 아니라 **현재 코드를 실행 중인 해당 OS 스레드를 지정된 시간 동안 대기(Sleep) 상태로 전환**시킵니다. ROS 2의 기본 단일 스레드 실행기(`SingleThreadedExecutor`) 환경에서는 하나의 스레드가 모든 콜백을 순차적으로 처리하므로, 타이머나 콜백 내부에서 `time.sleep()`이 실행되면 그 시간 동안 큐에 대기 중인 다른 센서 콜백이나 비상 정지 명령을 전혀 스케줄링할 수 없습니다. (다중 스레드 실행기를 사용하더라도 스레드 풀 고갈, 락 경쟁, 데드락 위험이 발생하므로 콜백을 블로킹시키는 것은 엄격한 안티패턴입니다.)
2. **상태 관리의 분산 및 상태 오염:** 전역 변수(`count`)를 사용하여 상태를 추적할 경우, 여러 기능이나 객체가 동일한 전역 변수를 조작하면서 경쟁 상태(Race Condition)와 예기치 못한 상태 오염이 발생합니다.
3. **재사용성 및 컴포지션(Composition) 부재:** 하나의 프로세스 내에서 여러 개의 노드를 동시에 띄우거나, 다른 모듈에서 클래스로 가져와 파라미터를 다르게 주어 인스턴스화하는 객체지향적 확장이 불가능합니다.

따라서 ROS 2는 모든 연산 주체를 **객체지향 프로그래밍(OOP) 기반의 `Node` 클래스**로 캡슐화하도록 강제합니다.

---

## 2. 개념 (Core Concepts)

ROS 2의 Python 클라이언트 라이브러리(`rclpy`)에서 노드는 독립적인 실행 단위이자 계산 그래프(Computation Graph)의 기본 구성 요소입니다.

### 2.1 클래스 상속과 수명주기
- **`class MinimalPublisher(Node)`**: Python 표준 상속 문법을 사용하여 ROS 2의 핵심 기반 클래스인 `rclpy.node.Node`의 모든 기능을 물려받습니다.
- **인스턴스 초기화 (`__init__`)**: 노드가 메모리에 생성될 때 ROS 2 통신 미들웨어(DDS)에 노드 이름을 등록하고, 퍼블리셔/서브스크라이버/타이머 리소스를 바인딩합니다.
- **부모 클래스 초기화 (`super().__init__()`)**: 부모 클래스의 생성자를 명시적으로 호출하여 노드 전용 로거(`self.get_logger()`), 파라미터 서버, 통신 인터페이스를 초기화합니다.

### 2.2 인스턴스 변수(`self`)와 클래스 변수(Class Attribute)의 차이
상태 변수(`sequence_number`)를 다룰 때, 변수가 선언되는 스코프에 따라 메모리 구조와 동작이 완전히 달라집니다:

```python
# [안티패턴] 클래스 변수로 상태를 관리하는 경우
class BadPublisher(Node):
    sequence_number = 0  # 클래스 네임스페이스에 선언됨 (모든 인스턴스가 공유)

    def timer_callback(self):
        BadPublisher.sequence_number += 1

# [올바른 패턴] 인스턴스 변수로 상태를 격리하는 경우 (ROS 2 표준)
class GoodPublisher(Node):
    def __init__(self):
        super().__init__('good_publisher')
        self.sequence_number = 0  # self에 바인딩되어 개별 객체마다 독립 메모리 할당
```

- **클래스 변수:** 클래스 정의문 직하에 선언되는 변수로, 해당 클래스로 생성된 모든 인스턴스가 단 하나의 메모리 주소를 공유합니다. 만약 동일한 프로세스 내에서 `node_1 = BadPublisher()`와 `node_2 = BadPublisher()`를 동시에 실행하면, 두 노드가 동일한 `sequence_number`를 증감시켜 심각한 상태 오염(State Pollution)이 발생합니다.
- **인스턴스 변수 (`self.sequence_number`):** 생성자(`__init__`) 내부에서 `self.` 접두사를 붙여 선언되는 변수로, 개별 노드 인스턴스마다 독립적인 힙 메모리 공간을 갖습니다. 하나의 프로세스 내에서 다수의 노드 인스턴스를 컴포지션(Composition)하더라도 각 노드의 상태가 완벽히 격리됩니다.

### 2.3 제어의 역전 (Inversion of Control, IoC)과 실행기(Executor)
절차적 코드에서는 개발자가 `while` 루프로 프로그램의 흐름을 직접 제어하지만, ROS 2에서는 `rclpy.spin(node)`에 제어권을 넘깁니다.  
- **이벤트 스케줄링:** `create_timer()`는 타이머 만료 이벤트를 예약(Schedule)할 뿐입니다. 타이머가 만료되면 실행기(Executor)의 대기 큐에 콜백이 진입합니다.
- **디스패칭 메커니즘:** 실행기(Executor)가 백그라운드 이벤트 루프에서 대기하다가 등록된 타이머 주기가 도래하거나 네트워크 데이터가 도착했을 때 해당 콜백 함수를 비동기적으로 디스패치(Dispatch)합니다.
- **비차단의 한계:** `create_timer()`를 등록했다고 해서 시스템의 실시간성이나 비차단 처리가 무조건 보장되는 것은 아닙니다. 실행기가 단일 스레드(`SingleThreadedExecutor`)인 경우, 콜백 함수 본문이 실행되는 동안에는 스레드가 점유되므로 다른 콜백 처리가 순차적으로 지연될 수 있습니다. 따라서 **콜백 본문은 항상 연산량이 적고 블로킹이 없는 경량 코드여야 합니다.**

---

## 3. 코드 해석 (Code Anatomy)

`core_pubsub_py/minimal_publisher.py`의 핵심 구문을 상세히 분해합니다.

### 3.1 노드 클래스 정의 및 부모 초기화
```python
class MinimalPublisher(Node):
    def __init__(self) -> None:
        super().__init__('minimal_publisher')
```
- `super().__init__('minimal_publisher')`:
  - `super()`는 부모 클래스인 `rclpy.node.Node`를 가리킵니다.
  - `'minimal_publisher'`라는 문자열을 부모 생성자에 전달하여 ROS 2 그래프 상에 노드 고유 이름을 등록합니다.
  - 이 과정에서 노드 전용 로거(`self.get_logger()`), 파라미터 서버, 통신 인터페이스가 인스턴스에 준비됩니다.

### 3.2 퍼블리셔 및 비차단 타이머 생성
```python
        self.publisher_ = self.create_publisher(String, 'heartbeat', 10)
        self.timer_period_sec: float = 1.0
        self.timer = self.create_timer(self.timer_period_sec, self.timer_callback)
        self.sequence_number: int = 0
```
- `create_publisher(String, 'heartbeat', 10)`:
  - 첫 번째 인자 `String`: 토픽을 통해 주고받을 데이터 규격(인터페이스) 타입.
  - 두 번째 인자 `'heartbeat'`: 미들웨어 상에서 식별되는 토픽 이름.
  - 세 번째 인자 `10`: QoS(Quality of Service) 큐 깊이(Queue Depth). 네트워크 지연 시 최대 10개의 메시지를 버퍼에 유지합니다.
- `create_timer(1.0, self.timer_callback)`:
  - `time.sleep`을 호출하지 않고, ROS 2 실행기(Executor)에 "1.0초마다 `self.timer_callback` 메서드를 호출하라"는 타이머 이벤트를 등록합니다.
- `self.sequence_number = 0`:
  - 전역 변수나 클래스 변수가 아닌, `self`에 바인딩된 인스턴스 변수로 시퀀스를 관리하여 독립성을 보장합니다.

### 3.3 타이머 콜백과 페이로드 발행
```python
    def timer_callback(self) -> None:
        msg = String()
        msg.data = f'Heartbeat seq={self.sequence_number} status=ACTIVE'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Published: "{msg.data}"')
        self.sequence_number += 1
```
- `msg = String()`: DDS 미들웨어가 직렬화할 수 있는 표준 ROS 2 메시지 객체를 인스턴스화합니다.
- `self.publisher_.publish(msg)`: 직렬화된 데이터를 네트워크(DDS 버스)로 브로드캐스트합니다.
- `self.get_logger().info(...)`: 표준 `print()` 대신 ROS 2 로깅 시스템을 사용하여 타임스탬프, 노드 이름, 심각도(INFO)를 포함해 출력합니다.

### 3.4 메인 함수와 결정론적 수명주기 정리
```python
def main(args=None) -> None:
    rclpy.init(args=args)
    node = MinimalPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
```
- `rclpy.init(args=args)`: 통신 계층 및 DDS 컨텍스트를 초기화합니다.
- `rclpy.spin(node)`: 이벤트 루프를 시작하고 콜백이 트리거될 때까지 블로킹 대기합니다.
- `try ... finally`: 사용자가 `Ctrl+C`로 중단하더라도 `finally` 블록에서 `node.destroy_node()`와 `rclpy.try_shutdown()`을 호출하여 시스템 자원을 완전히 해제(Deterministic Cleanup)합니다.
  - **ROS 2 Humble 기술적 주의점:** `rclpy.spin()` 도중 `SIGINT`가 발생하면 ROS 2의 C 신호 핸들러가 이미 컨텍스트를 종료(`rcl_shutdown`)할 수 있습니다. 이때 `rclpy.shutdown()`을 무조건 재호출하면 `RCLError: failed to shutdown: rcl_shutdown already called` 예외가 발생하므로, 컨텍스트 종료 여부를 안전하게 확인하고 처리하는 멱등(Idempotent) 함수인 `rclpy.try_shutdown()`을 사용하는 것이 공식 표준 패턴입니다.

---

## 4. 설계 이유 (Design Rationale)

| 설계 선택 | 채택한 방식 (`MinimalPublisher`) | 대안 (`while True + sleep`) | 채택 이유 |
|---|---|---|---|
| **프로그래밍 패러다임** | 객체지향 상속 (`Node` 서브클래스) | 단일 파일 절차적 스크립트 | 상태 격리, 다중 노드 조합(Composition), 단위 테스트 용이성 |
| **시간 동기화** | `create_timer` (실행기 스케줄링) | `time.sleep(1.0)` (스레드 블로킹) | 작업 스레드를 직접 블로킹하지 않고 실행기 이벤트 루프에 제어권을 양보 |
| **상태 관리** | `self.sequence_number` (인스턴스 변수) | 전역 변수 / 클래스 변수 | 다중 노드 인스턴스화 시 상태 오염 방지 및 스레드별 독립성 확보 |
| **출력 방식** | `self.get_logger().info()` | `print()` | 로그 레벨 필터링, 타임스탬프 자동 첨부, 원격 진단(`rqt_console`) 연동 |
| **종료 처리** | `try ... finally` 자원 해제 | 강제 프로세스 킬 (`kill -9`) | DDS 미들웨어에 노드 퇴장을 명시적으로 알려 잔여 엔드포인트 방지 |

---

## 5. 실행 예제 (Minimal Run Instructions)

### 5.1 패키지 디렉터리 레이아웃
```text
portfolio/src/core_pubsub_py/
├── package.xml
├── setup.py
├── setup.cfg
├── resource/core_pubsub_py
└── core_pubsub_py/
    ├── __init__.py
    ├── minimal_publisher.py
    └── minimal_subscriber.py
```

### 5.2 빌드 및 실행 (ROS 2 Humble 환경)
모든 빌드 및 실행 명령어는 워크스페이스 루트인 `/home/cjinw/learning/portfolio` 디렉터리를 기준으로 수행합니다:

```bash
# 1. ROS 2 환경 소싱 및 워크스페이스 빌드
source /opt/ros/humble/setup.bash
cd /home/cjinw/learning/portfolio
colcon build --packages-select core_pubsub_py

# 2. 로컬 오버레이 환경 반영
source install/setup.bash

# 3. 터미널 1: 퍼블리셔 실행
ros2 run core_pubsub_py minimal_publisher

# 4. 터미널 2: 서브스크라이버 실행
ros2 run core_pubsub_py minimal_subscriber
```

---

## 6. 응용 (Real-world Robotics Application)

이 미니멀 Pub/Sub 패턴은 실제 이동 로봇에서 다음과 같은 핵심 서브시스템으로 확장됩니다:
1. **로봇 하트비트(Heartbeat) 감시:** 로봇 제어 PC와 원격 조종기 간에 1초 주기로 생존 신호를 주고받아 통신 단절 시 비상 정지 트리거.
2. **센서 텔레메트리 스트리밍:** IMU, GPS, 초음파 거리 센서가 주기적으로 계측값을 발행하고 주행 제어기가 이를 구독.
3. **상태 모니터링:** 로봇 상태(READY, DRIVING, ERROR)를 모니터링 UI 및 대시보드로 전달.

---

## 7. 오류와 한계 (Pitfalls & Limitations)

### 7.1 콜백 기아 (Callback Starvation)
- **증상:** 타이머 콜백 안에서 0.5초 이상의 무거운 연산(예: 복잡한 이미지 처리)을 수행하면 타이머 주기(1.0초)가 밀리거나 서브스크라이버 콜백이 제때 실행되지 않습니다.
- **원인:** ROS 2의 기본 `SingleThreadedExecutor`는 하나의 스레드로 모든 콜백을 순차 실행하기 때문입니다. `create_timer()`를 사용하더라도 콜백 함수 자체가 오래 걸리면 해당 스레드는 여전히 블로킹됩니다.
- **대응:** 무거운 연산은 별도 작업자 스레드로 분리하거나 `MultiThreadedExecutor`와 `ReentrantCallbackGroup`을 사용해야 합니다 (후속 모듈에서 다룸).

### 7.2 큐 오버플로 (Queue Overflow)
- **증상:** 퍼블리셔가 100Hz로 메시지를 발행하는데 서브스크라이버가 10Hz로만 처리하면 지연이 누적되거나 메시지가 유실됩니다.
- **원인:** 기본 QoS 큐 깊이(`10`)가 가득 차면 오래된 메시지부터 버려지기(Drop) 때문입니다.
- **대응:** 통신 목적에 맞는 적절한 QoS 프로파일(SensorData vs Services)을 선택해야 합니다.

---

## 8. 실습 과제 및 예상 출력 (Hands-on Challenge with Expected Output)

학습자는 다음 3가지 실습 과제를 순차적으로 수행하고, 자신이 수정한 코드의 동작을 단계별로 검증할 수 있습니다.

### 과제 1: 발행 주기 단축 실습
- **목적:** 타이머 주기 변경을 통해 이벤트 디스패칭 빈도 조절 체감.
- **수정 위치:** `core_pubsub_py/minimal_publisher.py`의 `self.timer_period_sec` 값을 `1.0`에서 `0.2`로 변경 (5 Hz 발행).
- **실행 명령:** (워크스페이스 빌드 후) `ros2 run core_pubsub_py minimal_publisher`
- **예상 출력 (Expected Output):**
  ```text
  [INFO] [minimal_publisher]: MinimalPublisher node initialized. Publishing to "heartbeat" at 0.2s interval.
  [INFO] [minimal_publisher]: Published: "Heartbeat seq=0 status=ACTIVE"
  [INFO] [minimal_publisher]: Published: "Heartbeat seq=1 status=ACTIVE"
  [INFO] [minimal_publisher]: Published: "Heartbeat seq=2 status=ACTIVE"
  [INFO] [minimal_publisher]: Published: "Heartbeat seq=3 status=ACTIVE"
  [INFO] [minimal_publisher]: Published: "Heartbeat seq=4 status=ACTIVE"
  [INFO] [minimal_publisher]: Published: "Heartbeat seq=5 status=ACTIVE"
  ```
- **결과가 예상과 다를 때 점검 사항:**
  - 코드 수정 후 `colcon build --packages-select core_pubsub_py`를 다시 실행했는지 확인.
  - 실행 터미널에서 `source install/setup.bash`를 다시 적용했는지 확인.

---

### 과제 2: 방어적 조건부 로깅 실습 (로깅 API 표준화)
- **목적:** 특정 시퀀스 도달 시 조건부로 로그 심각도(Severity)를 높여 경고 로그 출력.
- **로깅 API 표준 고지:** ROS 2 Humble의 `rclpy`는 내부적으로 `self.get_logger().warning(...)`과 `self.get_logger().warn(...)`을 모두 지원하지만, Python 표준 라이브러리(`logging.warning`) 및 PEP 8 권장 사항에 부합하는 **`warning()`을 공식 표준 표기로 사용**합니다.
- **수정 위치:** `minimal_publisher.py`의 `timer_callback` 내부에 마일스톤 조건문 추가:
  ```python
  if self.sequence_number > 0 and self.sequence_number % 10 == 0:
      self.get_logger().warning(f'마일스톤 도달: {self.sequence_number}번째 시퀀스 발행 중')
  ```
- **실행 명령:** `ros2 run core_pubsub_py minimal_publisher`
- **예상 출력 (Expected Output):**
  ```text
  [INFO] [minimal_publisher]: Published: "Heartbeat seq=9 status=ACTIVE"
  [WARN] [minimal_publisher]: 마일스톤 도달: 10번째 시퀀스 발행 중
  [INFO] [minimal_publisher]: Published: "Heartbeat seq=10 status=ACTIVE"
  [INFO] [minimal_publisher]: Published: "Heartbeat seq=11 status=ACTIVE"
  ```
- **결과가 예상과 다를 때 점검 사항:**
  - 파이썬 들여쓰기(Indentation)가 `timer_callback` 스코프 내에 올바르게 위치하는지 확인.
  - 조건문에서 `self.sequence_number > 0`을 누락하여 초기값 `0`에서 경고가 즉시 발생하지 않는지 확인.

---

### 과제 3: 서브스크라이버 페이로드 분석 실습
- **목적:** 메시지 수신 콜백에서 안전하게 문자열 속성을 가공하여 부가 정보 로깅.
- **수정 위치:** `minimal_subscriber.py`의 `listener_callback` 내부에 문자열 길이 계산 로깅 추가:
  ```python
  def listener_callback(self, msg: String) -> None:
      self.get_logger().info(f'Received: "{msg.data}"')
      self.get_logger().info(f'Payload length: {len(msg.data)} bytes')
  ```
- **실행 명령:** (터미널 2에서) `ros2 run core_pubsub_py minimal_subscriber`
- **예상 출력 (Expected Output):**
  ```text
  [INFO] [minimal_subscriber]: MinimalSubscriber node initialized. Listening to "heartbeat" topic...
  [INFO] [minimal_subscriber]: Received: "Heartbeat seq=0 status=ACTIVE"
  [INFO] [minimal_subscriber]: Payload length: 30 bytes
  [INFO] [minimal_subscriber]: Received: "Heartbeat seq=1 status=ACTIVE"
  [INFO] [minimal_subscriber]: Payload length: 30 bytes
  ```
- **결과가 예상과 다를 때 점검 사항:**
  - 퍼블리셔 노드가 동일한 토픽명 `'heartbeat'`로 실행 중인지 확인 (`ros2 topic list`로 확인).
  - 서브스크라이버의 토픽 인터페이스 타입(`std_msgs/msg/String`)이 퍼블리셔와 일치하는지 확인.

---

## 9. 검증 및 테스트 방법 (Verification)

### 9.1 정적 문법 및 린트 검증 (오프라인 환경 검증 가능)
환경 종속성을 최소화하기 위해 Python 모듈 실행 방식(`python3 -m`)을 사용합니다. 모든 명령은 워크스페이스 루트 `/home/cjinw/learning/portfolio`에서 실행합니다:

```bash
# 1. Python 문법 및 바이트코드 컴파일 검사 (오류 없을 시 무출력 종료)
python3 -m py_compile /home/cjinw/learning/portfolio/src/core_pubsub_py/setup.py /home/cjinw/learning/portfolio/src/core_pubsub_py/core_pubsub_py/*.py

# 2. PEP 8 스타일 가이드라인 검사 (줄 길이 120자 기준)
python3 -m flake8 --max-line-length=120 /home/cjinw/learning/portfolio/src/core_pubsub_py/
```

### 9.2 런타임 통신 검증 (ROS 2 Humble 설치 환경)
- **토픽 리스트 확인:** `ros2 topic list` 실행 시 `/heartbeat` 토픽이 출력되어야 합니다.
- **토픽 대역폭 확인:** `ros2 topic hz /heartbeat` 실행 시 약 `1.0 Hz`로 계측되어야 합니다.
- **CLI 직접 구독:** `ros2 topic echo /heartbeat` 실행 시 퍼블리셔가 발행한 메시지가 실시간 출력되어야 합니다.
- **실환경 검증 완료 사실 (`[VERIFIED]`):**
  - Ubuntu 22.04 LTS / ROS 2 Humble 환경에서 `colcon build --packages-select core_pubsub_py` 빌드 성공.
  - `minimal_publisher`와 `minimal_subscriber` 간 `/heartbeat` 토픽 실시간 데이터 송수신 확인.
  - SIGINT(Ctrl+C) 전달 시 `RCLError` 및 Traceback 없이 정상 종료(Exit Code 0) 확인.

---

## 10. 출처 및 라이선스 (Attribution & License)

- **공식 표준 문서:** 
  - [ROS 2 Humble Documentation: Writing a simple publisher and subscriber (Python)](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html)
  - [Python 3.10 Data Model & Classes Tutorial](https://docs.python.org/3.10/tutorial/classes.html)
- **라이선스:** Apache License, Version 2.0
- **저작권 및 배포 고지:** 본 교육 콘텐츠는 오픈소스 공식 규격을 기반으로 독자 설계되었으며, 어떠한 비공개 상용 교재 문장이나 영상을 포함하지 않습니다.
