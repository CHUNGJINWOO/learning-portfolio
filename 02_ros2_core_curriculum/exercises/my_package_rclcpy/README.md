# my_package_rclcpy

`my_package_rclcpy`는 ROS 2 Humble 환경에서 Python(`rclpy`)을 이용해 노드 생성, 토픽 발행/구독, 서비스 서버/클라이언트 통신을 학습하고 실습하기 위해 작성된 ROS 2 Python 표준 패키지입니다.

대화형 환경(Jupyter Notebook)에서 개별적으로 실습했던 `rclpy` 통신 개념을 ROS 2 표준 패키지 구조(`ament_python`, `setup.py`, `package.xml`, `entry_points`)로 정형화하여 빌드 및 배포할 수 있도록 구성되어 있습니다.

---

## 🔗 연관 학습 자료 및 발전 경로 (Pedagogical Links)

본 패키지는 도메인 02 커리큘럼 내에서 다음과 같은 체계적인 3단계 학습 경로로 연결되어 있습니다:

- **1단계 (선행 실습):** [`../../notebooks/`](../../notebooks/) — Turtlesim 대화형 주피터 노트북을 통한 기초 토픽 발행/구독 시각적 탐색
- **2단계 (현재 단계):** **`my_package_rclcpy`** — 단편 스크립트를 클래스 상속(`Node`) 및 진입점(`setup.py`)을 갖춘 독립 ROS 2 패키지로 정형화
- **3단계 (심화 패키지):** [`../../src/core_pubsub_py/`](../../src/core_pubsub_py/) — 타입 힌트, 정형 로거, 자원 해제 루틴을 갖춘 구조화된 정규 학습 패키지
- **연계 이론 가이드:** [`../../docs/01_python_oop_and_ros2_node.md`](../../docs/01_python_oop_and_ros2_node.md) — Python OOP 설계와 Node 수명주기 이론 해설

---

## 1. 패키지 개요

- **패키지 이름**: `my_package_rclcpy`
- **빌드 타입**: `ament_python`
- **지원 환경**: ROS 2 Humble / Ubuntu 22.04 LTS (Python 3.10)
- **주요 의존성**:
  - `rclpy`: ROS 2 Python 클라이언트 라이브러리
  - `std_msgs`: ROS 2 표준 메시지 인터페이스 (`String` 등)
  - `example_interfaces`: 예제 인터페이스 (`AddTwoInts` 서비스 등)

---

## 2. 포함된 노드 및 실행 항목

`setup.py`의 `console_scripts` 엔트리포인트에 등록된 5개의 실행 노드 목록입니다.

| 실행 명령어 (Console Script) | 소스 파일 위치 | 노드 이름 | 통신 유형 및 대상 인터페이스 | 주요 기능 |
| :--- | :--- | :--- | :--- | :--- |
| `my_first_node` | `my_package_rclcpy/my_first_node.py` | `my_first_node` | 기본 노드 라이프사이클 | `Node` 클래스를 상속받는 기본 객체지향 노드 생성 및 `'Hello ROS 2!'` 로깅 |
| `talker` | `my_package_rclcpy/talker.py` | `talker` | Topic Publisher (`std_msgs/msg/String`, 토픽명: `chatter`) | 0.5초 주기의 타이머 콜백을 통해 한글 안내 메시지와 카운트를 지속 발행 |
| `listener` | `my_package_rclcpy/listener.py` | `listener` | Topic Subscriber (`std_msgs/msg/String`, 토픽명: `chatter`) | `chatter` 토픽을 구독하여 수신된 메시지를 로거(`I heard: ...`)로 출력 |
| `add_two_ints_server` | `my_package_rclcpy/add_two_ints_server.py` | `add_two_ints_server` | Service Server (`example_interfaces/srv/AddTwoInts`, 서비스명: `add_two_ints`) | 두 정수(`a`, `b`)를 요청받아 합계(`sum = a + b`)를 계산하여 응답 반환 |
| `add_two_ints_client` | `my_package_rclcpy/add_two_ints_client.py` | `add_two_ints_client` | Service Client (`example_interfaces/srv/AddTwoInts`, 서비스명: `add_two_ints`) | 서비스 준비 상태를 대기한 뒤 `a=12`, `b=34`를 비동기 호출하고 완료 시까지 스핀하여 결과 로깅 |

