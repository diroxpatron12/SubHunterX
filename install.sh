#!/bin/bash
# ╔══════════════════════════════════════════════════════════════╗
# ║           SubHunterX — Installation Script                   ║
# ║           Author: Khaled Ben Ali                             ║
# ╚══════════════════════════════════════════════════════════════╝

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}"
echo "  ____        _     _   _             _           __  __"
echo " / ___| _   _| |__ | | | |_   _ _ __ | |_ ___ _ _\ \/ /"
echo " \___ \| | | | '_ \| |_| | | | | '_ \| __/ _ \ '__\  / "
echo "  ___) | |_| | |_) |  _  | |_| | | | | ||  __/ |  /  \ "
echo " |____/ \__,_|_.__/|_| |_|\__,_|_| |_|\__\___|_| /_/\_\\"
echo -e "${NC}"
echo -e "${BOLD}Ultimate Subdomain Enumeration Tool${NC}"
echo -e "${CYAN}by Khaled Ben Ali${NC}"
echo ""

# Check Python
echo -e "${YELLOW}[*] Checking Python version...${NC}"
python3 --version || { echo -e "${RED}[!] Python 3 required${NC}"; exit 1; }

# Install pip dependencies
echo -e "${YELLOW}[*] Installing Python dependencies...${NC}"
pip3 install -r requirements.txt --quiet

# Check for Go (optional — for httprobe)
echo -e "${YELLOW}[*] Checking for Go...${NC}"
if command -v go &> /dev/null; then
    echo -e "${GREEN}[+] Go found. Installing httprobe...${NC}"
    go install github.com/tomnomnom/httprobe@latest 2>/dev/null || true
else
    echo -e "${YELLOW}[~] Go not found — httprobe skipped (built-in HTTP prober will be used)${NC}"
fi

# Check for Chrome/Chromium (for screenshots)
echo -e "${YELLOW}[*] Checking for Chrome/Chromium (screenshots)...${NC}"
if command -v google-chrome &> /dev/null || command -v chromium-browser &> /dev/null || command -v chromium &> /dev/null; then
    echo -e "${GREEN}[+] Browser found. Screenshots enabled.${NC}"
else
    echo -e "${YELLOW}[~] Chrome/Chromium not found.${NC}"
    echo -e "${YELLOW}    Install with: sudo apt install chromium-browser  (Debian/Ubuntu)${NC}"
    echo -e "${YELLOW}                  brew install --cask google-chrome  (macOS)${NC}"
fi

# Check for TOR (optional)
echo -e "${YELLOW}[*] Checking for TOR...${NC}"
if command -v tor &> /dev/null; then
    echo -e "${GREEN}[+] TOR found. Use --tor flag to route through TOR.${NC}"
else
    echo -e "${YELLOW}[~] TOR not found. Install: sudo apt install tor${NC}"
fi

# Create output directories
mkdir -p output wordlists config

echo ""
echo -e "${GREEN}[✓] SubHunterX installed successfully!${NC}"
echo ""
echo -e "${BOLD}Quick Start:${NC}"
echo -e "  ${CYAN}python3 subhunterx.py -d example.com${NC}"
echo -e "  ${CYAN}python3 subhunterx.py -l domains.txt${NC}"
echo -e "  ${CYAN}python3 subhunterx.py -d example.com --recursive --tor${NC}"
echo ""
echo -e "${YELLOW}[!] Don't forget to add your API keys in config/config.yaml${NC}"
echo ""
