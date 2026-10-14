#!/bin/bash
# =====================================================================
# 04_setup_rclone.sh
# 실행 위치: 노트북의 WSL2 (Ubuntu)
# 목적: rclone을 설치하고, 오라클 오브젝트 스토리지(S3 호환 API)를
#       원격 저장소로 등록한다. 이후 rclone sync/copy 명령으로
#       블록 볼륨과는 별개인 20GB 무료 오브젝트 스토리지에
#       "이중 백업" 형태로 결과물을 보낼 수 있다.
#
# 왜 S3 호환 방식(type=s3, provider=Other)을 쓰는가:
#   오라클 오브젝트 스토리지는 Amazon S3와 호환되는 API를 제공한다.
#   OCI 고유의 API 키(개인키/공개키 페어)를 만들 필요 없이,
#   콘솔에서 발급하는 Customer Secret Key(Access Key + Secret Key)만으로
#   접속할 수 있어 설정이 훨씬 간단하다.
#
# 보안 주의: Access Key / Secret Key는 절대 이 스크립트 파일이나
#            git 리포지토리에 하드코딩하지 않는다. 실행할 때마다
#            터미널에서 직접 입력받는다 (Secret Key는 화면에 표시되지 않음).
# =====================================================================
 
set -e
 
REMOTE_NAME="oracle-obj"   # rclone 안에서 이 저장소를 부를 이름
 
# 1) rclone 설치
if ! command -v rclone &> /dev/null; then
    curl https://rclone.org/install.sh | sudo bash
else
    echo "rclone이 이미 설치되어 있습니다."
fi
 
# 2) 콘솔에서 발급받은 정보 입력받기
echo ""
read -p "Object Storage Namespace (예: axxxxxxxxxx): " NAMESPACE
read -p "Region (예: ap-tokyo-1): " REGION
read -p "Customer Secret Key - Access Key ID: " ACCESS_KEY_ID
read -s -p "Customer Secret Key - Secret Access Key (화면에 표시되지 않음): " SECRET_ACCESS_KEY
echo ""
 
ENDPOINT="${NAMESPACE}.compat.objectstorage.${REGION}.oraclecloud.com"
 
# 3) rclone 원격 저장소를 비대화형으로 생성
#    provider=Other : 표준 AWS가 아닌 S3 호환 서비스임을 명시
#    env_auth=false : 환경변수가 아니라 아래 access_key_id/secret_access_key를 직접 사용
rclone config create "$REMOTE_NAME" s3 \
    provider=Other \
    env_auth=false \
    access_key_id="$ACCESS_KEY_ID" \
    secret_access_key="$SECRET_ACCESS_KEY" \
    endpoint="$ENDPOINT"
 
echo ""
echo "설정 완료. 연결 테스트:"
echo "  rclone lsd ${REMOTE_NAME}:"
echo ""
echo "버킷이 없다면 먼저 생성하세요:"
echo "  rclone mkdir ${REMOTE_NAME}:limo-backup"
 