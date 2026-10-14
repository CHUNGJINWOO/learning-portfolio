# LIMO 자율주행 캡스톤 — 시뮬레이션 결과물 클라우드 백업 인프라 구축기

> 드론 로봇공학 전공 캡스톤 프로젝트: AgileX LIMO 로봇 기반 자율주행 시뮬레이션 환경 구축 및 결과물 저장 인프라 설계

---

## 0. 폴더 구조

```
.
├── limo-capstone-cloud-storage-setup.md   (이 문서)
└── scripts/
    ├── 01_setup_ssh_key.sh        # SSH 키 생성 및 오라클 서버 등록
    ├── 02_mount_data_volume.sh    # 블록 볼륨 포맷 및 마운트
    └── 03_test_transfer.sh        # 연결 테스트 (파일 전송)
```

문서 안의 코드 블록은 설명을 위한 발췌이고, **실제로 실행 가능한 전체 스크립트는 `scripts/` 폴더**에 있다. 각 스크립트 상단에 실행 위치(WSL vs 오라클 서버)와 목적, 주의사항을 주석으로 남겨두었다.

---

## 1. 프로젝트 배경

캡스톤 프로젝트에서 **AgileX LIMO** 로봇 플랫폼(ROS2 + Gazebo 기반)을 활용한 자율주행 구현을 진행하고 있다. 시뮬레이션은 SLAM, 경로계획, 장애물 회피 등의 반복 실험이 많아 결과물(로그, rosbag, 지도 파일 등)이 누적되는데, 노트북 저장공간이 넉넉하지 않은 상황(C드라이브 21.8GB, D드라이브 59.5GB)에서 이를 어떻게 안전하게 보관할지가 과제였다.

동시에 학교/개인 실습용으로 Oracle Cloud Always Free 인스턴스를 이미 보유하고 있어서, 이 자원을 시뮬레이션 컴퓨팅과 스토리지 양쪽으로 활용할 수 있는지 검토하는 과정을 거쳤다.

**이 문서의 목적**: 인프라 설계 과정에서 겪은 시행착오와 최종 구조를 기록해, 나중에 동일한 문제가 재발했을 때 빠르게 복구하거나, 이후 다른 프로젝트에 동일 패턴을 재사용할 수 있도록 하기 위함이다.

---

## 2. 문제 인식: 왜 클라우드에서 Gazebo 시뮬레이션이 불가능했는가

### 2.1 초기 계획
Oracle Cloud Always Free의 Ampere(ARM, A1 Flex) 인스턴스(2 OCPU / 12GB RAM)에서 ROS2 Humble + Gazebo Classic 시뮬레이션을 직접 돌리려고 시도했다.

### 2.2 발견한 문제
```bash
apt-cache policy ros-humble-gazebo-ros-pkgs
# N: Unable to locate package ros-humble-gazebo-ros-pkgs
```

