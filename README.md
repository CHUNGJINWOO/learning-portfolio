# 🤖 ROS 2 로보틱스 개발 및 학습 저장소

> **ROS 2 Humble 기반의 프로그래밍 학습 기록**, **AgileX LIMO 로봇 시뮬레이션 및 분산 제어**, **클라우드(OCI) 기반 원격 개발 인프라**를 통합 관리하는 저장소입니다.

---

## 📌 목차 (Table of Contents)

1. [프로젝트 소개 (Introduction)](#1-프로젝트-소개-introduction)
2. [저장소 구조 (Repository Architecture)](#2-저장소-구조-repository-architecture)
3. [ROS 2 학습 시작하기 (Learning Records)](#3-ros-2-학습-시작하기-learning-records)
4. [LIMO 로봇 개발 및 제어 (LIMO Robot Application)](#4-limo-로봇-개발-및-제어-limo-robot-application)
5. [원격 개발 및 분산 통신 인프라 (Cloud Infrastructure)](#5-원격-개발-및-분산-통신-인프라-cloud-infrastructure)
6. [현재 상태 및 검증 범위 (Status & Verification Scope)](#6-현재-상태-및-검증-범위-status-verification-scope)
7. [문서 탐색 (Documentation Index)](#7-문서-탐색-documentation-index)

---

## 1. 프로젝트 소개 (Introduction)

본 저장소는 로보틱스 소프트웨어 개발 역량을 단계별로 축적하고 실전 플랫폼에 적용하기 위해 구성된 통합 프로젝트 저장소입니다. 세 가지 핵심 축으로 구성되어 있습니다:

1. **ROS 2 Python 프로그래밍 기초 학습**: 수학적 신호 모델링과 객체지향(OOP) 클래스 설계부터 시작하여, 대화형 환경(Jupyter Notebook)에서의 Turtlesim 제어 실습, 그리고 정식 `ament_python` 기반 ROS 2 패키지 구축까지의 단계별 기록을 관리합니다.
2. **AgileX LIMO 자율주행 플랫폼 및 원격 제어**: 소형 모바일 로봇인 LIMO의 ROS 2 드라이버, 가제보(Gazebo) 시뮬레이션 모델, URDF/Xacro 형상 및 메시지 패키지와 더불어 로컬-클라우드 간 원격 조향을 위한 퍼블리셔 노드를 포함합니다.
3. **클라우드 기반 원격 개발 및 고신뢰성 인프라**: 로컬 노트북의 하드웨어 한계를 극복하기 위해 Oracle Cloud Infrastructure(OCI) 상에 웹 IDE(`code-server`)를 구축하고, 사설 가상망(`Tailscale VPN`), Fast DDS Discovery Server 분산 통신, 자동화 백업 체계를 결합한 원격 로보틱스 개발 환경을 운영합니다.

---

## 2. 저장소 구조 (Repository Architecture)

실제 저장소 디렉터리 및 주요 파일 구성은 다음과 같습니다:

```text
ros2/
├── README.md                      # [본 문서] 저장소 통합 대시보드 및 인덱스
├── learning/                      # ROS 2 Python 단계별 학습 기록 영역
│   ├── README.md                  # 학습 로드맵 및 단계별 실습 가이드
│   ├── 01_ros2_core_and_interfaces.md     # 1단계: ROS 2 통신 메커니즘, 커스텀 인터페이스, 센서 규격
│   ├── 02_limo_application_programming.md # 2단계: LIMO IMU 회전, LiDAR 비상정지, 카메라 차선인식, 통합제어
│   ├── 03_tf2_and_pose_control.md         # 3단계: TF2 좌표 변환, LIMO TF 트리, 목표 자세 제어(move_to_pose)
│   ├── 04_local_state_estimation.md       # 4단계: 지역 위치 추정 기초 (엔코더 슬립, IMU 드리프트, 센서융합)
│   ├── notebooks/                 # 대화형 주피터 노트북 5종 (01~05)
│   │   ├── 01_sin_modeling.ipynb             # 1단계: NumPy 기반 사인파 신호 모델링
│   │   ├── 02_python_oop_class.ipynb         # 2단계: OOP 클래스 상속 및 super()
│   │   ├── 03_topic_publisher_turtlesim.ipynb # 3단계: Topic Publisher (/turtle1/cmd_vel)
│   │   ├── 04_topic_subscriber_turtlesim.ipynb# 4단계: Topic Subscriber (/turtle1/pose)
│   │   └── 05_service_client_turtlesim.ipynb  # 5단계: Service Client (/turtle1/teleport_absolute)
│   └── my_package_rclcpy/         # ROS 2 Python 정규 패키지
│       ├── README.md              # 패키지 빌드 방법 및 5개 노드 실행 가이드
│       ├── package.xml            # 패키지 메타데이터 및 의존성 선언
│       ├── setup.py               # console_scripts 엔트리포인트 5종 등록
│       └── my_package_rclcpy/     # 소스 코드 (my_first_node, talker, listener 등)
├── src/                           # 로봇 애플리케이션 소스 코드 영역
│   ├── README.md                  # 소스 코드 및 알고리즘 설계 문서
│   ├── remote_teleop_node.py      # 로컬에서 클라우드 로봇으로 Twist 명령을 전송하는 원격 제어 노드
│   ├── limo_ros2/                 # AgileX LIMO 로봇 공식 패키지 모음
│   │   ├── limo_base/             # LIMO 베이스 드라이버 노드
│   │   ├── limo_car/              # Gazebo 시뮬레이션 구동 런치 및 환경 설정
│   │   ├── limo_description/      # 로봇 URDF/Xacro 모델 및 3D 메시(DAE, STL)
│   │   ├── limo_msgs/             # LIMO 전용 커스텀 상태 메시지
│   │   └── Readme.md              # LIMO 패키지 설명서
│   └── gazebo_ros_pkgs/           # Gazebo 시뮬레이션 연동을 위한 플레이스홀더 (현재 비어 있음)
├── docs/                          # 인프라, 아키텍처 및 트러블슈팅 전문 문서
│   ├── ARCHITECTURE.md            # 시스템 아키텍처 및 기술 스택 선정 이유
│   ├── SETUP_GUIDE.md             # OCI, Tailscale, code-server 단계별 구축 가이드
│   ├── CLOUD.md                   # 시뮬레이션 결과물 클라우드 저장 및 백업 인프라 구축기
│   ├── TROUBLESHOOTING.md         # 네트워크 충돌, 보안, XML 파싱 트러블슈팅 일지
│   ├── CLOUD_WEB_IDE_SECURITY_RECOVERY.md # 웹 IDE 보안 침해 분석 및 fail2ban 복구 기록
│   └── README_CLOUD_IDE_UPDATE.md # 원격 개발 환경 운영 및 보안 패치 기록
├── scripts/                       # 관리, 보안, 백업 자동화 스크립트 모음
│   ├── 01 setup ssh key · SH      # SSH 키 생성 및 클라우드 서버 등록
│   ├── 02 mount data volume · SH  # OCI 블록 볼륨 포맷 및 마운트
│   ├── 03 test transfer · SH      # 파일 전송 연결 테스트
│   ├── 04 setup rclone · SH       # Google Drive / Cloud rclone 연동 설정
│   ├── 05 backup · SH             # rclone 기반 이중 백업 실행
│   ├── 06_register_task_scheduler.ps1 # Windows 작업 스케줄러 등록 스크립트
│   └── 07 harden code server · SH # fail2ban + msmtp 보안 강화 스크립트
└── wokwi/                         # 아두이노/임베디드 시뮬레이션 프로젝트들
    └── 임베디드 시스템 ...         # LED, FND, 스위치, 조이스틱, 센서 등 9종 Wokwi 시뮬레이션
```

---

## 3. ROS 2 학습 시작하기 (Learning Records)

기초 개념 학습과 실습 코드는 [`learning/`](learning/README.md) 디렉터리에 체계화되어 있습니다.

### 3.1. 대화형 실습 순서 (Jupyter Notebooks)
Turtlesim을 활용하여 통신 메커니즘을 빠르게 실험한 5개의 노트북입니다:
1. **[01_sin_modeling.ipynb](learning/notebooks/01_sin_modeling.ipynb)**: NumPy와 Matplotlib을 활용한 사인파 수식 모델링 및 그래프 시각화
2. **[02_python_oop_class.ipynb](learning/notebooks/02_python_oop_class.ipynb)**: 클래스 선언, 상속, 메서드 오버라이딩, `super()`를 통한 ROS 2 Node 클래스 상속 선수학습
3. **[03_topic_publisher_turtlesim.ipynb](learning/notebooks/03_topic_publisher_turtlesim.ipynb)**: `geometry_msgs/msg/Twist` 메시지 발행을 통한 거북이 이동 제어
4. **[04_topic_subscriber_turtlesim.ipynb](learning/notebooks/04_topic_subscriber_turtlesim.ipynb)**: `turtlesim/msg/Pose` 메시지 구독을 통한 실시간 좌표 수신
5. **[05_service_client_turtlesim.ipynb](learning/notebooks/05_service_client_turtlesim.ipynb)**: `turtlesim/srv/TeleportAbsolute` 서비스 클라이언트 비동기 호출 및 서비스 대기

> [!NOTE]
> 자세한 학습 로드맵과 노트북 실행 시 주의사항(대화형 spin 블로킹 탈출 기법, 서비스 미기동 시 대기 루프 분석)은 [`learning/README.md`](learning/README.md)를 참고하십시오.

### 3.2. 정규 ROS 2 패키지 (`my_package_rclcpy`)
대화형 실습을 거쳐 ROS 2 표준 빌드 시스템으로 패키징한 예제입니다.

- **포함된 노드**:
  - `my_first_node`: `Node` 상속 기반 최소 노드
  - `talker` / `listener`: `std_msgs/msg/String` 기반 토픽 발행/구독
  - `add_two_ints_server` / `add_two_ints_client`: `example_interfaces/srv/AddTwoInts` 기반 정수 덧셈 서비스 서버/클라이언트
- **빌드 방법 (`colcon` 외부 경로 직접 빌드 권장)**:
  ```bash
  source /opt/ros/humble/setup.bash
  cd ~/ros2_ws
  colcon build --symlink-install --paths ~/ros2/learning/my_package_rclcpy
  source install/setup.bash
  ```
- **상세 안내**: 노드별 실행 및 검증 명령어는 [`learning/my_package_rclcpy/README.md`](learning/my_package_rclcpy/README.md)를 참조하십시오.

### 3.3. ROS 2 & LIMO 심화 학습 가이드 (01~04)
기초 실습을 거쳐 LIMO 로봇의 센서 응용, 좌표 변환, 위치 추정 기초까지 확장된 체계적인 기술 문서입니다:
1. **[01. ROS 2 핵심 개념과 통신 인터페이스](learning/01_ros2_core_and_interfaces.md)**: Topic/Service/Action 상태 머신 비교, `wego_msgs` 커스텀 인터페이스 빌드, 파라미터/YAML/Launch 연동, 표준 센서 인터페이스 규격
2. **[02. LIMO 센서 응용 프로그래밍](learning/02_limo_application_programming.md)**: IMU Yaw 회전 제어(`rotate_absolute`), LiDAR 직교좌표 변환 및 장애물 ROI 판정(`limo_e_stop`), 카메라 CvBridge/HLS 차선 인식(`detect_line`), 3노드 통합 라인트레이싱 제어기(`limo_control`)
3. **[03. TF2 좌표 변환 및 목표 자세 제어](learning/03_tf2_and_pose_control.md)**: 동차 변환 행렬, 사원수, Broadcaster/Listener, LIMO TF 트리/URDF, 극좌표 제어기(`move_to_pose`)와 후진 주행 로직
4. **[04. 지역 위치 추정 기초](learning/04_local_state_estimation.md)**: 추측 항법(Dead Reckoning), 바퀴 엔코더 슬립(Slip), IMU 적분 표류(Drift) 현상, 복합 센서 융합(Sensor Fusion)의 당위성

---

## 4. LIMO 로봇 개발 및 제어 (LIMO Robot Application)

`src/` 디렉터리는 학습용 예제와 명확히 분리된 **로봇 애플리케이션 소스 코드 영역**입니다.

### 4.1. LIMO ROS 2 패키지 (`src/limo_ros2/`)
AgileX Robotics의 다목적 모바일 로봇 LIMO를 제어하기 위한 ROS 2 Humble 패키지군입니다.
- **`limo_base`**: 시리얼 통신 기반 LIMO 로봇 하드웨어 드라이버 및 베이스 제어 노드
- **`limo_car`**: Gazebo 시뮬레이션 환경 실행 launch 파일 및 RViz 설정
- **`limo_description`**: 4륜 차동(Differential), 아커만(Ackermann), 메카넘(Mecanum) 등 다양한 주행 모드를 지원하는 URDF/Xacro 모델 및 3D 메시
- **`limo_msgs`**: 로봇 모션 상태 및 오류 코드를 전달하는 전용 메시지(`LimoStatus.msg`)
- 상세 가이드는 [`src/limo_ros2/Readme.md`](src/limo_ros2/Readme.md)를 참고하십시오.

### 4.2. 원격 제어 노드 (`src/remote_teleop_node.py`)
- **설계 의도**: 사용자의 물리적 입력 장치(키보드 등)는 로컬 노트북(LG Gram)에 연결되어 있고, 무거운 시뮬레이션 연산(Gazebo)은 OCI 클라우드 서버에서 동작하는 분산 환경을 전제로 설계되었습니다.
- **동작 원리**: 표준 `geometry_msgs/msg/Twist` 메시지를 사용하며, Tailscale VPN 가상 사설망을 경유해 클라우드 서버의 `/cmd_vel` 토픽으로 선속도와 각속도를 원격 전송합니다.
- 자세한 아키텍처 배경은 [`src/README.md`](src/README.md)에 기술되어 있습니다.

> [!IMPORTANT]
> `src/gazebo_ros_pkgs/`는 시뮬레이션 연동을 위한 플레이스홀더 디렉터리(현재 비어 있음)입니다. 전체 LIMO 시뮬레이션 및 실제 로봇 주행 테스트는 추후 실기 연동 단계에서 진행될 예정입니다.

---

## 5. 원격 개발 및 분산 통신 인프라 (Cloud Infrastructure)

본 프로젝트는 원격 클라우드(Oracle Cloud)와 로컬 환경(Windows WSL2) 간의 안전하고 유연한 로보틱스 개발 환경을 구축하여 운영하고 있습니다.

### 5.1. 아키텍처 요약
- **Compute Server**: Oracle Cloud Infrastructure (Ubuntu 22.04 LTS, ROS 2 Humble)
- **Zero-Install Web IDE**: `code-server`를 활용한 웹 브라우저 기반 VS Code 개발 환경
- **보안 가상망**: `Tailscale VPN` 및 `Tailscale Funnel` 기반 HTTPS 터널링과 접근 통제

### 5.2. Fast DDS Discovery Server 분산 통신
VPN 환경에서는 멀티캐스트(Multicast) 패킷이 차단되는 한계가 있습니다. 이를 해결하기 위해 Fast DDS Discovery Server 아키텍처를 도입했습니다.

1. **오라클 클라우드 서버 (Discovery Server)**:
   - 방화벽 수신 포트: `TCP/UDP 11811` 개방
   - `systemd` 서비스(`fastdds.service`)를 통해 부팅 시 자동 기동:
     ```bash
     fastdds discovery -i 0 -p 11811
     ```
2. **로컬 노트북 WSL2 (Client Profile)**:
   - `~/fastdds.xml` 프로필을 통해 서버의 Tailscale VPN IP 및 포트(`11811`)를 명시적으로 지정
   - 빠른 망 전환을 위한 `.bashrc` 환경 변수 스위칭 Alias 제공:
     ```bash
     # 클라우드 통신 모드 활성화
     cloud_on

     # 로컬 와이파이 / LIMO 로컬 모드로 복귀
     cloud_off
     ```

<details>
<summary>📌 기존 설정 파일 원문 예시 (과거 기록 보존, 현재 운영 상태 미검증)</summary>

> 다음 설정 블록은 기존 저장소 기록(`HEAD:README.md`)에 보존되어 있던 설정 예시 원문입니다. 현재 서버 및 네트워크의 실시간 운영 상태와 일치하는지는 이번 작업 범위에서 재검증하지 않았습니다.

#### 1) Discovery Server 자동 실행 서비스 (`/etc/systemd/system/fastdds.service`)
```ini
[Unit]
Description=Fast DDS Discovery Server
After=network.target

[Service]
Type=simple
User=ubuntu
ExecStart=/bin/bash -c "source /opt/ros/humble/setup.bash && fastdds discovery -i 0 -p 11811"
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

#### 2) Discovery Server 클라이언트 프로필 (`~/fastdds.xml`)
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<profiles xmlns="http://www.eprosima.com/XMLSchemas/fastRTPS_Profiles">
    <participant profile_name="client_profile" is_default_profile="true">
        <rtps>
            <builtin>
                <discovery_config>
                    <discoveryProtocol>CLIENT</discoveryProtocol>
                    <discoveryServersList>
                        <!-- 오라클 서버의 GUID Prefix -->
                        <RemoteServer prefix="44.53.00.5f.45.50.52.4f.53.49.49.41">
                            <metatrafficUnicastLocatorList>
                                <locator>
                                    <udpv4>
                                        <!-- 오라클 서버의 Tailscale IP 및 개방된 포트 -->
                                        <address>100.127.79.18</address>
                                        <port>11811</port>
                                    </udpv4>
                                </locator>
                            </metatrafficUnicastLocatorList>
                        </RemoteServer>
                    </discoveryServersList>
                </discovery_config>
            </builtin>
        </rtps>
    </participant>
</profiles>
```

#### 3) 초기 P2P 유니캐스트 프로필 (`fastdds.xml`)
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<profiles xmlns="http://www.eprosima.com/XMLSchemas/fastRTPS_Profiles">
    <participant profile_name="connect_profile" is_default_profile="true">
        <rtps>
            <builtin>
                <initialPeersList>
                    <locator>
                        <udpv4>
                            <address>100.127.79.18</address>
                        </udpv4>
                    </locator>
                </initialPeersList>
            </builtin>
        </rtps>
    </participant>
</profiles>
```
</details>

### 5.3. 주요 트러블슈팅 및 보안 운영 이력
- **Windows NAT 패킷 차단**: WSL2 내부에 독립적으로 Linux용 Tailscale을 설치하여 해결
- **미들웨어 충돌**: `.bashrc`의 Cyclone DDS 강제 지정을 해제하고 Fast DDS로 일원화
- **XML 프로필 파싱 오류**: `is_default_profile="true"` 속성 오기입 수정
- **웹 IDE 보안 강화**: 외부 무단 접근을 방지하기 위해 `fail2ban`과 `msmtp` 기반 침입 차단 및 실시간 알림 체계 구축 ([`docs/CLOUD_WEB_IDE_SECURITY_RECOVERY.md`](docs/CLOUD_WEB_IDE_SECURITY_RECOVERY.md) 참조)

---

## 6. 현재 상태 및 검증 범위 (Status & Verification Scope)

본 저장소의 실제 구현 및 검증 현황을 투명하게 기록합니다:

| 영역 | 항목 | 검증 상태 | 상세 내용 |
| :--- | :--- | :---: | :--- |
| **학습** | Python 신호 모델링 & OOP | ✅ 검증 완료 | `01_sin_modeling.ipynb`, `02_python_oop_class.ipynb` 실행 확인 |
| **학습** | Turtlesim 토픽/서비스 실습 | ⚠️ 기록 보존 | 주피터 대화형 코드 및 실행 로그 보존 (서비스 클라이언트는 대기 로그 상태) |
| **학습** | `my_package_rclcpy` 패키지 | ✅ 빌드 검증 완료 | 격리된 빌드 환경에서 `colcon build` 및 5개 실행 바이너리 생성 확인 |
| **학습** | 통신 인터페이스 & 파라미터 | ✅ 소스 검증 완료 | `wego_msgs`, `wego_service_demo` (Action, Service, Launch, YAML) 확인 |
| **학습** | LIMO 센서 응용 노드 | 🔍 교재 분석 완료 | 회전(`rotate_absolute`), 비상정지(`limo_e_stop`), 차선인식(`detect_line`), 제어기(`limo_control`) 알고리즘 분석 (실제 하드웨어 미주행) |
| **학습** | TF2 변환 및 목표 자세 제어 | 🔍 교재 분석 완료 | 동차 변환, Turtlesim TF 시뮬레이션, LIMO TF 트리, `move_to_pose` 극좌표 제어 로직 분석 (실제 하드웨어 미주행) |
| **학습** | 지역 위치 추정 기초 | 💡 개념 학습 완료 | 엔코더 휠 슬립, IMU 적분 드리프트, 센서 융합 당위성 이해 (가우시안/EKF/SLAM 미학습 분류) |
| **애플리케이션** | LIMO ROS 2 소스 코드 | ⚠️ 정적 코드 확인 | `limo_base`, `limo_car`, `limo_description`, `limo_msgs` 소스 보존 (전체 빌드 미수행) |
| **애플리케이션** | 원격 제어 노드 (`remote_teleop_node`) | ✅ 문법 검증 완료 | 독립 Python 노드 구조 확인 (실제 로봇 주행 테스트 대기) |
| **인프라** | Tailscale VPN & code-server | ✅ 운영 중 | 웹 브라우저 접속 및 분산 개발 환경 가동 중 |
| **인프라** | Fast DDS Discovery Server | ⚠️ 과거 검증 이력 | 클라우드-WSL2 간 `talker`/`listener` 통신 검증 이력 확인. 이번 작업에서는 실시간 통신을 재검증하지 않음. |

> [!CAUTION]
> 본 프로젝트는 현재 학습 및 분산 시뮬레이션 인프라 구축 단계이며, 상용 배포(Production-ready) 상태나 완전 자율주행이 구현된 상태가 아닙니다.

---

## 7. 문서 탐색 (Documentation Index)

프로젝트 세부 사항은 아래 링크를 통해 확인할 수 있습니다:

### 📖 학습 문서
- [ROS 2 Python 학습 가이드 & 통합 인덱스](learning/README.md)
- [01. ROS 2 핵심 개념과 통신 인터페이스](learning/01_ros2_core_and_interfaces.md)
- [02. LIMO 센서 응용 프로그래밍](learning/02_limo_application_programming.md)
- [03. TF2 좌표 변환 및 목표 자세 제어](learning/03_tf2_and_pose_control.md)
- [04. 지역 위치 추정 기초](learning/04_local_state_estimation.md)
- [my_package_rclcpy 패키지 빌드 및 실행 가이드](learning/my_package_rclcpy/README.md)

### 🤖 소스 및 로봇 문서
- [ROS 2 소스 코드 및 분산 알고리즘 설계](src/README.md)
- [AgileX LIMO ROS 2 공식 가이드](src/limo_ros2/Readme.md)
- [원격 조향 퍼블리셔 노드 소스](src/remote_teleop_node.py)

### ☁️ 인프라 및 운영 문서
- [시스템 아키텍처 및 기술 스택 선정 이유](docs/ARCHITECTURE.md)
- [원격 개발 환경 단계별 구축 가이드](docs/SETUP_GUIDE.md)
- [클라우드 저장소 및 백업 인프라 구축기](docs/CLOUD.md)
- [네트워크 및 미들웨어 트러블슈팅 일지](docs/TROUBLESHOOTING.md)
- [원격 개발 환경 보안 침해 복구 및 fail2ban 설정](docs/CLOUD_WEB_IDE_SECURITY_RECOVERY.md)
- [Cloud IDE 최신 운영 기록](docs/README_CLOUD_IDE_UPDATE.md)
- [인프라 및 백업 자동화 스크립트 모음](scripts/)
