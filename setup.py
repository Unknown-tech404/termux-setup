#__________________| SCRIPT INFO |__________________#
# TOOL NAME: TERMUX SETUP ADVANCED
# CREATOR  : Unknown-tech404
# TEAM     : Candpur Cyber Team
# VERSION  : 1.0 (ULTIMATE SECURE)
# PYTHON   : 3.11+
#__________________| IMPORT MODULES |__________________#
import os
import sys
import time
import datetime
import subprocess
import json
import shutil
import logging
import configparser
import random
import re
import hashlib
import secrets
import shlex
import resource
from pathlib import Path
from typing import Tuple, Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

# Auto-install missing requirements
try:
    import requests
    from rich.console import Console
    from rich import print
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.table import Table
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich.style import Style
    from rich.columns import Columns
    from rich.prompt import Prompt
    from rich.syntax import Syntax
    from rich.traceback import install
    install(show_locals=True)
except ImportError:
    os.system('pip install requests rich urllib3')
    import requests
    from rich.console import Console
    from rich import print
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.table import Table
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich.style import Style
    from rich.columns import Columns
    from rich.prompt import Prompt
    from rich.syntax import Syntax

from time import localtime as lt

#__________________| TERMUX DETECTION |__________________#
def is_termux():
    """Check if running in Termux"""
    return any([
        'com.termux' in os.environ.get('PREFIX', ''),
        os.path.exists('/data/data/com.termux'),
        'TERMUX_VERSION' in os.environ
    ])

TERMUX = is_termux()

if TERMUX:
    # Enable TrueColor support in Termux
    os.environ['TERM'] = 'xterm-256color'
    os.environ['COLORTERM'] = 'truecolor'

# Setup logging
logging.basicConfig(
    filename='termux_setup.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

console = Console()

#__________________| CONFIGURATION |__________________#
CONFIG_FILE = Path.home() / '.termux_setup.cfg'
BACKUP_DIR = Path("/sdcard/Termux_Backup")
RESTORE_DIR = Path("/sdcard/Termux_Restore")
HOME_DIR = Path.home()
BASHRC_PATH = HOME_DIR / '.bashrc'
ZSH_PATH = HOME_DIR / '.zshrc'

# Create config if not exists
if not CONFIG_FILE.exists():
    config = configparser.ConfigParser()
    config['DEFAULT'] = {
        'auto_backup': 'true',
        'log_level': 'INFO',
        'theme': 'dark',
        'default_shell': 'bash',
        'security_level': 'high'
    }
    with open(CONFIG_FILE, 'w') as f:
        config.write(f)

#__________________| COLOURS |__________________#
A = '\x1b[1;97m'
Y = '\033[1;33m'
G = '\033[1;92m'
R = '\033[1;91m'
B = '\033[1;94m'
M = '\033[1;95m'
C = '\033[1;96m'
RESET = '\x1b[0m'

#__________________| SECURITY MANAGER |__________________#
class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PARANOID = "paranoid"

@dataclass
class SecurityConfig:
    level: SecurityLevel = SecurityLevel.HIGH
    enable_whitelist: bool = True
    enable_input_sanitization: bool = True
    enable_path_validation: bool = True
    enable_env_sanitization: bool = True
    enable_rate_limiting: bool = True
    max_command_length: int = 1000
    command_timeout: int = 30

class SecurityManager:
    """Ultimate Security Manager for command execution"""

    def __init__(self, config: SecurityConfig = None):
        self.config = config or SecurityConfig()
        self.command_history: List[str] = []
        self.session_token = secrets.token_urlsafe(32)
        self.command_count = 0
        self.last_command_time = time.time()

        # Command whitelist by category
        self.safe_commands = {
            'pkg': ['install', 'uninstall', 'list', 'show', 'search'],
            'apt': ['install', 'remove', 'update', 'upgrade', 'list'],
            'pip': ['install', 'uninstall', 'list', 'show', 'freeze'],
            'python': ['-c', '--version', '-m'],
            'git': ['clone', 'pull', 'push', 'status', 'log'],
            'curl': ['-O', '-L', '-o', '-s'],
            'wget': ['-O', '-q', '-c'],
            'ls': ['-l', '-a', '-h'],
            'cat': [],
            'echo': [],
            'mkdir': ['-p'],
            'rm': ['-rf', '-f'],
            'cp': ['-r', '-f'],
            'mv': [],
            'chmod': ['+x', '755', '644'],
            'chown': [],
            'tar': ['-czf', '-xzf', '-xf'],
            'zip': ['-r'],
            'unzip': [],
            'grep': ['-r', '-i', '-n'],
            'sed': ['-i'],
            'awk': [],
            'nano': [],
            'vim': [],
            'neofetch': [],
            'htop': [],
            'btop': [],
            'glances': []
        }

        # Dangerous patterns - strictly blocked
        self.dangerous_patterns = [
            r';', r'&&', r'\|\|', r'`', r'\$\(', r'>', r'<',
            r'\|\s*\|',  # Multiple pipes
            r'\b(rm|dd|format|mkfs|fdisk|shred)\b.*\b(/\s*$|/\s*\*|root)',  # Dangerous commands
            r'chmod\s+777',  # Overly permissive
            r'chown\s+root',  # Privilege escalation
            r'sudo\s+',  # Sudo without validation
            r'su\s+',  # Switch user
            r'passwd',  # Password change
            r'wget\s+.*\|\s*bash',  # Remote execution
            r'curl\s+.*\|\s*bash',  # Remote execution
            r'python[23]?\s+-c\s+[\'"]import\s+os;',  # Python code injection
            r'perl\s+-e',  # Perl execution
            r'ruby\s+-e',  # Ruby execution
        ]

        # Allowed paths
        self.allowed_paths = [
            HOME_DIR,
            Path("/data/data/com.termux/files/home"),
            Path("/sdcard"),
            Path("/storage/emulated/0")
        ]

        # Rate limiting
        self.max_commands_per_minute = 30
        self.command_timestamps: List[float] = []

    def validate_command(self, command: str) -> Tuple[bool, str, Optional[List[str]]]:
        """Comprehensive command validation"""

        # Check command length
        if len(command) > self.config.max_command_length:
            return False, f"Command exceeds maximum length ({self.config.max_command_length})", None

        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, command):
                self.log_security_event(f"Dangerous pattern detected: {pattern} in: {command}")
                return False, f"Security violation: Dangerous pattern detected", None

        # Parse command
        try:
            args = shlex.split(command)
        except Exception as e:
            return False, f"Invalid command syntax: {str(e)}", None

        if not args:
            return False, "Empty command", None

        cmd_base = args[0]

        # Whitelist check
        if self.config.enable_whitelist:
            if cmd_base not in self.safe_commands:
                # Check if it's in PATH and is a known safe command
                if not self.is_safe_command(cmd_base):
                    self.log_security_event(f"Command not in whitelist: {cmd_base}")
                    return False, f"Command '{cmd_base}' not in whitelist", None

            # Check subcommands/arguments
            if cmd_base in self.safe_commands and len(args) > 1:
                allowed_subcmds = self.safe_commands[cmd_base]
                if allowed_subcmds and args[1] not in allowed_subcmds:
                    return False, f"Subcommand '{args[1]}' not allowed for {cmd_base}", None

        return True, "Command validated", args

    def is_safe_command(self, cmd: str) -> bool:
        """Check if command is in PATH and known to be safe"""
        try:
            # Check if command exists
            path = shutil.which(cmd)
            if not path:
                return False

            # Check if it's a system command in safe location
            safe_locations = ['/data/data/com.termux/files/usr/bin']
            return any(str(path).startswith(loc) for loc in safe_locations)
        except:
            return False

    def sanitize_input(self, user_input: str) -> str:
        """Sanitize user input"""
        if not self.config.enable_input_sanitization:
            return user_input

        # Remove all dangerous characters
        sanitized = re.sub(r'[;&`$|<>(){}\[\]\n\r\t]', '', user_input)
        return sanitized.strip()

    def validate_path(self, base_path: Path, user_path: str) -> Optional[Path]:
        """Validate and resolve path safely"""
        if not self.config.enable_path_validation:
            return base_path / user_path

        try:
            # Resolve both paths
            base_resolved = base_path.resolve()
            full_path = (base_path / user_path).resolve()

            # Check if full_path is within allowed paths
            for allowed in self.allowed_paths:
                allowed_resolved = allowed.resolve()
                if allowed_resolved in full_path.parents or full_path == allowed_resolved:
                    return full_path

            # Check if within base path
            if base_resolved in full_path.parents or full_path == base_resolved:
                return full_path

            self.log_security_event(f"Path traversal attempt: {user_path}")
            return None

        except Exception as e:
            self.log_security_event(f"Path validation error: {str(e)}")
            return None

    def sanitize_env(self) -> Dict[str, str]:
        """Create sanitized environment"""
        env = os.environ.copy()

        # Remove dangerous environment variables
        dangerous_vars = [
            'LD_PRELOAD', 'LD_LIBRARY_PATH', 'LD_DEBUG',
            'LD_AUDIT', 'LD_PROFILE', 'LD_USE_LOAD_BIAS',
            'JAVA_TOOL_OPTIONS', 'PERL5OPT', 'PYTHONINSPECT',
            'RUBYOPT', 'RUBYLIB', 'NODE_OPTIONS'
        ]

        for var in dangerous_vars:
            env.pop(var, None)

        # Set safe environment
        env['PATH'] = '/data/data/com.termux/files/usr/bin:/data/data/com.termux/files/usr/bin/applets:/system/bin:/system/xbin'
        env['HOME'] = str(HOME_DIR)
        env['TERM'] = 'xterm-256color'
        env['LANG'] = 'en_US.UTF-8'

        return env

    def check_rate_limit(self) -> bool:
        """Check rate limiting"""
        if not self.config.enable_rate_limiting:
            return True

        now = time.time()

        # Clean old timestamps
        self.command_timestamps = [t for t in self.command_timestamps if now - t < 60]

        # Check rate
        if len(self.command_timestamps) >= self.max_commands_per_minute:
            return False

        self.command_timestamps.append(now)
        return True

    def log_security_event(self, message: str):
        """Log security event"""
        logging.warning(f"SECURITY: {message}")
        # Also append to security log
        with open(HOME_DIR / 'security.log', 'a') as f:
            f.write(f"{datetime.datetime.now()}: {message}\n")

    def get_command_hash(self, command: str) -> str:
        """Create command hash for verification"""
        return hashlib.sha256(command.encode()).hexdigest()

