# 개념 및 이론 학습 노트 (Knowledge Notes)

본 디렉터리는 학교 강의, 개인 학습, 공식 문서에서 배운 핵심 개념과 동작 원리를 **학습자가 자신의 언어로 직접 재구성하여 정리한 심층 학습 노트 공간**입니다.

단순한 강의 요약이나 외부 텍스트 복제를 지양하고, 개념의 본질과 원리를 깊이 있게 이해하도록 돕습니다. 시간이 지나 다시 읽었을 때도 동작 원리와 설계 이유를 즉시 복기할 수 있도록 체계적으로 정리합니다.

---

## 🗂️ 핵심 이론 및 LIMO 자율주행 학습 노트 목록

교재(`[WeGo] Limo_ROS2_교재.pdf`)와 공식 문서를 정밀 분석하여 작성된 단계별 이론 기술 문서입니다:

| 단계 | 문서명 | 핵심 주제 | 교재 출처 및 검증 상태 |
| :---: | :--- | :--- | :--- |
| **01** | [`01_ros2_core_and_interfaces.md`](01_ros2_core_and_interfaces.md) | **ROS 2 통신 메커니즘 & 인터페이스**<br>- Topic, Service, Action 상태 머신 비교<br>- Custom msg/srv/action (`wego_msgs`) 빌드<br>- Parameter & Launch 시스템 연동<br>- 표준 센서 인터페이스 (`Imu`, `LaserScan`, `Image`, `Odometry`) | `[WeGo] Limo_ROS2_교재.pdf` (Ch 4 & 5)<br>`[로컬 소스 검증 완료]` (`wego_msgs`, `wego_service_demo`)<br>`[시뮬레이터 실습 완료]` |
| **02** | [`02_limo_application_programming.md`](02_limo_application_programming.md) | **LIMO 센서 응용 프로그래밍**<br>- `rotate_absolute.py`: IMU Yaw 오일러 변환 및 각속도 P제어<br>- `limo_e_stop.py`: LiDAR 직교좌표 변환, ROI 장애물 판정<br>- `detect_line.py`: 카메라 CvBridge, HLS 차선 마스킹, 모멘트 도심 오차<br>- `limo_control.py`: 통합 토픽 파이프라인 및 안전 정지 | `[WeGo] Limo_ROS2_교재.pdf` (Ch 6)<br>`[교재 코드 분석 완료]`<br>`[로컬 소스 미구현 (교재 분석 완료)]`<br>`[미검증 (실제 하드웨어 미주행)]` |
| **03** | [`03_tf2_and_pose_control.md`](03_tf2_and_pose_control.md) | **TF2 좌표 변환 & 목표 자세 제어**<br>- 동차 변환 행렬, 사원수, Broadcaster / Listener<br>- LIMO 표준 TF 트리, URDF / Xacro, 카메라 틸트 라디안 변환<br>- `move_to_pose.py`: 목표 상대 좌표 조회, 극좌표 ($\rho, \alpha, \beta$) 유도, 비례 제어 및 후진 주행 | `[WeGo] Limo_ROS2_교재.pdf` (Ch 7)<br>`[시뮬레이터 개념 검증 완료]` (Turtlesim)<br>`[교재 코드 분석 완료]` (LIMO TF)<br>`[미검증 (실제 하드웨어 미주행)]` |
| **04** | [`04_local_state_estimation.md`](04_local_state_estimation.md) | **지역 위치 추정 기초 (Local State Estimation)**<br>- 추측 항법(Dead Reckoning)과 Local Problem<br>- 바퀴 엔코더 휠 슬립(Slip) 및 누적 오차 특성<br>- IMU 적분 드리프트(Drift) 현상<br>- 상호 보완적 센서 융합(Sensor Fusion)의 당위성 | `[WeGo] Limo_ROS2_교재.pdf` (Ch 8.1)<br>`[개념 학습 완료]`<br>*(가우시안 수학, EKF 수식, SLAM은 미학습으로 분류)* |

---

## 📊 종합 학습 검증 현황 및 미확인 항목

