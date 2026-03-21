#!/usr/bin/env python3
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                         SubHunterX - Ultimate Subdomain Hunter              ║
# ║                         Author: Khaled Ben Ali                              ║
# ║                         Version: 1.0.0                                      ║
# ║                         License: MIT                                        ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

import os
import sys
import json
import csv
import time
import yaml
import socket
import asyncio
import argparse
import hashlib
import ipaddress
import threading
import subprocess
import re
import requests
import dns.resolver
import dns.exception
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

# UI / Display
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.text import Text
from rich.live import Live
from rich.columns import Columns
from rich.rule import Rule
from rich import box
import pyfiglet
from colorama import init, Fore, Back, Style

init(autoreset=True)
console = Console()

# ──────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────────────────────────────────────
VERSION = "1.0.0"
AUTHOR  = "Khaled Ben Ali"
GITHUB  = "https://github.com/khaledbenali/SubHunterX"

BANNER = pyfiglet.figlet_format("SubHunterX", font="slant")

TAKEOVER_SIGNATURES = {
    "GitHub Pages":         ["There isn't a GitHub Pages site here"],
    "Heroku":               ["No such app", "herokucdn.com"],
    "Shopify":              ["Sorry, this shop is currently unavailable"],
    "AWS S3":               ["NoSuchBucket", "The specified bucket does not exist"],
    "Azure":                ["404 Web Site not found"],
    "Fastly":               ["Fastly error: unknown domain"],
    "Ghost":                ["The thing you were looking for is no longer here"],
    "Netlify":              ["Not Found - Request ID"],
    "Zendesk":              ["Help Center Closed"],
    "Tumblr":               ["There's nothing here"],
    "Wordpress":            ["Do you want to register"],
    "Pantheon":             ["The gods are wise"],
    "Surge.sh":             ["project not found"],
    "Cargo":                ["If you're moving your domain away from Cargo"],
    "Bitbucket":            ["Repository not found"],
    "UserVoice":            ["This UserVoice subdomain is currently available"],
    "Freshdesk":            ["We couldn't find the page"],
    "Pingdom":              ["Sorry, couldn't find the status page"],
    "Statuspage":           ["You are being redirected"],
    "Unbounce":             ["The requested URL was not found on this server"],
    "Tilda":                ["Please renew your subscription"],
    "Launchrock":           ["It looks like you may have taken a wrong turn"],
    "HubSpot":              ["does not exist in our system"],
}

CLOUD_PATTERNS = {
    "AWS S3":         r"[a-zA-Z0-9\-\.]+\.s3\.amazonaws\.com",
    "AWS CloudFront": r"[a-zA-Z0-9\-]+\.cloudfront\.net",
    "Azure Blob":     r"[a-zA-Z0-9\-]+\.blob\.core\.windows\.net",
    "Azure Web":      r"[a-zA-Z0-9\-]+\.azurewebsites\.net",
    "GCP Storage":    r"[a-zA-Z0-9\-]+\.storage\.googleapis\.com",
    "GCP App":        r"[a-zA-Z0-9\-]+\.appspot\.com",
    "Cloudflare":     r"[a-zA-Z0-9\-]+\.pages\.dev",
    "Netlify":        r"[a-zA-Z0-9\-]+\.netlify\.app",
    "Vercel":         r"[a-zA-Z0-9\-]+\.vercel\.app",
    "Heroku":         r"[a-zA-Z0-9\-]+\.herokuapp\.com",
    "DigitalOcean":   r"[a-zA-Z0-9\-]+\.digitaloceanspaces\.com",
    "Fastly":         r"[a-zA-Z0-9\-]+\.fastly\.net",
}

DEFAULT_CONFIG = {
    "api_keys": {
        "shodan": "",
        "censys_id": "",
        "censys_secret": "",
        "securitytrails": "",
        "virustotal": "",
        "binaryedge": "",
        "c99": "",
        "whoisxml": "",
        "github": "",
        "fofa_email": "",
        "fofa_key": "",
        "zoomeye": "",
        "chaos": "",
        "fullhunt": "",
    },
    "settings": {
        "threads": 100,
        "timeout": 10,
        "rate_limit": 0.5,
        "retries": 3,
        "user_agent": "Mozilla/5.0 SubHunterX/1.0",
        "proxy": "",
        "use_tor": False,
        "recursive": False,
        "recursive_depth": 2,
        "brute_force": True,
        "wordlist": "wordlists/subdomains.txt",
        "screenshot": True,
        "screenshot_timeout": 15,
    },
    "notifications": {
        "slack_webhook": "",
        "discord_webhook": "",
    }
}

# ──────────────────────────────────────────────────────────────────────────────
# CONFIG MANAGER
# ──────────────────────────────────────────────────────────────────────────────
class ConfigManager:
    def __init__(self, config_path="config/config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load()

    def _load(self):
        if self.config_path.exists():
            with open(self.config_path) as f:
                loaded = yaml.safe_load(f) or {}
            # Deep merge
            merged = DEFAULT_CONFIG.copy()
            for section, vals in loaded.items():
                if section in merged and isinstance(vals, dict):
                    merged[section].update(vals)
                else:
                    merged[section] = vals
            return merged
        else:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w") as f:
                yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False)
            console.print(f"[yellow]⚙️  Config created at {self.config_path} — fill in your API keys![/yellow]")
            return DEFAULT_CONFIG

    def get(self, *keys, default=None):
        val = self.config
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k, default)
            else:
                return default
        return val


# ──────────────────────────────────────────────────────────────────────────────
# CHECKPOINT / RESUME
# ──────────────────────────────────────────────────────────────────────────────
class Checkpoint:
    def __init__(self, domain, output_dir):
        self.path = Path(output_dir) / ".checkpoint.json"
        self.domain = domain
        self.data = self._load()

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path) as f:
                    return json.load(f)
            except Exception:
                pass
        return {"domain": self.domain, "completed_sources": [], "subdomains": []}

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2)

    def mark_source(self, source):
        if source not in self.data["completed_sources"]:
            self.data["completed_sources"].append(source)
        self.save()

    def add_subdomains(self, subs):
        existing = set(self.data["subdomains"])
        new = [s for s in subs if s not in existing]
        self.data["subdomains"].extend(new)
        self.save()

    def is_done(self, source):
        return source in self.data["completed_sources"]

    def clear(self):
        if self.path.exists():
            self.path.unlink()