---

## 3. 패키지 빌드 방법

패키지 소스는 `02_ros2_core_curriculum/exercises/my_package_rclcpy`에 있습니다. 이 저장소의 기본 빌드 위치는 저장소 루트입니다. 아래 명령은 이번 문서 정리에서 실행 검증하지 않았습니다.

```bash
source /opt/ros/humble/setup.bash
cd ~/learning/learning-portfolio  # 또는 클론한 저장소 루트
colcon list  # 패키지 탐색 결과 확인
colcon build --symlink-install --packages-select my_package_rclcpy
source install/setup.bash
```

새 터미널에서도 ROS 2 기본 환경과 저장소 루트의 `install/setup.bash`를 소싱합니다. 아래 세 방법은 별도의 `~/ros2_ws`를 사용할 때의 선택지이며, 해당 워크스페이스의 overlay를 사용합니다.

### 방법 1: 외부 경로 직접 지정 빌드 (`--paths` 옵션 활용)
`colcon`의 `--paths` 옵션을 사용하면 워크스페이스 디렉터리 구조를 변경하지 않고도 외부 경로의 패키지를 직접 지정하여 빌드할 수 있습니다 (`colcon-core 0.21.3+`에서 공식 지원).

```bash
# 1. ROS 2 기본 환경 설정 로드
source /opt/ros/humble/setup.bash

# 2. 워크스페이스 디렉터리로 이동
cd ~/ros2_ws

# 3. 외부 경로의 패키지를 직접 지정하여 빌드
colcon build --symlink-install --paths ~/learning/learning-portfolio/02_ros2_core_curriculum/exercises/my_package_rclcpy

# 4. 빌드 결과물 환경 변수 반영
source install/setup.bash
```
- **장점**: 워크스페이스 내부에 별도 파일이나 링크를 생성하지 않아 깔끔하며, 저장소의 원본 소스를 그대로 빌드합니다.

### 방법 2: 심볼릭 링크(Symbolic Link) 연결 후 빌드
`~/ros2_ws/src/` 아래에 저장소의 패키지를 가리키는 심볼릭 링크를 생성하여 표준 워크스페이스 패키지처럼 빌드하는 방법입니다.

```bash
# 심볼릭 링크 생성 (원본: ~/learning/learning-portfolio/02_ros2_core_curriculum/exercises/my_package_rclcpy)
ln -s ~/learning/learning-portfolio/02_ros2_core_curriculum/exercises/my_package_rclcpy ~/ros2_ws/src/my_package_rclcpy

# 워크스페이스에서 패키지 선택 빌드
cd ~/ros2_ws
colcon build --symlink-install --packages-select my_package_rclcpy
source install/setup.bash
```
- **장점 및 특징**: 저장소의 원본 소스를 실시간으로 참조하므로 `~/learning/learning-portfolio`에서 소스를 수정하면 워크스페이스에도 즉시 반영되어 단일 원본(Single Source of Truth)이 유지됩니다.

### 방법 3: 패키지 복사(Copy) 후 빌드
`~/learning/learning-portfolio/02_ros2_core_curriculum/exercises/my_package_rclcpy`를 `~/ros2_ws/src/` 디렉터리로 직접 복사하여 빌드하는 방법입니다.

```bash
cp -r ~/learning/learning-portfolio/02_ros2_core_curriculum/exercises/my_package_rclcpy ~/ros2_ws/src/
cd ~/ros2_ws
colcon build --symlink-install --packages-select my_package_rclcpy
source install/setup.bash
```
- **주의점**: 소스 코드가 두 위치에 독립적으로 복제되므로, 한쪽에서 수정한 내용이 다른 쪽에 자동 반영되지 않아 코드 불일치(Drift)가 발생할 수 있습니다.