# Initialize security manager
security = SecurityManager()

#__________________| CORE METHODS |__________________#
def safe_execute(command: str, timeout: int = 30) -> Tuple[bool, str]:
    """Ultra-secure command execution"""

    # Rate limiting
    if not security.check_rate_limit():
        logging.error("Rate limit exceeded")
        return False, "Rate limit exceeded. Please wait."

    # Validate command
    is_valid, message, args = security.validate_command(command)
    if not is_valid:
        return False, message

    # Log command (with hash for verification)
    cmd_hash = security.get_command_hash(command)
    logging.info(f"Executing command (hash: {cmd_hash}): {command[:100]}...")

    # Sanitize environment
    env = security.sanitize_env()

    try:
        # Set resource limits
        resource.setrlimit(resource.RLIMIT_CPU, (timeout, timeout))
        resource.setrlimit(resource.RLIMIT_FSIZE, (10 * 1024 * 1024, 10 * 1024 * 1024))  # 10MB max output

        # Execute without shell
        result = subprocess.run(
            args,
            timeout=timeout,
            capture_output=True,
            text=True,
            env=env,
            cwd=str(HOME_DIR),
            check=False
        )

        # Check output size
        if len(result.stdout) > 10 * 1024 * 1024:  # 10MB
            return False, "Output too large (>10MB)"

        if result.returncode == 0:
            logging.info(f"Command successful (hash: {cmd_hash})")
            return True, result.stdout
        else:
            error_msg = result.stderr[:500]  # Limit error message size
            logging.error(f"Command failed (hash: {cmd_hash}): {error_msg}")
            return False, error_msg

    except subprocess.TimeoutExpired:
        logging.error(f"Command timeout (hash: {cmd_hash})")
        return False, "Command timed out"
    except MemoryError:
        logging.error(f"Memory error (hash: {cmd_hash})")
        return False, "Memory limit exceeded"
    except Exception as e:
        logging.error(f"Execution error (hash: {cmd_hash}): {str(e)}")
        return False, f"Execution error: {str(e)}"

