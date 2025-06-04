#!/usr/bin/env python3
"""Test Teensy communication before ROS integration."""

import serial
import struct
import time
from typing import Optional, Tuple

class TeensyCommsTester:
    """Test Teensy UART communication."""
    
    def __init__(self, port: str = "/dev/ttyACM0", baud: int = 1000000):
        self.port = port
        self.baud = baud
        self.ser: Optional[serial.Serial] = None
        
    def connect(self) -> bool:
        """Connect to Teensy."""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baud,
                timeout=1.0
            )
            time.sleep(2)  # Arduino reset time
            print(f"✅ Connected to Teensy on {self.port}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False
    
    def test_version(self) -> bool:
        """Request firmware version."""
        print("\n📋 Testing firmware version request...")
        
        # Send version request (based on your protocol)
        cmd = struct.pack('<BB', 0x01, 0x00)  # CMD_VERSION
        self.ser.write(cmd)
        
        # Read response
        response = self.ser.read(64)
        if response:
            print(f"✅ Version response: {response}")
            return True
        else:
            print("❌ No version response")
            return False
    
    def test_imu_stream(self) -> bool:
        """Test IMU data streaming."""
        print("\n📊 Testing IMU data stream...")
        
        # Clear buffer
        self.ser.reset_input_buffer()
        
        # Collect data for 2 seconds
        start_time = time.time()
        packet_count = 0
        
        while time.time() - start_time < 2.0:
            if self.ser.in_waiting >= 64:  # Expected packet size
                packet = self.ser.read(64)
                packet_count += 1
        
        rate = packet_count / 2.0
        print(f"📈 Received {packet_count} packets ({rate:.1f} Hz)")
        
        expected_rate = 100  # 100Hz target
        if rate > expected_rate * 0.9:
            print(f"✅ IMU streaming at target rate")
            return True
        else:
            print(f"❌ IMU rate too low (expected {expected_rate}Hz)")
            return False
    
    def test_motor_command(self) -> bool:
        """Test sending motor commands."""
        print("\n🎮 Testing motor command...")
        
        # Send safe test command
        # Structure based on your protocol
        cmd = struct.pack(
            '<BBHHf',  # cmd, motor_id, position, speed, current
            0x10,      # CMD_MOTOR
            0x01,      # Motor 1
            2048,      # Center position
            100,       # Slow speed
            0.5        # Low current
        )
        
        self.ser.write(cmd)
        time.sleep(0.1)
        
        # Check for ACK
        response = self.ser.read(8)
        if response and response[0] == 0xAA:  # ACK byte
            print("✅ Motor command acknowledged")
            return True
        else:
            print("❌ No motor command ACK")
            return False
    
    def run_all_tests(self):
        """Run all communication tests."""
        print("🧪 Teensy Communication Test Suite")
        print("=" * 50)
        
        if not self.connect():
            return False
        
        tests = [
            ("Firmware Version", self.test_version),
            ("IMU Streaming", self.test_imu_stream),
            ("Motor Command", self.test_motor_command),
        ]
        
        passed = 0
        for name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                print(f"❌ {name} failed: {e}")
        
        print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
        return passed == len(tests)

if __name__ == "__main__":
    tester = TeensyCommsTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)