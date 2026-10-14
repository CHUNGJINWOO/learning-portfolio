# 🤖 로보틱스 소프트웨어 엔지니어링 학습 및 개발 포트폴리오
> **Robotics Software Engineering Portfolio**  
> *(현재 저장소: `CHUNGJINWOO/ros2` / 차기 통합 명칭 후보: `robotics-engineering-portfolio`)*

본 저장소는 **ROS 2 Humble 기반의 분산 로보틱스 시스템**, **Python 객체지향(OOP) 소프트웨어 설계**, **공간 기하 및 매핑 알고리즘**, **컴퓨터 비전 전처리**, **마이크로컨트롤러 임베디드 제어**, 그리고 **클라우드(OCI) 기반 원격 개발 및 고신뢰성 보안 인프라**를 아우르는 통합 로보틱스 엔지니어링 학습 포트폴리오입니다.

---

## 📌 목차 (Table of Contents)

1. [도메인 아키텍처 (Domain Architecture)](#1-도메인-아키텍처-domain-architecture)
2. [도메인별 핵심 학습 내용 및 패키지](#2-도메인별-핵심-학습-내용-및-패키지)
   - [01. Python & 객체지향 설계](#01-python--객체지향-설계)
   - [02. ROS 2 핵심 커리큘럼 & 패키지](#02-ros-2-핵심-커리큘럼--패키지)
   - [03. 로보틱스 공간 수학 및 매핑 알고리즘](#03-로보틱스-공간-수학-및-매핑-알고리즘)
   - [04. 컴퓨터 비전 & 영상처리](#04-컴퓨터-비전--영상처리)
   - [05. 임베디드 시스템 & 센서 제어](#05-임베디드-시스템--센서-제어)
   - [06. 클라우드 인프라 & 운영 보안](#06-클라우드-인프라--운영-보안)
3. [LIMO 로봇 플랫폼 & 시뮬레이션 소스 (`src/`)](#3-limo-로봇-플랫폼--시뮬레이션-소스-src)
4. [빌드 및 검증 가이드 (Build & Run Guide)](#4-빌드-및-검증-가이드-build--run-guide)
5. [현재 상태 및 검증 범위 (Verification Scope)](#5-현재-상태-및-검증-범위-verification-scope)
6. [문서 및 리소스 색인 (Documentation Index)](#6-문서-및-리소스-색인-documentation-index)

---

## 1. 도메인 아키텍처 (Domain Architecture)

본 저장소는 로보틱스 개발 역량을 체계적으로 입증할 수 있도록 6대 전문 도메인으로 구조화되어 있습니다:

```text
ros2/ (향후 robotics-engineering-portfolio 제안)
├── 01_python_and_oop/             # [도메인 1] Python 객체지향(OOP) 및 수치 신호 모델링
├── 02_ros2_core_curriculum/       # [도메인 2] ROS 2 핵심 5대 Phase 패키지 및 심층 개념 가이드
│   ├── docs/                      # Phase 01~05 개념/설계/트러블슈팅 가이드
│   └── src/                       # 5개 독립 ament_python 정규 ROS 2 패키지
├── 03_robotics_algorithms/        # [도메인 3] 브레젠험 레이 트레이싱 및 점유격자 좌표 수학
├── 04_computer_vision/            # [도메인 4] NumPy 행렬 조작, OpenCV 필터, 색공간, 에지/이진화
├── 05_embedded_systems/           # [도메인 5] Wokwi 기반 아두이노 마이크로컨트롤러 8종 시뮬레이션
├── 06_cloud_and_devops/           # [도메인 6] OCI 원격 개발 환경, Fast DDS, Tailscale, Fail2ban
├── learning/                      # 대화형 주피터 노트북 5종 및 my_package_rclcpy, LIMO 기술문서
└── src/                           # AgileX LIMO 로봇 ROS 2 패키지 및 원격 제어 노드
```

---

## 2. 도메인별 핵심 학습 내용 및 패키지

### 01. Python & 객체지향 설계
- **경로:** [`01_python_and_oop/`](01_python_and_oop/README.md)
- **핵심 역량:**
  - 절차적 무한 루프(`while True` + `time.sleep`)의 스레드 블로킹 안티패턴 분석
  - 클래스 상속과 `super().__init__()`을 통한 ROS 2 Node 클래스 캡슐화
  - 클래스 변수(인스턴스 간 상태 오염)와 인스턴스 변수(`self`, 독립 힙 메모리 할당)의 메모리 격리
  - NumPy 기반 연속 사인파 수식의 이산 시간 수열 샘플링 및 시각화
- **연계 노트북:** [`learning/notebooks/01_sin_modeling.ipynb`](learning/notebooks/01_sin_modeling.ipynb), [`learning/notebooks/02_python_oop_class.ipynb`](learning/notebooks/02_python_oop_class.ipynb)

---

### 02. ROS 2 핵심 커리큘럼 & 패키지
- **경로:** [`02_ros2_core_curriculum/`](02_ros2_core_curriculum/README.md)
- **개념 가이드:**
  - [Phase 1. Python OOP와 ROS 2 Node 수명주기](02_ros2_core_curriculum/docs/01_python_oop_and_ros2_node.md)
  - [Phase 2. 동적 파라미터 및 QoS 정책 심층 실습](02_ros2_core_curriculum/docs/02_parameters_and_qos.md)
  - [Phase 3. Services(RPC) 및 Actions(선점/취소) 통신 패러다임](02_ros2_core_curriculum/docs/03_services_and_actions.md)
  - [Phase 4. Launch 시스템 및 시스템 오케스트레이션](02_ros2_core_curriculum/docs/04_launch_and_system_orchestration.md)
  - [Phase 5. TF2 공간 좌표 변환 및 결정론적 예외 진단](02_ros2_core_curriculum/docs/05_tf2_coordinate_transforms.md)
- **실전 ament_python 패키지 5종:**
  1. `core_pubsub_py`: 타이머 기반 하트비트 텔레메트리 퍼블리셔 및 이벤트 서브스크라이버
  2. `param_qos_py`: 원자적 파라미터 검증 가드, Best Effort 센서 스트리머, Transient Local 래칭 퍼블리셔
  3. `service_action_py`: Future 기반 비동기 서비스 클라이언트, 취소/선점 제어 피보나치 액션 서버
  4. `launch_orchestration_py`: CLI 오버라이드, 네임스페이스 격리, `OnProcessExit` 이벤트 셧다운 핸들러
  5. `tf2_transforms_py`: 순수 math ZYX 오일러-사원수 변환, 정적/동적 브로드캐스터, 3대 TF2 예외 진단 노드

---

### 03. 로보틱스 공간 수학 및 매핑 알고리즘
- **경로:** [`03_robotics_algorithms/`](03_robotics_algorithms/README.md)
- **핵심 역량:**
  - **브레젠험 레이 트레이싱 (`ray_trace.py`):** LiDAR 빔이 통과하는 2D 정수 격자 경로를 계산하여 관통 셀(Free)과 반사 셀(Occupied)을 분리
  - **점유격자 좌표 변환 (`map_inspector.py`):** 연속 월드 좌표 `(x, y)`와 이산 격자 인덱스 `(grid_x, grid_y)` 간 상호 변환 및 해상도/원점 오프셋 연산
  - **격자 델타 모니터 (`map_change_monitor.py`):** 실시간 맵 토픽 갱신량 추적

---

### 04. 컴퓨터 비전 & 영상처리
- **경로:** [`04_computer_vision/`](04_computer_vision/README.md)
- **핵심 역량:**
  - NumPy 다차원 이미지 배열 슬라이싱, 차원 재구성, 채널 분리
  - BGR ↔ HSV 색공간 변환 및 조명 강인 차선 마스킹
  - Gaussian, Median 평활화 필터를 이용한 노이즈 제거
  - Canny Edge, Sobel 미분 연산자, 적응형 이진화 및 ROI(관심영역) 마스킹
- **학업 아카이브 연계:** 원본 교과목 실습 자료는 `school/2026-2/`에 안전하게 보존되어 있습니다.

---

### 05. 임베디드 시스템 & 센서 제어
- **경로:** [`05_embedded_systems/`](05_embedded_systems/README.md)
- **핵심 역량:**
  - Wokwi 기반 아두이노(C/C++) 마이크로컨트롤러 8종 시뮬레이션
  - DIP 스위치(비트 입력), FND 7세그먼트(디코딩 표시), LED GPIO 제어
  - PIR 모션 센서(인터럽트 감지), 2축 조이스틱(ADC 및 데드존), 풀업/풀다운 택트 스위치, 가변저항(분압 법칙)

---

### 06. 클라우드 인프라 & 운영 보안
- **경로:** [`06_cloud_and_devops/`](06_cloud_and_devops/README.md)
- **핵심 역량:**
  - Oracle Cloud Infrastructure(OCI) Always-Free 인스턴스 기반 `code-server` 웹 IDE 구축
  - Tailscale VPN 가상 사설망 및 Fast DDS Discovery Server 분산 통신
  - Cloudflare Funnel 보안 취약점 진단 및 `fail2ban` + `msmtp` 침입 차단/실시간 경보 체계 구축
  - OCI 블록 볼륨 iSCSI 마운트 및 `rclone` 이중 백업 자동화 파이프라인
- **세부 문서:** [ARCHITECTURE.md](06_cloud_and_devops/docs/ARCHITECTURE.md), [SETUP_GUIDE.md](06_cloud_and_devops/docs/SETUP_GUIDE.md), [CLOUD_WEB_IDE_SECURITY_RECOVERY.md](06_cloud_and_devops/docs/CLOUD_WEB_IDE_SECURITY_RECOVERY.md)

---

## 3. LIMO 로봇 플랫폼 & 시뮬레이션 소스 (`src/`)

- **패키지 구성:**
  - `limo_base`: 시리얼 통신 기반 LIMO 로봇 모터 드라이버 및 센서 인터페이스
  - `limo_car`: Gazebo 시뮬레이션 환경 브링업 및 환경 설정
  - `limo_description`: URDF/Xacro 로봇 기구학 형상 모델 및 COLLADA DAE 메시
  - `limo_msgs`: 로봇 전용 커스텀 상태 메시지 (`LimoStatus.msg`)
  - `remote_teleop_node.py`: 분산 환경 원격 조향 퍼블리셔 노드
- **메시 최적화 기록:**
  - Xacro/URDF 어디에서도 참조되지 않는 중복 STL 파일 4종(89.6 MB)을 안전하게 정리하여 저장소를 대폭 경량화하였습니다.
  - 시뮬레이션 및 RViz 렌더링에 필수적인 COLLADA(`.dae`) 메시는 온전히 유지되어 정상 시각화가 가능합니다.
- **실기기 프로젝트 연계:**
  - 실제 AgileX LIMO Pro 하드웨어 기반의 온보드 PC 구동, YDLiDAR T-mini Plus 센서 검증, TF 트리 분석 및 실차 SLAM 주행 기록은 전용 프로젝트 저장소인 [`CHUNGJINWOO/Capstone1_limo`](https://github.com/CHUNGJINWOO/Capstone1_limo)에서 독립적으로 관리됩니다.

---

## 4. 빌드 및 검증 가이드 (Build & Run Guide)

### 4.1 ROS 2 Humble 빌드 환경 구성

```bash
# 1. ROS 2 기본 환경 로드
source /opt/ros/humble/setup.bash

# 2. 통합 학습 패키지 빌드 (02_ros2_core_curriculum)
cd ~/learning/ros2  # 또는 클론한 저장소 루트
colcon build --symlink-install --packages-select \
  core_pubsub_py \
  param_qos_py \
  service_action_py \
  launch_orchestration_py \
  tf2_transforms_py

# 3. 환경 반영
source install/setup.bash
```

### 4.2 주요 검증 명령어

```bash
# [Phase 1] 하트비트 통신 테스트
ros2 run core_pubsub_py minimal_publisher
# (다른 터미널) ros2 run core_pubsub_py minimal_subscriber

# [Phase 2] 동적 파라미터 갱신 및 QoS 스트리밍
ros2 run param_qos_py dynamic_telemetry_publisher
ros2 param set /dynamic_telemetry_publisher publish_rate_hz 5.0

# [Phase 3] 피보나치 액션 서버 및 비동기 클라이언트
ros2 run service_action_py fibonacci_action_server
ros2 run service_action_py fibonacci_action_client

# [Phase 4] 오케스트레이션 런치 통합 실행
ros2 launch launch_orchestration_py 05_integrated_system.launch.py

# [Phase 5] TF2 좌표 변환 데모 런치
ros2 launch tf2_transforms_py tf2_demo.launch.py

# [도메인 3] 레이 트레이싱 공간 수학 시뮬레이션
python3 03_robotics_algorithms/ray_trace.py
```

---

## 5. 현재 상태 및 검증 범위 (Verification Scope)

| 도메인 | 항목 | 검증 수준 | 상세 근거 |
| :--- | :--- | :---: | :--- |
| **01. Python/OOP** | 수치 모델링 & OOP 클래스 | ✅ 실행 검증 완료 | NumPy 사인파 및 OOP 상속 주피터 노트북 실행 확인 |
| **02. ROS 2 Core** | 5개 정규 패키지 빌드 | ✅ 빌드/코드 검증 | `colcon build` 성공, ament linter 규격 준수 |
| **02. ROS 2 Core** | TF2 및 좌표 변환 | ✅ 문법/노드 검증 | ZYX 오일러 사원수 변환, 정적/동적 브로드캐스터 구현 |
| **03. Algorithms** | 브레젠험 레이 트레이싱 | ✅ 수학 검증 완료 | 격자 셀 관통 및 점유 확률 산출 단독 시뮬레이션 통과 |
| **03. Algorithms** | 점유격자 좌표 변환기 | ✅ 코드 검증 완료 | `nav_msgs/OccupancyGrid` 해상도/원점 오프셋 연산 구조 확인 |
| **04. Vision** | OpenCV 기초 파이프라인 | 🔍 교과목 실습 검증 | 색공간 변환, 블러, Canny 에지, 이진화 원본 검증 |
| **05. Embedded** | Wokwi 아두이노 시뮬레이션 | ✅ 회로/코드 확인 | 8종 시뮬레이션 diagram.json 및 INO 소스 무결성 확인 |
| **06. Cloud/DevOps**| Tailscale VPN & code-server | ✅ 실운영 검증 | 웹 IDE 접근 및 사설망 원격 개발 환경 운영 기록 보유 |
| **06. Cloud/DevOps**| Fail2ban 침입 차단 | ✅ 실전 대응 완료 | Cloudflare Funnel 공격 차단 룰셋 및 실시간 알림 검증 |
| **LIMO Application**| LIMO ROS 2 소스 | ⚠️ 모델 보존/정리 | DAE 시각화 모델 보존, 미참조 STL(89.6MB) 정리 완료 |
| **LIMO Application**| 실기기 주행 및 SLAM | 🔄 캡스톤 프로젝트 연계 | `Capstone1_limo` 저장소에서 LIMO Pro 실차 검증 진행 중 |

---

## 6. 문서 및 리소스 색인 (Documentation Index)

### 📖 학습 및 커리큘럼
- [01. Python & OOP 학습 가이드](01_python_and_oop/README.md)
- [02. ROS 2 핵심 커리큘럼 대시보드](02_ros2_core_curriculum/README.md)
  - [Phase 1: OOP & Node 수명주기](02_ros2_core_curriculum/docs/01_python_oop_and_ros2_node.md)
  - [Phase 2: 파라미터 & QoS](02_ros2_core_curriculum/docs/02_parameters_and_qos.md)
  - [Phase 3: Services & Actions](02_ros2_core_curriculum/docs/03_services_and_actions.md)
  - [Phase 4: Launch 시스템](02_ros2_core_curriculum/docs/04_launch_and_system_orchestration.md)
  - [Phase 5: TF2 공간 변환](02_ros2_core_curriculum/docs/05_tf2_coordinate_transforms.md)
- [03. 로보틱스 알고리즘 & 레이 트레이싱](03_robotics_algorithms/README.md)
- [04. 컴퓨터 비전 파이프라인 가이드](04_computer_vision/README.md)
- [05. 임베디드 시스템 Wokwi 시뮬레이션](05_embedded_systems/README.md)
- [기존 Turtlesim 및 LIMO 심화 학습 기록](learning/README.md)

### ☁️ 인프라 및 운영
- [06. 클라우드 인프라 & 운영 보안 대시보드](06_cloud_and_devops/README.md)
- [시스템 아키텍처 및 기술 스택 선정 이유](06_cloud_and_devops/docs/ARCHITECTURE.md)
- [원격 개발 환경 단계별 구축 가이드](06_cloud_and_devops/docs/SETUP_GUIDE.md)
- [클라우드 저장소 및 백업 인프라 구축기](06_cloud_and_devops/docs/CLOUD.md)
- [네트워크 및 미들웨어 트러블슈팅 일지](06_cloud_and_devops/docs/TROUBLESHOOTING.md)
- [웹 IDE 보안 침해 복구 및 fail2ban 설정](06_cloud_and_devops/docs/CLOUD_WEB_IDE_SECURITY_RECOVERY.md)
- [인프라 및 백업 자동화 스크립트 모음](06_cloud_and_devops/scripts/)

### 🚗 외부 연계 프로젝트
- [Capstone1_limo 실전 자율주행 프로젝트](https://github.com/CHUNGJINWOO/Capstone1_limo)
- [Guidebook AI 개발 표준 가이드북](https://github.com/CHUNGJINWOO/guidebook)
