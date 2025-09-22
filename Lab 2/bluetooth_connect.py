# code from https://chatgpt.com/share/68d1a454-700c-800d-97b9-185324e69dee

#!/usr/bin/env python3
import subprocess
import time

JBL_MAC = "D8:37:3B:84:AA:F1"  # JBL Flip 5

def connect_device(mac):
    """Pair, trust, and connect to a Bluetooth device by MAC address."""
    print(f"Connecting to JBL Flip 5 ({mac})...")

    commands = [
        "power on",
        "agent on",
        "default-agent",
        f"pair {mac}",
        f"trust {mac}",
        f"connect {mac}",
        "quit"
    ]

    process = subprocess.Popen(
        ["bluetoothctl"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    for cmd in commands:
        print(f"> {cmd}")
        process.stdin.write(cmd + "\n")
        process.stdin.flush()
        # wait a bit after each command so bluetoothctl can respond
        time.sleep(2)

    process.stdin.close()
    process.wait()
    print("Finished connecting process. If successful, audio will now route to your JBL Flip 5.")

if __name__ == "__main__":
    connect_device(JBL_MAC)