# ──────────────────────────────────────────────────────────────────────────────
# SUBDOMAIN SOURCES
# ──────────────────────────────────────────────────────────────────────────────
class SubdomainSources:
    def __init__(self, config: ConfigManager, proxies=None):
        self.cfg = config
        self.proxies = proxies or {}
        self.timeout = config.get("settings", "timeout", default=10)
        self.ua = config.get("settings", "user_agent", default="SubHunterX/1.0")
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.ua})
        if self.proxies:
            self.session.proxies.update(self.proxies)

    def _get(self, url, params=None, headers=None, retries=3):
        for attempt in range(retries):
            try:
                r = self.session.get(url, params=params, headers=headers,
                                     timeout=self.timeout, verify=False)
                return r
            except Exception:
                time.sleep(1.5 ** attempt)
        return None

    def _extract_subdomains(self, text, domain):
        pattern = rf"(?:[a-zA-Z0-9_\-\*]+\.)+{re.escape(domain)}"
        found = re.findall(pattern, text, re.IGNORECASE)
        return {s.lower().strip(".") for s in found}

    # ── 1. crt.sh ──────────────────────────────────────────────────────────────
    def crtsh(self, domain):
        subs = set()
        try:
            r = self._get(f"https://crt.sh/?q=%.{domain}&output=json")
            if r and r.status_code == 200:
                for entry in r.json():
                    names = entry.get("name_value", "")
                    for n in names.split("\n"):
                        n = n.strip().lstrip("*.")
                        if n.endswith(domain):
                            subs.add(n.lower())
        except Exception:
            pass
        return subs

    # ── 2. HackerTarget ────────────────────────────────────────────────────────
    def hackertarget(self, domain):
        subs = set()
        try:
            r = self._get(f"https://api.hackertarget.com/hostsearch/?q={domain}")
            if r and r.status_code == 200:
                for line in r.text.splitlines():
                    parts = line.split(",")
                    if parts and parts[0].endswith(domain):
                        subs.add(parts[0].lower())
        except Exception:
            pass
        return subs

    # ── 3. AlienVault OTX ─────────────────────────────────────────────────────
    def alienvault(self, domain):
        subs = set()
        page = 1
        while True:
            try:
                r = self._get(f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns",
                              params={"page": page, "limit": 500})
                if not r or r.status_code != 200:
                    break
                data = r.json()
                entries = data.get("passive_dns", [])
                if not entries:
                    break
                for e in entries:
                    h = e.get("hostname", "")
                    if h.endswith(domain):
                        subs.add(h.lower())
                if not data.get("has_next"):
                    break
                page += 1
            except Exception:
                break
        return subs

    # ── 4. VirusTotal ──────────────────────────────────────────────────────────
    def virustotal(self, domain):
        subs = set()
        key = self.cfg.get("api_keys", "virustotal")
        if not key:
            return subs
        try:
            cursor = None
            while True:
                params = {"limit": 40}
                if cursor:
                    params["cursor"] = cursor
                r = self._get(f"https://www.virustotal.com/api/v3/domains/{domain}/subdomains",
                              params=params,
                              headers={"x-apikey": key})
                if not r or r.status_code != 200:
                    break
                data = r.json()
                for item in data.get("data", []):
                    subs.add(item["id"].lower())
                cursor = data.get("meta", {}).get("cursor")
                if not cursor:
                    break
        except Exception:
            pass
        return subs

    # ── 5. Wayback Machine ────────────────────────────────────────────────────
    def wayback(self, domain):
        subs = set()
        try:
            r = self._get(f"http://web.archive.org/cdx/search/cdx",
                          params={"url": f"*.{domain}/*", "output": "json",
                                  "fl": "original", "collapse": "urlkey", "limit": 5000})
            if r and r.status_code == 200:
                data = r.json()
                for row in data[1:]:
                    url = row[0]
                    host = urlparse(url).netloc
                    if host.endswith(domain):
                        subs.add(host.lower())
        except Exception:
            pass
        return subs

    # ── 6. URLScan.io ─────────────────────────────────────────────────────────
    def urlscan(self, domain):
        subs = set()
        try:
            r = self._get(f"https://urlscan.io/api/v1/search/",
                          params={"q": f"domain:{domain}", "size": 10000})
            if r and r.status_code == 200:
                data = r.json()
                for result in data.get("results", []):
                    page = result.get("page", {})
                    host = page.get("domain", "")
                    if host.endswith(domain):
                        subs.add(host.lower())
        except Exception:
            pass
        return subs

    # ── 7. ThreatCrowd ────────────────────────────────────────────────────────
    def threatcrowd(self, domain):
        subs = set()
        try:
            r = self._get(f"https://www.threatcrowd.org/searchApi/v2/domain/report/",
                          params={"domain": domain})
            if r and r.status_code == 200:
                data = r.json()
                for sub in data.get("subdomains", []):
                    if sub.endswith(domain):
                        subs.add(sub.lower())
        except Exception:
            pass
        return subs

    # ── 8. DNSdumpster ────────────────────────────────────────────────────────
    def dnsdumpster(self, domain):
        subs = set()
        try:
            s = requests.Session()
            s.headers.update({"User-Agent": self.ua})
            if self.proxies:
                s.proxies.update(self.proxies)
            r = s.get("https://dnsdumpster.com", timeout=self.timeout)
            csrf = re.search(r'csrfmiddlewaretoken.*?value="(.*?)"', r.text)
            if csrf:
                token = csrf.group(1)
                r2 = s.post("https://dnsdumpster.com/", data={
                    "csrfmiddlewaretoken": token,
                    "targetip": domain,
                    "user": "free"
                }, headers={"Referer": "https://dnsdumpster.com"},
                timeout=self.timeout)
                subs = self._extract_subdomains(r2.text, domain)
        except Exception:
            pass
        return subs

    # ── 9. BufferOver ─────────────────────────────────────────────────────────
    def bufferover(self, domain):
        subs = set()
        try:
            r = self._get(f"https://dns.bufferover.run/dns?q=.{domain}")
            if r and r.status_code == 200:
                data = r.json()
                for record in data.get("FDNS_A", []) + data.get("RDNS", []):
                    parts = record.split(",")
                    for p in parts:
                        p = p.strip()
                        if p.endswith(domain):
                            subs.add(p.lower())
        except Exception:
            pass
        return subs

    # ── 10. Shodan ────────────────────────────────────────────────────────────
    def shodan(self, domain):
        subs = set()
        key = self.cfg.get("api_keys", "shodan")
        if not key:
            return subs
        try:
            r = self._get(f"https://api.shodan.io/dns/domain/{domain}",
                          params={"key": key})
            if r and r.status_code == 200:
                data = r.json()
                for sub in data.get("subdomains", []):
                    subs.add(f"{sub}.{domain}".lower())
        except Exception:
            pass
        return subs

    # ── 11. SecurityTrails ────────────────────────────────────────────────────
    def securitytrails(self, domain):
        subs = set()
        key = self.cfg.get("api_keys", "securitytrails")
        if not key:
            return subs
        try:
            r = self._get(f"https://api.securitytrails.com/v1/domain/{domain}/subdomains",
                          params={"children_only": False},
                          headers={"APIKEY": key})
            if r and r.status_code == 200:
                data = r.json()
                for sub in data.get("subdomains", []):
                    subs.add(f"{sub}.{domain}".lower())
        except Exception:
            pass
        return subs

    # ── 12. BinaryEdge ────────────────────────────────────────────────────────
    def binaryedge(self, domain):
        subs = set()
        key = self.cfg.get("api_keys", "binaryedge")
        if not key:
            return subs
        try:
            page = 1
            while True:
                r = self._get(f"https://api.binaryedge.io/v2/query/domains/subdomain/{domain}",
                              params={"page": page},
                              headers={"X-Key": key})
                if not r or r.status_code != 200:
                    break
                data = r.json()
                for evt in data.get("events", []):
                    if evt.endswith(domain):
                        subs.add(evt.lower())
                if page >= data.get("pagesize", 1):
                    break
                page += 1
        except Exception:
            pass
        return subs

    # ── 13. C99.nl ───────────────────────────────────────────────────────────
    def c99(self, domain):
        subs = set()
        key = self.cfg.get("api_keys", "c99")
        if not key:
            return subs
        try:
            r = self._get(f"https://api.c99.nl/subdomainfinder",
                          params={"key": key, "domain": domain, "json": True})
            if r and r.status_code == 200:
                data = r.json()
                for sub in data.get("subdomains", []):
                    name = sub.get("subdomain", "")
                    if name.endswith(domain):
                        subs.add(name.lower())
        except Exception:
            pass
        return subs

    # ── 14. WhoisXMLAPI ───────────────────────────────────────────────────────
    def whoisxml(self, domain):
        subs = set()
        key = self.cfg.get("api_keys", "whoisxml")
        if not key:
            return subs
        try:
            r = self._get("https://subdomains.whoisxmlapi.com/api/v1",
                          params={"apiKey": key, "domainName": domain, "outputFormat": "JSON"})
            if r and r.status_code == 200:
                data = r.json()
                result = data.get("result", {})
                for rec in result.get("records", []):
                    name = rec.get("domain", "")
                    if name.endswith(domain):
                        subs.add(name.lower())
        except Exception:
            pass
        return subs

    # ── 15. Censys ────────────────────────────────────────────────────────────
    def censys(self, domain):
        subs = set()
        cid = self.cfg.get("api_keys", "censys_id")
        csec = self.cfg.get("api_keys", "censys_secret")
        if not cid or not csec:
            return subs
        try:
            r = self._get("https://search.censys.io/api/v2/certificates/search",
                          params={"q": f"parsed.names: {domain}", "per_page": 100},
                          headers={"Accept": "application/json"})
            if r:
                r.auth = (cid, csec)
                # Retry with auth
                r2 = self.session.get("https://search.censys.io/api/v2/certificates/search",
                                      params={"q": f"parsed.names: {domain}", "per_page": 100},
                                      auth=(cid, csec), timeout=self.timeout)
                if r2.status_code == 200:
                    data = r2.json()
                    for hit in data.get("result", {}).get("hits", []):
                        for name in hit.get("parsed", {}).get("names", []):
                            name = name.lstrip("*.").lower()
                            if name.endswith(domain):
                                subs.add(name)
        except Exception:
            pass
        return subs

    # ── 16. GitHub Search ─────────────────────────────────────────────────────
    def github(self, domain):
        subs = set()
        token = self.cfg.get("api_keys", "github")
        if not token:
            return subs
        try:
            headers = {"Authorization": f"token {token}",
                       "Accept": "application/vnd.github.v3+json"}
            r = self._get("https://api.github.com/search/code",
                          params={"q": domain, "per_page": 100},
                          headers=headers)
            if r and r.status_code == 200:
                data = r.json()
                for item in data.get("items", []):
                    content_url = item.get("url", "")
                    if content_url:
                        rc = self._get(content_url, headers=headers)
                        if rc and rc.status_code == 200:
                            import base64
                            content = rc.json().get("content", "")
                            try:
                                decoded = base64.b64decode(content).decode("utf-8", errors="ignore")
                                subs |= self._extract_subdomains(decoded, domain)
                            except Exception:
                                pass
                        time.sleep(0.3)
        except Exception:
            pass
        return subs

    # ── 17. Robtex ────────────────────────────────────────────────────────────
    def robtex(self, domain):
        subs = set()
        try:
            r = self._get(f"https://freeapi.robtex.com/pdns/forward/{domain}")
            if r and r.status_code == 200:
                for line in r.text.splitlines():
                    try:
                        data = json.loads(line)
                        name = data.get("rrname", "")
                        if name.endswith(domain):
                            subs.add(name.strip(".").lower())
                    except Exception:
                        pass
        except Exception:
            pass
        return subs

    # ── 18. ViewDNS ───────────────────────────────────────────────────────────
    def viewdns(self, domain):
        subs = set()
        try:
            r = self._get(f"https://viewdns.info/reverseip/",
                          params={"host": domain, "apikey": "", "output": "json"})
            if r and r.status_code == 200:
                subs = self._extract_subdomains(r.text, domain)
        except Exception:
            pass
        return subs

    # ── 19. CommonCrawl ───────────────────────────────────────────────────────
    def commoncrawl(self, domain):
        subs = set()
        try:
            # Get latest index
            r = self._get("http://index.commoncrawl.org/collinfo.json")
            if not r or r.status_code != 200:
                return subs
            indexes = r.json()
            latest = indexes[0].get("cdx-api", "")
            if latest:
                r2 = self._get(latest, params={
                    "url": f"*.{domain}", "output": "json",
                    "fl": "url", "limit": 5000, "filter": "statuscode:200"
                })
                if r2 and r2.status_code == 200:
                    for line in r2.text.splitlines():
                        try:
                            data = json.loads(line)
                            url = data.get("url", "")
                            host = urlparse(url).netloc
                            if host.endswith(domain):
                                subs.add(host.lower())
                        except Exception:
                            pass
        except Exception:
            pass
        return subs

    # ── 20. ThreatMiner ───────────────────────────────────────────────────────
    def threatminer(self, domain):
        subs = set()
        try:
            r = self._get(f"https://api.threatminer.org/v2/domain.php",
                          params={"q": domain, "rt": "5"})
            if r and r.status_code == 200:
                data = r.json()
                for sub in data.get("results", []):
                    if sub.endswith(domain):
                        subs.add(sub.lower())
        except Exception:
            pass
        return subs

    # ── 21. Netcraft ──────────────────────────────────────────────────────────
    def netcraft(self, domain):
        subs = set()
        try:
            r = self._get(f"https://searchdns.netcraft.com/",
                          params={"restriction": "site+ends+with", "host": domain})
            if r and r.status_code == 200:
                subs = self._extract_subdomains(r.text, domain)
        except Exception:
            pass
        return subs

    # ── 22. CIRCL PassiveDNS ──────────────────────────────────────────────────
    def circl(self, domain):
        subs = set()
        try:
            r = self._get(f"https://www.circl.lu/pdns/query/{domain}")
            if r and r.status_code == 200:
                for line in r.text.splitlines():
                    try:
                        data = json.loads(line)
                        rname = data.get("rrname", "").strip(".")
                        if rname.endswith(domain):
                            subs.add(rname.lower())
                    except Exception:
                        pass
        except Exception:
            pass
        return subs

    # ── 23. FullHunt ──────────────────────────────────────────────────────────
    def fullhunt(self, domain):
        subs = set()
        key = self.cfg.get("api_keys", "fullhunt")
        if not key:
            return subs
        try:
            r = self._get(f"https://fullhunt.io/api/v1/domain/{domain}/subdomains",
                          headers={"X-API-KEY": key})
            if r and r.status_code == 200:
                data = r.json()
                for host in data.get("hosts", []):
                    if host.endswith(domain):
                        subs.add(host.lower())
        except Exception:
            pass
        return subs

    # ── 24. Chaos (ProjectDiscovery) ──────────────────────────────────────────
    def chaos(self, domain):
        subs = set()
        key = self.cfg.get("api_keys", "chaos")
        if not key:
            return subs
        try:
            r = self._get(f"https://dns.projectdiscovery.io/dns/{domain}/subdomains",
                          headers={"Authorization": key})
            if r and r.status_code == 200:
                data = r.json()
                for sub in data.get("subdomains", []):
                    subs.add(f"{sub}.{domain}".lower())
        except Exception:
            pass
        return subs

    # ── 25. ZoomEye ───────────────────────────────────────────────────────────
    def zoomeye(self, domain):
        subs = set()
        key = self.cfg.get("api_keys", "zoomeye")
        if not key:
            return subs
        try:
            r = self._get("https://api.zoomeye.org/web/search",
                          params={"query": f"site:{domain}", "page": 1},
                          headers={"API-KEY": key})
            if r and r.status_code == 200:
                data = r.json()
                for match in data.get("matches", []):
                    url = match.get("site", "")
                    if url.endswith(domain):
                        subs.add(url.lower())
        except Exception:
            pass
        return subs

    # ── 26. FOFA ──────────────────────────────────────────────────────────────
    def fofa(self, domain):
        subs = set()
        email = self.cfg.get("api_keys", "fofa_email")
        key = self.cfg.get("api_keys", "fofa_key")
        if not email or not key:
            return subs
        try:
            import base64
            query = base64.b64encode(f"domain=\"{domain}\"".encode()).decode()
            r = self._get("https://fofa.info/api/v1/search/all",
                          params={"email": email, "key": key, "qbase64": query,
                                  "fields": "host", "size": 10000})
            if r and r.status_code == 200:
                data = r.json()
                for row in data.get("results", []):
                    host = row[0].strip() if row else ""
                    host = host.replace("http://", "").replace("https://", "").split("/")[0]
                    if host.endswith(domain):
                        subs.add(host.lower())
        except Exception:
            pass
        return subs

    # ── 27. Certspotter ───────────────────────────────────────────────────────
    def certspotter(self, domain):
        subs = set()
        try:
            r = self._get(f"https://api.certspotter.com/v1/issuances",
                          params={"domain": domain, "include_subdomains": True,
                                  "expand": "dns_names"})
            if r and r.status_code == 200:
                for cert in r.json():
                    for name in cert.get("dns_names", []):
                        name = name.lstrip("*.").lower()
                        if name.endswith(domain):
                            subs.add(name)
        except Exception:
            pass
        return subs

    # ── 28. GreyNoise ─────────────────────────────────────────────────────────
    def greynoise(self, domain):
        subs = set()
        try:
            r = self._get(f"https://api.greynoise.io/v3/community/{domain}")
            if r and r.status_code == 200:
                subs = self._extract_subdomains(r.text, domain)
        except Exception:
            pass
        return subs

    # ── 29. Google Dork ───────────────────────────────────────────────────────
    def google_dork(self, domain):
        subs = set()
        try:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; SubHunterX)"}
            dorks = [f"site:*.{domain}", f"site:{domain} -www"]
            for dork in dorks:
                r = self._get("https://www.google.com/search",
                              params={"q": dork, "num": 100},
                              headers=headers)
                if r and r.status_code == 200:
                    subs |= self._extract_subdomains(r.text, domain)
                time.sleep(2)
        except Exception:
            pass
        return subs

    # ── 30. Bing Dork ─────────────────────────────────────────────────────────
    def bing_dork(self, domain):
        subs = set()
        try:
            for page in range(1, 6):
                r = self._get("https://www.bing.com/search",
                              params={"q": f"site:{domain}", "first": (page - 1) * 10 + 1})
                if r and r.status_code == 200:
                    subs |= self._extract_subdomains(r.text, domain)
                time.sleep(1)
        except Exception:
            pass
        return subs

    # ── 31. Baidu Dork ────────────────────────────────────────────────────────
    def baidu_dork(self, domain):
        subs = set()
        try:
            for page in range(1, 4):
                r = self._get("https://www.baidu.com/s",
                              params={"wd": f"site:{domain}", "pn": (page - 1) * 10})
                if r and r.status_code == 200:
                    subs |= self._extract_subdomains(r.text, domain)
                time.sleep(1.5)
        except Exception:
            pass
        return subs

    # ── 32. RapidDNS ──────────────────────────────────────────────────────────
    def rapiddns(self, domain):
        subs = set()
        try:
            r = self._get(f"https://rapiddns.io/subdomain/{domain}?full=1#result")
            if r and r.status_code == 200:
                subs = self._extract_subdomains(r.text, domain)
        except Exception:
            pass
        return subs

    # ── 33. Anubis DB ─────────────────────────────────────────────────────────
    def anubis(self, domain):
        subs = set()
        try:
            r = self._get(f"https://jldc.me/anubis/subdomains/{domain}")
            if r and r.status_code == 200:
                for sub in r.json():
                    if sub.endswith(domain):
                        subs.add(sub.lower())
        except Exception:
            pass
        return subs

    # ── 34. Columbus Project ──────────────────────────────────────────────────
    def columbus(self, domain):
        subs = set()
        try:
            r = self._get(f"https://columbus.elmasy.com/api/lookup/{domain}")
            if r and r.status_code == 200:
                for sub in r.json():
                    full = f"{sub}.{domain}".lower()
                    subs.add(full)
        except Exception:
            pass
        return subs

    # ── 35. ShrewdEye ─────────────────────────────────────────────────────────
    def shrewdeye(self, domain):
        subs = set()
        try:
            r = self._get(f"https://shrewdeye.app/domains/{domain}.json")
            if r and r.status_code == 200:
                subs = self._extract_subdomains(r.text, domain)
        except Exception:
            pass
        return subs

    # ── 36. WebArchive CDX ────────────────────────────────────────────────────
    def webarchive_cdx(self, domain):
        subs = set()
        try:
            r = self._get(f"http://web.archive.org/cdx/search/cdx",
                          params={"url": f"*.{domain}", "output": "text",
                                  "fl": "original", "collapse": "urlkey", "limit": 10000})
            if r and r.status_code == 200:
                for line in r.text.splitlines():
                    host = urlparse(line.strip()).netloc
                    if host.endswith(domain):
                        subs.add(host.lower())
        except Exception:
            pass
        return subs

    # ── 37. PassiveTotal (Community) ─────────────────────────────────────────
    def passivetotal(self, domain):
        subs = set()
        try:
            r = self._get(f"https://api.passivetotal.org/v2/enrichment/subdomains",
                          params={"query": domain})
            if r and r.status_code == 200:
                data = r.json()
                for sub in data.get("subdomains", []):
                    subs.add(f"{sub}.{domain}".lower())
        except Exception:
            pass
        return subs

    # ── 38. Riddler ───────────────────────────────────────────────────────────
    def riddler(self, domain):
        subs = set()
        try:
            r = self._get(f"https://riddler.io/search/exportcsv",
                          params={"q": f"pld:{domain}"})
            if r and r.status_code == 200:
                subs = self._extract_subdomains(r.text, domain)
        except Exception:
            pass
        return subs

    # ── 39. Phonebook.cz ─────────────────────────────────────────────────────
    def phonebook(self, domain):
        subs = set()
        try:
            r = self._get(f"https://phonebook.cz/",
                          params={"q": domain, "p": 1, "type": 1})
            if r and r.status_code == 200:
                subs = self._extract_subdomains(r.text, domain)
        except Exception:
            pass
        return subs

    # ── 40. DNSrepo ───────────────────────────────────────────────────────────
    def dnsrepo(self, domain):
        subs = set()
        try:
            r = self._get(f"https://dnsrepo.noc.org/", params={"domain": domain})
            if r and r.status_code == 200:
                subs = self._extract_subdomains(r.text, domain)
        except Exception:
            pass
        return subs

    # ── 41. Synapsint ─────────────────────────────────────────────────────────
    def synapsint(self, domain):
        subs = set()
        try:
            r = self._get(f"https://synapsint.com/report.php",
                          params={"q": domain})
            if r and r.status_code == 200:
                subs = self._extract_subdomains(r.text, domain)
        except Exception:
            pass
        return subs

    # ── 42. Subdomain.center ──────────────────────────────────────────────────
    def subdomaincenter(self, domain):
        subs = set()
        try:
            r = self._get(f"https://api.subdomain.center/",
                          params={"domain": domain})
            if r and r.status_code == 200:
                for sub in r.json():
                    if sub.endswith(domain):
                        subs.add(sub.lower())
        except Exception:
            pass
        return subs

    # ── 43. Ceres (passive) ───────────────────────────────────────────────────
    def ceres(self, domain):
        subs = set()
        try:
            r = self._get(f"https://sonar.omnisint.io/subdomains/{domain}")
            if r and r.status_code == 200:
                for sub in r.json():
                    if sub.endswith(domain):
                        subs.add(sub.lower())
        except Exception:
            pass
        return subs

    # ── 44. PublicWWW ─────────────────────────────────────────────────────────
    def publicwww(self, domain):
        subs = set()
        try:
            r = self._get(f"https://publicwww.com/websites/{domain}/",
                          params={"export": "csv"})
            if r and r.status_code == 200:
                subs = self._extract_subdomains(r.text, domain)
        except Exception:
            pass
        return subs

    # ── 45. Recon.dev ─────────────────────────────────────────────────────────
    def recondev(self, domain):
        subs = set()
        try:
            r = self._get(f"https://recon.dev/api/search",
                          params={"key": "test", "domain": domain})
            if r and r.status_code == 200:
                for item in r.json():
                    for raw in item.get("rawDomains", []):
                        if raw.endswith(domain):
                            subs.add(raw.lower())
        except Exception:
            pass
        return subs

    # ── 46. DNSSpy ────────────────────────────────────────────────────────────
    def dnspy(self, domain):
        subs = set()
        try:
            r = self._get(f"https://dnspy.org/domain/{domain}/subdomains.json")
            if r and r.status_code == 200:
                subs = self._extract_subdomains(r.text, domain)
        except Exception:
            pass
        return subs

    # ── 47. LeakIX ────────────────────────────────────────────────────────────
    def leakix(self, domain):
        subs = set()
        try:
            r = self._get(f"https://leakix.net/domain/{domain}",
                          headers={"Accept": "application/json"})
            if r and r.status_code == 200:
                data = r.json()
                for event in data.get("Services", []):
                    host = event.get("host", "")
                    if host.endswith(domain):
                        subs.add(host.lower())
        except Exception:
            pass
        return subs

    # ── 48. DNS Brute Force ───────────────────────────────────────────────────
    def dns_bruteforce(self, domain, wordlist_path):
        subs = set()
        resolver = dns.resolver.Resolver()
        resolver.timeout = 3
        resolver.lifetime = 3
        resolver.nameservers = ["8.8.8.8", "1.1.1.1", "8.8.4.4", "9.9.9.9"]

        if not Path(wordlist_path).exists():
            return subs

        with open(wordlist_path) as f:
            words = [w.strip() for w in f if w.strip()]

        def resolve(word):
            target = f"{word}.{domain}"
            try:
                resolver.resolve(target, "A")
                return target
            except Exception:
                return None

        with ThreadPoolExecutor(max_workers=200) as ex:
            futures = {ex.submit(resolve, w): w for w in words}
            for fut in as_completed(futures):
                result = fut.result()
                if result:
                    subs.add(result.lower())
        return subs

    def get_all_sources(self):
        return [
            ("crt.sh",            self.crtsh),
            ("HackerTarget",      self.hackertarget),
            ("AlienVault OTX",    self.alienvault),
            ("VirusTotal",        self.virustotal),
            ("Wayback Machine",   self.wayback),
            ("URLScan.io",        self.urlscan),
            ("ThreatCrowd",       self.threatcrowd),
            ("DNSDumpster",       self.dnsdumpster),
            ("BufferOver",        self.bufferover),
            ("Shodan",            self.shodan),
            ("SecurityTrails",    self.securitytrails),
            ("BinaryEdge",        self.binaryedge),
            ("C99.nl",            self.c99),
            ("WhoisXMLAPI",       self.whoisxml),
            ("Censys",            self.censys),
            ("GitHub",            self.github),
            ("Robtex",            self.robtex),
            ("ViewDNS",           self.viewdns),
            ("CommonCrawl",       self.commoncrawl),
            ("ThreatMiner",       self.threatminer),
            ("Netcraft",          self.netcraft),
            ("CIRCL PassiveDNS",  self.circl),
            ("FullHunt",          self.fullhunt),
            ("Chaos (PD)",        self.chaos),
            ("ZoomEye",           self.zoomeye),
            ("FOFA",              self.fofa),
            ("Certspotter",       self.certspotter),
            ("GreyNoise",         self.greynoise),
            ("Google Dork",       self.google_dork),
            ("Bing Dork",         self.bing_dork),
            ("Baidu Dork",        self.baidu_dork),
            ("RapidDNS",          self.rapiddns),
            ("Anubis DB",         self.anubis),
            ("Columbus",          self.columbus),
            ("ShrewdEye",         self.shrewdeye),
            ("WebArchive CDX",    self.webarchive_cdx),
            ("PassiveTotal",      self.passivetotal),
            ("Riddler",           self.riddler),
            ("Phonebook.cz",      self.phonebook),
            ("DNSrepo",           self.dnsrepo),
            ("Synapsint",         self.synapsint),
            ("Subdomain.center",  self.subdomaincenter),
            ("Omnisint/Ceres",    self.ceres),
            ("PublicWWW",         self.publicwww),
            ("Recon.dev",         self.recondev),
            ("LeakIX",            self.leakix),
        ]


