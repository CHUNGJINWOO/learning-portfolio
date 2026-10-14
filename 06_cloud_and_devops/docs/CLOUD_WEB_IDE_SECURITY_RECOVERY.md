Cloud-Based 원격 개발 환경 운영 및 보안 복구 기록

1. 개요

본 프로젝트는 Oracle Cloud Infrastructure(OCI)의 Ubuntu 서버를 항상 실행되는 원격 개발 서버로 사용하고, 로컬 PC에서는 웹 브라우저만으로 VS Code 기반 개발 환경에 접근하는 것을 목표로 한다.

핵심 구성은 다음과 같다.

[Chrome / Edge]
       │
       │ HTTPS
       ▼
[Tailscale Funnel]
       │
       ▼
[127.0.0.1:8080]
       │
       ▼
[code-server]
       │
       ├── VS Code Web IDE
       ├── ROS2 Workspace
       └── 개발 프로젝트

서버 내부에서는 별도의 AI Knowledge Hub도 운영한다.

Oracle Cloud Ubuntu
│
├── code-server : 127.0.0.1:8080
│   └── 웹 기반 원격 개발 환경
│
├── AI Hub API : 127.0.0.1:8000
│   └── FastAPI + PostgreSQL + pgvector
│
└── PostgreSQL : 5432 (Docker 내부 네트워크)

현재 외부 웹 IDE의 주 진입점은 Tailscale Funnel이며, code-server는 127.0.0.1:8080에만 바인딩한다.

2. 왜 Cloud-Based 원격 개발 환경을 구축했는가

2.1 로컬 하드웨어의 한계 보완

노트북만으로 ROS2, 빌드, 시뮬레이션 등을 동시에 수행하면 CPU, RAM, 저장장치 등의 제약이 발생할 수 있다.

Oracle Cloud 서버를 항상 실행되는 개발 서버로 사용하면:

프로젝트 파일을 중앙에서 관리

SSH 또는 웹 브라우저를 통한 원격 개발

ROS2 작업 환경의 지속성 확보

장소와 장치에 관계없이 동일한 개발 환경 사용

이 가능하다.

2.2 Zero-Install 개발 환경

code-server를 사용하면 로컬 PC에 별도의 VS Code 설치 없이 웹 브라우저에서 VS Code 인터페이스를 사용할 수 있다.

즉,

로컬 PC
  └── Chrome / Edge만 필요
          ↓
      HTTPS 접속
          ↓
Oracle Cloud
  └── code-server + ROS2

구조가 된다.

2.3 환경 일관성

로컬 PC마다 Python, ROS2, 패키지 버전 등을 다시 구성하는 대신 서버에 개발 환경을 유지하면 프로젝트별 환경 차이를 줄일 수 있다.

2.4 저장소와 개발 환경의 분리

소스 코드는 GitHub에서 버전 관리하고, 실제 실행 환경은 Oracle Cloud에 유지하는 방식으로 역할을 분리할 수 있다.

GitHub
  └── 소스 코드 / 문서 / 버전 관리

Oracle Cloud
  └── 실행 환경 / ROS2 / 웹 IDE / 데이터

Local PC
  └── 브라우저 / 필요 시 로컬 고성능 연산

3. Tailscale Funnel을 사용하는 이유

OCI에서 개발 서버 포트를 직접 인터넷에 공개하는 대신 Tailscale Funnel을 외부 진입점으로 사용한다.

기존 운영 구조:

sudo tailscale funnel --bg 8080

결과:

https://ros2-server.<tailnet>.ts.net/
        ↓
Tailscale Funnel
        ↓
127.0.0.1:8080
        ↓
code-server

장점:

서버의 code-server는 localhost에만 바인딩할 수 있다.

외부 통신은 HTTPS 기반으로 제공된다.

Oracle Cloud에서 8080 포트를 직접 인터넷에 공개하지 않아도 된다.

브라우저만으로 접근할 수 있다.

4. 실제 운영 중 발생한 문제

4.1 증상

기존 웹 IDE 주소에 접속했을 때 HTTP 502가 발생했다.

원래는:

Funnel → 127.0.0.1:8080 → code-server

여야 하지만 실제로는 8080 포트가 비어 있었다.

당시 확인 결과:

ai-hub-api        127.0.0.1:8000
ai-hub-postgres   Docker 내부 5432

만 실행 중이었다.

또한:

sudo ss -lntp | grep ':8080'

에서 아무 결과가 나오지 않았다.

4.2 원인

code-server@ubuntu.service가 실패 상태였다.

