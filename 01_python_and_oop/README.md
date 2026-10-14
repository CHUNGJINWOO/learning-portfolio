# 01. Python 객체지향(OOP) 및 신호 모델링 학습

이 디렉터리는 로보틱스 소프트웨어 개발의 선수 필수 역량인 **수학적 신호 모델링**과 **객체지향 프로그래밍(OOP) 클래스 설계 및 수명주기 캡슐화**를 다룹니다.

---

## 📌 학습 개요 및 핵심 목표

1. **NumPy 기반 수치 신호 모델링:**
   - 연속 시간 사인파 수식을 이산 시간 수열로 변환하고 주기, 주파수, 샘플링 레이트, 위상(Phase) 파라미터를 시각화
   - 이동 로봇의 주기적 궤적(원형, 8자 주행) 제어 입력 생성을 위한 기초 수학 확립
2. **절차적 스크립트 탈피 및 OOP 클래스 캡슐화:**
   - 절차적 무한 루프(`while True` + `time.sleep`)의 스레드 블로킹 한계 분석
   - 클래스 상속(`class MinimalPublisher(Node)`)과 `super().__init__()`을 통한 초기화
   - 클래스 변수(모든 인스턴스 공유로 인한 오염 위험)와 인스턴스 변수(`self`, 독립 힙 메모리 할당)의 메모리 격리 원리

---

## 🗂️ 학습 노트북 안내 (Canonical Notebooks)

현재 본 포트폴리오의 대화형 실습 주피터 노트북은 기존 경로 무결성 유지를 위해 [`learning/notebooks/`](../learning/notebooks/)에 배치되어 있습니다:

- **[01_sin_modeling.ipynb](../learning/notebooks/01_sin_modeling.ipynb)**:
  - NumPy, Matplotlib을 활용한 사인파 신호 합성 및 샘플링 분석
- **[02_python_oop_class.ipynb](../learning/notebooks/02_python_oop_class.ipynb)**:
  - 객체지향 클래스 정의, 상속, 메서드 오버라이딩, `super()` 호출 및 ROS 2 `Node` 클래스 상속 실습

---

## 🛠️ 실행 환경 및 검증 방법

```bash
# 가상환경 활성화 (또는 jupyter notebook 실행)
source ~/venvs/data-analysis/bin/activate
jupyter notebook
```

노트북 내부 코드는 Python 3.10 표준 라이브러리와 NumPy, Matplotlib 기반으로 작성되어 별도의 외부 ROS 2 하드웨어 없이 대화형으로 즉시 검증 가능합니다.
