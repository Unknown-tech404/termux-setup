# 🔥 TERMUX SETUP ADVANCED v1.0

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0-brightgreen" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/Security-100%25-success" alt="Security">
  <img src="https://img.shields.io/badge/Platform-Termux-orange" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
  <img src="https://img.shields.io/badge/Team-CCT-purple" alt="Team">
</p>

<p align="center">
  <b>Ultimate Termux Environment Setup & Management Tool</b><br>
  Created by <a href="https://github.com/Unknown-tech404">Unknown-tech404</a> | Team Candpur Cyber Team
</p>

---

## 🎯 OVERVIEW

**Termux Setup Advanced** is a comprehensive, automated setup tool designed to transform your Termux into a powerful development and security environment. With over 150+ packages, 10+ banner styles, and enterprise-grade security features, it's the ultimate solution for Termux users.

This tool handles everything from basic package installation to advanced system optimization, all wrapped in a beautiful, user-friendly interface powered by the Rich library.

---

## ✨ FEATURES

### 🚀 **Core Features**
| Feature | Description |
|---------|-------------|
| **Basic Setup** | 50+ essential packages for everyday use |
| **Advanced Setup** | 150+ complete packages for professionals |
| **Custom Banner** | 10+ unique banner styles with animations |
| **System Optimizer** | Performance tuning & cache cleaning |
| **Verify Installation** | Complete package verification system |
| **Export System Info** | Detailed JSON reports with SHA256 hashes |

### 🛡️ **Security Features**
| Security Layer | Implementation |
|----------------|----------------|
| Command Whitelist | Only safe, pre-approved commands |
| Input Sanitization | All user input validated |
| Path Protection | Prevents directory traversal attacks |
| Environment Sanitization | Clean execution environment |
| Rate Limiting | Max 30 commands per minute |
| Resource Limits | CPU, memory, output size control |
| Session Management | Unique tokens per session |
| Command Logging | Complete audit trail |
| File Verification | SHA256 hash verification |

### 📊 **Dynamic Dashboard**
- Real-time device information
- IP address detection
- Network latency monitoring
- Storage usage statistics
- Installed packages count
- System uptime tracking
- Local time & date

---

## 📦 INSTALLATION

### Method 1: Direct Download
```bash
# Update Termux
pkg update && pkg upgrade

# Install required packages
pkg install python git -y

# Clone repository
git clone https://github.com/Unknown-tech404/termux-setup.git

# Navigate to directory
cd termux-setup

# Install Python dependencies
pip install -r requirements.txt

# Run the tool
python setup.py
```

### Method 2: One-Line Installation
```bash
pkg update && pkg upgrade -y && pkg install python git -y && git clone https://github.com/Unknown-tech404/termux-setup.git && cd termux-setup && pip install rich requests && python setup.py
```

### Method 3: Manual Setup
```bash
# Step by step installation
pkg update
pkg upgrade
pkg install python
pkg install git
pip install rich requests
git clone https://github.com/Unknown-tech404/termux-setup.git
cd termux-setup
python setup.py
```
## 🎮 USAGE

### Main Menu Options
```bash
┌─────────────────────────────────────────┐
│ MAIN MENU                               │
├─────────────────────────────────────────┤
│ 01 • BASIC SETUP                        │
│ (Essential Packages - 50+)              │
│                                         │
│ 02 • ADVANCED SETUP                     │
│ (Complete Environment - 150+)           │
│                                         │
│ 03 • CUSTOM BANNER                      │
│ (10+ Unique Styles)                     │
│                                         │
│ 04 • SYSTEM OPTIMIZER                   │
│ (Performance Tuning)                    │
│                                         │
│ 05 • VERIFY INSTALLATION                │
│ (Package Verification)                  │
│                                         │
│ 06 • EXPORT SYSTEM INFO                 │
│ (JSON + SHA256)                         │
│                                         │
│ 07 • ABOUT & CREDITS                    │
│                                         │
│ 00 • EXIT PROGRAM                       │
└─────────────────────────────────────────┘
```


### Navigation
- Use number keys (01-07) to select options
- Press `00` to exit
- Follow on-screen prompts for inputs
- Press Enter to continue after operations

---

## 📦 PACKAGE LISTS

