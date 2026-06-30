cat > python/03_config_ospf.py << 'EOF'
from pathlib import Path
from time import sleep

import yaml
from netmiko import ConnectHandler


BASE_DIR = Path(__file__).resolve().parent.parent
DEVICES_FILE = BASE_DIR / "vars" / "devices.yml"
LAB_FILE = BASE_DIR / "vars" / "lab.yml"
OUTPUT_FILE = BASE_DIR / "outputs" / "ospf_verification.txt"


def load_yaml(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def build_ospf_commands(router_config):
    ospf = router_config["ospf"]
    process_id = ospf["process_id"]
    router_id = ospf["router_id"]

    commands = [
        f"router ospf {process_id}",
        f"router-id {router_id}",
    ]

    loopback = router_config["loopback"]
    commands.append(f"network {loopback['ip']} 0.0.0.0 area 0")

    for interface in router_config["interfaces"]:
        commands.append(f"network {interface['ip']} 0.0.0.0 area 0")

    return commands


def configure_ospf():
    devices_data = load_yaml(DEVICES_FILE)
    lab_data = load_yaml(LAB_FILE)

    devices = devices_data["routers"]
    lab_routers = lab_data["routers"]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as output_file:
        for device in devices:
            device_name = device["name"]

            if device_name not in lab_routers:
                print(f"[!] No lab configuration found for {device_name}")
                continue

            print(f"[+] Connecting to {device_name} ({device['host']})")

            connection = ConnectHandler(
                device_type=device["device_type"],
                host=device["host"],
                username=device["username"],
                password=device["password"],
                secret=device["password"],
            )

            connection.enable()

            commands = build_ospf_commands(lab_routers[device_name])

            print(f"[+] Applying OSPF configuration to {device_name}")
            config_result = connection.send_config_set(commands)

            print(f"[+] Saving configuration on {device_name}")
            connection.save_config()

            output_file.write("=" * 60 + "\n")
            output_file.write(f"{device_name} - OSPF configuration result\n")
            output_file.write("=" * 60 + "\n")
            output_file.write(config_result + "\n\n")

            connection.disconnect()

    print("[+] Waiting for OSPF neighbor adjacency...")
    sleep(15)

    with open(OUTPUT_FILE, "a", encoding="utf-8") as output_file:
        for device in devices:
            device_name = device["name"]

            print(f"[+] Verifying OSPF on {device_name}")

            connection = ConnectHandler(
                device_type=device["device_type"],
                host=device["host"],
                username=device["username"],
                password=device["password"],
                secret=device["password"],
            )

            connection.enable()

            verification_commands = [
                "show ip ospf neighbor",
                "show ip route ospf",
                "show ip protocols",
            ]

            output_file.write("=" * 60 + "\n")
            output_file.write(f"{device_name} - OSPF verification\n")
            output_file.write("=" * 60 + "\n")

            for command in verification_commands:
                result = connection.send_command(command)

                output_file.write(f"\n--- {command} ---\n")
                output_file.write(result + "\n")

            print(f"[+] Completed OSPF verification on {device_name}")

            connection.disconnect()

    print(f"[+] Result saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    configure_ospf()
EOF