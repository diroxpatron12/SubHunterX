<div align="center">

```
  ____        _     _   _             _           __  __
 / ___| _   _| |__ | | | |_   _ _ __ | |_ ___ _ _\ \/ /
 \___ \| | | | '_ \| |_| | | | | '_ \| __/ _ \ '__\  /
  ___) | |_| | |_) |  _  | |_| | | | | ||  __/ |  /  \
 |____/ \__,_|_.__/|_| |_|\__,_|_| |_|\__\___|_| /_/\_\
```

# 🔍 SubHunterX
### Ultimate Subdomain Enumeration & Reconnaissance Tool

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-orange?style=for-the-badge)](https://github.com/khaledxbenali92/SubHunterX/releases)
[![Sources](https://img.shields.io/badge/Sources-47%2B-red?style=for-the-badge)](https://github.com/khaledxbenali92/SubHunterX)
[![Stars](https://img.shields.io/github/stars/khaledbenali/SubHunterX?style=for-the-badge&color=yellow)](https://github.com/khaledxbenali92/SubHunterX/stargazers)

**The most powerful subdomain enumeration tool on the market.**
Aggregates 47+ sources, DNS brute forcing, live probing, screenshots, takeover detection, cloud asset discovery, and rich HTML reports — all in one tool.

[Features](#-features) · [Installation](#-installation) · [Usage](#-usage) · [Sources](#-sources-47) · [Configuration](#-configuration) · [Roadmap](#-roadmap)

</div>

---

## ✨ Features

### 🎯 Core Engine
| Feature | Description |
|---|---|
| **47+ Passive Sources** | crt.sh, Shodan, VirusTotal, AlienVault, Censys, SecurityTrails, BinaryEdge, and more |
| **DNS Brute Force** | Multi-threaded DNS resolution with customizable wordlist (200+ threads) |
| **Recursive Enumeration** | Enumerate subdomains of subdomains automatically |
| **Wildcard Detection** | Detect and filter wildcard DNS to eliminate false positives |
| **Deduplication** | Automatic deduplication across all sources |

### 🌐 HTTP Probing
| Feature | Description |
|---|---|
| **Live / Dead Split** | Separates live from dead subdomains with detailed status |
| **HTTP Status Codes** | Full status codes — 200, 301, 302, 403, 404, 500... |
| **Dead Details File** | Detailed error info for every unreachable subdomain |
| **Title Extraction** | Extracts `<title>` from every live page |
| **Server Detection** | Identifies web server technology (nginx, Apache, IIS...) |

### 🔐 Security Analysis
| Feature | Description |
|---|---|
| **Takeover Detection** | Identifies subdomain takeover vulnerabilities (20+ providers) |
| **WAF Detection** | Detects Cloudflare, AWS WAF, Akamai, Sucuri, Imperva, F5 |
| **Cloud Asset Detection** | Identifies AWS S3, Azure Blob, GCP, Netlify, Vercel, Heroku... |
| **CNAME Chain Analysis** | Analyzes CNAME chains for dangling records |
| **Historical DNS** | Fetches historical DNS records via SecurityTrails |

### 📊 Output & Reporting
| Feature | Description |
|---|---|
| **HTML Report** | Beautiful dark-theme report with charts, screenshots, and full stats |
| **JSON Export** | Machine-readable JSON for pipeline integration |
| **CSV Export** | Spreadsheet-compatible CSV for live and dead results |
| **Screenshots** | Full-page screenshots of every live subdomain |
| **Organized Output** | Per-domain timestamped folders |

### ⚙️ Operational Features
| Feature | Description |
|---|---|
| **Resume / Checkpoint** | Save progress and resume interrupted scans |
| **Proxy Support** | Full HTTP/SOCKS5 proxy support |
| **TOR Routing** | Anonymous scanning through TOR |
| **Rate Limiting** | Configurable request rate to avoid bans |
| **Slack / Discord** | Real-time notifications when scan completes |
| **Config File** | YAML config for API keys and preferences |
| **Rich CLI** | Colored progress bars, spinners, and result tables |

---

## 📦 Installation

### Requirements
- Python 3.8+
- Chrome or Chromium (for screenshots)
- TOR (optional, for anonymous scanning)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/khaledxbenali92/SubHunterX.git
cd SubHunterX

# Run the installer
chmod +x install.sh
./install.sh
```

### Manual Install

```bash
git clone https://github.com/khaledxbenali92/SubHunterX.git
cd SubHunterX
pip3 install -r requirements.txt
```

### Install Chrome (for Screenshots)

```bash
# Debian / Ubuntu / Kali
sudo apt update && sudo apt install -y chromium-browser

# Fedora / RHEL
sudo dnf install chromium

# macOS
brew install --cask google-chrome

# Arch Linux
sudo pacman -S chromium
```

### Install TOR (Optional)

```bash
# Debian / Ubuntu / Kali
sudo apt install tor && sudo service tor start

# macOS
brew install tor && brew services start tor
```

---

## 🚀 Usage

### Basic Usage

```bash
# Single domain
python3 subhunterx.py -d example.com

# Multiple domains from file
python3 subhunterx.py -l domains.txt
```

### Advanced Usage

```bash
# Recursive enumeration (subdomains of subdomains)
python3 subhunterx.py -d example.com --recursive

# Use custom wordlist for brute force
python3 subhunterx.py -d example.com --wordlist /path/to/wordlist.txt

# Route through TOR (anonymous)
python3 subhunterx.py -d example.com --tor

# Use a proxy (Burp Suite, ZAP, etc.)
python3 subhunterx.py -d example.com --proxy http://127.0.0.1:8080

# Disable screenshots (faster)
python3 subhunterx.py -d example.com --no-screenshot

# Disable brute force (passive only)
python3 subhunterx.py -d example.com --no-brute

# Custom thread count and timeout
python3 subhunterx.py -d example.com --threads 200 --timeout 15

# Custom config file
python3 subhunterx.py -d example.com -c /path/to/config.yaml
```

### All Options

```
usage: subhunterx.py [-h] [-d DOMAIN] [-l LIST] [-c CONFIG]
                     [--recursive] [--proxy PROXY] [--tor]
                     [--no-screenshot] [--no-brute]
                     [--wordlist WORDLIST] [--threads THREADS]
                     [--timeout TIMEOUT] [-v]

options:
  -h, --help            Show this help message and exit
  -d, --domain          Single target domain
  -l, --list            File containing list of domains (one per line)
  -c, --config          Config file path (default: config/config.yaml)
  --recursive           Enable recursive subdomain enumeration
  --proxy               Proxy URL (e.g. http://127.0.0.1:8080)
  --tor                 Route all traffic through TOR
  --no-screenshot       Disable live subdomain screenshots
  --no-brute            Disable DNS brute force
  --wordlist            Custom wordlist path for brute force
  --threads             Thread count for DNS resolution (default: 100)
  --timeout             HTTP request timeout in seconds (default: 10)
  -v, --version         Show version and exit
```

---

## 📁 Output Structure

```
output/
└── example.com_20260101_120000/
    ├── all-subdomains.txt          ← All unique subdomains found
    ├── live-subdomains.txt         ← Only live/reachable subdomains
    ├── dead-subdomains.txt         ← Only dead/unreachable subdomains
    ├── dead-subdomains-details.txt ← Dead subdomains with error details
    ├── live-subdomains.csv         ← Live results in CSV format
    ├── dead-subdomains.csv         ← Dead results in CSV format
    ├── results.json                ← Full results in JSON format
    ├── report.html                 ← Beautiful HTML report
    └── live-subdomains-screenshots/
        ├── www.example.com.png
        ├── api.example.com.png
        └── ...
```

---

## 📡 Sources (47+)

### Certificate Transparency
| Source | Type | API Key |
|---|---|---|
| crt.sh | Cert Transparency | Free |
| Certspotter | Cert Transparency | Free |

### Threat Intelligence & OSINT
| Source | Type | API Key |
|---|---|---|
| Shodan | Internet Scanner | Required |
| Censys | Internet Scanner | Required |
| VirusTotal | Threat Intel | Required |
| AlienVault OTX | Threat Intel | Free |
| SecurityTrails | DNS History | Required |
| BinaryEdge | Threat Intel | Required |
| ThreatCrowd | Threat Intel | Free |
| ThreatMiner | Threat Intel | Free |
| FullHunt | Asset Discovery | Required |
| LeakIX | Threat Intel | Free |
| GreyNoise | Internet Noise | Free |

### Internet Scanners
| Source | Type | API Key |
|---|---|---|
| ZoomEye | Internet Scanner | Required |
| FOFA | Internet Scanner | Required |

### DNS & Passive DNS
| Source | Type | API Key |
|---|---|---|
| HackerTarget | DNS Lookup | Free |
| DNSDumpster | DNS Recon | Free |
| BufferOver | DNS Dataset | Free |
| Robtex | DNS Graph | Free |
| CIRCL PassiveDNS | Passive DNS | Free |
| RapidDNS | Passive DNS | Free |
| Anubis DB | DNS Dataset | Free |
| Columbus | DNS Dataset | Free |
| PassiveTotal | Passive DNS | Free |
| Riddler.io | DNS Dataset | Free |
| DNSrepo | DNS Dataset | Free |

### Public APIs & Databases
| Source | Type | API Key |
|---|---|---|
| C99.nl | Subdomain API | Required |
| WhoisXMLAPI | WHOIS Data | Required |
| Chaos (ProjectDiscovery) | Bug Bounty DB | Required |
| Subdomain.center | Subdomain API | Free |
| Omnisint / Ceres | DNS Dataset | Free |
| Recon.dev | Recon API | Free |
| ShrewdEye | Recon API | Free |
| Synapsint | OSINT | Free |
| Phonebook.cz | OSINT | Free |
| ViewDNS | DNS Tools | Free |
| Netcraft | Site Report | Free |

### Web Archives & Crawling
| Source | Type | API Key |
|---|---|---|
| Wayback Machine | Web Archive | Free |
| CommonCrawl | Web Crawl | Free |
| URLScan.io | URL Scanner | Free |
| WebArchive CDX | Web Archive | Free |
| PublicWWW | Source Search | Free |

### Code Search
| Source | Type | API Key |
|---|---|---|
| GitHub | Code Search | Required |

### Search Engine Dorking
| Source | Type | API Key |
|---|---|---|
| Google | Dork | Free |
| Bing | Dork | Free |
| Baidu | Dork | Free |

### DNS Brute Force
| Source | Type |
|---|---|
| Custom Wordlist | DNS Brute Force |
| Permutation Engine | DNS Mutation |

---

## ⚙️ Configuration

Edit `config/config.yaml` to set your API keys and preferences:

```yaml
api_keys:
  shodan: "YOUR_SHODAN_KEY"
  censys_id: "YOUR_CENSYS_ID"
  censys_secret: "YOUR_CENSYS_SECRET"
  securitytrails: "YOUR_ST_KEY"
  virustotal: "YOUR_VT_KEY"
  binaryedge: "YOUR_BE_KEY"
  c99: "YOUR_C99_KEY"
  github: "YOUR_GITHUB_TOKEN"
  fofa_email: "your@email.com"
  fofa_key: "YOUR_FOFA_KEY"
  zoomeye: "YOUR_ZOOMEYE_KEY"
  chaos: "YOUR_CHAOS_KEY"
  fullhunt: "YOUR_FULLHUNT_KEY"
  whoisxml: "YOUR_WHOISXML_KEY"

settings:
  threads: 100
  timeout: 10
  brute_force: true
  recursive: false
  screenshot: true
  use_tor: false
  proxy: ""

notifications:
  slack_webhook: "https://hooks.slack.com/..."
  discord_webhook: "https://discord.com/api/webhooks/..."
```

### Free API Keys (Quick Start)
| Service | URL |
|---|---|
| VirusTotal | https://virustotal.com/gui/join-us |
| Shodan | https://account.shodan.io/register |
| SecurityTrails | https://securitytrails.com/app/signup |
| Censys | https://accounts.censys.io/register |
| BinaryEdge | https://app.binaryedge.io/sign-up |
| GitHub Token | https://github.com/settings/tokens |
| Chaos | https://chaos.projectdiscovery.io |
| FullHunt | https://fullhunt.io/register |

---

## 🗺️ Roadmap

### v1.0.0 — Current Release ✅
- [x] 47+ passive enumeration sources
- [x] DNS brute force with threading
- [x] Wildcard DNS detection
- [x] HTTP probing with live/dead split
- [x] Full screenshots of live subdomains
- [x] Subdomain takeover detection (20+ providers)
- [x] WAF detection
- [x] Cloud asset discovery (AWS, Azure, GCP, Netlify...)
- [x] CNAME chain analysis
- [x] HTML/JSON/CSV reports
- [x] Resume / checkpoint system
- [x] Proxy & TOR support
- [x] Slack / Discord notifications
- [x] YAML config file
- [x] Recursive enumeration

### v1.1.0 — Planned 🔄
- [ ] Port scanning integration (top 1000 ports per live subdomain)
- [ ] Technology fingerprinting (Wappalyzer-style)
- [ ] Nuclei templates auto-run on live subdomains
- [ ] Diff mode (compare new scan vs old scan)
- [ ] ASN & geolocation mapping per subdomain
- [ ] Web dashboard for viewing results

### v1.2.0 — Future 🔮
- [ ] GraphQL API for integration
- [ ] Docker container
- [ ] Kubernetes deployment
- [ ] CI/CD pipeline integration
- [ ] Machine learning false positive filtering
- [ ] Auto-generated bug report templates
- [ ] Integration with Burp Suite Extension

---

## 📋 Requirements

| Tool | Required | Purpose |
|---|---|---|
| Python 3.8+ | ✅ Required | Core runtime |
| pip packages | ✅ Required | See requirements.txt |
| Chrome/Chromium | ⚠️ Optional | Screenshots |
| TOR | ⚠️ Optional | Anonymous scanning |
| Go + httprobe | ⚠️ Optional | Alternative HTTP prober |

---

## ⚠️ Legal Disclaimer

> **SubHunterX is intended for legal security research, bug bounty hunting, and authorized penetration testing ONLY.**
>
> Always obtain proper written authorization before scanning any domain or network you do not own.
> The author is not responsible for any misuse or damage caused by this tool.
> Use responsibly and ethically.

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- 🐛 Report bugs via [Issues](https://github.com/khaledxbenali92/SubHunterX/issues)
- 💡 Request features via [Issues](https://github.com/khaledxbenali92/SubHunterX/issues)
- 🔧 Submit [Pull Requests](https://github.com/khaledxbenali92/SubHunterX/pulls)
- ⭐ Star the repo if it helped you!

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ by [Khaled Ben Ali](https://github.com/khaledxbenali92)**

[![GitHub](https://img.shields.io/badge/GitHub-khaledbenali-black?style=flat-square&logo=github)](https://github.com/khaledxbenali92)

*If SubHunterX helped your bug bounty hunting, consider giving it a ⭐*

</div>