# ──────────────────────────────────────────────────────────────────────────────
# DNS ANALYZER
# ──────────────────────────────────────────────────────────────────────────────
class DNSAnalyzer:
    def __init__(self, threads=100, timeout=3):
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = timeout
        self.resolver.lifetime = timeout
        self.resolver.nameservers = ["8.8.8.8", "1.1.1.1", "8.8.4.4", "9.9.9.9"]
        self.threads = threads

    def resolve(self, subdomain):
        result = {"subdomain": subdomain, "ips": [], "cnames": [], "resolves": False}
        try:
            ans = self.resolver.resolve(subdomain, "A")
            result["ips"] = [r.address for r in ans]
            result["resolves"] = True
        except Exception:
            pass
        try:
            ans = self.resolver.resolve(subdomain, "CNAME")
            result["cnames"] = [str(r.target).rstrip(".") for r in ans]
        except Exception:
            pass
        return result

    def resolve_all(self, subdomains):
        results = {}
        with ThreadPoolExecutor(max_workers=self.threads) as ex:
            futures = {ex.submit(self.resolve, s): s for s in subdomains}
            for fut in as_completed(futures):
                res = fut.result()
                results[res["subdomain"]] = res
        return results

    def detect_wildcard(self, domain):
        import random, string
        fake = "".join(random.choices(string.ascii_lowercase, k=16))
        try:
            self.resolver.resolve(f"{fake}.{domain}", "A")
            return True
        except Exception:
            return False


