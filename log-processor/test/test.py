#!/usr/bin/env python3
"""
Test Script for Incident Pilot Log Generation
==============================================

This script generates various types of logs that will trigger the anomaly detection rules
in the anomaly-detector service. The logs are written to ~/test-logs.log and follow
the LogModel format defined in log_model.py.

Usage:
    python test.py [--count COUNT] [--delay DELAY] [--output OUTPUT]

Options:
    --count COUNT    Number of log batches to generate (default: 5)
    --delay DELAY    Delay between batches in seconds (default: 2)
    --output OUTPUT  Output file path (default: ~/test-logs.log)
"""

import json
import random
import time
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any


class LogGenerator:
    """Generates test logs that trigger anomaly detection rules"""
    
    def __init__(self, output_file: str):
        self.output_file = Path(output_file).expanduser()
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Common sources and hostnames
        self.sources = [
            "web-server-01", "web-server-02", "api-gateway", 
            "auth-service", "database-proxy", "load-balancer",
            "payment-service", "user-service", "notification-service"
        ]
        
        self.hostnames = [
            "prod-web-01", "prod-web-02", "prod-api-01",
            "prod-auth-01", "prod-db-01", "prod-lb-01"
        ]
        
        # User agents for scraper detection
        self.scraper_user_agents = [
            "python-requests/2.28.1",
            "curl/7.68.0",
            "wget/1.20.3",
            "Scrapy/2.6.1",
            "bot/1.0",
            "spider/3.2"
        ]
        
        self.normal_user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]
        
        # Common error messages for system call failures
        self.syscall_errors = [
            "Connection refused",
            "Connection timeout",
            "Disk full",
            "Permission denied",
            "No such file or directory",
            "Network unreachable",
            "Out of memory",
            "Resource temporarily unavailable"
        ]

    def generate_base_log(self, source: str = None, hostname: str = None) -> Dict[str, Any]:
        """Generate a base log entry with common fields"""
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": source or random.choice(self.sources),
            "hostname": hostname or random.choice(self.hostnames),
            "tenant": "production"
        }

    def generate_high_error_rate_logs(self, count: int = 8) -> List[Dict[str, Any]]:
        """Generate logs that simulate repeated database errors from one source."""
        logs = []
        source = random.choice(self.sources)
        
        for _ in range(count):
            log = self.generate_base_log(source=source)
            log.update({
                "log_level": "ERROR",
                "message": f"Database connection failed: {random.choice(['timeout after 5s', 'Connection refused', 'Authentication failed'])}",
                "event_type": "database_error",
                "http_status": random.choice([500, 502, 503, 504]),
                "tags": ["database", "error"],
                "extra": {
                    "error_code": random.choice(["08001", "08006", "08004"]),
                    "db_host": f"db{random.randint(1,3)}.internal",
                    "db_port": 5432,
                    "retry_count": random.randint(0, 3)
                }
            })
            logs.append(log)
        return logs

    def generate_web_scraper_logs(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate logs with high request frequency from a suspicious user agent."""
        logs = []
        scraper_ip = f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
        
        for _ in range(count):
            log = self.generate_base_log(source="web-server-01")
            log.update({
                "log_level": "INFO",
                "message": f"HTTP {random.choice(['GET','POST'])} /api/data/{random.randint(1, 1000)} from {scraper_ip}",
                "event_type": "http_request",
                "source_ip": scraper_ip,
                "http_method": random.choice(["GET", "POST"]),
                "http_url": f"/api/data/{random.randint(1, 1000)}",
                "http_status": 200,
                "user_agent": random.choice(self.scraper_user_agents),
                "tags": ["http", "access"],
                "extra": {
                    "bytes_sent": random.randint(3000, 8000),
                    "referer": "-",
                    "session_id": f"sess_{random.randint(1000,9999)}",
                    "requests_per_minute": random.randint(300, 500)
                }
            })
            logs.append(log)
        return logs

    def generate_unauthorized_access_logs(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate failed login attempts from the same IP."""
        logs = []
        attacker_ip = f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}"
        
        for _ in range(count):
            log = self.generate_base_log(source="auth-service")
            log.update({
                "log_level": "WARN",
                "message": f"Authentication failed for user '{random.choice(['admin','root','user','test'])}' from {attacker_ip}",
                "event_type": "auth_failure",
                "source_ip": attacker_ip,
                "username": random.choice(["admin", "root", "user", "test"]),
                "http_method": "POST",
                "http_url": "/auth/login",
                "http_status": 401,
                "tags": ["auth", "security"],
                "extra": {
                    "geoip_country": random.choice(["RU", "CN", "US", "BR"]),
                    "auth_method": "password",
                    "failure_reason": random.choice(["invalid_credentials", "account_locked"]),
                    "user_agent": random.choice(self.normal_user_agents + self.scraper_user_agents)
                }
            })
            logs.append(log)
        return logs

    def generate_system_call_failure_logs(self, count: int = 3) -> List[Dict[str, Any]]:
        """Generate critical logs for system call failures."""
        logs = []
        for _ in range(count):
            error_msg = random.choice(self.syscall_errors)
            log = self.generate_base_log(source="database-proxy")
            log.update({
                "log_level": "CRITICAL",
                "message": f"System call '{random.choice(['connect','read','write','open'])}' failed: {error_msg}",
                "event_type": "syscall_failure",
                "tags": ["system", "error"],
                "extra": {
                    "syscall": random.choice(["connect", "read", "write", "open"]),
                    "errno": random.randint(1, 255),
                    "error_message": error_msg,
                    "pid": random.randint(1000, 9999)
                }
            })
            logs.append(log)
        return logs

    def generate_silence_detection_scenario(self) -> List[Dict[str, Any]]:
        """Generate a monitoring event showing a service not responding."""
        logs = []
        silent_source = "notification-service"
        log = self.generate_base_log(source="monitoring-agent")
        log.update({
            "log_level": "WARN",
            "message": f"No heartbeat from {silent_source} for {random.randint(300, 600)}s",
            "event_type": "service_check",
            "tags": ["monitoring", "availability"],
            "extra": {
                "checked_service": silent_source,
                "last_seen": (datetime.utcnow() - timedelta(minutes=5)).isoformat() + "Z",
                "check_interval_sec": 60
            }
        })
        logs.append(log)
        return logs

    def generate_latency_threshold_logs(self, count: int = 4) -> List[Dict[str, Any]]:
        """Generate logs with unusually high response times."""
        logs = []
        for _ in range(count):
            latency = random.randint(2000, 5000)
            log = self.generate_base_log(source="api-gateway")
            log.update({
                "log_level": "WARN",
                "message": f"Slow HTTP GET /api/users/{random.randint(1, 1000)} took {latency}ms",
                "event_type": "http_request",
                "http_method": "GET",
                "http_url": f"/api/users/{random.randint(1, 1000)}",
                "http_status": 200,
                "tags": ["performance", "http"],
                "extra": {
                    "response_time_ms": latency,
                    "db_queries": random.randint(1, 10),
                    "cache_hit": random.choice([True, False])
                }
            })
            logs.append(log)
        return logs

    def generate_normal_logs(self, count: int = 10) -> List[Dict[str, Any]]:
        """Generate logs that represent normal application activity."""
        logs = []
        for _ in range(count):
            log = self.generate_base_log()
            log.update({
                "log_level": random.choice(["INFO", "DEBUG"]),
                "message": f"HTTP {random.choice(['GET','POST','PUT'])} /home processed successfully",
                "event_type": "http_request",
                "source_ip": f"192.168.1.{random.randint(1, 100)}",
                "http_method": random.choice(["GET", "POST", "PUT"]),
                "http_url": f"/api/endpoint/{random.randint(1, 100)}",
                "http_status": random.choice([200, 201, 204]),
                "user_agent": random.choice(self.normal_user_agents),
                "tags": ["http", "access"],
                "extra": {
                    "bytes_sent": random.randint(1000, 9000),
                    "cache_hit": random.choice([True, False]),
                    "processing_time_ms": random.randint(50, 200)
                }
            })
            logs.append(log)
        return logs


    def write_logs_to_file(self, logs: List[Dict[str, Any]]):
        """Write logs to the output file in JSON format"""
        with open(self.output_file, 'a', encoding='utf-8') as f:
            for log in logs:
                f.write(json.dumps(log, default=str) + '\n')

    def generate_all_test_scenarios(self, batch_count: int = 1, delay: float = 2.0):
        """Generate all test scenarios"""
        print(f"📝 Starting log generation to {self.output_file}")
        print(f"🔄 Will generate {batch_count} batch(es) with {delay}s delay between batches\n")
        
        # Clear the file
        with open(self.output_file, 'w') as f:
            pass
        
        for batch in range(batch_count):
            print(f"📦 Batch {batch + 1}/{batch_count}")
            print("=" * 50)
            
            # Generate different types of anomalous logs
            all_logs = []
            
            # 1. High Error Rate (triggers recent_error_count >= 5)
            all_logs.extend(self.generate_high_error_rate_logs(8))
            
            # 2. Web Scraper Detection (triggers potential_scraper = true)
            all_logs.extend(self.generate_web_scraper_logs(5))
            
            # 3. Unauthorized Access (triggers unauthorized_count >= 3)
            all_logs.extend(self.generate_unauthorized_access_logs(5))
            
            # 4. System Call Failures (triggers failed_syscall = true)
            all_logs.extend(self.generate_system_call_failure_logs(3))
            
            # 5. Silence Detection (triggers is_silent = true)
            all_logs.extend(self.generate_silence_detection_scenario())
            
            # 6. High Latency logs
            all_logs.extend(self.generate_latency_threshold_logs(4))
            
            # 7. Some normal logs
            all_logs.extend(self.generate_normal_logs(10))
            
            # Shuffle logs to simulate realistic timing
            random.shuffle(all_logs)
            
            # Write logs to file
            self.write_logs_to_file(all_logs)
            
            print(f"✅ Generated {len(all_logs)} logs in batch {batch + 1}")
            
            if batch < batch_count - 1:
                print(f"⏳ Waiting {delay} seconds before next batch...\n")
                time.sleep(delay)
        
        print(f"\n🎉 Log generation completed!")
        print(f"📁 Logs written to: {self.output_file}")
        print(f"📊 Total file size: {self.output_file.stat().st_size} bytes")
        
        # Display summary
        print("\n📋 Generated Log Types Summary:")
        print("  🔥 High Error Rate logs (8 per batch)")
        print("  🕷️ Web Scraper Detection logs (5 per batch)")
        print("  🚫 Unauthorized Access logs (5 per batch)")
        print("  💥 System Call Failure logs (3 per batch)")
        print("  🔇 Silence Detection logs (1 per batch)")
        print("  ⏰ High Latency logs (4 per batch)")
        print("  ✅ Normal logs (10 per batch)")
        print(f"  📦 Total logs per batch: 36")
        print(f"  📦 Total logs generated: {36 * batch_count}")


