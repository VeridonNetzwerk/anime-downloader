<div align="center">

# 📺 Anime Downloader

**Download any anime available on AniWorld & AniWatch — Subbed & Dubbed ;)**

<p>
  <a href="https://github.com/VeridonNetzwerk/anime-downloader/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/VeridonNetzwerk/anime-downloader?style=flat-square" alt="License: MIT">
  </a>
  <a href="https://github.com/VeridonNetzwerk/anime-downloader/issues">
    <img src="https://img.shields.io/github/issues/VeridonNetzwerk/anime-downloader?style=flat-square" alt="Open Issues">
  </a>
  <a href="https://github.com/VeridonNetzwerk/anime-downloader/stargazers">
    <img src="https://img.shields.io/github/stars/VeridonNetzwerk/anime-downloader?style=flat-square" alt="Stars">
  </a>
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blue?style=flat-square" alt="Platform: Windows, Linux, macOS">
  <img src="https://img.shields.io/badge/Node.js-24.x-339933?style=flat-square&logo=node.js&logoColor=white" alt="Node.js 24.x">
  <img src="https://img.shields.io/badge/Python-3.13.x-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.13.x">
</p>

<p>
  <a href="https://www.paypal.com/donate/?hosted_button_id=972P9WTWE7RBU">
    <img src="https://img.shields.io/badge/Donate-PayPal-0070ba?style=for-the-badge&logo=paypal&logoColor=white" alt="Donate via PayPal">
  </a>
</p>

> ⚠️ **Disclaimer:** This tool is intended for **private use only**.
> It is not affiliated with, sponsored by, or associated with AniWorld, AniWatch, or their operators.
> Use may violate a platform's Terms of Service and could be illegal in your country.
> **You are solely responsible for your use of this software.**

</div>

---

## 🛠️ Requirements

| Component | Version | Notes |
|-----------|---------|-------|
| OS | Windows 10/11, Linux, macOS | Python launcher supports all three |
| Node.js | 24.x (LTS) | For AniWatch API + download server |
| Python | **3.13.x** recommended | 3.14+ breaks `curses` on Windows |
| FFmpeg | Latest | Required for native video download/merge |

---

## 🚀 Quick Start

1. Download the **[latest Release](https://github.com/VeridonNetzwerk/anime-downloader/releases)** (start-anime-downloader.zip)
2. Start the Programm:

```bash
python start-anime-downloader.py
```

3. On first run, select **`4` → Install / Repair**. The script detects your OS and runs the matching setup flow automatically.
4. Once done, pick your mode:

| Option | Action | URL |
|--------|--------|-----|
| `1` | AniWorld Downloader | http://localhost:8080 |
| `2` | AniWatch Downloader | http://localhost:4001 |
| `3` | Start both | http://localhost:8080 + :4001 |
| `4` | Install / Repair (all downloaders) | (Run this on first run!) |
| `5` | Exit | — |

If you have problems with the installation, feel free to check out the **[Installation Page](https://github.com/VeridonNetzwerk/anime-downloader/wiki/Installation)** in the Github Wiki.

---

## 🙏 Attribution

This project builds on the work of:

| Project | Author |
|---------|--------|
| [aniwatch-dl](https://github.com/ruxartic/aniwatch-dl) | ruxartic |
| [nodejs/installer](https://github.com/nodejs/installer) | Node.js team |
| [AniWorld-Downloader](https://github.com/phoenixthrush/AniWorld-Downloader) | phoenixthrush |

---

## 📺 Download Sources

Content can be searched and downloaded from these sites with the Downloaders:

| Site | Best suited for | URL |
|------|-----------------|-----|
| AniWorld | German Sub / Dub | https://aniworld.to |
| AniWatch | English Sub / Dub | https://aniwatchtv.to |

If you mainly want German audio or subtitles, start with AniWorld.
If you mainly want English audio or subtitles, start with AniWatch.

---

## 📖 Wiki

Full documentation is available in the **[GitHub Wiki](https://github.com/VeridonNetzwerk/anime-downloader/wiki)**:

| Page | Description |
|------|-------------|
| [Home](https://github.com/VeridonNetzwerk/anime-downloader/wiki/Home) | Overview and navigation |
| [Installation](https://github.com/VeridonNetzwerk/anime-downloader/wiki/Installation) | Step-by-step first-time setup |
| [Usage Guide](https://github.com/VeridonNetzwerk/anime-downloader/wiki/Usage-Guide) | Menu reference, ports, log files |
| [How It Works](https://github.com/VeridonNetzwerk/anime-downloader/wiki/How-It-Works) | Architecture and component overview |
| [Troubleshooting](https://github.com/VeridonNetzwerk/anime-downloader/wiki/Troubleshooting) | Common errors and fixes |
| [FAQ](https://github.com/VeridonNetzwerk/anime-downloader/wiki/FAQ) | Frequently asked questions |

---

## 🐛 Reporting Issues

Found a bug? Open an [**Issue**](https://github.com/VeridonNetzwerk/anime-downloader/issues/new/choose) and include:

- Which menu option you used (`1` / `2` / `3` / `4`)
- What you expected vs. what actually happened
- The relevant section of `latest.log`
- Your Windows, Node.js, and Python versions

An issue template is pre-filled at `.github/ISSUE_TEMPLATE/bug_report.md`.

---

## 💖 Support

If you like this project, consider Donating: 

<a href="https://www.paypal.com/donate/?hosted_button_id=972P9WTWE7RBU">
  <img src="https://img.shields.io/badge/Donate-PayPal-0070ba?style=for-the-badge&logo=paypal&logoColor=white" alt="Donate via PayPal">
</a>

---

## ⚖️ Legal Disclaimer

This project is provided **as-is** for educational and personal use only.
The author is not responsible for illegal use, copyright infringement, or any misuse of this software.
Users are solely responsible for compliance with local laws, copyright regulations, and platform terms of service.

---

## 🤖 Built With AI

Parts of this project were created and refined with the assistance of AI tools.

---

<div align="center">
  <sub>MIT License · © 2026 VeridonNetzwerk</sub>
</div>