# ──────────────────────────────────────────────────────────────────────────────
# HTTP PROBER
# ──────────────────────────────────────────────────────────────────────────────
class HTTPProber:
    def __init__(self, threads=50, timeout=10, proxies=None):
        self.threads = threads
        self.timeout = timeout
        self.proxies = proxies or {}

    def probe(self, subdomain):
        result = {
            "subdomain": subdomain,
            "alive": False,
            "url": "",
            "status_code": None,
            "title": "",
            "server": "",
            "content_length": 0,
            "redirect_url": "",
            "technologies": [],
            "waf": "",
            "cloud": "",
            "takeover_risk": "",
            "cname": "",
            "error": "",
        }
        for scheme in ["https", "http"]:
            url = f"{scheme}://{subdomain}"
            try:
                r = requests.get(url, timeout=self.timeout, verify=False,
                                 allow_redirects=True, proxies=self.proxies,
                                 headers={"User-Agent": "Mozilla/5.0 SubHunterX/1.0"})
                result["alive"] = True
                result["url"] = url
                result["status_code"] = r.status_code
                result["server"] = r.headers.get("Server", "")
                result["content_length"] = len(r.content)
                if r.history:
                    result["redirect_url"] = r.url

                # Extract title
                title_match = re.search(r"<title[^>]*>(.*?)</title>", r.text, re.IGNORECASE | re.DOTALL)
                if title_match:
                    result["title"] = title_match.group(1).strip()[:100]

                # Cloud detection
                for provider, pattern in CLOUD_PATTERNS.items():
                    if re.search(pattern, subdomain, re.IGNORECASE):
                        result["cloud"] = provider
                        break

                # WAF detection
                waf_headers = {
                    "Cloudflare": ["cf-ray", "cf-cache-status"],
                    "AWS WAF":    ["x-amzn-requestid"],
                    "Akamai":     ["x-akamai-transformed"],
                    "Sucuri":     ["x-sucuri-id"],
                    "Imperva":    ["x-iinfo"],
                    "F5 BIG-IP":  ["x-cnection"],
                }
                for waf, hdrs in waf_headers.items():
                    for h in hdrs:
                        if h in {k.lower() for k in r.headers.keys()}:
                            result["waf"] = waf
                            break

                # Takeover detection
                for service, signatures in TAKEOVER_SIGNATURES.items():
                    for sig in signatures:
                        if sig.lower() in r.text.lower():
                            result["takeover_risk"] = service
                            break

                return result
            except requests.exceptions.SSLError:
                continue
            except Exception as e:
                result["error"] = str(e)[:80]

        # Dead — probe for dead details
        for scheme in ["https", "http"]:
            url = f"{scheme}://{subdomain}"
            try:
                r = requests.get(url, timeout=self.timeout, verify=False,
                                 allow_redirects=False, proxies=self.proxies)
                result["url"] = url
                result["status_code"] = r.status_code
                result["server"] = r.headers.get("Server", "")
                return result
            except Exception as e:
                result["error"] = str(e)[:80]

        return result

    def probe_all(self, subdomains):
        results = []
        with ThreadPoolExecutor(max_workers=self.threads) as ex:
            futures = {ex.submit(self.probe, s): s for s in subdomains}
            for fut in as_completed(futures):
                results.append(fut.result())
        return results


