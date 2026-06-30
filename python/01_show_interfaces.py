from pathlib import Path

import yaml
from netmiko import ConnectHandler


BASE_DIR = Path(__file__).resolve().parent.parent
DEVICES_FILE = BASE_DIR / "vars" / "devices.yml"
OUTPUT_FILE = BASE_DIR / "outputs" / "show_interfaces_before.txt"


def load_devices():
    with open(DEVICES_FILE, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return data["routers"]


def collect_interface_status():
    devices = load_devices()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as output_file:
        for device in devices:
            device_name = device["name"]

            print(f"[+] Connecting to {device_name} ({device['host']})")

            connection = ConnectHandler(
                device_type=device["device_type"],
                host=device["host"],
                username=device["username"],
                password=device["password"],
                secret=device["password"],
            )

            connection.enable()

            command = "show ip interface brief"
            result = connection.send_command(command)

            output_file.write("=" * 60 + "\n")
            output_file.write(f"{device_name} - {command}\n")
            output_file.write("=" * 60 + "\n")
            output_file.write(result + "\n\n")

            print(f"[+] Collected interface status from {device_name}")

            connection.disconnect()

    print(f"[+] Result saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    collect_interface_status()