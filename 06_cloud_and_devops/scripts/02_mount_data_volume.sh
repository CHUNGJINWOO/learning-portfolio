#!/bin/bash
# =====================================================================
# 02_mount_data_volume.sh
# 실행 위치: 오라클 클라우드 서버 (ros2-server) 안에서 직접 실행
# 목적: 콘솔에서 인스턴스에 연결(Attach)한 블록 볼륨(150GB, /dev/sdb)을
#       ext4로 포맷하고 /mnt/data에 마운트한 뒤, 재부팅 후에도
#       자동으로 다시 마운트되도록 /etc/fstab에 등록한다.
#
# 사전 조건: 오라클 콘솔에서 블록 볼륨을 생성하고 인스턴스에
#            "매개변수 가상화(Paravirtualized)" 방식으로 연결까지 완료한 상태.
#            연결 직후 `lsblk`로 새 디바이스명(예: sdb)을 확인해야 한다.
#
# 주의: DEVICE 변수는 lsblk 결과에 맞게 반드시 확인 후 수정할 것.
#       잘못된 디바이스를 지정하면 기존 데이터가 있는 디스크를
#       포맷해버릴 위험이 있다 (이 스크립트는 "빈 새 볼륨"을 전제로 한다).
# =====================================================================
 
set -e
 
DEVICE="/dev/sdb"       # lsblk로 확인한 새 볼륨의 디바이스명
MOUNT_POINT="/mnt/data" # 마운트할 경로
OWNER="ubuntu"          # 소유권을 넘길 계정 (자동화 스크립트가 sudo 없이 쓰기 위함)
 
echo "현재 연결된 디스크 목록:"
lsblk
 
read -p "위 목록에서 ${DEVICE} 를 포맷합니다. 맞습니까? (데이터가 모두 삭제됩니다) [y/N] " confirm
if [[ "$confirm" != "y" ]]; then
    echo "취소되었습니다."
    exit 1
fi
 
# 1) ext4 파일시스템으로 포맷
#    리눅스 표준 파일시스템 — 포맷 없이는 디스크에 파일을 저장할 수 없다
sudo mkfs.ext4 "$DEVICE"
 
# 2) 마운트 지점 생성 및 마운트
sudo mkdir -p "$MOUNT_POINT"
sudo mount "$DEVICE" "$MOUNT_POINT"
 
# 3) UUID 확인 (디바이스명은 재부팅 시 바뀔 수 있어 UUID로 fstab에 등록해야 안전)
UUID=$(sudo blkid -s UUID -o value "$DEVICE")
echo "확인된 UUID: $UUID"
 
# 4) /etc/fstab에 등록 → 서버가 재부팅돼도 자동으로 다시 마운트됨
#    nofail: 혹시 볼륨 인식에 실패해도 서버 자체 부팅은 막지 않는 안전장치
FSTAB_LINE="UUID=${UUID} ${MOUNT_POINT} ext4 defaults,nofail 0 2"
if ! grep -qF "$UUID" /etc/fstab; then
    echo "$FSTAB_LINE" | sudo tee -a /etc/fstab
else
    echo "이미 fstab에 등록되어 있습니다."
fi
 
# 5) 소유권 이전 — root 소유 상태면 일반 계정 스크립트가 sudo 없이 쓸 수 없음
sudo chown "${OWNER}:${OWNER}" "$MOUNT_POINT"
 
echo ""
echo "마운트 완료. 결과 확인:"
df -h "$MOUNT_POINT"
 