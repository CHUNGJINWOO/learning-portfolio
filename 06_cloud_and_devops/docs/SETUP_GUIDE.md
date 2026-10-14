# 🛠️ 원격 개발 환경 구축 가이드 (Setup Guide)

본 문서는 Oracle Cloud, Tailscale, 그리고 code-server를 활용한 로보틱스 원격 개발 환경의 단계별 구축 명령어와 설정 방법을 기록합니다.

---

## 1. Oracle Cloud Infrastructure (OCI) 서버 프로비저닝
- **OS**: Ubuntu 22.04 LTS
- **네트워크 보안**: VCN(가상 클라우드 네트워크) 설정 시 SSH(22) 포트만 최소한으로 개방하여 초기 보안을 확보했습니다.
- **초기 접속 명령어**: OCI 콘솔에서 발급받은 프라이빗 키(`.key`)를 사용하여 로컬 환경에서 서버로 최초 접속을 수행했습니다.
  ```bash
  ssh -i <private_key.key> ubuntu@<OCI_공인_IP>

# 보안 통신망 (Tailscale VPN) 구축

# 1. Tailscale 자동 설치 스크립트 실행
curl -fsSL [https://tailscale.com/install.sh](https://tailscale.com/install.sh) | sh

# 2. 기기 등록 및 VPN 네트워크 실행
sudo tailscale up

# 로컬 PC (VS Code Remote-SSH) 연결 설정

Host ros2-server_oracle
    HostName <Tailscale_할당_IP>
    User ubuntu
    IdentityFile ~/.ssh/oci_private_key.key

# 무설치 웹 IDE (code-server) 및 HTTPS 접근 구축

# 1. code-server 설치
curl -fsSL [https://code-server.dev/install.sh](https://code-server.dev/install.sh) | sh

# 2. 백그라운드 서비스 활성화 및 서버 시작
sudo systemctl enable --now code-server@$USER

# code-server 보안 설정
bind-addr: 127.0.0.1:8080
auth: password
password: <본인만의_안전한_비밀번호>
cert: false

# Tailscale Funnel을 이용한 외부 웹 접속 개방
sudo tailscale funnel 8080



<Elicitations message="구축 가이드 문서 작성 및 깃허브 업로드를 성공적으로 완료하셨습니까?">
  <Elicitation label="빌드 임시 파일 숨기기 (.gitignore)" query="깃허브에 업로드할 때 계속 거슬리는 19개의 build, install 임시 파일들을 안 보이게 숨기는 방법(.gitignore)을 알려줘."/>
  <Elicitation label="ROS2 분산 통신 (Domain ID) 설정" query="문서화 작업과 깃허브 업로드는 완벽하게 끝났어. 이제 본격적으로 클라우드 서버와 노트북 간의 ROS2 분산 통신 설정을 진행해 줘."/>
</Elicitations>

## 클라우드 백업 인프라 설정 (빠른 실행 순서)

> 각 단계의 원리와 트러블슈팅은 [CLOUD.md](./CLOUD.md), [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) 참고

### WSL에서 실행

\`\`\`bash
cd ~/scripts  # 또는 리포를 클론한 경로의 scripts/
chmod +x *.sh

# 1) SSH 키 생성 (최초 1회)
./01_setup_ssh_key.sh
# → 출력된 공개키를 오라클 서버의 ~/.ssh/authorized_keys에 등록

# 2) 연결 테스트
./03_test_transfer.sh

# 3) 오브젝트 스토리지 연동 (Customer Secret Key 필요 — Oracle 콘솔에서 미리 발급)
./04_setup_rclone.sh

# 4) 결과물 폴더 준비 및 백업 스크립트 연결
mkdir -p ~/limo_ws/results/important
ln -s ~/scripts/05_backup.sh ~/limo_ws/backup.sh

# 5) 수동 테스트
~/limo_ws/backup.sh
cat ~/limo_ws/backup.log
\`\`\`

### 오라클 서버(`ros2-server`)에서 실행 (최초 1회)

\`\`\`bash
# 콘솔에서 블록 볼륨 생성 + 인스턴스에 연결(Attach) 완료 후:
./02_mount_data_volume.sh
\`\`\`

### Windows PowerShell에서 실행 (관리자 권한)

\`\`\`powershell
cd <스크립트 다운로드 경로>
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\06_register_task_scheduler.ps1
\`\`\`

### 확인

\`\`\`powershell
Start-ScheduledTask -TaskName 'LimoCapstoneBackup'
\`\`\`
이후 WSL에서 `cat ~/limo_ws/backup.log`로 정상 실행 확인.
