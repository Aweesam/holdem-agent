#!/usr/bin/env python3
"""
holdemctl - Holdem Project Launch Control System

A fool-proof way to start the complete holdem stack:
- API Server (FastAPI) 
- Dashboard (NextJS)
- Poker Agent (via API control)

Usage:
  holdemctl up           - Start all services
  holdemctl down         - Stop all services
  holdemctl status       - Show service status
  holdemctl logs <service> [--follow] - View service logs

Environment Variables:
  HOLDEM_API_PORT=8000        - API server port
  HOLDEM_DASHBOARD_PORT=3000  - Dashboard port  
  HOLDEM_AGENT_HEADLESS=true  - Run agent in headless mode
  HOLDEM_AGENT_SITE_URL=...   - Override poker site URL
  LOG_LEVEL=INFO              - Python services log level
  LOG_FORMAT=standard         - Log format (standard|json)
  DASH_LOG_LEVEL=info         - Dashboard log level
"""

import argparse
import os
import sys
import time
import signal
import subprocess
import json
import socket
import requests
import webbrowser
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from holdem.utils.logging_config import setup_logger, ensure_log_directories
    # Setup logging for holdemctl
    logger = setup_logger(__name__, 'holdemctl')
except ImportError:
    # Fallback if logging module not available
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    def ensure_log_directories():
        pass


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m' 
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class ServiceManager:
    """Manages holdem services with health checks and process management"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.dashboard_dir = self.project_root / "holdem-dashboard"
        self.state_file = self.project_root / ".holdemctl_state.json"
        
        # Ensure log directories exist
        ensure_log_directories()
        self.log_dir = self.project_root / "logs"
        
        # Configuration from environment
        self.api_port = int(os.environ.get('HOLDEM_API_PORT', 8000))
        self.dashboard_port = int(os.environ.get('HOLDEM_DASHBOARD_PORT', 3000))
        self.agent_headless = os.environ.get('HOLDEM_AGENT_HEADLESS', 'true').lower() == 'true'
        self.agent_site_url = os.environ.get('HOLDEM_AGENT_SITE_URL')
        
        self.processes = {}
        self.log_files = {}  # Track open log files
        self.load_state()
        
        # Setup signal handlers for graceful shutdown
        self._shutdown_in_progress = False
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        if self._shutdown_in_progress:
            return  # Prevent recursive calls
        self._shutdown_in_progress = True
        print(f"\n{Colors.WARNING}🛑 Received signal {signum}, shutting down gracefully...{Colors.ENDC}")
        self.stop_all_services()
        sys.exit(0)
    
    def log(self, message: str, color: str = Colors.ENDC):
        """Print colored log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{color}[{timestamp}] {message}{Colors.ENDC}")
        
        # Also log to file
        if color == Colors.FAIL:
            logger.error(message)
        elif color == Colors.WARNING:
            logger.warning(message)
        elif color == Colors.OKGREEN:
            logger.info(message)
        else:
            logger.info(message)
    
    def start_process_with_logs(self, name: str, command: List[str], cwd: Optional[str] = None, env: Optional[Dict] = None) -> subprocess.Popen:
        """Start a process and capture its output to log files."""
        # Create log files for stdout and stderr
        holdemctl_log_dir = self.log_dir / "holdemctl"
        holdemctl_log_dir.mkdir(exist_ok=True)
        
        stdout_log = holdemctl_log_dir / f"{name}_stdout.log"
        stderr_log = holdemctl_log_dir / f"{name}_stderr.log"
        
        # Open log files
        stdout_file = open(stdout_log, 'a', buffering=1)  # Line buffered
        stderr_file = open(stderr_log, 'a', buffering=1)  # Line buffered
        
        # Store file handles for cleanup
        self.log_files[name] = {'stdout': stdout_file, 'stderr': stderr_file}
        
        # Add timestamp header to logs
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        stdout_file.write(f"\n=== Process started at {timestamp} ===\n")
        stderr_file.write(f"\n=== Process started at {timestamp} ===\n")
        stdout_file.flush()
        stderr_file.flush()
        
        # Start the process
        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            stdout=stdout_file,
            stderr=stderr_file,
            text=True
        )
        
        return process
    
    def close_log_files(self, name: str):
        """Close log files for a service."""
        if name in self.log_files:
            try:
                self.log_files[name]['stdout'].close()
                self.log_files[name]['stderr'].close()
            except:
                pass
            del self.log_files[name]
    
    def find_free_port(self, preferred_port: int) -> int:
        """Find a free port, starting with the preferred one"""
        for port in range(preferred_port, preferred_port + 100):
            if self.is_port_available(port):
                return port
        raise RuntimeError(f"Could not find free port starting from {preferred_port}")
    
    def is_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return True
            except socket.error:
                return False
    
    def wait_for_health_check(self, url: str, timeout: int = 30) -> bool:
        """Wait for a service to become healthy"""
        self.log(f"⏳ Waiting for service at {url}")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    self.log(f"✅ Service healthy at {url}", Colors.OKGREEN)
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        
        self.log(f"❌ Service failed to become healthy at {url}", Colors.FAIL)
        return False
    
    def save_state(self):
        """Save current process state to file"""
        state = {
            'processes': {name: proc.pid for name, proc in self.processes.items() if proc.poll() is None},
            'ports': {
                'api': self.api_port,
                'dashboard': self.dashboard_port
            },
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.log(f"⚠️  Warning: Could not save state: {e}", Colors.WARNING)
    
    def load_state(self):
        """Load process state from file"""
        if not self.state_file.exists():
            return
        
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                
            # Clean up stale processes
            stale_pids = []
            for name, pid in state.get('processes', {}).items():
                try:
                    os.kill(pid, 0)  # Check if process exists
                except OSError:
                    stale_pids.append(name)
            
            # Remove stale entries
            for name in stale_pids:
                del state['processes'][name]
            
            if stale_pids:
                self.log(f"🧹 Cleaned up {len(stale_pids)} stale process(es)", Colors.WARNING)
                
        except Exception as e:
            self.log(f"⚠️  Warning: Could not load state: {e}", Colors.WARNING)
    
    def kill_processes_on_ports(self, ports: List[int]):
        """Kill any processes using the specified ports"""
        killed_any = False
        for port in ports:
            try:
                result = subprocess.run(
                    ['lsof', '-ti', f':{port}'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0 and result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        try:
                            os.kill(int(pid), signal.SIGTERM)
                            self.log(f"🧹 Killed stale process {pid} on port {port}", Colors.WARNING)
                            killed_any = True
                        except (OSError, ValueError):
                            pass
            except FileNotFoundError:
                # lsof not available, try netstat approach
                pass
        
        if killed_any:
            time.sleep(2)  # Give processes time to die
    
    def start_api_server(self) -> bool:
        """Start the API server"""
        if not self.is_port_available(self.api_port):
            # Try to find alternative port
            new_port = self.find_free_port(self.api_port + 1)
            self.log(f"⚠️  Port {self.api_port} busy, using {new_port}", Colors.WARNING)
            self.api_port = new_port
        
        self.log(f"🚀 Starting API server on port {self.api_port}")
        
        env = os.environ.copy()
        env['PORT'] = str(self.api_port)
        
        try:
            cmd = [sys.executable, "live_agent_server.py"]
            proc = self.start_process_with_logs('api', cmd, cwd=str(self.project_root), env=env)
            
            self.processes['api'] = proc
            self.save_state()
            
            # Wait for API to be healthy
            health_url = f"http://localhost:{self.api_port}/api/health"
            if not self.wait_for_health_check(health_url):
                return False
            
            self.log(f"✅ API server ready at http://localhost:{self.api_port}", Colors.OKGREEN)
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to start API server: {e}", Colors.FAIL)
            return False
    
    def start_dashboard(self) -> bool:
        """Start the NextJS dashboard"""
        if not self.dashboard_dir.exists():
            self.log(f"❌ Dashboard directory not found: {self.dashboard_dir}", Colors.FAIL)
            return False
        
        # Check if dashboard port is available
        if not self.is_port_available(self.dashboard_port):
            new_port = self.find_free_port(self.dashboard_port + 1)
            self.log(f"⚠️  Port {self.dashboard_port} busy, using {new_port}", Colors.WARNING)
            self.dashboard_port = new_port
        
        self.log(f"🚀 Starting dashboard on port {self.dashboard_port}")
        
        env = os.environ.copy()
        env['PORT'] = str(self.dashboard_port)
        env['NEXT_PUBLIC_API_URL'] = f"http://localhost:{self.api_port}"
        
        try:
            # Check for node_modules
            if not (self.dashboard_dir / "node_modules").exists():
                self.log("📦 Installing dashboard dependencies...", Colors.OKCYAN)
                install_proc = subprocess.run(
                    ["npm", "install"],
                    cwd=self.dashboard_dir,
                    capture_output=True,
                    text=True
                )
                if install_proc.returncode != 0:
                    self.log(f"❌ npm install failed: {install_proc.stderr}", Colors.FAIL)
                    return False
            
            cmd = ["npm", "run", "dev", "--", "--port", str(self.dashboard_port)]
            proc = self.start_process_with_logs('dashboard', cmd, cwd=str(self.dashboard_dir), env=env)
            
            self.processes['dashboard'] = proc
            self.save_state()
            
            # Wait for dashboard to be ready with simple HTTP check
            # NextJS output parsing was causing issues, so we use health check
            dashboard_url = f"http://localhost:{self.dashboard_port}"
            if not self.wait_for_health_check(dashboard_url, timeout=60):
                # If still not ready, check if process died
                if proc.poll() is not None:
                    self.log("❌ Dashboard process died during startup", Colors.FAIL)
                    if 'dashboard' in self.processes:
                        del self.processes['dashboard']
                return False
            
            self.log(f"✅ Dashboard ready at {dashboard_url}", Colors.OKGREEN)
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to start dashboard: {e}", Colors.FAIL)
            return False
    
    def start_agent(self) -> bool:
        """Start the poker agent via API"""
        self.log("🤖 Starting poker agent...")
        
        try:
            control_url = f"http://localhost:{self.api_port}/api/agent/control"
            payload = {
                "action": "start",
                "headless": self.agent_headless
            }
            
            if self.agent_site_url:
                payload["site_url"] = self.agent_site_url
            
            response = requests.post(control_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'started':
                    self.log("✅ Poker agent started successfully", Colors.OKGREEN)
                    return True
                else:
                    self.log(f"⚠️  Agent start result: {result.get('message', 'Unknown')}", Colors.WARNING)
                    return True  # Sometimes agent needs manual login
            else:
                self.log(f"❌ Failed to start agent: HTTP {response.status_code}", Colors.FAIL)
                return False
                
        except Exception as e:
            self.log(f"❌ Failed to start agent: {e}", Colors.FAIL)
            return False
    
    def stop_service(self, name: str) -> bool:
        """Stop a specific service"""
        if name not in self.processes:
            return True
            
        proc = self.processes[name]
        if proc.poll() is not None:
            # Process already stopped
            del self.processes[name]
            return True
        
        self.log(f"🛑 Stopping {name}...")
        
        try:
            # For processes with process groups (like npm), kill the whole group
            try:
                if hasattr(proc, 'pid'):
                    # Try to kill process group first (for npm/node processes)
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                    self.log(f"   Sent SIGTERM to process group {os.getpgid(proc.pid)}")
            except (OSError, AttributeError):
                # Fall back to single process termination
                proc.terminate()
            
            try:
                proc.wait(timeout=8)
                self.log(f"✅ {name} stopped gracefully", Colors.OKGREEN)
            except subprocess.TimeoutExpired:
                # Force kill if graceful shutdown fails
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                except (OSError, AttributeError):
                    proc.kill()
                proc.wait()
                self.log(f"⚠️  {name} force-killed", Colors.WARNING)
            
            del self.processes[name]
            return True
            
        except Exception as e:
            self.log(f"❌ Error stopping {name}: {e}", Colors.FAIL)
            return False
    
    def stop_all_services(self):
        """Stop all running services"""
        self.log("🛑 Stopping all services...")
        
        # Stop in reverse order
        services = ['dashboard', 'api']
        for service_name in services:
            self.stop_service(service_name)
        
        # Clean up state file
        if self.state_file.exists():
            self.state_file.unlink()
        
        self.log("✅ All services stopped", Colors.OKGREEN)
    
    def show_status(self):
        """Show status of all services"""
        self.log("📊 Service Status", Colors.HEADER)
        print("=" * 50)
        
        # Check API
        api_status = "❌ Stopped"
        if 'api' in self.processes and self.processes['api'].poll() is None:
            try:
                response = requests.get(f"http://localhost:{self.api_port}/api/health", timeout=2)
                if response.status_code == 200:
                    api_status = f"✅ Running (port {self.api_port})"
                else:
                    api_status = f"⚠️  Unhealthy (port {self.api_port})"
            except:
                api_status = f"⚠️  Not responding (port {self.api_port})"
        
        print(f"API Server:  {api_status}")
        
        # Check Dashboard
        dashboard_status = "❌ Stopped"
        if 'dashboard' in self.processes and self.processes['dashboard'].poll() is None:
            try:
                response = requests.get(f"http://localhost:{self.dashboard_port}", timeout=2)
                if response.status_code == 200:
                    dashboard_status = f"✅ Running (port {self.dashboard_port})"
                else:
                    dashboard_status = f"⚠️  Unhealthy (port {self.dashboard_port})"
            except:
                dashboard_status = f"⚠️  Not responding (port {self.dashboard_port})"
        
        print(f"Dashboard:   {dashboard_status}")
        
        # Check Agent
        agent_status = "❌ Stopped"
        if 'api' in self.processes and self.processes['api'].poll() is None:
            try:
                response = requests.get(f"http://localhost:{self.api_port}/api/agent/status", timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    status = data.get('status', 'unknown')
                    if status == 'running':
                        agent_status = "✅ Running"
                    elif status == 'stopped':
                        agent_status = "⏸️  Stopped"
                    else:
                        agent_status = f"⚠️  {status.title()}"
            except:
                agent_status = "❌ Unknown"
        
        print(f"Poker Agent: {agent_status}")
        print("=" * 50)
        
        if api_status.startswith("✅") and dashboard_status.startswith("✅"):
            print(f"\n📊 Dashboard: http://localhost:{self.dashboard_port}")
            print(f"🚀 API Docs:  http://localhost:{self.api_port}/docs")
    
    def start_all_services(self):
        """Start all services in correct order"""
        self.log("🎰 Starting Holdem Stack", Colors.HEADER)
        print("=" * 50)
        
        # Clean up any stale processes on our ports
        self.log("🧹 Cleaning up stale processes...")
        self.kill_processes_on_ports([self.api_port, self.dashboard_port])
        
        # Step 1: Start API Server
        if not self.start_api_server():
            self.log("❌ Failed to start API server, aborting", Colors.FAIL)
            return False
        
        time.sleep(2)  # Brief pause between services
        
        # Step 2: Start Dashboard
        if not self.start_dashboard():
            self.log("❌ Failed to start dashboard", Colors.FAIL)
            self.stop_service('api')
            return False
        
        time.sleep(3)  # Let dashboard fully initialize
        
        # Step 3: Start Agent (optional, may require manual login)
        agent_started = self.start_agent()
        if not agent_started:
            self.log("⚠️  Agent start failed, but continuing (manual login may be needed)", Colors.WARNING)
        
        print("\n" + "=" * 50)
        self.log("🎉 Holdem Stack Started Successfully!", Colors.OKGREEN)
        print("=" * 50)
        
        print(f"\n📊 Dashboard URLs:")
        print(f"   - Frontend:  http://localhost:{self.dashboard_port}")
        print(f"   - API:       http://localhost:{self.api_port}")
        print(f"   - API Docs:  http://localhost:{self.api_port}/docs")
        print(f"\n🔄 WebSocket:   ws://localhost:{self.api_port}/ws")
        
        if not agent_started:
            print(f"\n🤖 Agent Control:")
            print(f"   Use the dashboard to start the poker agent")
            print(f"   Manual login may be required for Club WPT Gold")
        
        print(f"\n💡 Commands:")
        print(f"   - Stop all:     holdemctl down")
        print(f"   - View status:  holdemctl status")
        
        # Optional: Open browser
        try:
            time.sleep(2)
            self.log("🌐 Opening dashboard in browser...")
            webbrowser.open(f"http://localhost:{self.dashboard_port}")
        except Exception as e:
            self.log(f"⚠️  Could not open browser: {e}", Colors.WARNING)
        
        print(f"\n🛑 Press Ctrl+C to stop all services")
        
        # Monitor processes
        try:
            while True:
                time.sleep(5)
                # Check if any critical process died
                for name, proc in list(self.processes.items()):
                    if proc.poll() is not None:
                        self.log(f"❌ {name} process died unexpectedly", Colors.FAIL)
                        if name in ['api', 'dashboard']:
                            self.log("🛑 Critical service died, shutting down", Colors.FAIL)
                            self.stop_all_services()
                            return False
                        else:
                            del self.processes[name]
        
        except KeyboardInterrupt:
            self.stop_all_services()
        
        return True
    
    def show_logs(self, service: str, follow: bool = False):
        """Show logs for a specific service."""
        log_files = []
        
        if service == 'api':
            log_files = [
                self.log_dir / 'api' / 'api.log',
                self.log_dir / 'holdemctl' / 'api_stdout.log',
                self.log_dir / 'holdemctl' / 'api_stderr.log'
            ]
        elif service == 'dashboard':
            log_files = [
                self.log_dir / 'dashboard' / 'dashboard-*.log',  # Will be expanded
                self.log_dir / 'holdemctl' / 'dashboard_stdout.log',
                self.log_dir / 'holdemctl' / 'dashboard_stderr.log'
            ]
        elif service == 'agent':
            log_files = [
                self.log_dir / 'agent' / 'agent.log'
            ]
        elif service == 'holdemctl':
            log_files = [
                self.log_dir / 'holdemctl' / 'holdemctl.log'
            ]
        else:
            print(f"❌ Unknown service: {service}")
            print("Available services: api, dashboard, agent, holdemctl")
            return
        
        # Find existing log files
        existing_files = []
        for log_file in log_files:
            if '*' in str(log_file):
                # Expand glob pattern
                import glob
                matches = glob.glob(str(log_file))
                existing_files.extend(matches)
            else:
                if log_file.exists():
                    existing_files.append(str(log_file))
        
        if not existing_files:
            print(f"❌ No log files found for service: {service}")
            print(f"Expected locations: {[str(f) for f in log_files]}")
            return
        
        print(f"📋 Showing logs for service: {service}")
        print(f"Log files: {existing_files}")
        print("=" * 60)
        
        if follow:
            # Use tail -f to follow logs
            try:
                cmd = ['tail', '-f'] + existing_files
                subprocess.run(cmd)
            except KeyboardInterrupt:
                print(f"\n📋 Stopped following logs for {service}")
        else:
            # Show recent logs
            try:
                cmd = ['tail', '-n', '100'] + existing_files
                subprocess.run(cmd)
            except Exception as e:
                print(f"❌ Error reading logs: {e}")
                # Fallback to reading files directly
                for log_file in existing_files:
                    try:
                        print(f"\n--- {log_file} ---")
                        with open(log_file, 'r') as f:
                            lines = f.readlines()
                            for line in lines[-50:]:  # Show last 50 lines
                                print(line.rstrip())
                    except Exception:
                        continue


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Holdem Project Launch Control System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  HOLDEM_API_PORT         API server port (default: 8000)
  HOLDEM_DASHBOARD_PORT   Dashboard port (default: 3000)
  HOLDEM_AGENT_HEADLESS   Run agent headless (default: true)
  HOLDEM_AGENT_SITE_URL   Override poker site URL

Examples:
  holdemctl up                       # Start all services
  holdemctl down                     # Stop all services  
  holdemctl status                   # Show service status
  holdemctl logs api --follow        # Follow API logs
  holdemctl logs dashboard           # Show recent dashboard logs
  LOG_LEVEL=DEBUG holdemctl up       # Start with debug logging
  HOLDEM_API_PORT=8080 holdemctl up  # Use custom API port
        """
    )
    
    parser.add_argument(
        'command',
        choices=['up', 'down', 'status', 'logs'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Do not open browser automatically'
    )
    
    parser.add_argument(
        'service',
        nargs='?',
        choices=['api', 'dashboard', 'agent', 'holdemctl'],
        help='Service name for logs command'
    )
    
    parser.add_argument(
        '--follow', '-f',
        action='store_true',
        help='Follow log output (like tail -f)'
    )
    
    args = parser.parse_args()
    
    manager = ServiceManager()
    
    if args.command == 'up':
        success = manager.start_all_services()
        sys.exit(0 if success else 1)
    elif args.command == 'down':
        manager.stop_all_services()
        sys.exit(0)
    elif args.command == 'status':
        manager.show_status()
        sys.exit(0)
    elif args.command == 'logs':
        if not args.service:
            print("❌ Service name required for logs command")
            print("Usage: holdemctl logs <service> [--follow]")
            print("Available services: api, dashboard, agent, holdemctl")
            sys.exit(1)
        manager.show_logs(args.service, args.follow)
        sys.exit(0)


if __name__ == "__main__":
    main()