# ──────────────────────────────────────────────────────────────────────────────
# SCREENSHOT ENGINE
# ──────────────────────────────────────────────────────────────────────────────
class ScreenshotEngine:
    def __init__(self, output_dir, timeout=15):
        self.output_dir = Path(output_dir) / "live-subdomains-screenshots"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.driver = None

    def _init_driver(self):
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            opts = Options()
            opts.add_argument("--headless")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            opts.add_argument("--window-size=1280,800")
            opts.add_argument("--ignore-certificate-errors")
            opts.add_argument("--disable-gpu")
            self.driver = webdriver.Chrome(options=opts)
            self.driver.set_page_load_timeout(self.timeout)
            return True
        except Exception as e:
            console.print(f"[yellow]⚠️  Screenshot driver unavailable: {e}[/yellow]")
            return False

    def take(self, url, subdomain):
        if not self.driver:
            if not self._init_driver():
                return None
        fname = re.sub(r"[^\w\-]", "_", subdomain) + ".png"
        fpath = self.output_dir / fname
        try:
            self.driver.get(url)
            time.sleep(2)
            self.driver.save_screenshot(str(fpath))
            return str(fpath)
        except Exception:
            return None

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass


# ──────────────────────────────────────────────────────────────────────────────
# NOTIFIER
# ──────────────────────────────────────────────────────────────────────────────
class Notifier:
    def __init__(self, config: ConfigManager):
        self.slack_url = config.get("notifications", "slack_webhook")
        self.discord_url = config.get("notifications", "discord_webhook")

    def send(self, message):
        if self.slack_url:
            try:
                requests.post(self.slack_url, json={"text": message}, timeout=10)
            except Exception:
                pass
        if self.discord_url:
            try:
                requests.post(self.discord_url, json={"content": message}, timeout=10)
            except Exception:
                pass


