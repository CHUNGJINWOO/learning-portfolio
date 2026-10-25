# 01. Python 객체지향(OOP) 및 신호 모델링 실습 노트북

본 디렉터리는 이동 로봇 소프트웨어 개발의 수학적 기초(사인파 신호 모델링)와 소프트웨어 설계 기초(객체지향 클래스 상속 및 수명주기 캡슐화)를 대화형 환경에서 실습하기 위한 Jupyter Notebook 모음입니다.

---

## 🗂️ 실습 노트북 목록

| 순서 | 노트북 파일명 | 핵심 주제 | 주요 라이브러리 | 학습 내용 요약 |
| :---: | :--- | :--- | :--- | :--- |
| **01** | [`01_sin_modeling.ipynb`](01_sin_modeling.ipynb) | 기초 신호 모델링 | `numpy`, `matplotlib` | 시간 축(`arange`) 생성, 사인파 수식($y = A \sin(2\pi ft) + b$) 계산 및 파라미터(진폭, 주파수, 오프셋) 시각화 절차형 구현 |
| **02** | [`02_python_oop_class.ipynb`](02_python_oop_class.ipynb) | 객체지향 프로그래밍 (OOP) | Python 표준 문법 | `DrawSin` 기본 클래스 선언, 인스턴스화, 단일 상속, 메서드 오버라이딩, `super().__init__()` 활용 및 ROS 2 `Node` 클래스 상속 원리 연결 |

---

## 🛠️ 실행 환경 및 검증 방법

```bash
# 가상환경 활성화 (Python 3.10+, numpy, matplotlib 필요)
source ~/venvs/data-analysis/bin/activate
jupyter notebook
```

노트북 내부 코드는 Python 3.10 표준 라이브러리와 NumPy, Matplotlib 기반으로 작성되어 별도의 외부 ROS 2 하드웨어 없이 즉시 검증 가능합니다.
