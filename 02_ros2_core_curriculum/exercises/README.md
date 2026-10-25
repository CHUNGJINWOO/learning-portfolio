# 복습 및 자가점검 과제 (Exercises & Challenges)

본 디렉터리는 학습한 내용을 스스로 검증하고 장기 기억으로 정착시키기 위한 **복습 질문, 자가점검 퀴즈, 입문 실습 패키지 및 미니 응용 과제를 보관하고 수행하는 공간**입니다.

---

## 📌 목적

- "코드가 빌드되었다고 해서 개념을 이해한 것은 아니다"라는 원칙에 따라, 학습자가 원리를 진정으로 이해했는지 스스로 점검합니다.
- 단순 암기식 문항이 아닌, 동작 원리와 아키텍처적 인과관계를 묻는 질문을 통해 사고력을 확장합니다.
- 복습 과제를 완수함으로써 학습 상태를 `NEEDS_REVIEW`에서 최종 단계인 `VERIFIED_UNDERSTANDING`(이해 확인)으로 전이시킵니다.

---

## 🗂️ 입문 실습 패키지 (Introductory Packages)

### [`my_package_rclcpy/`](my_package_rclcpy/)
- **역할:** 대화형 주피터 노트북([`../notebooks/`](../notebooks/))에서 실습한 Turtlesim 발행/구독 및 서비스 코드를 최초로 표준 ROS 2 `ament_python` 패키지로 정형화한 실습 패키지.
- **포함 노드 (5종):**
  - `my_first_node`: `Node` 클래스를 상속받는 기본 객체지향 노드 수명주기
  - `talker`: `std_msgs/msg/String` 토픽 퍼블리셔 (`chatter` 토픽, 0.5초 주기)
  - `listener`: `std_msgs/msg/String` 토픽 서브스크라이버
  - `add_two_ints_server`: `example_interfaces/srv/AddTwoInts` 서비스 서버
  - `add_two_ints_client`: `example_interfaces/srv/AddTwoInts` 비동기 서비스 클라이언트
- **상세 빌드 및 실행 가이드:** [`my_package_rclcpy/README.md`](my_package_rclcpy/README.md) 참조.

---

## 📥 넣을 자료 (Included)

1. **입문 실습 패키지**: 대화형 코드를 패키지화한 초기 학습 산출물.
2. **원리 중심 복습 질문 (Self-Reflection Questions)**: "왜 이 상황에서 타이머 대신 파라미터 이벤트 콜백을 써야 하는가?"와 같은 핵심 원리 질문.
3. **자가진단 퀴즈 (Self-Assessments)**: 개념의 미묘한 차이를 구별하는 객관식, 진위형(T/F), 단답형 퀴즈.
4. **핸즈온 미니 응용 과제 (Hands-on Challenges)**: 기존의 검증된 코드(예: `service_action_py`)를 약간 변형하여 새로운 요구사항을 구현하는 실습 과제.
5. **학습자의 풀이 및 답안 (Solutions & Insights)**: 학습자가 직접 고민하여 작성한 답변, 풀이 과정, 파악한 핵심 원리.

---

## 🚫 넣지 않을 자료 (Excluded)

1. **학교 비공개 시험 문제 원본**: 학교 평가의 공정성과 보안을 위해 원본 시험 문제는 등록하지 않습니다.
2. **사고 과정 없는 단순 정답**: 왜 그 답이 도출되었는지에 대한 설명이 배제된 단순 복사본은 지양합니다.

---

## ⚙️ AI를 이용한 처리 절차

1. 사용자가 특정 Phase나 개념의 복습을 원할 때, 에이전트가 해당 개념 문서(`docs/`, `notes/`)를 바탕으로 3~5개의 핵심 복습 질문이나 미니 과제를 제안합니다.
2. 사용자의 승인을 거쳐 `exercises/` 하위 디렉터리(예: `ros2_basics/`, `tf2_transforms/`, `python_core/`)에 문제 파일이 생성됩니다.
3. 사용자가 풀이를 작성하면, 에이전트가 이를 검토하여 논리적 비약이나 누락된 원리가 있는지 피드백을 제공합니다.
4. 기준을 충족하여 스스로 설명할 수 있음이 확인되면, 해당 주제의 학습 상태를 `VERIFIED_UNDERSTANDING`으로 갱신합니다.