# ──────────────────────────────────────────────────────────────────────────────
# REPORT GENERATOR
# ──────────────────────────────────────────────────────────────────────────────
class ReportGenerator:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)

    def generate_html(self, domain, live_results, dead_results, stats):
        live_rows = ""
        for r in live_results:
            takeover_badge = f'<span class="badge badge-danger">⚠️ {r["takeover_risk"]}</span>' if r.get("takeover_risk") else ""
            cloud_badge    = f'<span class="badge badge-info">{r["cloud"]}</span>' if r.get("cloud") else ""
            waf_badge      = f'<span class="badge badge-warning">{r["waf"]}</span>' if r.get("waf") else ""
            screenshot_tag = ""
            ss_path = Path(self.output_dir) / "live-subdomains-screenshots" / (re.sub(r"[^\w\-]", "_", r["subdomain"]) + ".png")
            if ss_path.exists():
                screenshot_tag = f'<a href="live-subdomains-screenshots/{ss_path.name}" target="_blank"><img src="live-subdomains-screenshots/{ss_path.name}" style="max-width:120px;border-radius:4px;cursor:pointer"></a>'
            live_rows += f"""
            <tr>
              <td><a href="{r['url']}" target="_blank">{r['subdomain']}</a></td>
              <td><span class="status-{r['status_code']}">{r['status_code']}</span></td>
              <td>{r['title']}</td>
              <td>{r['server']}</td>
              <td>{r['content_length']}</td>
              <td>{cloud_badge}{waf_badge}{takeover_badge}</td>
              <td>{screenshot_tag}</td>
            </tr>"""

        dead_rows = ""
        for r in dead_results:
            dead_rows += f"""
            <tr>
              <td>{r['subdomain']}</td>
              <td>{r.get('url','')}</td>
              <td><span class="status-dead">{r.get('status_code','N/A')}</span></td>
              <td>{r.get('error','')}</td>
            </tr>"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SubHunterX Report — {domain}</title>
<style>
  :root {{
    --bg: #0d1117; --bg2: #161b22; --bg3: #21262d;
    --green: #3fb950; --red: #f85149; --yellow: #d29922;
    --blue: #58a6ff; --purple: #bc8cff; --text: #c9d1d9;
    --border: #30363d;
  }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:var(--bg); color:var(--text); font-family:'Segoe UI',monospace; }}
  header {{ background: linear-gradient(135deg,#0d1117 0%,#161b22 100%);
            border-bottom:1px solid var(--border); padding:2rem; text-align:center; }}
  header h1 {{ font-size:2.5rem; color:var(--green); letter-spacing:3px; }}
  header p {{ color:#8b949e; margin-top:.5rem; }}
  .stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
            gap:1rem; padding:2rem; }}
  .stat-card {{ background:var(--bg2); border:1px solid var(--border); border-radius:8px;
               padding:1.5rem; text-align:center; }}
  .stat-card .num {{ font-size:2.5rem; font-weight:700; }}
  .stat-card .lbl {{ color:#8b949e; font-size:.85rem; margin-top:.25rem; }}
  .green {{ color:var(--green); }} .red {{ color:var(--red); }}
  .blue {{ color:var(--blue); }} .purple {{ color:var(--purple); }}
  .yellow {{ color:var(--yellow); }}
  .section {{ padding:0 2rem 2rem; }}
  .section h2 {{ color:var(--blue); border-bottom:1px solid var(--border);
                padding-bottom:.5rem; margin-bottom:1rem; }}
  table {{ width:100%; border-collapse:collapse; background:var(--bg2);
          border-radius:8px; overflow:hidden; }}
  th {{ background:var(--bg3); color:var(--blue); padding:.75rem 1rem;
       text-align:left; font-size:.85rem; text-transform:uppercase; }}
  td {{ padding:.65rem 1rem; border-top:1px solid var(--border);
       font-size:.85rem; vertical-align:middle; }}
  tr:hover td {{ background:rgba(88,166,255,.05); }}
  .badge {{ padding:.2rem .6rem; border-radius:4px; font-size:.75rem; margin-right:.25rem; }}
  .badge-danger  {{ background:#3d1a1a; color:var(--red); }}
  .badge-info    {{ background:#1a2a3d; color:var(--blue); }}
  .badge-warning {{ background:#3d2e1a; color:var(--yellow); }}
  .status-200,.status-201,.status-204 {{ color:var(--green); font-weight:600; }}
  .status-301,.status-302,.status-307 {{ color:var(--yellow); font-weight:600; }}
  .status-403,.status-401 {{ color:var(--purple); font-weight:600; }}
  .status-404,.status-500,.status-dead {{ color:var(--red); font-weight:600; }}
  footer {{ text-align:center; padding:2rem; color:#8b949e; font-size:.8rem;
           border-top:1px solid var(--border); }}
</style>
</head>
<body>
<header>
  <h1>🔍 SubHunterX</h1>
  <p>Subdomain Enumeration Report for <strong style="color:var(--blue)">{domain}</strong></p>
  <p style="margin-top:.25rem;font-size:.85rem">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
</header>

<div class="stats">
  <div class="stat-card"><div class="num green">{stats['total']}</div><div class="lbl">Total Subdomains</div></div>
  <div class="stat-card"><div class="num green">{stats['live']}</div><div class="lbl">Live Subdomains</div></div>
  <div class="stat-card"><div class="num red">{stats['dead']}</div><div class="lbl">Dead Subdomains</div></div>
  <div class="stat-card"><div class="num yellow">{stats['takeovers']}</div><div class="lbl">Takeover Risks</div></div>
  <div class="stat-card"><div class="num blue">{stats['cloud']}</div><div class="lbl">Cloud Assets</div></div>
  <div class="stat-card"><div class="num purple">{stats['sources']}</div><div class="lbl">Sources Used</div></div>
</div>

<div class="section">
  <h2>✅ Live Subdomains ({stats['live']})</h2>
  <table>
    <thead><tr>
      <th>Subdomain</th><th>Status</th><th>Title</th>
      <th>Server</th><th>Size</th><th>Flags</th><th>Screenshot</th>
    </tr></thead>
    <tbody>{live_rows}</tbody>
  </table>
</div>

<div class="section">
  <h2>❌ Dead Subdomains ({stats['dead']})</h2>
  <table>
    <thead><tr>
      <th>Subdomain</th><th>URL Tried</th><th>Status</th><th>Error</th>
    </tr></thead>
    <tbody>{dead_rows}</tbody>
  </table>
</div>

<footer>SubHunterX v{VERSION} — by {AUTHOR} — {GITHUB}</footer>
</body>
</html>"""

        html_path = self.output_dir / "report.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        return html_path

    def generate_csv(self, results, filename):
        path = self.output_dir / filename
        if not results:
            return path
        keys = ["subdomain", "url", "status_code", "title", "server",
                "content_length", "waf", "cloud", "takeover_risk", "error"]
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(results)
        return path

    def generate_json(self, data, filename):
        path = self.output_dir / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return path