def main():
    """Main function to run the log generator"""
    parser = argparse.ArgumentParser(
        description="Generate test logs for Incident Pilot anomaly detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test.py                          # Generate 5 batches with default settings
  python test.py --count 3 --delay 1      # Generate 3 batches with 1s delay
  python test.py --output ./my-logs.log   # Use custom output file
        """
    )
    
    parser.add_argument(
        '--count', '-c', 
        type=int, 
        default=5,
        help='Number of log batches to generate (default: 5)'
    )
    
    parser.add_argument(
        '--delay', '-d', 
        type=float, 
        default=2.0,
        help='Delay between batches in seconds (default: 2.0)'
    )
    
    parser.add_argument(
        '--output', '-o', 
        type=str, 
        default='~/test-logs.log',
        help='Output file path (default: ~/test-logs.log)'
    )
    
    args = parser.parse_args()
    
    try:
        generator = LogGenerator(args.output)
        generator.generate_all_test_scenarios(
            batch_count=args.count,
            delay=args.delay
        )
        
        print(f"\n🚀 Next Steps:")
        print(f"1. Start your log processor service")
        print(f"2. Start your anomaly detector service")
        print(f"3. Feed the generated logs into your pipeline")
        print(f"4. Monitor the anomaly detection results")
        
    except KeyboardInterrupt:
        print("\n⏹️ Log generation interrupted by user")
    except Exception as e:
        print(f"\n❌ Error generating logs: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