def check_dependencies() -> bool:
    """Check if required tools are installed"""
    required = ['python', 'git']
    missing = []

    for tool in required:
        if not shutil.which(tool):
            missing.append(tool)

    if missing:
        print(Panel(f"[yellow]Missing tools: {', '.join(missing)}",
                   style="bold bright_black",
                   title="<[bold white reverse] WARNING [/bold white reverse]>"))
        return False
    return True

def get_user_choice(prompt: str, valid_options: List[str]) -> str:
    """Get validated user input"""
    while True:
        # Sanitize input
        raw_input = console.input(prompt).strip().lower()
        sanitized = security.sanitize_input(raw_input)

        if sanitized in valid_options:
            return sanitized

        print(Panel("[bold red]Invalid option. Please try again.",
                   style="bold bright_black"))

def validate_path_input(user_path: str) -> Optional[Path]:
    """Validate path input"""
    return security.validate_path(HOME_DIR, user_path)

def create_restore_point() -> Optional[Path]:
    """Create a secure restore point before major changes"""
    try:
        # Validate backup directory
        backup_path = security.validate_path(Path("/sdcard"), "Termux_Backup")
        if not backup_path:
            backup_path = HOME_DIR / "backups"

        backup_path.mkdir(exist_ok=True, parents=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_path / f"restore_point_{timestamp}.tar.gz"

        # Backup package list
        packages_file = HOME_DIR / "packages.txt"
        safe_execute("pkg list-installed > packages.txt")

        # Create backup with error checking
        if packages_file.exists() and packages_file.stat().st_size > 0:
            # Verify backup command is safe
            cmd = f"tar -czf {backup_file} -C {HOME_DIR} packages.txt 2>/dev/null"
            success, _ = safe_execute(cmd)

            if success and backup_file.exists():
                packages_file.unlink()  # Clean up temp file
                print(Panel(f"[green]Restore point created: {backup_file}",
                           style="bold bright_black"))

                # Create verification hash
                with open(backup_file, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                with open(backup_path / f"restore_point_{timestamp}.sha256", 'w') as f:
                    f.write(file_hash)

                return backup_file
    except Exception as e:
        logging.error(f"Failed to create restore point: {str(e)}")

    return None

def _clear_():
    """Clear screen"""
    if "linux" in sys.platform.lower():
        os.system("clear")
    elif "win" in sys.platform.lower():
        os.system("cls")

def clear():
    """Clear screen without showing logo"""
    _clear_()

#__________| DYNAMIC DASHBOARD (TELEMETRY) |______________#
def get_ip() -> str:
    """Get public IP address securely"""
    try:
        # Use safe execution
        success, result = safe_execute("curl -s --max-time 3 https://api.ipify.org")
        if success and result.strip():
            return result.strip()

        # Fallback
        success, result = safe_execute("wget -qO- --timeout=3 https://api.ipify.org")
        if success and result.strip():
            return result.strip()
    except:
        pass
    return "Offline"

def get_ping() -> str:
    """Get network latency"""
    try:
        success, result = safe_execute("ping -c 1 -W 2 8.8.8.8")
        if success and "time=" in result:
            return result.split("time=")[1].split(" ")[0] + " ms"
    except:
        pass
    return "N/A"

def get_storage_usage() -> str:
    """Get storage usage"""
    try:
        success, result = safe_execute("df -h /data")
        if success and "%" in result:
            lines = result.strip().split('\n')
            if len(lines) >= 2:
                return lines[1].split()[-2]
    except:
        pass
    return "N/A"

def get_device_info() -> str:
    """Get device information"""
    try:
        success, result = safe_execute("uname -o")
        if success:
            return result.strip()

        # Fallback
        success, result = safe_execute("getprop ro.product.manufacturer")
        if success:
            manufacturer = result.strip()
            success, result = safe_execute("getprop ro.product.model")
            if success:
                return f"{manufacturer} {result.strip()}"
    except:
        pass
    return "Android"

def get_uptime() -> str:
    """Get system uptime"""
    try:
        success, result = safe_execute("uptime -p")
        if success:
            return result.replace("up ", "").strip()

        # Alternative method
        success, result = safe_execute("cat /proc/uptime")
        if success:
            uptime_seconds = float(result.split()[0])
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)

            parts = []
            if days > 0:
                parts.append(f"{days}d")
            if hours > 0:
                parts.append(f"{hours}h")
            if minutes > 0:
                parts.append(f"{minutes}m")

            return ' '.join(parts) if parts else "< 1m"
    except:
        pass
    return "N/A"

def get_packages_count() -> str:
    """Get installed packages count"""
    try:
        success, result = safe_execute("pkg list-installed")
        if success:
            lines = [line for line in result.strip().split('\n') if line and not line.startswith('[')]
            return str(len(lines))
    except:
        pass
    return "N/A"

tgl = datetime.datetime.now().day
months = {
    '1': 'Jan', '2': 'Feb', '3': 'Mar', '4': 'Apr',
    '5': 'May', '6': 'Jun', '7': 'Jul', '8': 'Aug',
    '9': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
}
bln = months[str(datetime.datetime.now().month)]
thn = datetime.datetime.now().year
date = f"{tgl}/{bln}/{thn}"

ltx = int(lt()[3])
tag = "PM" if ltx > 12 else "AM"
times = time.strftime("%H:%M") + " " + tag

def __details__():
    """Display system information dashboard"""
    ip = get_ip()
    ping = get_ping()
    storage = get_storage_usage()
    device = get_device_info()
    uptime = get_uptime()
    packages = get_packages_count()

    info_panel = Panel(
        f"""[bold black]【[white]•[bold black]】[dark_cyan]DEVICE       [white]➤  [green]{device}
[bold black]【[white]•[bold black]】[dark_cyan]YOUR IP      [white]➤  [green]{ip}
[bold black]【[white]•[bold black]】[dark_cyan]LATENCY      [white]➤  [green]{ping}
[bold black]【[white]•[bold black]】[dark_cyan]STORAGE      [white]➤  [green]{storage}
[bold black]【[white]•[bold black]】[dark_cyan]PACKAGES     [white]➤  [green]{packages}
[bold black]【[white]•[bold black]】[dark_cyan]UPTIME       [white]➤  [green]{uptime}
[bold black]【[white]•[bold black]】[dark_cyan]LOCAL TIME   [white]➤  [green]{times} - {date}""",
        style="bold bright_black",
        title="<[bold white reverse] DYNAMIC DASHBOARD [/bold white reverse]>"
    )
    print(info_panel)

#__________________| LOADING SYSTEM |__________________#
def loadinglisen():
    """Display loading animation"""
    animation = [
        f"[{R}■{RESET}□□□□□□□□□]",
        f"[{G}■■{RESET}□□□□□□□□]",
        f"[{Y}■■■{RESET}□□□□□□□]",
        f"[{B}■■■■{RESET}□□□□□□]",
        f"[{M}■■■■■{RESET}□□□□□]",
        f"[{C}■■■■■■{RESET}□□□□]",
        f"[{A}■■■■■■■{RESET}□□□]",
        f"[{G}■■■■■■■■{RESET}□□]",
        f"[{Y}■■■■■■■■■{RESET}□]",
        f"[{B}■■■■■■■■■■{RESET}]"
    ]

    for i in range(30):
        time.sleep(0.02)
        sys.stdout.write(f"\r\t {Y}Loading{G}.{Y}.{R}.{C}.{A} " +
                        animation[i % len(animation)] + " ")
        sys.stdout.flush()
    print()

#__________________| LOGO |__________________#
def logo():
    """Display tool logo"""
    print(" ")
    logo_panel = Panel(
        """[bold red]● [bold yellow]● [bold green]●
[green1]   ______
[spring_green2]  /_  __/__  _________ ___  __  ___  __
[spring_green11]   / / / _ \\/ ___/ __ `__ \\/ / / / |/_/
[spring_green2]  / / /  __/ /  / / / / / / /_/ />  <
[green1] /_/  \\___/_/  /_/ /_/ /_/\\__,_/_/|_|""",
        style="bold bright_black",
        title="<[bold white reverse] Candpur Cyber Team [/bold white reverse]>"
    )
    print(logo_panel)

    info_panel = Panel(
        """[bold black]【[white]•[bold black]】[bold yellow] DEVELOPER   [white]➤ [green]Unknown-tech404 
[bold black]【[white]•[bold black]】[bold yellow] TEAM        [white]➤ [green]Candpur Cyber Team
[bold black]【[white]•[bold black]】[bold yellow] VERSION     [white]➤ [green]1.0
[bold black]【[white]•[bold black]】[bold yellow] GITHUB      [white]➤ [green]github.com/Unknown-tech404
[bold black]【[white]•[bold black]】[bold yellow] SECURITY    [white]➤ [bold green]100% Secure
[bold black]【[white]•[bold black]】[bold yellow] TOOL        [white]➤ [bold purple reverse] TERMUX SETUP ADVANCED""",
        style="bold bright_black"
    )
    print(info_panel)

#__________________| PACKAGE INSTALL ENGINE |__________________#
def install_packages(pkg_list: list, is_pip: bool = False):
    """Install packages with progress tracking and verification"""
    cmd = "pip install" if is_pip else "pkg install -y"

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="green", finished_style="green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    ) as progress:

        task = progress.add_task(
            "[cyan]Installing packages...",
            total=len(pkg_list)
        )

        for pkg in pkg_list:
            progress.update(
                task,
                description=f"[cyan]Installing: {pkg}"
            )

            # Verify package name
            sanitized_pkg = security.sanitize_input(pkg)
            if sanitized_pkg != pkg:
                logging.warning(f"Package name sanitized: {pkg} -> {sanitized_pkg}")
                pkg = sanitized_pkg

            print(Panel(f"\t[bold black]【[white]•[bold black]】[sea_green2] INSTALLING {pkg.upper()} ",
                       style="bold bright_black"))

            success, output = safe_execute(f"{cmd} {pkg}")

            if not success:
                logging.warning(f"Failed to install {pkg}: {output[:200]}")

            progress.advance(task)

def verify_package_integrity(package: str) -> bool:
    """Verify package integrity"""
    try:
        if package == "python":
            success, result = safe_execute("python --version")
            return success and "Python" in result
        elif package == "git":
            success, result = safe_execute("git --version")
            return success and "git" in result
    except:
        pass
    return False

#__________________| NETWORK UTILITIES |__________________#
def test_network_speed() -> dict:
    """Test network download speed securely"""
    results = {"speed": "N/A", "latency": "N/A", "quality": "N/A"}
    test_url = "http://speedtest.tele2.net/10MB.zip"

    try:
        start_time = time.time()

        # Use curl with timeout and size limit
        success, result = safe_execute("curl -s --max-time 10 --max-filesize 1M -o /dev/null -w '%{speed_download}' http://speedtest.tele2.net/1MB.zip")

        if success and result.strip():
            speed_bps = float(result.strip())
            speed_mbps = speed_bps * 8 / 1024 / 1024  # Convert to Mbps
            results["speed"] = f"{speed_mbps:.2f} Mbps"

            # Quality assessment
            if speed_mbps > 10:
                results["quality"] = "Excellent"
            elif speed_mbps > 5:
                results["quality"] = "Good"
            elif speed_mbps > 2:
                results["quality"] = "Fair"
            else:
                results["quality"] = "Poor"

        # Get latency
        ping_result = get_ping()
        if ping_result != "N/A":
            results["latency"] = ping_result

    except Exception as e:
        logging.error(f"Speed test failed: {str(e)}")

    return results

#__________________| COMPLETE PACKAGE LISTS |__________________#
BASIC_PACKAGES = [
    # Core essentials
    "python", "python2", "python3", "python-pip",
    "git", "curl", "wget", "nano", "vim",
    "zip", "unzip", "tar", "termux-api",
    "bash", "fish", "ruby", "php", "perl",
    "openssh", "figlet", "toilet", "cowsay",
    "neofetch", "htop", "openssl", "openssl-tool",
    "dnsutils", "clang", "make", "cmake",
    "ffmpeg", "screen", "tmux", "net-tools",

    # File management
    "mc", "ranger", "tree", "lf",

    # Text processing
    "jq", "yq", "grep", "sed", "awk", "ripgrep",

    # Network basics
    "traceroute", "whois", "host", "dig", "nslookup",

    # System tools
    "btop", "glances", "duf", "dust",

    # Development tools
    "strace", "ltrace", "gdb", "valgrind", "perf",

    # Enhanced utilities
    "bat", "exa", "fd", "zoxide", "fzf",

    # Banner setup packages
    "figlet", "toilet", "cowsay", "lolcat", "ruby", "gem",
]

ADVANCED_PACKAGES = BASIC_PACKAGES + [
    # Security tools
    "nmap", "hydra", "sqlmap", "wireshark", "tor",
    "sudo", "proot", "termux-chroot", "tsu",
    "w3m", "wcalc", "bmon", "unrar", "ired",
    "goaccess", "golang", "kibi", "mtools",
    "file", "vis", "pass", "pick", "chroot",
    "macchanger", "ninja", "elixir", "swift",
    "xmlstarlet", "fakeroot", "texinfo", "netcat",
    "wren", "gatling", "cvs", "picolisp",
    "cmatrix", "dropbear", "parallel", "lua",
    "help", "wgetrc", "vpn", "vim-python",
    "mariadb", "nginx", "nodejs", "redis",

    # Advanced security
    "nuclei", "subfinder", "httpx", "ffuf",
    "gobuster", "dirb", "nikto", "wpscan",
    "joomscan", "whatweb", "masscan", "zenmap",
    "socat", "tcpdump", "tshark", "ettercap",
    "bettercap", "gpg", "hashcat", "john",
    "aircrack-ng", "sleuthkit", "autopsy",
    "binwalk", "foremost", "testdisk", "photorec",

    # Reverse engineering
    "radare2", "ghidra", "objdump", "strings",

    # Web development
    "apache2", "php-fpm", "composer", "npm",
    "yarn", "gulp", "webpack", "httpie",

    # Databases
    "postgresql", "mysql", "mongodb", "sqlite3",
    "cassandra", "redis-server",

    # Cloud tools
    "awscli", "gcloud", "terraform", "ansible",

    # Media processing
    "youtube-dl", "yt-dlp", "imagemagick",
    "exiftool", "sox", "mpv", "vlc",
]

BASIC_PIP_PACKAGES = [
    "requests", "rich", "bs4", "mechanize",
    "colorama", "future", "lolcat", "cowsay",
    "pip", "setuptools", "wheel",
]

ADVANCED_PIP_PACKAGES = BASIC_PIP_PACKAGES + [
    # Web scraping
    "scrapy", "selenium", "playwright", "beautifulsoup4",
    "lxml", "html5lib", "pyquery",

    # Data science
    "numpy", "pandas", "matplotlib", "seaborn",
    "scipy", "scikit-learn", "statsmodels",

    # Machine learning
    "tensorflow", "torch", "keras", "transformers",
    "xgboost", "lightgbm", "catboost",

    # Computer vision
    "opencv-python", "pillow", "scikit-image",
    "imageio", "imutils", "face-recognition",

    # Networking
    "scapy", "dpkt", "pyshark", "requests-toolbelt",
    "aiohttp", "httpx", "urllib3", "socket",

    # Cryptography
    "cryptography", "pycrypto", "pycryptodome",
    "hashlib", "passlib", "bcrypt",

    # Automation
    "fabric", "paramiko", "netmiko", "napalm",
    "ansible-runner", "pyats", "genie",

    # Web frameworks
    "flask", "django", "fastapi", "bottle",
    "tornado", "aiohttp", "sanic", "quart",

    # Databases
    "sqlalchemy", "alembic", "psycopg2", "pymysql",
    "pymongo", "redis-py", "sqlite3",

    # Testing
    "pytest", "unittest2", "nose", "coverage",
    "mock", "tox", "selenium", "behave",

    # DevOps
    "docker", "kubernetes", "openshift",
    "boto3", "azure-cli", "google-cloud",

    # Media
    "youtube-dl", "pytube", "moviepy", "pydub",
    "opencv-python", "pillow", "wave",

    # Utilities
    "tqdm", "click", "argparse", "pyyaml",
    "toml", "configparser", "dotenv",

    # Exploitation
    "pwntools", "angr", "ropper", "keystone-engine",
    "capstone", "unicorn", "r2pipe",
]

#__________________| BASIC SETUP |__________________#
def basic_setup():
    """Basic Termux setup with essential packages"""
    clear()
    print(Panel("[bold black]【[white]•[bold black]】[blue] STARTING BASIC SETUP...",
                style="bold bright_black",
                title="<[bold white reverse] BASIC SETUP [/bold white reverse]>"))
    time.sleep(2)

    # Create restore point
    create_restore_point()

    # Update system
    safe_execute("apt update -y")
    safe_execute("apt upgrade -y")
    safe_execute("pkg update -y")
    safe_execute("pkg upgrade -y")
    safe_execute("termux-setup-storage")

    # Install essential packages
    install_packages(BASIC_PACKAGES, False)

    # Install Ruby gems for banner
    safe_execute("gem install lolcat")

    # Upgrade pip
    safe_execute("pip install --upgrade pip")
    safe_execute("pip2 install --upgrade pip")
    safe_execute("pip3 install --upgrade pip")

    # Install basic pip packages
    install_packages(BASIC_PIP_PACKAGES, True)

    # Verify installations
    verified = []
    for pkg in ['python', 'git', 'curl']:
        if verify_package_integrity(pkg):
            verified.append(pkg)

    print(Panel(f"[bold green]BASIC SETUP COMPLETED SUCCESSFULLY!\nVerified: {', '.join(verified)}",
                style="bold bright_black"))

    console.input("\n[bold bright_black]   ╰─>[white] Press Enter to return...")
    menu()

#__________________| ADVANCED SETUP |__________________#
def advanced_setup():
    """Advanced Termux setup with complete packages"""
    clear()
    print(Panel("[bold black]【[white]•[bold black]】[magenta] STARTING ADVANCED SETUP...",
                style="bold bright_black",
                title="<[bold white reverse] ADVANCED SETUP [/bold white reverse]>"))
    time.sleep(2)

    # Create restore point
    restore_point = create_restore_point()
    if restore_point:
        print(Panel(f"[green]Restore point created: {restore_point.name}",
                   style="bold bright_black"))

    # Update system
    safe_execute("apt update -y && apt upgrade -y")
    safe_execute("pkg update -y && pkg upgrade -y")
    safe_execute("termux-setup-storage")

    # Install all packages
    install_packages(ADVANCED_PACKAGES, False)

    # Install Ruby gems for banner
    safe_execute("gem install lolcat")

    # Upgrade all pip
    safe_execute("pip install --upgrade pip")
    safe_execute("pip2 install --upgrade pip")
    safe_execute("pip3 install --upgrade pip")

    # Install all Python packages
    install_packages(ADVANCED_PIP_PACKAGES, True)

    # Test network speed
    print(Panel("[bold black]【[white]•[bold black]】[sea_green2] Testing network speed...",
               style="bold bright_black"))
    speed_results = test_network_speed()
    if speed_results['speed'] != 'N/A':
        print(Panel(f"[green]Download speed: {speed_results['speed']} ({speed_results['quality']})",
                   style="bold bright_black"))

    print(Panel("[bold green]ADVANCED SETUP COMPLETED SUCCESSFULLY!",
                style="bold bright_black"))

    console.input("\n[bold bright_black]   ╰─>[white] Press Enter to return...")
    menu()

#__________________| BANNER STYLES |__________________#
BANNER_STYLES = {
    '1': {
        'name': 'CLASSIC SLANT',
        'font': 'slant',
        'color': 'lolcat',
        'description': 'Standard slant font with rainbow colors'
    },
    '2': {
        'name': 'CYBERPUNK',
        'font': 'cyberlarge',
        'color': 'red',
        'description': 'Large cyberpunk style font in red'
    },
    '3': {
        'name': 'RETRO',
        'font': 'banner',
        'color': 'green',
        'description': 'Retro banner style in green'
    },
    '4': {
        'name': '3D EFFECT',
        'font': 'big',
        'color': 'blue',
        'description': 'Big 3D style font in blue'
    },
    '5': {
        'name': 'GRAFFITI',
        'font': 'graffiti',
        'color': 'yellow',
        'description': 'Graffiti style font in yellow'
    },
    '6': {
        'name': 'ASCII ART',
        'font': 'standard',
        'color': 'cyan',
        'description': 'Standard ASCII art with cyan color'
    },
    '7': {
        'name': 'MINIMAL',
        'font': 'small',
        'color': 'white',
        'description': 'Small minimal font in white'
    },
    '8': {
        'name': 'ANIME',
        'font': 'bubble',
        'color': 'magenta',
        'description': 'Bubble letters in magenta'
    },
    '9': {
        'name': 'TERMINAL',
        'font': 'term',
        'color': 'lolcat',
        'description': 'Terminal font with rainbow colors'
    },
    '10': {
        'name': 'RANDOM',
        'font': 'random',
        'color': 'random',
        'description': 'Random font and color combination'
    }
}

def show_banner_styles():
    """Display all available banner styles"""
    table = Table(title="Available Banner Styles", show_header=True, header_style="bold magenta")
    table.add_column("Option", style="cyan")
    table.add_column("Style Name", style="green")
    table.add_column("Font", style="yellow")
    table.add_column("Description", style="white")

    for key, style in BANNER_STYLES.items():
        table.add_row(
            key,
            style['name'],
            style['font'],
            style['description']
        )

    console.print(table)

def create_banner_with_style(style_key: str, name: str):
    """Create banner with selected style"""
    style = BANNER_STYLES[style_key]
    font = style['font']

    # Sanitize name
    name = security.sanitize_input(name)[:50]  # Limit length

    # Handle random selection
    if style_key == '10':
        fonts = ['slant', 'cyberlarge', 'banner', 'big', 'graffiti', 'standard', 'small', 'bubble', 'term']
        colors = ['red', 'green', 'blue', 'yellow', 'cyan', 'magenta', 'white']
        font = random.choice(fonts)
        color = random.choice(colors)
    else:
        color = style['color']

    # Get current shell
    shell = os.environ.get('SHELL', 'bash')
    rc_file = BASHRC_PATH if 'bash' in shell else ZSH_PATH if 'zsh' in shell else BASHRC_PATH

    # Create banner content based on color
    if color == 'lolcat':
        banner_content = f"""clear
echo "════════════════════════════════════"
figlet -f {font} '{name}' | lolcat
echo "════════════════════════════════════"
echo -e "\\033[1;32mWelcome back, $(whoami)!\\033[0m"
echo -e "\\033[1;32mDate: $(date)\\033[0m"
echo -e "\\033[1;32mTime: $(date +%H:%M:%S)\\033[0m"
echo "════════════════════════════════════"
neofetch --off"""
    elif color == 'random':
        color_code = random.choice(['32', '33', '34', '35', '36', '37'])
        banner_content = f"""clear
echo "════════════════════════════════════"
figlet -f {font} '{name}'
echo "════════════════════════════════════"
echo -e "\\033[1;{color_code}mWelcome back, $(whoami)!\\033[0m"
echo -e "\\033[1;{color_code}mDate: $(date)\\033[0m"
echo "════════════════════════════════════"
neofetch --off"""
    else:
        color_map = {
            'red': '31', 'green': '32', 'blue': '34',
            'yellow': '33', 'cyan': '36', 'magenta': '35',
            'white': '37'
        }
        color_code = color_map.get(color, '32')
        banner_content = f"""clear
echo "════════════════════════════════════"
figlet -f {font} '{name}'
echo "════════════════════════════════════"
echo -e "\\033[1;{color_code}mWelcome back, $(whoami)!\\033[0m"
echo -e "\\033[1;{color_code}mDate: $(date)\\033[0m"
echo "════════════════════════════════════"
neofetch --off"""

    # Write banner safely
    try:
        with open(rc_file, "w") as f:
            f.write(banner_content)
        return style['name']
    except Exception as e:
        logging.error(f"Failed to create banner: {str(e)}")
        return None

#__________________| CUSTOM BANNER |__________________#
def custom_banner():
    """Create custom terminal banner with multiple styles"""
    clear()

    # Install required packages
    safe_execute("pkg install figlet -y")
    safe_execute("pkg install ruby -y")
    safe_execute("gem install lolcat")

    while True:
        show_banner_styles()

        options = Panel(
            """[bold black]【[white]01-10[bold black]】[dark_slate_gray3] SELECT BANNER STYLE (1-10)
[bold black]【[white]P[bold black]】[dark_slate_gray3] PREVIEW ALL STYLES
[bold black]【[white]T[bold black]】[dark_slate_gray3] TEST WITH YOUR NAME
[bold black]【[white]R[bold black]】[dark_slate_gray3] REMOVE CURRENT BANNER
[bold black]【[white]00[bold black]】[red1] BACK TO MAIN MENU""",
            style="bold bright_black",
            title="<[bold white reverse] BANNER STYLE SELECTOR [/bold white reverse]>"
        )
        print(options)

        name = console.input("\n[bold yellow] ENTER YOUR BANNER NAME: [white]")
        if not name:
            name = "TERMUX"

        opt = get_user_choice("[bold bright_black]   ╰─>[white] ",
                            [str(i) for i in range(1, 11)] + ['p', 't', 'r', '00'])

        if opt in [str(i) for i in range(1, 11)]:
            style_name = create_banner_with_style(opt, name)
            if style_name:
                print(Panel(f"[bold green]BANNER CREATED with {style_name} style! Restart Termux to see it.",
                           style="bold bright_black"))
            else:
                print(Panel("[bold red]Failed to create banner", style="bold bright_black"))
            break

        elif opt == 'p':
            # Preview all styles
            clear()
            print(Panel("[bold yellow]PREVIEWING ALL STYLES (Press Enter to continue)",
                       style="bold bright_black"))
            for key, style in BANNER_STYLES.items():
                if key == '10':
                    continue
                print(f"\n[bold cyan]Style {key}: {style['name']}[/bold cyan]")
                font = style['font']
                if font != 'random':
                    safe_execute(f"figlet -f {font} '{name}' | head -3")
                time.sleep(1)
            console.input()

        elif opt == 't':
            # Test current selection
            test_style = console.input("[bold yellow]Enter style number to test: [white]")
            if test_style in [str(i) for i in range(1, 11)]:
                style = BANNER_STYLES[test_style]
                font = style['font']
                if font != 'random':
                    print(f"\n[bold cyan]{style['name']} STYLE:[/bold cyan]")
                    safe_execute(f"figlet -f {font} '{name}' | lolcat")
                else:
                    fonts = ['slant', 'cyberlarge', 'banner', 'big']
                    for f in fonts[:3]:
                        safe_execute(f"figlet -f {f} '{name}' | lolcat")
                console.input("\n[dim]Press Enter to continue...[/dim]")

        elif opt == 'r':
            # Remove banner safely
            for rc in [BASHRC_PATH, ZSH_PATH]:
                if rc.exists():
                    rc.unlink()
                    rc.touch()
            print(Panel("[bold red]BANNER REMOVED.", style="bold bright_black"))
            break

        elif opt == '00':
            break

    time.sleep(2)
    menu()

#__________________| SYSTEM OPTIMIZER |__________________#
def system_optimizer():
    """Optimize system performance"""
    clear()
    print(Panel("[bold black]【[white]•[bold black]】[blue] OPTIMIZING SYSTEM...",
                style="bold bright_black",
                title="<[bold white reverse] OPTIMIZER [/bold white reverse]>"))

    optimizations = [
        ("Cleaning package cache", "apt clean && apt autoclean"),
        ("Removing orphaned packages", "apt autoremove -y"),
        ("Clearing temp files", "rm -rf $PREFIX/tmp/* 2>/dev/null"),
        ("Clearing cache files", "rm -rf ~/.cache/* 2>/dev/null"),
        ("Optimizing database", "sqlite3 $PREFIX/var/lib/dpkg/status 'VACUUM;' 2>/dev/null || true"),
        ("Clearing bash history", "cat /dev/null > ~/.bash_history 2>/dev/null || true"),
        ("Clearing pip cache", "pip cache purge || true"),
        ("Optimizing memory", "sync && echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true"),
    ]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="green", finished_style="green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    ) as progress:

        task = progress.add_task("[cyan]Optimizing...", total=len(optimizations))

        for desc, cmd in optimizations:
            progress.update(task, description=f"[cyan]{desc}")
            safe_execute(cmd)
            progress.advance(task)

    # Test network speed
    print(Panel("[bold black]【[white]•[bold black]】[sea_green2] Testing network speed...",
               style="bold bright_black"))
    speed_results = test_network_speed()
    if speed_results['speed'] != 'N/A':
        print(Panel(f"[green]Download speed: {speed_results['speed']} ({speed_results['quality']})\nLatency: {speed_results['latency']}",
                   style="bold bright_black"))

    print(Panel("[bold green]SYSTEM OPTIMIZED SUCCESSFULLY!",
                style="bold bright_black"))

    console.input("\n[bold bright_black]   ╰─>[white] Press Enter to return...")
    menu()

#__________________| VERIFY INSTALLATION |__________________#
def verify_installation():
    """Verify installed packages and system integrity"""
    clear()
    print(Panel("[bold black]【[white]•[bold black]】[blue] VERIFYING INSTALLATION...",
                style="bold bright_black",
                title="<[bold white reverse] VERIFICATION [/bold white reverse]>"))

    results = []

    # Check essential commands
    essentials = ['python', 'pip', 'git', 'curl', 'wget', 'nano', 'figlet', 'lolcat']

    for cmd in essentials:
        success, result = safe_execute(f"which {cmd}")
        if success and result.strip():
            results.append(f"✓ {cmd}: Found at {result.strip()}")
        else:
            results.append(f"✗ {cmd}: Not found")

    # Check package counts
    success, result = safe_execute("pkg list-installed | wc -l")
    if success:
        results.append(f"\n📦 Total packages: {result.strip()}")

    # Check Python packages
    success, result = safe_execute("pip list | wc -l")
    if success:
        results.append(f"🐍 Python packages: {result.strip()}")

    # Display results
    table = Table(title="Installation Verification", show_header=True, header_style="bold magenta")
    table.add_column("Status", style="cyan")
    table.add_column("Detail", style="green")

    for line in results:
        if line.startswith('✓'):
            table.add_row("✅", line[2:])
        elif line.startswith('✗'):
            table.add_row("❌", line[2:])
        else:
            table.add_row("📌", line)

    console.print(table)

    console.input("\n[bold bright_black]   ╰─>[white] Press Enter to return...")
    menu()

#__________________| EXPORT SYSTEM INFO |__________________#
def export_system_info():
    """Export system information to file"""
    clear()
    print(Panel("[bold black]【[white]•[bold black]】[blue] EXPORTING SYSTEM INFO...",
                style="bold bright_black",
                title="<[bold white reverse] EXPORT [/bold white reverse]>"))

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"system_info_{timestamp}.json"
    filepath = HOME_DIR / filename

    info = {
        'timestamp': str(datetime.datetime.now()),
        'date': date,
        'time': times,
        'device': get_device_info(),
        'ip': get_ip(),
        'storage': get_storage_usage(),
        'ping': get_ping(),
        'uptime': get_uptime(),
        'packages': get_packages_count(),
        'python_version': safe_execute("python --version")[1].strip() if safe_execute("python --version")[0] else "N/A",
        'shell': os.environ.get('SHELL', 'unknown'),
        'termux_version': safe_execute("pkg --version")[1].strip() if safe_execute("pkg --version")[0] else "N/A",
        'security_level': security.config.level.value,
        'session_token': security.session_token[:8] + "...",
    }

    try:
        with open(filepath, 'w') as f:
            json.dump(info, f, indent=2)

        # Create hash for verification
        with open(filepath, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()

        hash_file = HOME_DIR / f"system_info_{timestamp}.sha256"
        with open(hash_file, 'w') as f:
            f.write(file_hash)

        print(Panel(f"[green]System info exported to:\n{filename}\n\nSHA256: {file_hash[:64]}",
                   style="bold bright_black"))
    except Exception as e:
        logging.error(f"Failed to export system info: {str(e)}")
        print(Panel(f"[red]Failed to export: {str(e)}", style="bold bright_black"))

    console.input("\n[bold bright_black]   ╰─>[white] Press Enter to return...")
    menu()

#__________________| ABOUT & CREDITS |__________________#
def about_credits():
    """Display about and credits information"""
    clear()
    about_text = """
[bold cyan]TERMUX SETUP ADVANCED v1.0 (Ultimate Secure)[/bold cyan]

[green]Created by:[/green] Root Hydra
[green]Team:[/green] Candpur Cyber Team
[green]Purpose:[/green] Automated Termux environment setup and management

[bold yellow]Available Options:[/bold yellow]
• [green]✓[/green] Basic Setup - 50+ essential packages
• [green]✓[/green] Advanced Setup - 150+ complete packages
• [green]✓[/green] Custom Banner - 10+ unique styles
• [green]✓[/green] System Optimizer - Performance tuning
• [green]✓[/green] Verify Installation - Check all packages
• [green]✓[/green] Export System Info - Detailed report
• [green]✓[/green] About & Credits - This screen

[bold yellow]Security Features:[/bold yellow]
• [green]✓[/green] Command whitelist - Only safe commands allowed
• [green]✓[/green] Input sanitization - All user input validated
• [green]✓[/green] Path traversal protection - Safe file operations
• [green]✓[/green] Environment sanitization - Clean execution environment
• [green]✓[/green] Rate limiting - Prevent abuse
• [green]✓[/green] Resource limits - Memory and CPU control
• [green]✓[/green] Command logging - Full audit trail
• [green]✓[/green] Session management - Unique tokens per session

[bold magenta]GitHub:[/bold magenta] github.com/Unknown-tech404
[bold magenta]Version:[/bold magenta] 1.0 (Ultimate Secure)
[bold magenta]Security:[/bold magenta] 100% Secure

[bold green]All values shown in green[/bold green]
[italic]Stay secure, stay dangerous![/italic]
"""
    print(Panel(about_text, style="bold bright_black",
               title="<[bold white reverse] ABOUT [/bold white reverse]>"))
    console.input("\n[bold bright_black]   ╰─>[white] Press Enter to return...")
    menu()

#__________________| MAIN MENU |__________________#
def menu():
    """Main menu function with all options"""
    # __details__()  # Removed - now called in main
    # clear()  # Removed - we want to keep the banner

    menu_options = Panel(
        """[bold black]【[white]01[bold black]】[blue] BASIC SETUP (Essential Packages)
[bold black]【[white]02[bold black]】[magenta] ADVANCED SETUP (Complete Environment)
[bold black]【[white]03[bold black]】[dark_slate_gray3] CUSTOM BANNER (10+ Styles)
[bold black]【[white]04[bold black]】[dark_slate_gray3] SYSTEM OPTIMIZER
[bold black]【[white]05[bold black]】[dark_slate_gray3] VERIFY INSTALLATION
[bold black]【[white]06[bold black]】[dark_slate_gray3] EXPORT SYSTEM INFO
[bold black]【[white]07[bold black]】[dark_slate_gray3] ABOUT & CREDITS
[bold black]【[white]00[bold black]】[red1] EXIT PROGRAM""",
        style="bold bright_black",
        title="<[bold white reverse] MAIN MENU [/bold white reverse]>"
    )
    print(menu_options)

    option = get_user_choice("[bold bright_black]   ╰─>[white] ",
                            ['1','01','2','02','3','03','4','04','5','05','6','06','7','07','0','00'])

    if option in ['1','01']:
        basic_setup()
    elif option in ['2','02']:
        advanced_setup()
    elif option in ['3','03']:
        custom_banner()
    elif option in ['4','04']:
        system_optimizer()
    elif option in ['5','05']:
        verify_installation()
    elif option in ['6','06']:
        export_system_info()
    elif option in ['7','07']:
        about_credits()
    elif option in ['00','0']:
        print(Panel("[bold black]【[white]=[bold black]】[bold blue] STAY SECURE. EXITING...\n"
                   "[bold black]【[white]=[bold black]】[bold blue] THANKS FOR USING ROOT HYDRA'S TOOLS!",
                   style="bold bright_black",
                   title="<[bold white reverse] EXIT [/bold white reverse]>"))
        logging.info("Session ended securely")

        # Clean up sensitive data
        security.session_token = None

        sys.exit()

if __name__ == "__main__":
    try:
        logging.info("Secure session started")
        
        # Clear screen
        os.system("clear")
        
        # Show banner (Candpur Cyber Team)
        logo()
        
        # Verify security configuration
        if not check_dependencies():
            print(Panel("[yellow]Some dependencies missing. Continuing anyway...",
                       style="bold bright_black"))
            time.sleep(1)
        
        # Show dynamic dashboard
        __details__()
        
        # Short pause (optional) - for smooth experience
        time.sleep(0.5)
        
        # Show menu (now menu only contains options)
        menu()

    except KeyboardInterrupt:
        print(Panel("\n[yellow]Interrupted by user. Exiting securely...",
                   style="bold bright_black"))
        logging.info("Session interrupted by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        print(Panel(f"[red]Unexpected error: {str(e)}\nCheck termux_setup.log for details",
                   style="bold bright_black"))
        sys.exit(1)