> [!NOTE]
> - `--symlink-install` 옵션을 지정하면 Python 소스 파일(`*.py`)을 수정하더라도 매번 `colcon build`를 재실행할 필요 없이 수정 사항이 즉시 런타임에 반영됩니다.
> - 기존 `~/ros2_ws/src/`에 이미 `my_package_rclcpy`가 존재하는 경우에는 중복 심볼릭 링크나 덮어쓰기 복사를 피하고 **방법 1**을 사용하거나 기존 패키지를 그대로 빌드하십시오.

---

## 4. 노드 실행 및 검증 방법

빌드 후 환경을 `source`한 각 터미널에서 아래 명령어로 노드를 실행합니다.

### 4.1. 기본 노드 실행 (`my_first_node`)
```bash
ros2 run my_package_rclcpy my_first_node
```
- **예상 출력**:
  ```text
  [INFO] [1728551400.000000000] [my_first_node]: Hello ROS 2!
  ```
  *(종료는 `Ctrl+C`)*

### 4.2. 토픽 발행 및 구독 (`talker` & `listener`)

**터미널 1 (퍼블리셔 실행):**
```bash
ros2 run my_package_rclcpy talker
```
- **예상 출력**:
  ```text
  [INFO] [talker]: Published: "안녕하세요! ROS 2 실습 중입니다. Count: 0"
  [INFO] [talker]: Published: "안녕하세요! ROS 2 실습 중입니다. Count: 1"
  ...
  ```

**터미널 2 (서브스크라이버 실행):**
```bash
ros2 run my_package_rclcpy listener
```
- **예상 출력**:
  ```text
  [INFO] [listener]: I heard: "안녕하세요! ROS 2 실습 중입니다. Count: 0"
  [INFO] [listener]: I heard: "안녕하세요! ROS 2 실습 중입니다. Count: 1"
  ...
  ```

**CLI 토픽 검증:**
```bash
# 활성 토픽 확인
ros2 topic list
# /chatter

# 토픽 데이터 직접 에코
ros2 topic echo /chatter
```

### 4.3. 서비스 서버 및 클라이언트 (`add_two_ints_server` & `add_two_ints_client`)

**터미널 1 (서비스 서버 실행):**
```bash
ros2 run my_package_rclcpy add_two_ints_server
```
- **예상 출력**:
  ```text
  [INFO] [add_two_ints_server]: AddTwoInts service server is ready.
  ```

**터미널 2 (서비스 클라이언트 실행):**
```bash
ros2 run my_package_rclcpy add_two_ints_client
```
- **예상 출력 (클라이언트 측)**:
  ```text
  [INFO] [add_two_ints_client]: Result: 12 + 34 = 46
  ```
- **예상 출력 (서버 측)**:
  ```text
  [INFO] [add_two_ints_server]: Request: 12 + 34 = 46
  ```

**CLI 서비스 직접 호출 검증:**
```bash
ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: 10, b: 20}"
# response: example_interfaces.srv.AddTwoInts_Response(sum=30)
```

---

## 5. 테스트 실행 방법

패키지 코드 스타일 및 린트 검사는 다음 명령어로 수행할 수 있습니다.

```bash
cd ~/ros2_ws
colcon test --packages-select my_package_rclcpy
colcon test-result --verbose
```

포함된 테스트:
- `test/test_copyright.py`: 저작권 헤더 검사
- `test/test_flake8.py`: Python 코드 스타일 (PEP 8 / flake8) 검사
- `test/test_pep257.py`: 독스트링 규격 (PEP 257) 검사

---

## 6. 확인된 제한 사항 및 참고 사항

1. **서비스 클라이언트 인자 고정**:
   - `add_two_ints_client.py`는 현재 코드 내부에 `a=12`, `b=34`가 하드코딩되어 있습니다. 커맨드라인 인자(`sys.argv`)를 통한 동적 값 입력 기능은 후속 단계 개선 과제입니다.
2. **패키지 메타데이터 TODO 항목**:
   - `package.xml`과 `setup.py`에 `<license>TODO: License declaration</license>`, `maintainer_email='cjinw@todo.todo'`가 기본값 상태로 남아 있습니다.
3. **기본 노드 라이프사이클**:
   - `my_first_node.py`는 `__init__`에서 1회 로깅 후 타이머 없이 `spin()` 상태를 유지합니다 (`Ctrl+C`로 종료).
