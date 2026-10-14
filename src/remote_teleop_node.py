# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 CHUNGJINWOO
"""
@file: remote_teleop_node.py
@brief: 로컬 환경(Gram)에서 클라우드(OCI)의 시뮬레이션 로봇을 제어하기 위한 원격 조향 퍼블리셔 노드

[기술적 선택 이유 및 설계 의도 (Rationale)]
1. 분산 환경에서의 역할 분담 (Distributed Architecture)
   - 물리 연산이 필요한 무거운 로봇 시뮬레이션(Gazebo)은 OCI 클라우드 서버에서 실행합니다.
   - 본 노드는 키보드 등 사용자의 입력을 직접 받아야 하므로 로컬 노트북에서 실행되며,
     Tailscale VPN망을 통해 클라우드 서버의 '/cmd_vel' 토픽으로 제어 명령을 원격 전송합니다.

2. ROS2 표준 메시지 타입 사용 (Reusability)
   - 자체적인 문자열(String) 형식이 아닌 ROS2 표준인 'geometry_msgs/Twist'를 사용했습니다.
   - 이를 통해 향후 시뮬레이션 로봇에서 실제 하드웨어로 전환하더라도 통신 코드의 수정 없이 
     그대로 적용할 수 있는 높은 재사용성을 확보했습니다.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class RemoteTeleopNode(Node):
    def __init__(self):
        # 노드 이름 설정
        super().__init__('remote_teleop_node')
        
        # 클라우드 서버의 로봇을 제어할 속도 명령(cmd_vel) 퍼블리셔 생성
        # 큐 사이즈(QoS)를 10으로 설정하여 네트워크 지연 시 메시지 유실을 방지함
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        self.get_logger().info('✅ 원격 제어 노드가 시작되었습니다. (클라우드로 명령 전송 준비 완료)')

    def send_command(self, linear_x, angular_z):
        """
        로봇의 선속도(linear_x)와 각속도(angular_z)를 받아 Twist 메시지로 발행하는 함수
        """
        msg = Twist()
        msg.linear.x = float(linear_x)
        msg.angular.z = float(angular_z)
        
        self.publisher_.publish(msg)
        self.get_logger().info(f'📡 명령 전송됨: 전진 속도={linear_x} m/s, 회전 속도={angular_z} rad/s')

def main(args=None):
    rclpy.init(args=args)
    node = RemoteTeleopNode()
    
    try:
        # 테스트 예시: 실행 시 로봇을 앞으로 0.5m/s로 전진시키는 명령을 1회 전송합니다.
        # 실제 적용 시에는 이 부분을 키보드 입력(input) 모듈과 결합하여 동적으로 제어합니다.
        node.send_command(0.5, 0.0)
        
        # 노드를 살아있는 상태로 유지
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('🛑 사용자에 의해 원격 제어 노드를 종료합니다.')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()