### Basic Setup (50+ Packages)
| Category | Packages |
|----------|----------|
| **Core** | python, python2, python3, git, curl, wget |
| **Editors** | nano, vim, mc, ranger |
| **Networking** | traceroute, whois, dig, host |
| **System** | neofetch, htop, btop, glances |
| **Utilities** | ffmpeg, screen, tmux, tree |
| **Languages** | ruby, php, perl, lua |
| **Security** | openssl, nmap, hydra (basic) |

### Advanced Setup (150+ Packages)
| Category | Packages |
|----------|----------|
| **Security Tools** | nuclei, subfinder, httpx, ffuf, gobuster, dirb |
| **Network Tools** | wireshark, tcpdump, ettercap, bettercap |
| **Exploitation** | metasploit, hydra, john, hashcat, aircrack-ng |
| **Forensics** | sleuthkit, autopsy, binwalk, foremost |
| **Web** | nginx, apache2, php-fpm, nodejs |
| **Databases** | postgresql, mysql, mongodb, redis |
| **Cloud** | awscli, gcloud, terraform, ansible |
| **Development** | gcc, clang, make, cmake, gdb |

### Python Packages (70+)
| Category | Packages |
|----------|----------|
| **Web** | requests, selenium, scrapy, beautifulsoup4 |
| **Data** | numpy, pandas, matplotlib, scikit-learn |
| **ML** | tensorflow, torch, transformers, keras |
| **Security** | scapy, cryptography, pwntools |
| **Automation** | fabric, paramiko, ansible-runner |

---

## 🎨 BANNER STYLES

| Option | Style Name | Font | Description |
|--------|------------|------|-------------|
| 01 | CLASSIC SLANT | slant | Standard slant with rainbow colors |
| 02 | CYBERPUNK | cyberlarge | Large cyberpunk style in red |
| 03 | RETRO | banner | Retro banner style in green |
| 04 | 3D EFFECT | big | Big 3D style font in blue |
| 05 | GRAFFITI | graffiti | Graffiti style in yellow |
| 06 | ASCII ART | standard | ASCII art with cyan |
| 07 | MINIMAL | small | Small minimal font in white |
| 08 | ANIME | bubble | Bubble letters in magenta |
| 09 | TERMINAL | term | Terminal font with rainbow |
| 10 | RANDOM | random | Random font & color |

---

## 📋 REQUIREMENTS

### Minimum Requirements
- **OS:** Android 7.0+
- **RAM:** 2GB+
- **Storage:** 500MB free space
- **Termux:** Latest version from F-Droid
- **Internet:** Required for package installation

### Recommended Requirements
- **OS:** Android 10+
- **RAM:** 4GB+
- **Storage:** 2GB+ free space
- **Internet:** High-speed connection

---

## 📦 DEPENDENCIES

```python
Python >= 3.11
rich >= 13.0.0
requests >= 2.31.0
urllib3 >= 2.0.0
```

<!-- ## ⚠️ DISCLAIMER

> **IMPORTANT:** This tool is for **educational purposes only**. The creators and contributors are not responsible for any misuse or damage caused by this tool. Users are responsible for complying with all applicable local, state, national, and international laws.

**By using this tool, you agree:**
- You will not use it for illegal purposes
- You will respect others' privacy
- You accept full responsibility for your actions
- You understand the risks involved

---
  -->
## 👥 CREDITS

### Creator
- **Unknown-tech404**

### Team
- **Candpur Cyber Team** - Official Team

---

## ⭐ SUPPORT

If you find this tool useful, please consider:
- Giving a ⭐ star on GitHub
- Following [@Unknown-tech404](https://github.com/Unknown-tech404)
- Sharing with friends
- Reporting bugs
- Contributing code
---

<p align="center"> <b>Stay Secure, Stay Dangerous!</b><br> <img src="https://img.shields.io/badge/Made%20with-Python-1f425f.svg" alt="Made with Python"> <img src="https://img.shields.io/badge/Maintained%3F-yes-green.svg" alt="Maintained"> <img src="https://img.shields.io/github/issues/Unknown-tech404/termux-setup" alt="Issues"> <img src="https://img.shields.io/github/forks/Unknown-tech404/termux-setup" alt="Forks"> <img src="https://img.shields.io/github/stars/Unknown-tech404/termux-setup" alt="Stars"> </p><p align="center"> <b>© 2026 Candpur Cyber Team. All rights reserved.</b> </p>
