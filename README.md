# OpenGreenWave-India

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

OpenGreenWave-India is an open-source hardware and software solution designed to solve the "clock drift" problem in isolated, offline traffic lights, specifically targeting the infrastructure constraints of tier-2 and tier-3 Indian cities.

## The Problem
Most traffic lights in smaller Indian cities are "isolated." They use basic offline timers without any connection to a central network. While engineers can program them mathematically to create a continuous "Green Wave" (where vehicles driving at a steady speed hit all green lights), these microcontrollers rely on standard quartz clocks. 

Over a few days, these clocks suffer from **drift**—one junction runs a few seconds fast, another runs slow. Soon, the synchronization collapses, causing extreme gridlock. Traditional solutions require digging up roads to lay multi-million-rupee fiber-optic networks.

## The Solution
OpenGreenWave-India bridges this hardware limitation using atomic satellite time. By equipping cheap edge microcontrollers (like the ESP32) with a ₹300 NEO-6M GPS module, the offline traffic boxes sync their internal clocks to universal UTC time daily. 

**Result:** Flawless, indefinite Green Wave synchronization without requiring an internet connection, Wi-Fi, or centralized fiber-optics.

---

## Project Architecture

This repository consists of two parts:

### 1. The Calculator (`/calculator`)
A lightweight Python CLI tool. You input the distance between Junction A and Junction B, along with the target speed limit. It calculates the exact mathematical time offset required for a vehicle to hit the Green Wave, generating a JSON configuration snippet.

### 2. The Firmware (`/firmware`)
MicroPython code designed for an ESP32 or Raspberry Pi Pico. 
- It reads atomic NMEA sentences from the NEO-6M GPS module via UART.
- Syncs the microcontroller's internal Real-Time Clock (RTC).
- Triggers the Green/Yellow/Red GPIO relays precisely on the calculated schedule, indefinitely.

---

## Getting Started

### Prerequisites
- Python 3.8+ (For the calculator tool)
- Thonny IDE or esptool (For flashing the MicroPython firmware)
- Hardware: ESP32 development board, NEO-6M GPS module, jumper wires, relays/LEDs.

### Step 1: Run the Calculator
Navigate to the `calculator` directory and run the script:
```bash
cd calculator
python greenwave_calc.py
```
Follow the prompts to enter your intersection distance and speed limit. It will generate a `config.json` file containing your specific offset.

### Step 2: Flash the Firmware
1. Flash your ESP32 with the standard [MicroPython firmware](http://micropython.org/download/esp32/).
2. Open [Thonny IDE](https://thonny.org/).
3. Copy the `config.json` generated in Step 1 to the root of the ESP32 filesystem.
4. Upload `firmware/main.py` to the ESP32.

### Step 3: Wiring
Connect the NEO-6M GPS to the ESP32:
- GPS **TX** -> ESP32 **GPIO 16** (RX)
- GPS **RX** -> ESP32 **GPIO 17** (TX)
- GPS **VCC** -> ESP32 **3.3V** (or 5V depending on module)
- GPS **GND** -> ESP32 **GND**

The traffic light relays (simulated as LEDs in the code) are mapped to GPIO pins 25 (Red), 26 (Yellow), and 27 (Green).

## Contributing
We welcome contributions! Especially if you are traffic engineering student looking to adapt this for complex multi-lane junctions or integrate it into SUMO simulations.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
