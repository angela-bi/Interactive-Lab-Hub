#!/usr/bin/env python3
import smbus2
import time
import random

I2C_ADDR = 0x27
bus = smbus2.SMBus(1)

# Register map for TCA9534
OUTPUT_REG = 0x01
CONFIG_REG = 0x03  # 1=input, 0=output

# Configure all pins as outputs
bus.write_byte_data(I2C_ADDR, CONFIG_REG, 0x00)

print("Disco mode: random LED blinking on TCA9534")

try:
    while True:
        # Generate a random 8-bit pattern (0–255)
        pattern = random.randint(0, 255)
        # Write to output register
        bus.write_byte_data(I2C_ADDR, OUTPUT_REG, pattern)

        # Optional: print binary pattern for debugging
        print(f"LED pattern: {pattern:08b}")

        # Random delay for more “disco” feel
        time.sleep(random.uniform(0.05, 0.4))

except KeyboardInterrupt:
    # Turn off all LEDs before exiting
    bus.write_byte_data(I2C_ADDR, OUTPUT_REG, 0x00)
    print("\nLights off. Party over")