이 에러는 저장소 설정 실수가 아니라, **Gazebo Classic(gazebo11)이 arm64 아키텍처용 공식 patternage를 애초에 제공하지 않는다**는 근본적인 한계였다 (공식 [gazebo-classic GitHub 이슈 #3282](https://github.com/gazebosim/gazebo-classic/issues/3282)에서 확인). 소스 빌드도 `gazebo`, `libgazebo-dev` 자체가 arm64용으로 없어 사실상 불가능한 방향이었다.

### 2.3 의사결정
- GPU 없는 ARM 인스턴스의 소프트웨어 렌더링 한계
- Gazebo Classic의 arm64 미지원이라는 구조적 제약
- 2코어 환경에서의 낮은 빌드/시뮬레이션 성능

세 가지를 종합해 **시뮬레이션은 로컬 노트북(x86_64, GPU 보유)에서 실행**하고, **오라클 클라우드는 시뮬레이션 결과물의 백업 저장소 및 CPU 위주 후처리 작업**(SLAM 데이터 정리, 로그 분석 등)으로 역할을 재배치하기로 결정했다.

> **배운 점**: 클라우드 무료 티어의 스펙(코어/메모리)만 보고 판단하면 안 되고, 아키텍처(x86 vs ARM) 호환성을 프로젝트 초기에 먼저 검증해야 시간 낭비를 줄일 수 있다.

---

## 3. 최종 아키텍처

```
┌─────────────────────────┐         Tailscale (사설 네트워크, 암호화)
│  노트북 (Windows)         │◄──────────────────────────────┐
│  ├─ WSL2 (Ubuntu 22.04)  │                                │
│  │   └─ ROS2 Humble       │                                │
│  │      + Gazebo Classic  │                                ▼
│  │      (LIMO 시뮬레이션)  │                  ┌───────────────────────────┐
│  └─ 결과물: rosbag,        │   rsync (SSH)     │ Oracle Cloud (ros2-server) │
│     로그, 지도 파일         │──────────────────►│  Ampere A1 (ARM, 2코어/12GB)│
└─────────────────────────┘                     │  ├─ Block Volume 150GB     │
                                                 │  │   /mnt/data (주 백업)   │
                                                 │  └─ Object Storage 20GB    │
                                                 │      (rclone, 이중 백업)   │
                                                 └───────────────────────────┘
```

**역할 분리 원칙**: 컴퓨팅이 필요한 작업(3D 렌더링, 물리 시뮬레이션)은 로컬에서, 저장이 필요한 작업(결과물 보관)은 클라우드에서 — 각 환경의 강점만 사용한다.

---

## 4. 구현 단계별 정리

### 4.1 네트워크: Tailscale로 사설망 구성

**왜**: 오라클 서버의 SSH 포트를 공인 인터넷에 노출하지 않고, 노트북(WSL)과 클라우드 서버가 마치 같은 사설망에 있는 것처럼 통신하기 위해서. 포트포워딩이나 방화벽 규칙을 직접 관리할 필요가 없어진다.

**결과**: `jinwoo`(Windows), `jinwoo-1`(WSL2), `ros2-server`(Oracle) 세 기기가 모두 Tailscale 사설 IP(100.x.x.x 대역)로 서로 접근 가능한 상태로 연결됨.

### 4.2 SSH 키 기반 인증 설정 (무인 자동화의 전제조건)

> 전체 코드: [`scripts/01_setup_ssh_key.sh`](./scripts/01_setup_ssh_key.sh)

```bash
# WSL(jinwoo-1)에서 실행
ssh-keygen -t ed25519 -f ~/.ssh/oracle_key -N ""
```

**설명**:
- `-t ed25519`: RSA보다 짧고 빠르면서 보안성이 높은 최신 키 타입
- `-N ""`: 키에 암호(passphrase)를 걸지 않음. 자동화 스크립트는 사람이 옆에서 암호를 입력해줄 수 없기 때문에, 무인 실행을 위해서는 암호 없는 키가 필수. (대신 Tailscale 사설망 안에서만 접속 가능하도록 이미 네트워크 레벨에서 보호되고 있어 위험도는 낮췄다.)

**트러블슈팅**: 오라클 클라우드의 우분투 이미지는 기본적으로 비밀번호 SSH 로그인이 꺼져 있어 `ssh-copy-id`가 `Permission denied (publickey)`로 실패했다. 인스턴스 생성 시 발급받은 **원래 개인키**로 먼저 접속한 뒤, 그 세션 안에서 새 공개키를 `~/.ssh/authorized_keys`에 수동으로 추가하는 방식으로 우회했다.

```bash
# 원래 키로 접속 후, 서버 안에서 실행
echo "<새로 만든 oracle_key.pub 내용>" >> ~/.ssh/authorized_keys
```

### 4.3 오라클 블록 볼륨(150GB) 생성 및 마운트

> 전체 코드: [`scripts/02_mount_data_volume.sh`](./scripts/02_mount_data_volume.sh)

**왜**: Oracle Always Free의 블록 스토리지 한도는 부팅 볼륨 포함 총 200GB. 부팅 볼륨이 47GB였으므로, 여유를 두고 150GB를 데이터 전용 볼륨으로 할당했다.

콘솔에서 볼륨 생성 → `ros2-server` 인스턴스에 **매개변수 가상화(Paravirtualized)** 방식으로 연결(iSCSI보다 설정이 단순함) → 서버에서 포맷 및 마운트:

```bash
sudo mkfs.ext4 /dev/sdb                # ext4 파일시스템으로 포맷
sudo mkdir -p /mnt/data
sudo mount /dev/sdb /mnt/data          # 마운트
sudo blkid /dev/sdb                    # UUID 확인

# /etc/fstab에 등록 → 재부팅해도 자동 마운트
echo 'UUID="<확인한 UUID>" /mnt/data ext4 defaults,nofail 0 2' | sudo tee -a /etc/fstab

sudo chown ubuntu:ubuntu /mnt/data     # 소유권 이전 (sudo 없이 쓰기 가능하게)
```

**각 옵션 설명**:
- `mkfs.ext4`: 리눅스 표준 파일시스템으로 디스크를 초기화 — 포맷 없이는 파일을 저장할 수 없음
- `/etc/fstab`의 `nofail`: 볼륨 마운트에 실패해도 서버 자체 부팅은 막지 않는 안전장치
- `chown`: 마운트 직후 소유자가 `root`라 일반 계정(자동화 스크립트 포함)이 쓰기 권한이 없었던 것을 해결

### 4.4 결과물 전송 테스트

> 전체 코드: [`scripts/03_test_transfer.sh`](./scripts/03_test_transfer.sh)

```bash
# WSL에서
scp -i ~/.ssh/oracle_key ~/test.txt ubuntu@100.127.79.18:/mnt/data/
```
Tailscale IP(`100.127.79.18`)를 통해 SSH 키 인증만으로 비밀번호 없이 전송 성공 확인.

---

## 5. 앞으로 진행할 것 (TODO)

- [ ] Oracle Object Storage(20GB, `rclone`)를 이중 백업 계층으로 추가
- [ ] `rsync` + `rclone`을 하나의 `backup.sh` 스크립트로 통합
- [ ] Windows 작업 스케줄러에 등록해 `wsl.exe` 호출 방식으로 매일 자동 백업 실행
  (WSL이 완전히 꺼져 있어도 Windows 작업 스케줄러가 깨워서 실행 가능 — WSL 내부 cron은 WSL이 꺼지면 같이 정지되므로 부적합)

---

## 6. 이 작업으로 얻은 것

| 항목 | 내용 |
|---|---|
| 문제 진단 능력 | "설정 실수"와 "구조적 아키텍처 한계"를 구분해 원인을 정확히 짚어낸 경험 (arm64 미지원 이슈) |
| 인프라 설계 | 컴퓨팅과 스토리지의 역할을 분리해 각 환경의 제약을 우회하는 아키텍처 설계 |
| 네트워크 보안 | 공인 IP 노출 없이 Tailscale 사설망 + SSH 키 인증으로 안전한 무인 자동화 기반 마련 |
| 클라우드 실무 | Oracle Cloud 콘솔에서 블록 볼륨 생성·연결, Linux 파일시스템 마운트 및 영구 설정(fstab) 경험 |

---

## Oracle Cloud 백업 인프라 구축

> 아키텍처 배경은 [ARCHITECTURE.md](./ARCHITECTURE.md), 겪은 문제는 [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) 참고

### 1. Tailscale로 사설망 구성

오라클 서버의 SSH 포트를 공인 인터넷에 노출하지 않고, 노트북(WSL)과 클라우드 서버가
같은 사설망에 있는 것처럼 통신하기 위함. `jinwoo`(Windows), `jinwoo-1`(WSL2),
`ros2-server`(Oracle) 세 기기가 Tailscale 사설 IP(100.x.x.x 대역)로 연결됨.

### 2. SSH 키 기반 무인 인증

> 코드: [`scripts/01_setup_ssh_key.sh`](../scripts/01_setup_ssh_key.sh)

\`\`\`bash
ssh-keygen -t ed25519 -f ~/.ssh/oracle_key -N ""
\`\`\`
- `-N ""`: 암호 없는 키 — 자동화 스크립트가 사람 개입 없이 실행되기 위한 전제조건
  (Tailscale 사설망 안에서만 접속 가능해 위험도는 낮춤)

### 3. 블록 볼륨(150GB) 생성 및 마운트

> 코드: [`scripts/02_mount_data_volume.sh`](../scripts/02_mount_data_volume.sh)

Always Free 블록 스토리지 한도 200GB 중 부팅 볼륨(47GB)을 제외한 150GB를 데이터
전용으로 할당. 콘솔에서 **매개변수 가상화(Paravirtualized)** 방식으로 연결 후:

\`\`\`bash
sudo mkfs.ext4 /dev/sdb
sudo mkdir -p /mnt/data && sudo mount /dev/sdb /mnt/data
sudo blkid /dev/sdb   # UUID 확인
echo 'UUID="<UUID>" /mnt/data ext4 defaults,nofail 0 2' | sudo tee -a /etc/fstab
sudo chown ubuntu:ubuntu /mnt/data
\`\`\`

### 4. 연결 테스트

> 코드: [`scripts/03_test_transfer.sh`](../scripts/03_test_transfer.sh)

\`\`\`bash
scp -i ~/.ssh/oracle_key ~/test.txt ubuntu@100.127.79.18:/mnt/data/
\`\`\`

### 5. 오브젝트 스토리지(20GB) rclone 이중 백업

> 코드: [`scripts/04_setup_rclone.sh`](../scripts/04_setup_rclone.sh)

블록 볼륨은 인스턴스가 살아있어야 접근 가능한 반면, 오브젝트 스토리지는 S3 호환
API로 독립적으로 접근 가능해 완전히 다른 장애 지점을 가진 이중 백업 계층으로 적합.

\`\`\`bash
rclone config create oracle-obj s3 \\
    provider=Other env_auth=false \\
    access_key_id="<Access Key ID>" \\
    secret_access_key="<Secret Access Key>" \\
    endpoint="<namespace>.compat.objectstorage.<region>.oraclecloud.com"
\`\`\`
보안: Access/Secret Key는 스크립트에 하드코딩하지 않고 실행 시점에 터미널로 직접
입력받도록 설계 (git에 비밀키가 올라가는 사고 방지).

### 6. 자동화: rsync + rclone 통합

> 코드: [`scripts/05_backup.sh`](../scripts/05_backup.sh)

전체 결과물은 블록 볼륨(주력)으로, `results/important/`의 핵심 파일만 오브젝트
스토리지로 이중 백업. `--update` 옵션으로 이미 전송된 파일은 재전송하지 않음.

### 7. Windows 작업 스케줄러 등록 — 매일 23:00 자동 실행

> 코드: [`scripts/06_register_task_scheduler.ps1`](../scripts/06_register_task_scheduler.ps1)

WSL2가 꺼지면 내부 cron도 같이 멈추기 때문에, Windows 작업 스케줄러가 `wsl.exe`를
직접 호출해 필요할 때 WSL을 깨우는 방식을 사용. `-WakeToRun`, `-StartWhenAvailable`
옵션으로 절전/종료 상태에도 최대한 대응.