# ──────────────────────────────────────────────────────────────────────────────
# MAIN SCANNER
# ──────────────────────────────────────────────────────────────────────────────
class SubHunterX:
    def __init__(self, args):
        self.args     = args
        self.cfg      = ConfigManager(args.config)
        self.proxies  = self._build_proxies()
        self.sources  = SubdomainSources(self.cfg, self.proxies)
        self.dns      = DNSAnalyzer(
            threads=self.cfg.get("settings", "threads", default=100),
            timeout=self.cfg.get("settings", "timeout", default=3),
        )
        self.prober   = HTTPProber(threads=50, timeout=10, proxies=self.proxies)
        self.notifier = Notifier(self.cfg)

    def _build_proxies(self):
        proxy_url = self.cfg.get("settings", "proxy")
        use_tor   = self.cfg.get("settings", "use_tor")
        if use_tor:
            return {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}
        if proxy_url:
            return {"http": proxy_url, "https": proxy_url}
        return {}

    def _make_output_dir(self, domain):
        safe = re.sub(r"[^\w\-]", "_", domain)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = Path(f"output/{safe}_{ts}")
        out.mkdir(parents=True, exist_ok=True)
        return out

    def print_banner(self):
        console.print(f"[bold green]{BANNER}[/bold green]")
        console.print(Panel.fit(
            f"[bold cyan]v{VERSION}[/bold cyan]  ·  "
            f"[yellow]by {AUTHOR}[/yellow]  ·  "
            f"[blue]{GITHUB}[/blue]",
            border_style="green"
        ))
        console.print()

    def scan_domain(self, domain):
        domain = domain.strip().lower()
        if domain.startswith("http"):
            domain = urlparse(domain).netloc

        out_dir = self._make_output_dir(domain)
        chk     = Checkpoint(domain, out_dir)
        report  = ReportGenerator(out_dir)
        ss_eng  = ScreenshotEngine(out_dir, timeout=self.cfg.get("settings", "screenshot_timeout", default=15))

        console.print(Rule(f"[bold cyan]🎯 Target: {domain}[/bold cyan]"))

        # ── Wildcard check ───────────────────────────────────────────────────
        console.print("[dim]Checking for wildcard DNS...[/dim]")
        wildcard = self.dns.detect_wildcard(domain)
        if wildcard:
            console.print("[yellow]⚠️  Wildcard DNS detected — false positives possible![/yellow]")
        else:
            console.print("[green]✅ No wildcard DNS detected[/green]")

        # ── Source enumeration ────────────────────────────────────────────────
        all_subs = set(chk.data.get("subdomains", []))
        sources  = self.sources.get_all_sources()

        console.print(f"\n[bold]📡 Querying {len(sources)} sources...[/bold]")

        with Progress(
            SpinnerColumn(style="green"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=30, style="green", complete_style="bright_green"),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Enumerating...", total=len(sources))
            for name, func in sources:
                if chk.is_done(name):
                    progress.advance(task)
                    continue
                progress.update(task, description=f"[cyan]{name:<22}")
                try:
                    found = func(domain)
                    new   = found - all_subs
                    all_subs |= found
                    chk.mark_source(name)
                    chk.add_subdomains(list(found))
                    if new:
                        progress.print(f"  [green]+{len(new):>4}[/green] [dim]{name}[/dim]")
                except Exception as e:
                    progress.print(f"  [red]ERR[/red] [dim]{name}[/dim]: {e}")
                progress.advance(task)

        # ── DNS Bruteforce ────────────────────────────────────────────────────
        wordlist = self.cfg.get("settings", "wordlist", default="wordlists/subdomains.txt")
        if self.cfg.get("settings", "brute_force") and Path(wordlist).exists():
            console.print(f"\n[bold]🔨 DNS Brute Force (wordlist: {wordlist})...[/bold]")
            bf_subs = self.sources.dns_bruteforce(domain, wordlist)
            new_bf  = bf_subs - all_subs
            all_subs |= bf_subs
            console.print(f"[green]  +{len(new_bf)} new subdomains from brute force[/green]")

        # ── Recursive ────────────────────────────────────────────────────────
        if self.cfg.get("settings", "recursive") or self.args.recursive:
            depth = self.cfg.get("settings", "recursive_depth", default=2)
            console.print(f"\n[bold]🔁 Recursive enumeration (depth={depth})...[/bold]")
            for _ in range(depth - 1):
                new_targets = {s for s in all_subs if s.endswith(domain) and s.count(".") > domain.count(".") + 1}
                for sub in new_targets:
                    for _, func in self.sources.get_all_sources()[:10]:  # top sources only
                        try:
                            all_subs |= func(sub)
                        except Exception:
                            pass

        # ── Dedup & save all ─────────────────────────────────────────────────
        all_subs = {s for s in all_subs if s.endswith(domain)}
        all_path = out_dir / "all-subdomains.txt"
        with open(all_path, "w") as f:
            f.write("\n".join(sorted(all_subs)))

        console.print(f"\n[bold green]📋 Total unique subdomains: {len(all_subs)}[/bold green]")

        # ── DNS Resolution ────────────────────────────────────────────────────
        console.print(f"\n[bold]🔍 Resolving DNS for {len(all_subs)} subdomains...[/bold]")
        dns_results = self.dns.resolve_all(all_subs)

        # ── HTTP Probing ──────────────────────────────────────────────────────
        console.print(f"\n[bold]🌐 HTTP Probing {len(all_subs)} subdomains...[/bold]")
        with Progress(SpinnerColumn(style="blue"),
                      TextColumn("[progress.description]{task.description}"),
                      BarColumn(bar_width=30, style="blue", complete_style="bright_blue"),
                      TaskProgressColumn(), TimeRemainingColumn(), console=console) as progress:
            task = progress.add_task("[blue]Probing HTTP...", total=len(all_subs))
            http_results = []
            with ThreadPoolExecutor(max_workers=50) as ex:
                futures = {ex.submit(self.prober.probe, s): s for s in all_subs}
                for fut in as_completed(futures):
                    http_results.append(fut.result())
                    progress.advance(task)

        live_results = [r for r in http_results if r["alive"]]
        dead_results = [r for r in http_results if not r["alive"]]

        # ── Save live / dead ──────────────────────────────────────────────────
        live_path = out_dir / "live-subdomains.txt"
        dead_path = out_dir / "dead-subdomains.txt"
        dead_detail_path = out_dir / "dead-subdomains-details.txt"

        with open(live_path, "w") as f:
            f.write("\n".join(sorted(r["subdomain"] for r in live_results)))

        with open(dead_path, "w") as f:
            f.write("\n".join(sorted(r["subdomain"] for r in dead_results)))

        with open(dead_detail_path, "w") as f:
            f.write(f"{'Subdomain':<50} {'URL':<60} {'Status':<10} {'Error'}\n")
            f.write("-" * 150 + "\n")
            for r in sorted(dead_results, key=lambda x: x["subdomain"]):
                f.write(f"{r['subdomain']:<50} {r.get('url',''):<60} {str(r.get('status_code','N/A')):<10} {r.get('error','')}\n")

        # ── Screenshots ───────────────────────────────────────────────────────
        if self.cfg.get("settings", "screenshot") and live_results:
            console.print(f"\n[bold]📸 Taking screenshots of {len(live_results)} live subdomains...[/bold]")
            with Progress(SpinnerColumn(style="magenta"),
                          TextColumn("[progress.description]{task.description}"),
                          BarColumn(bar_width=30, style="magenta", complete_style="bright_magenta"),
                          TaskProgressColumn(), console=console) as progress:
                task = progress.add_task("[magenta]Screenshots...", total=len(live_results))
                for r in live_results:
                    ss_eng.take(r["url"], r["subdomain"])
                    progress.advance(task)
            ss_eng.close()

        # ── CNAME chain analysis ──────────────────────────────────────────────
        cname_risks = []
        for sub, dns_data in dns_results.items():
            chain = dns_data.get("cnames", [])
            if chain:
                for provider, pattern in CLOUD_PATTERNS.items():
                    for cname in chain:
                        if re.search(pattern, cname, re.IGNORECASE):
                            cname_risks.append({
                                "subdomain": sub,
                                "cname": cname,
                                "provider": provider
                            })

        # ── Export JSON / CSV ─────────────────────────────────────────────────
        report.generate_json({"domain": domain, "scan_date": str(datetime.now()),
                               "live": live_results, "dead": dead_results,
                               "cname_risks": cname_risks}, "results.json")
        report.generate_csv(live_results, "live-subdomains.csv")
        report.generate_csv(dead_results, "dead-subdomains.csv")

        # ── HTML Report ───────────────────────────────────────────────────────
        takeover_count = sum(1 for r in live_results if r.get("takeover_risk"))
        cloud_count    = sum(1 for r in live_results if r.get("cloud"))
        stats = {
            "total": len(all_subs),
            "live": len(live_results),
            "dead": len(dead_results),
            "takeovers": takeover_count,
            "cloud": cloud_count,
            "sources": len(self.sources.get_all_sources()),
        }
        html_path = report.generate_html(domain, live_results, dead_results, stats)

        # ── Notifications ─────────────────────────────────────────────────────
        self.notifier.send(
            f"🔍 SubHunterX scan complete for *{domain}*\n"
            f"• Total: {len(all_subs)}\n"
            f"• Live: {len(live_results)}\n"
            f"• Dead: {len(dead_results)}\n"
            f"• Takeover risks: {takeover_count}\n"
            f"• Cloud assets: {cloud_count}"
        )

        # ── Checkpoint clear ──────────────────────────────────────────────────
        chk.clear()

        # ── Summary table ─────────────────────────────────────────────────────
        console.print()
        console.print(Rule("[bold green]✅ Scan Complete[/bold green]"))
        table = Table(title=f"Results for {domain}", box=box.ROUNDED,
                      border_style="green", header_style="bold cyan")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="bold white")
        table.add_row("🎯 Total Subdomains",    str(len(all_subs)))
        table.add_row("✅ Live",                f"[green]{len(live_results)}[/green]")
        table.add_row("❌ Dead",                f"[red]{len(dead_results)}[/red]")
        table.add_row("⚠️  Takeover Risks",     f"[yellow]{takeover_count}[/yellow]")
        table.add_row("☁️  Cloud Assets",       f"[blue]{cloud_count}[/blue]")
        table.add_row("🔗 CNAME Risks",         str(len(cname_risks)))
        table.add_row("📁 Output Directory",    str(out_dir))
        table.add_row("📊 HTML Report",         str(html_path))
        console.print(table)

        return stats

    def run(self):
        self.print_banner()

        # Collect targets
        targets = []
        if self.args.domain:
            targets = [self.args.domain]
        elif self.args.list:
            with open(self.args.list) as f:
                targets = [l.strip() for l in f if l.strip() and not l.startswith("#")]

        if not targets:
            console.print("[red]❌ No targets specified. Use -d or -l.[/red]")
            sys.exit(1)

        console.print(f"[bold cyan]🚀 Scanning {len(targets)} domain(s)...[/bold cyan]\n")

        for domain in targets:
            try:
                self.scan_domain(domain)
            except KeyboardInterrupt:
                console.print("\n[yellow]⏸  Scan paused — checkpoint saved. Resume with same command.[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]❌ Error scanning {domain}: {e}[/red]")


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────
def main():
    import urllib3
    urllib3.disable_warnings()

    parser = argparse.ArgumentParser(
        description="SubHunterX — Ultimate Subdomain Enumeration Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python subhunterx.py -d example.com
  python subhunterx.py -l domains.txt
  python subhunterx.py -d example.com --recursive
  python subhunterx.py -d example.com --proxy http://127.0.0.1:8080
  python subhunterx.py -d example.com --tor
  python subhunterx.py -d example.com --no-screenshot
        """
    )
    parser.add_argument("-d", "--domain",       help="Single target domain")
    parser.add_argument("-l", "--list",         help="File containing list of domains")
    parser.add_argument("-c", "--config",       default="config/config.yaml", help="Config file path")
    parser.add_argument("--recursive",          action="store_true", help="Enable recursive enumeration")
    parser.add_argument("--proxy",              help="Proxy URL (e.g. http://127.0.0.1:8080)")
    parser.add_argument("--tor",                action="store_true", help="Route through TOR")
    parser.add_argument("--no-screenshot",      action="store_true", help="Disable screenshots")
    parser.add_argument("--no-brute",           action="store_true", help="Disable DNS brute force")
    parser.add_argument("--wordlist",           help="Custom wordlist for brute force")
    parser.add_argument("--threads",            type=int, default=100, help="Thread count (default: 100)")
    parser.add_argument("--timeout",            type=int, default=10, help="Request timeout (default: 10s)")
    parser.add_argument("-v", "--version",      action="version", version=f"SubHunterX v{VERSION}")
    args = parser.parse_args()

    scanner = SubHunterX(args)
    scanner.run()


if __name__ == "__main__":
    main()
