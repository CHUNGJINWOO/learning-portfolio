# 06. 클라우드 로보틱스 인프라 및 운영 보안 (Cloud & DevOps)

이 디렉터리는 로컬 개발 장비의 성능 한계를 극복하고 시뮬레이션 데이터를 안전하게 관리하기 위해 구축한 **Oracle Cloud Infrastructure(OCI) 기반 원격 개발 환경, 분산 네트워크 및 실전 보안 운영 체계**를 다룹니다.

---

## 📌 주요 아키텍처 및 인프라 구성

1. **원격 웹 IDE 인프라:**
   - Oracle Cloud Always-Free ARM Compute 인스턴스 (4 OCPU, 24GB RAM)
   - `code-server` 웹 IDE 구축 및 로컬-원격 간 seamless 개발 환경 동기화
2. **사설 가상망 및 분산 DDS 통신:**
   - `Tailscale VPN` 가상 사설망을 통한 공인 IP 노출 차단
   - ROS 2 Fast DDS Discovery Server 분산 토픽 라우팅
3. **실전 보안 침해 대응 및 하드닝 (Incident Response):**
   - Cloudflare Funnel 공개 취약점 진단 및 무차별 대입 공격(Brute-force) 감지
   - `fail2ban` 침입 차단 룰셋 및 `msmtp` 실시간 이메일 경보 체계 구축
4. **자동화 스토리지 및 백업 파이프라인:**
   - OCI iSCSI 블록 볼륨 포맷 및 자동 마운트 스크립트
   - `rclone` 기반 클라우드 이중 백업 및 Windows 작업 스케줄러 자동화

---

## 📚 세부 문서 색인 (`docs/`)

- [ARCHITECTURE.md](docs/ARCHITECTURE.md): 원격 개발 환경 시스템 설계 및 컴포넌트별 기술 스택 선정 이유
- [SETUP_GUIDE.md](docs/SETUP_GUIDE.md): OCI, Tailscale, code-server 단계별 구축 가이드
- [CLOUD.md](docs/CLOUD.md): 시뮬레이션 결과물 클라우드 저장 및 백업 체계 구축기
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md): 네트워크 충돌, 환경변수, XML 파싱 트러블슈팅 일지
- [CLOUD_WEB_IDE_SECURITY_RECOVERY.md](docs/CLOUD_WEB_IDE_SECURITY_RECOVERY.md): 웹 IDE 보안 침해 분석 및 fail2ban 복구 실전 기록
- [README_CLOUD_IDE_UPDATE.md](docs/README_CLOUD_IDE_UPDATE.md): 원격 개발 환경 운영 및 보안 패치 기록

---

## 🛠️ 관리 및 보안 자동화 스크립트 (`scripts/`)

- `01 setup ssh key · SH`: SSH 키 페어 생성 및 클라우드 공개키 자동 등록
- `02 mount data volume · SH`: OCI 블록 볼륨 iSCSI 마운트 및 `/etc/fstab` 영구 등록
- `03 test transfer · SH`: 로컬-원격 간 대용량 데이터 전송 대역폭 및 연결성 테스트
- `04 setup rclone · SH`: Google Drive 및 원격 스토리지 연동 설정
- `05 backup · SH`: rclone 기반 2차 안전 백업 실행 스크립트
- `06_register_task_scheduler.ps1`: Windows 클라이언트 백업 작업 스케줄러 등록
- `07 harden code server · SH`: fail2ban 필터 등록 및 msmtp 알림 보안 강화 자동화
