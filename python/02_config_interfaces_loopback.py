cat > python/02_config_interfaces_loopback.py << 'EOF'
from pathlib import Path

import yaml
from netmiko import ConnectHandler


BASE_DIR = Path(__file__).resolve().parent.parent
DEVICES_FILE = BASE_DIR / "vars" / "devices.yml"
LAB_FILE = BASE_DIR / "vars" / "lab.yml"
OUTPUT_FILE = BASE_DIR / "outputs" / "show_interfaces_after.txt"


def load_yaml(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def build_config_commands(router_config):
    commands = []

    loopback = router_config["loopback"]
    commands.extend([
        f"interface {loopback['interface']}",
        f"ip address {loopback['ip']} {loopback['mask']}",
        "no shutdown",
        "exit",
    ])

    for interface in router_config["interfaces"]:
        commands.extend([
            f"interface {interface['name']}",
            f"description {interface['description']}",
            f"ip address {interface['ip']} {interface['mask']}",
            "no shutdown",
            "exit",
        ])

    return commands


def configure_interfaces_and_loopbacks():
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

            commands = build_config_commands(lab_routers[device_name])

            print(f"[+] Applying interface and loopback configuration to {device_name}")
            config_result = connection.send_config_set(commands)

            print(f"[+] Saving configuration on {device_name}")
            connection.save_config()

            verify_command = "show ip interface brief"
            verify_result = connection.send_command(verify_command)

            output_file.write("=" * 60 + "\n")
            output_file.write(f"{device_name} - configuration result\n")
            output_file.write("=" * 60 + "\n")
            output_file.write(config_result + "\n\n")

            output_file.write("=" * 60 + "\n")
            output_file.write(f"{device_name} - {verify_command}\n")
            output_file.write("=" * 60 + "\n")
            output_file.write(verify_result + "\n\n")

            print(f"[+] Completed {device_name}")
            connection.disconnect()

    print(f"[+] Result saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    configure_interfaces_and_loopbacks()
EOF