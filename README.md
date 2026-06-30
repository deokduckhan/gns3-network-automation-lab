# Network Automation Lab

GNS3 환경에서 Python, YAML, Netmiko, Ansible을 활용하여 Cisco IOS 라우터의 상태 확인 및 기본 설정을 자동화하는 실습 프로젝트입니다.

## Topology

- NetworkAutomation-1: 192.168.100.10/24
- R1: 192.168.100.11/24
- R2: 192.168.100.12/24
- R3: 192.168.100.13/24

## Tools

- Python
- YAML
- Netmiko
- Ansible
- GNS3

## Security Note

실제 접속 정보가 포함된 `vars/devices.yml`과 `ansible/inventory.yml`은 `.gitignore`에 등록하여 GitHub에 업로드하지 않습니다.