| 영역 | 항목 | 검증 상태 | 상세 설명 및 근거 |
| :--- | :--- | :---: | :--- |
| **Python 기초** | 신호 모델링 & OOP | `[검증 완료]` | `01_sin_modeling.ipynb`, `02_python_oop_class.ipynb` 실행 확인 (`01_python_and_oop`) |
| **Turtlesim 대화형** | 토픽 발행/구독 실습 | `[기록 보존]` | 주피터 노트북 대화형 코드 및 카운터 탈출 로직 확인 (`notebooks/`) |
| **Turtlesim 대화형** | 서비스 클라이언트 | `[기록 보존]` | `05_service_client_turtlesim.ipynb` (서비스 미기동 대기 상태 출력 보존) |
| **ROS 2 패키지** | `my_package_rclcpy` | `[빌드 검증 완료]` | 5개 콘솔 스크립트 노드 정상 빌드 및 엔트리포인트 확인 (`exercises/`) |
| **통신 & 인터페이스** | `wego_msgs`, `wego_service_demo` | `[로컬 소스 검증 완료]` | Action Server/Client, Service, Launch, Parameter 소스 확인 완료 (`notes/01`) |
| **LIMO 응용 노드** | 회전, 비상정지, 차선인식, 제어 | `[교재 코드 분석 완료]` | 교재 6장 알고리즘·수학 분석 완료 (실제 하드웨어 미주행, `notes/02`) |
| **TF2 & Pose 제어** | TF 변환 이론, Turtlesim TF | `[시뮬레이터 개념 검증 완료]` | 동차 변환, 쿼터니언, Broadcaster/Listener, Carrot 예제 확인 (`notes/03`) |
| **TF2 & Pose 제어** | LIMO TF, `move_to_pose` | `[교재 코드 분석 완료]` | 교재 7장 URDF, 틸트 각도, 극좌표 제어 로직 분석 완료 (실제 하드웨어 미주행, `notes/03`) |
| **위치 추정 기초** | 엔코더 슬립, IMU 드리프트 | `[개념 학습 완료]` | 교재 8.1절 물리적 오차 요인 및 복합 센서 융합 당위성 이해 완료 (`notes/04`) |

> [!NOTE]
> **미학습 항목 (학습 완료로 기록하지 않는 대상)**:
> 가우시안 확률 분포 수학 공식, 분산/공분산 행렬 상세 유도, 칼만 필터 및 확장 칼만 필터(EKF) 유도 수식, SLAM(지도 작성) 및 Nav2 자율주행 프레임워크는 향후 단계적 학습 과제로 분류하여 본 포트폴리오의 완료된 학습에 포함하지 않았습니다.

---

## 📥 넣을 자료 (Included)

1. **원리 및 설계 이유 분석**: "왜 이 방식을 사용하는가?", "어떤 대안이 있는가?"에 대한 개념 분석 노트.
2. **아키텍처 및 통신 흐름 다이어그램**: 시스템 블록도, 상태 전이도(State Diagram), 시퀀스 다이어그램(Mermaid).
3. **핵심 문법 및 언어적 특성 비교**: Python 객체지향/비동기, C/C++ 메모리 모델 및 포인터 연산 등.
4. **트러블슈팅 일지 (Troubleshooting Log)**: 발생한 오류 메시지, 원인 분석, 해결 과정, 방어 기법 기록.

---

## 🚫 넣지 않을 자료 (Excluded)

1. **학교 강의 슬라이드(PPTX, PDF) 원본**: 교수자의 저작권 보호를 위해 원본 파일은 외부 디렉터리(`school/`)에만 보관하고 이곳에 복사하지 않습니다.
2. **외부 튜토리얼의 무단 복사본**: 스스로 이해하고 작성하지 않은 외부 텍스트는 수용하지 않습니다.
3. **미검증된 임시 코드 스니펫**: 실행 가능하고 검증된 패키지 코드는 `src/`에서 다루며, 본 디렉터리에는 개념 설명을 위한 최소 스니펫만 포함합니다.

---

## ⚙️ AI를 이용한 처리 절차

1. 사용자가 루트 `inbox/`에 원시 필기나 학습 자료를 투입하면, 에이전트가 이를 분석합니다.
2. 기존 `docs/` 및 `notes/`와의 중복 여부를 대조하고, 선행/후속 관계를 파악합니다.
3. 학습자가 이해한 내용을 바탕으로 적절한 주제별 하위 디렉터리에 배치할 것을 제안합니다.
4. **사용자의 명시적 승인을 받은 뒤에만** 정식 마크다운 노트로 정제하여 저장합니다.
