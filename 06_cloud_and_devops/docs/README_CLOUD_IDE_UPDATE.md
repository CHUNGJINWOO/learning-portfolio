Cloud-Based 원격 개발 환경 운영 기록

Oracle Cloud Ubuntu 서버에서 code-server + Tailscale Funnel 기반의 무설치 원격 개발 환경을 운영하고 있습니다.

Chrome / Edge
     ↓ HTTPS
Tailscale Funnel
     ↓
127.0.0.1:8080
     ↓
code-server
     ↓
ROS2 / 프로젝트 작업공간

보안

code-server는 127.0.0.1:8080에만 바인딩

code-server 비밀번호 인증 활성화

Fail2Ban code-server jail 적용

로그인 실패 5회 / 10분 → 1시간 차단

PostgreSQL은 외부 공개 포트를 사용하지 않음

장애 복구 사례

Tailscale Funnel 접속 시 HTTP 502가 발생한 사례에서 8080 포트가 비어 있음을 확인했고, code-server@ubuntu.service의 journal 로그를 분석하여 다음 원인을 확인했습니다.

Unknown option --trust-proxy

현재 설치된 code-server 버전이 해당 옵션을 인식하지 못하는 설정 호환성 문제였으며, 기존 설정을 백업한 뒤 문제 옵션만 제거하여 최소 변경으로 복구했습니다.

상세한 원인 분석, 복구 명령, Fail2Ban 검증 절차 및 보안 운영 방법은 다음 문서를 참고합니다.

docs/CLOUD_WEB_IDE_SECURITY_RECOVERY.md