로그에서 핵심 오류:

error reading /home/ubuntu/.config/code-server/config.yaml:
Unknown option --trust-proxy

즉 현재 설치된 code-server 버전이 config.yaml의 trust-proxy 옵션을 인식하지 못해 서비스가 시작되지 않았다.

이 문제는 code-server 자체가 삭제되거나 손상된 것이 아니라 호환되지 않는 설정 옵션 하나 때문에 서비스가 종료된 문제였다.

5. 복구 방법

5.1 설정 백업

변경 전 원본을 먼저 백업한다.

cp /home/ubuntu/.config/code-server/config.yaml \
   /home/ubuntu/.config/code-server/config.yaml.before-trust-proxy-fix

5.2 호환되지 않는 옵션 제거

sed -i '/^[[:space:]]*trust-proxy[[:space:]]*:/d' \
   /home/ubuntu/.config/code-server/config.yaml

전체 설정을 새로 작성하지 않고 문제가 된 한 줄만 제거하는 방식으로 기존 설정을 최대한 보존한다.

5.3 systemd 서비스 재시작

sudo systemctl reset-failed code-server@ubuntu.service
sudo systemctl restart code-server@ubuntu.service

확인:

sudo systemctl status code-server@ubuntu.service --no-pager -l

정상 상태:

Active: active (running)

5.4 8080 포트 확인

sudo ss -lntp | grep ':8080'

정상적으로 code-server가 실행되면 127.0.0.1:8080이 LISTEN 상태가 된다.

5.5 로컬 HTTP 확인

curl -I http://127.0.0.1:8080/

code-server의 비밀번호 인증이 활성화되어 있기 때문에 인증 관련 HTTP 응답이 반환되어도 정상이다.

5.6 Tailscale Funnel 복구

8080 포트가 정상화된 뒤 기존 외부 진입점으로 되돌린다.

sudo tailscale funnel --bg 8080

확인:

tailscale funnel status

기대 결과:

https://ros2-server.<tailnet>.ts.net (Funnel on)
|-- / proxy http://127.0.0.1:8080

6. 보안 구성

6.1 code-server 비밀번호 인증

code-server는 다음과 같은 형태로 비밀번호 인증을 사용한다.

bind-addr: 127.0.0.1:8080
auth: password
cert: false

핵심은 code-server가 외부 인터페이스가 아니라 localhost에만 바인딩된다는 점이다.

비밀번호는 GitHub 저장소에 절대 커밋하지 않는다.

또한 설정 파일 전체를 출력하는 명령을 사용할 경우 비밀번호가 노출될 수 있으므로 다음과 같은 출력은 피한다.

cat /home/ubuntu/.config/code-server/config.yaml

설정 확인이 필요할 때는 비밀번호 줄을 제외한다.

grep -v '^password:' /home/ubuntu/.config/code-server/config.yaml

6.2 Fail2Ban

code-server 전용 Fail2Ban jail이 운영되고 있다.

확인:

sudo fail2ban-client status

code-server jail:

sudo fail2ban-client status code-server

확인된 핵심 정책:

maxretry = 5
findtime = 600
bantime  = 3600

의미:

10분(findtime) 안에
5회(maxretry) 로그인 실패
        ↓
1시간(bantime) 차단

설정값 직접 확인:

sudo fail2ban-client get code-server maxretry
sudo fail2ban-client get code-server findtime
sudo fail2ban-client get code-server bantime

6.3 현재 차단 상태 확인

sudo fail2ban-client status code-server

예:

Currently banned: 0
Total banned: 0
Banned IP list:

현재 차단자가 없더라도 jail과 정책이 정상 동작하고 있으면 된다.

7. 비밀번호 변경 시 안전한 방법

기존 비밀번호가 외부에 노출된 경우 새 비밀번호로 변경해야 한다.

터미널에 새 비밀번호를 평문으로 출력하지 않는 방식:

read -rsp "새 code-server 비밀번호: " NEW_PASSWORD
echo
read -rsp "새 code-server 비밀번호 확인: " NEW_PASSWORD2
echo

if [ "$NEW_PASSWORD" != "$NEW_PASSWORD2" ]; then
    echo "비밀번호가 일치하지 않습니다."
    unset NEW_PASSWORD NEW_PASSWORD2
    exit 1
fi

cp /home/ubuntu/.config/code-server/config.yaml \
   /home/ubuntu/.config/code-server/config.yaml.before-password-change

python3 - "$NEW_PASSWORD" <<'PY'
import sys
from pathlib import Path

password = sys.argv[1]
path = Path("/home/ubuntu/.config/code-server/config.yaml")
lines = path.read_text().splitlines()

out = []
replaced = False

for line in lines:
    if line.startswith("password:"):
        out.append(f"password: {password}")
        replaced = True
    else:
        out.append(line)

if not replaced:
    out.append(f"password: {password}")

path.write_text("\n".join(out) + "\n")
PY

unset NEW_PASSWORD NEW_PASSWORD2

chmod 600 /home/ubuntu/.config/code-server/config.yaml
sudo systemctl restart code-server@ubuntu.service

코드 설명

read -rsp: 입력한 비밀번호를 화면에 표시하지 않는다.

두 번 입력하여 오타를 확인한다.

기존 설정 파일을 백업한다.

Python으로 password: 줄만 교체하여 다른 설정을 유지한다.

unset: 셸 환경 변수에 남아 있는 비밀번호를 제거한다.

chmod 600: 설정 파일을 소유자만 읽고 쓸 수 있도록 제한한다.

systemd 서비스를 재시작하여 새 비밀번호를 적용한다.

8. 문제 해결 과정의 핵심 원칙

이번 장애에서 중요한 점은 단순히 서비스를 재설치하지 않았다는 것이다.

잘못된 접근

code-server 접속 실패
        ↓
code-server 삭제
        ↓
재설치
        ↓
설정 복구

이 방법은 기존 인증 설정, 사용자 데이터, 확장 프로그램 등의 상태를 불필요하게 변경할 위험이 있다.

실제로 사용한 접근

502 확인
  ↓
8080 LISTEN 여부 확인
  ↓
code-server 서비스 상태 확인
  ↓
journalctl 로그 분석
  ↓
Unknown option --trust-proxy 확인
  ↓
문제 옵션 한 줄만 제거
  ↓
서비스 재시작
  ↓
8080 확인
  ↓
Funnel을 8080으로 복귀

이 방식의 장점은 원인을 확인한 뒤 최소한의 변경만 수행한다는 것이다.

9. AI Knowledge Hub와의 공존

Oracle Cloud에서 웹 IDE와 AI Knowledge Hub를 동시에 운영할 수 있다.

                      Oracle Cloud
                           │
            ┌──────────────┴──────────────┐
            │                             │
   code-server :8080             AI Hub API :8000
            │                             │
       ROS2 / 개발                     FastAPI
                                          │
                                      PostgreSQL
                                      + pgvector

현재 AI Hub는 Docker Compose로 운영하며 API는 호스트의 localhost에만 바인딩한다.

예:

ports:
  - "127.0.0.1:8000:8000"

PostgreSQL은 외부 공개 포트를 사용하지 않고 Docker 내부 네트워크에서 API와 통신한다.

이 구조를 유지하면:

code-server는 원격 개발용

AI Hub는 지식 검색/문서/메모리 관리용

PostgreSQL은 내부 데이터 저장용

으로 역할을 분리할 수 있다.

10. 운영 체크리스트

code-server

sudo systemctl status code-server@ubuntu.service --no-pager
sudo ss -lntp | grep ':8080'

Tailscale

tailscale funnel status

Fail2Ban

sudo fail2ban-client status
sudo fail2ban-client status code-server
sudo fail2ban-client get code-server maxretry
sudo fail2ban-client get code-server findtime
sudo fail2ban-client get code-server bantime

설정 파일 보안

stat -c '%A %U:%G %n' /home/ubuntu/.config/code-server/config.yaml
grep -v '^password:' /home/ubuntu/.config/code-server/config.yaml

11. 정리

이번 장애는 외부 네트워크 자체의 문제가 아니라 code-server 설정 파일의 호환되지 않는 trust-proxy 옵션으로 인해 서비스가 시작되지 않았던 문제였다.

복구의 핵심은:

원인 로그 확인

기존 설정 백업

문제 옵션만 제거

code-server 서비스 복구

8080 포트 복구

Tailscale Funnel을 8080으로 복귀

code-server 비밀번호 인증 확인

Fail2Ban의 5회/10분/1시간 정책 확인

이다.

이 기록은 향후 같은 문제가 발생했을 때 무작정 재설치하지 않고 로그 → 원인 → 최소 변경 → 검증 순서로 복구하기 위한 운영 문서로 활용할 수 있다.

보안 주의: 실제 비밀번호, API 키, DB 비밀번호, 토큰, 개인 인증 정보는 이 문서와 Git 저장소에 기록하지 않는다.