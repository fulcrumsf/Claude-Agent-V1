---
title: System Map
type: install-map
tags: [system-map, install-map, tools, assets]
---

# System Map

> **Auto-generated:** 2026-07-04 18:44  
> Do not edit manually. Refresh by running:
> `python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/generate_system_map.py`

**When Tony says 'look at the system map' — this is that file.**

### ⚠️ Manual Environment Customizations
- **Antigravity (VS Code fork):** We manually patched `/Applications/Antigravity.app/Contents/Resources/app/out/vs/code/electron-browser/workbench/workbench.html` to load custom CSS for explorer row colors. **Note:** This causes Antigravity to display a "Your Antigravity installation appears to be corrupt. Please reinstall." warning. This is expected behavior when modifying core files and can be ignored or reverted later.

---

## Table of Contents
1. [Installed Applications](#1-installed-applications)
2. [Homebrew — Formulae & Casks](#2-homebrew--formulae--casks)
3. [Python Installs & Virtual Environments](#3-python-installs--virtual-environments)
4. [Docker](#4-docker)
5. [MCP Servers](#5-mcp-servers)
6. [CLIs](#6-clis)
7. [Python Scripts](#7-python-scripts)
8. [Claude Code Skills](#8-claude-code-skills)
9. [Adobe & Creative App Plugins](#9-adobe--creative-app-plugins)
10. [Node.js Global Packages](#10-nodejs-global-packages)

---

## 1. Installed Applications

| App | Version | Path |
|---|---|---|
| 1Password | 8.12.24 | `/Applications/1Password.app` |
| 1Password Browser Helper | 8.12.24 | `/Applications/1Password.app/Contents/Library/LoginItems/1Password Browser Helper.app` |
| 1Password Launcher | 1.0 | `/Applications/1Password.app/Contents/Library/LoginItems/1Password Launcher.app` |
| 1Password Updater | 8.12.24 | `/Applications/1Password.app/Contents/XPCServices/OP Updater Service.xpc/Contents/Helpers/1Password Updater.app` |
| Acrobat | 26.001.21691 | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app` |
| Acrobat | 26.001.21691 | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Helpers/Adobe Acrobat Helper.app` |
| Acrobat Uninstaller | Acrobat Uninstaller version | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Helpers/Acrobat Uninstaller.app` |
| AcroCEF | — | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Helpers/AcroCEF/AcroCEF.app` |
| AcroCEF Helper | — | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Frameworks/AcroCEF Helper.app` |
| AcroCEF Helper (GPU) | — | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Frameworks/AcroCEF Helper (GPU).app` |
| AcroCEF Helper (Renderer) | — | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Frameworks/AcroCEF Helper (Renderer).app` |
| Adobe Analysis Server | 26.3.0 | `/Applications/Adobe After Effects 2026/Adobe After Effects 2026.app/Contents/Adobe Analysis Server.app` |
| Adobe Audition 2026 | 26.3.0 | `/Applications/Adobe Audition 2026/Adobe Audition 2026.app` |
| Adobe Crash Processor | 26.10.0 | `/Applications/Adobe Acrobat DC/Acrobat Distiller.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Processor.app` |
| Adobe Crash Processor | 26.10.0 | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Frameworks/AcroCEF Helper (GPU).app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Processor.app` |
| Adobe Crash Processor | 26.10.0 | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Frameworks/AcroCEF Helper (Renderer).app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Processor.app` |
| Adobe Crash Processor | 26.10.0 | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Frameworks/AcroCEF Helper.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Processor.app` |
| Adobe Crash Processor | 26.10.0 | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Processor.app` |
| Adobe Crash Processor | 26.10.0 | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Helpers/AcroCEF/AcroCEF.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Processor.app` |
| Adobe Crash Processor | 26.10.0 | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Helpers/AdobeResourceSynchronizer.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Processor.app` |
| Adobe Crash Processor | 29.11.0 | `/Applications/Adobe Illustrator 2026/Adobe Illustrator.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Processor.app` |
| Adobe Crash Processor | 29.5.0 | `/Applications/Adobe InDesign 2026/Adobe InDesign 2026.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Processor.app` |
| Adobe Crash Processor | 29.5.0 | `/Applications/Adobe Lightroom CC/Adobe Lightroom.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Processor.app` |
| Adobe Crash Processor | 29.5.0 | `/Applications/Adobe Lightroom Classic/Adobe Lightroom Classic.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Processor.app` |
| Adobe Crash Processor | 26.5.0 | `/Applications/Adobe Photoshop 2026/Adobe Photoshop 2026.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Processor.app` |
| Adobe Crash Processor | 26.8.0 | `/Applications/Utilities/Adobe Creative Cloud/ACC/Creative Cloud Helper.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Processor.app` |
| Adobe Crash Processor | 26.8.0 | `/Applications/Utilities/Adobe Creative Cloud/ACC/Creative Cloud.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Processor.app` |
| Adobe Crash Processor | 26.8.0 | `/Applications/Utilities/Adobe Creative Cloud/ACC/Creative Cloud.app/Contents/Frameworks/Creative Cloud UI Helper (GPU).app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Processor.app` |
| Adobe Crash Processor | 26.8.0 | `/Applications/Utilities/Adobe Creative Cloud/ACC/Creative Cloud.app/Contents/Frameworks/Creative Cloud UI Helper (Renderer).app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Processor.app` |
| Adobe Crash Processor | 26.8.0 | `/Applications/Utilities/Adobe Creative Cloud/ACC/Creative Cloud.app/Contents/Frameworks/Creative Cloud UI Helper.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Processor.app` |
| Adobe Crash Processor | 26.8.0 | `/Applications/Utilities/Adobe Sync/CoreSync/Core Sync.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Processor.app` |
| Adobe Crash Reporter | — | `/Applications/Adobe After Effects 2026/Adobe After Effects 2026.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Reporter.app` |
| Adobe Crash Reporter | — | `/Applications/Adobe Audition 2026/Adobe Audition 2026.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Reporter.app` |
| Adobe Crash Reporter | — | `/Applications/Adobe Media Encoder (Beta)/Adobe Media Encoder (Beta).app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Reporter.app` |
| Adobe Crash Reporter | — | `/Applications/Adobe Media Encoder 2026/Adobe Media Encoder 2026.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Reporter.app` |
| Adobe Crash Reporter | — | `/Applications/Adobe Premiere Pro (Beta)/Adobe Premiere Pro (Beta).app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Reporter.app` |
| Adobe Crash Reporter | — | `/Applications/Adobe Premiere Pro 2026/Adobe Premiere Pro 2026.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Reporter.app` |
| Adobe Creative Cloud Diagnostics | 1.4.0.15 | `/Applications/Utilities/Adobe Creative Cloud/Diagnostics/Adobe Creative Cloud Diagnostics.app` |
| Adobe Genuine Software Integrity Service  | 9.1.0.50 | `/Applications/Utilities/Adobe Genuine Service/AdobeGCClient.app` |
| Adobe Lightroom | 9.4.1 | `/Applications/Adobe Lightroom CC/Adobe Lightroom.app` |
| Adobe Lightroom Classic | 15.4.1 | `/Applications/Adobe Lightroom Classic/Adobe Lightroom Classic.app` |
| Adobe Lightroom Helper | 1.0 | `/Applications/Adobe Lightroom Classic/Adobe Lightroom Classic.app/Contents/Frameworks/Adobe Lightroom Helper.app` |
| Adobe Lightroom Helper (GPU) | 1.0 | `/Applications/Adobe Lightroom Classic/Adobe Lightroom Classic.app/Contents/Frameworks/Adobe Lightroom Helper (GPU).app` |
| Adobe Lightroom Helper (Plugin) | 1.0 | `/Applications/Adobe Lightroom Classic/Adobe Lightroom Classic.app/Contents/Frameworks/Adobe Lightroom Helper (Plugin).app` |
| Adobe Lightroom Helper (Renderer) | 1.0 | `/Applications/Adobe Lightroom Classic/Adobe Lightroom Classic.app/Contents/Frameworks/Adobe Lightroom Helper (Renderer).app` |
| Adobe UXP Developer Tools | 2.2.1 | `/Applications/Adobe UXP Developer Tools/Adobe UXP Developer Tools.app` |
| Adobe UXP Developer Tools | 2.2.1 | `/Applications/Adobe UXP Developer Tools/Adobe UXP Developer Tools.app/Contents/Resources/app.asar.unpacked/node_modules/@adobe/uxp-inspect-frontend/dist/mac/Adobe UXP Developer Tools.app` |
| Adobe_Acrobat_Diagnostics | 1.6.1 | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Helpers/Adobe_Acrobat_Diagnostics.app` |
| AdobeCleanUpUtility | 9.1.0.50 | `/Applications/Utilities/Adobe Genuine Service/AdobeCleanUpUtility.app` |
| AdobeCrashReport | 26.3.0 | `/Applications/Adobe After Effects 2026/Adobe After Effects 2026.app/Contents/AdobeCrashReport.app` |
| AdobeCrashReport | 26.3.0 | `/Applications/Adobe Audition 2026/Adobe Audition 2026.app/Contents/AdobeCrashReport.app` |
| AdobeCrashReport | 26.5.0 | `/Applications/Adobe Media Encoder (Beta)/Adobe Media Encoder (Beta).app/Contents/AdobeCrashReport.app` |
| AdobeCrashReport | 26.3.1 | `/Applications/Adobe Media Encoder 2026/Adobe Media Encoder 2026.app/Contents/AdobeCrashReport.app` |
| AdobeCrashReport | 22.4.0 | `/Applications/Adobe Photoshop 2026/Adobe Photoshop 2026.app/Contents/AdobeCrashReport.app` |
| AdobeCrashReport | 26.5.0 | `/Applications/Adobe Premiere Pro (Beta)/Adobe Premiere Pro (Beta).app/Contents/AdobeCrashReport.app` |
| AdobeCrashReport | 26.3.0 | `/Applications/Adobe Premiere Pro 2026/Adobe Premiere Pro 2026.app/Contents/AdobeCrashReport.app` |
| AdobeCrashReporter | 26.10.0 | `/Applications/Adobe Acrobat DC/Acrobat Distiller.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Reporter.app` |
| AdobeCrashReporter | 26.10.0 | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Frameworks/AcroCEF Helper (GPU).app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Reporter.app` |
| AdobeCrashReporter | 26.10.0 | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Frameworks/AcroCEF Helper (Renderer).app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Reporter.app` |
| AdobeCrashReporter | 26.10.0 | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Frameworks/AcroCEF Helper.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Reporter.app` |
| AdobeCrashReporter | 26.10.0 | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Reporter.app` |
| AdobeCrashReporter | 26.10.0 | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Helpers/AcroCEF/AcroCEF.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Reporter.app` |
| AdobeCrashReporter | 26.10.0 | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Helpers/AdobeResourceSynchronizer.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Reporter.app` |
| AdobeCrashReporter | 29.11.0 | `/Applications/Adobe Illustrator 2026/Adobe Illustrator.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Reporter.app` |
| AdobeCrashReporter | 29.5.0 | `/Applications/Adobe InDesign 2026/Adobe InDesign 2026.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Reporter.app` |
| AdobeCrashReporter | 29.5.0 | `/Applications/Adobe Lightroom CC/Adobe Lightroom.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Reporter.app` |
| AdobeCrashReporter | 29.5.0 | `/Applications/Adobe Lightroom Classic/Adobe Lightroom Classic.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Reporter.app` |
| AdobeCrashReporter | 26.5.0 | `/Applications/Adobe Photoshop 2026/Adobe Photoshop 2026.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Reporter.app` |
| AdobeCrashReporter | 26.8.0 | `/Applications/Utilities/Adobe Creative Cloud/ACC/Creative Cloud Helper.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Reporter.app` |
| AdobeCrashReporter | 26.8.0 | `/Applications/Utilities/Adobe Creative Cloud/ACC/Creative Cloud.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Reporter.app` |
| AdobeCrashReporter | 26.8.0 | `/Applications/Utilities/Adobe Creative Cloud/ACC/Creative Cloud.app/Contents/Frameworks/Creative Cloud UI Helper (GPU).app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Reporter.app` |
| AdobeCrashReporter | 26.8.0 | `/Applications/Utilities/Adobe Creative Cloud/ACC/Creative Cloud.app/Contents/Frameworks/Creative Cloud UI Helper (Renderer).app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Reporter.app` |
| AdobeCrashReporter | 26.8.0 | `/Applications/Utilities/Adobe Creative Cloud/ACC/Creative Cloud.app/Contents/Frameworks/Creative Cloud UI Helper.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Reporter.app` |
| AdobeCrashReporter | 26.8.0 | `/Applications/Utilities/Adobe Sync/CoreSync/Core Sync.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/Adobe Crash Reporter.app` |
| AdobeCRDaemon | — | `/Applications/Adobe After Effects 2026/Adobe After Effects 2026.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/AdobeCRDaemon.app` |
| AdobeCRDaemon | — | `/Applications/Adobe Audition 2026/Adobe Audition 2026.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/AdobeCRDaemon.app` |
| AdobeCRDaemon | — | `/Applications/Adobe Media Encoder (Beta)/Adobe Media Encoder (Beta).app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/AdobeCRDaemon.app` |
| AdobeCRDaemon | — | `/Applications/Adobe Media Encoder 2026/Adobe Media Encoder 2026.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/AdobeCRDaemon.app` |
| AdobeCRDaemon | — | `/Applications/Adobe Premiere Pro (Beta)/Adobe Premiere Pro (Beta).app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/AdobeCRDaemon.app` |
| AdobeCRDaemon | — | `/Applications/Adobe Premiere Pro 2026/Adobe Premiere Pro 2026.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/AdobeCRDaemon.app` |
| AdobeResourceSynchronizer | 26.001.21691 | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Helpers/AdobeResourceSynchronizer.app` |
| aerendercore | 25.2 | `/Applications/Adobe After Effects 2026/Adobe After Effects 2026.app/Contents/aerendercore.app` |
| aeselflink | 25.2 | `/Applications/Adobe After Effects 2026/Adobe After Effects 2026.app/Contents/aeselflink.app` |
| After Effects | 26.3.0 | `/Applications/Adobe After Effects 2026/Adobe After Effects 2026.app` |
| After Effects Render Engine | 26.3.0 | `/Applications/Adobe After Effects 2026/Adobe After Effects Render Engine 2026.app` |
| AIMonitor | AIMonitor version 30.6.0 | `/Applications/Adobe Illustrator 2026/Adobe Illustrator.app/Contents/MacOS/AIMonitor.app` |
| airhost | 7.0.5 (81138) | `/Applications/zoom.us.app/Contents/Frameworks/airhost.app` |
| AIRobin | 30.6.0 | `/Applications/Adobe Illustrator 2026/Adobe Illustrator.app/Contents/MacOS/AIRobin.app` |
| AISafeModeLauncher | AISafeModeLauncher version 30.6.0 | `/Applications/Adobe Illustrator 2026/Adobe Illustrator.app/Contents/MacOS/AISafeModeLauncher.app` |
| AISniffer | AISniffer version 30.6.0 | `/Applications/Adobe Illustrator 2026/Adobe Illustrator.app/Contents/MacOS/AISniffer.app` |
| ame_webservice_console | 26.5.0 | `/Applications/Adobe Media Encoder (Beta)/Adobe Media Encoder (Beta).app/Contents/ame_webservice_console.app` |
| ame_webservice_console | 26.3.1 | `/Applications/Adobe Media Encoder 2026/Adobe Media Encoder 2026.app/Contents/ame_webservice_console.app` |
| Antigravity | 2.0.10 | `/Applications/Antigravity.app` |
| Antigravity IDE | 2.1.1 | `/Applications/Antigravity IDE.app` |
| Antigravity IDE Helper | — | `/Applications/Antigravity IDE.app/Contents/Frameworks/Antigravity IDE Helper.app` |
| Antigravity IDE Helper (GPU) | — | `/Applications/Antigravity IDE.app/Contents/Frameworks/Antigravity IDE Helper (GPU).app` |
| Antigravity IDE Helper (Plugin) | — | `/Applications/Antigravity IDE.app/Contents/Frameworks/Antigravity IDE Helper (Plugin).app` |
| Antigravity IDE Helper (Renderer) | — | `/Applications/Antigravity IDE.app/Contents/Frameworks/Antigravity IDE Helper (Renderer).app` |
| aomhost | 7.0.5 (81138) | `/Applications/zoom.us.app/Contents/Frameworks/aomhost.app` |
| Arc | 1.117.0 | `/Applications/Arc.app` |
| Arc Helper | 141.0.7390.108 | `/Applications/Arc.app/Contents/Frameworks/ArcCore.framework/Versions/A/Helpers/Browser Helper.app` |
| Arc Helper | 143.0.7499.110 | `/Applications/Dia.app/Contents/Frameworks/ArcCore.framework/Versions/A/Helpers/Browser Helper.app` |
| Arc Helper (Alerts) | 141.0.7390.108 | `/Applications/Arc.app/Contents/Frameworks/ArcCore.framework/Versions/A/Helpers/Browser Helper (Alerts).app` |
| Arc Helper (Alerts) | 143.0.7499.110 | `/Applications/Dia.app/Contents/Frameworks/ArcCore.framework/Versions/A/Helpers/Browser Helper (Alerts).app` |
| Arc Helper (GPU) | 141.0.7390.108 | `/Applications/Arc.app/Contents/Frameworks/ArcCore.framework/Versions/A/Helpers/Browser Helper (GPU).app` |
| Arc Helper (GPU) | 143.0.7499.110 | `/Applications/Dia.app/Contents/Frameworks/ArcCore.framework/Versions/A/Helpers/Browser Helper (GPU).app` |
| Arc Helper (Plugin) | 141.0.7390.108 | `/Applications/Arc.app/Contents/Frameworks/ArcCore.framework/Versions/A/Helpers/Browser Helper (Plugin).app` |
| Arc Helper (Plugin) | 143.0.7499.110 | `/Applications/Dia.app/Contents/Frameworks/ArcCore.framework/Versions/A/Helpers/Browser Helper (Plugin).app` |
| Arc Helper (Renderer) | 141.0.7390.108 | `/Applications/Arc.app/Contents/Frameworks/ArcCore.framework/Versions/A/Helpers/Browser Helper (Renderer).app` |
| Arc Helper (Renderer) | 143.0.7499.110 | `/Applications/Dia.app/Contents/Frameworks/ArcCore.framework/Versions/A/Helpers/Browser Helper (Renderer).app` |
| Artlist Hub | 4.5.4 | `/Applications/Artlist Hub.app` |
| Assert | 1.0 | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Helpers/Assert.app` |
| Atlas | 149.0.7827.29 | `/Applications/ChatGPT Atlas.app/Contents/Support/ChatGPT Atlas.app` |
| Atlas | 149.0.7827.29 | `/Applications/ChatGPT Atlas.app/Contents/Support/ChatGPT Atlas.app/Contents/Frameworks/ChatGPT Atlas Framework.framework/Versions/149.0.7827.29/Helpers/ChatGPT Atlas (Alerts).app` |
| Atlas | 149.0.7827.29 | `/Applications/ChatGPT Atlas.app/Contents/Support/ChatGPT Atlas.app/Contents/Frameworks/ChatGPT Atlas Framework.framework/Versions/149.0.7827.29/Helpers/ChatGPT Atlas (GPU).app` |
| Atlas | 149.0.7827.29 | `/Applications/ChatGPT Atlas.app/Contents/Support/ChatGPT Atlas.app/Contents/Frameworks/ChatGPT Atlas Framework.framework/Versions/149.0.7827.29/Helpers/ChatGPT Atlas (Renderer).app` |
| Atlas | 149.0.7827.29 | `/Applications/ChatGPT Atlas.app/Contents/Support/ChatGPT Atlas.app/Contents/Frameworks/ChatGPT Atlas Framework.framework/Versions/149.0.7827.29/Helpers/ChatGPT Atlas (Service).app` |
| Audio Hijack | 4.5.5 | `/Applications/Audio Hijack.app` |
| Autoupdate | 1.26.0 | `/Applications/Audio Hijack.app/Contents/Frameworks/Protein.framework/Versions/A/Frameworks/Sparkle.framework/Versions/A/Resources/Autoupdate.app` |
| Autoupdate | 1.24.0 334-g8721f93 | `/Applications/Brave Browser.app/Contents/Frameworks/Brave Browser Framework.framework/Versions/145.1.87.192/Frameworks/Sparkle.framework/Versions/A/Resources/Autoupdate.app` |
| Autoupdate | 1.20.0 | `/Applications/Elmedia Player.app/Contents/Frameworks/Sparkle.framework/Versions/A/Resources/Autoupdate.app` |
| Blackmagic Proxy Generator Lite | 19.1.0 | `/Applications/Blackmagic Proxy Generator Lite.app` |
| Blackmagic RAW Player | 4.3 | `/Applications/Blackmagic RAW/Blackmagic RAW Player.app` |
| Blackmagic RAW Speed Test | 4.3 | `/Applications/Blackmagic RAW/Blackmagic RAW Speed Test.app` |
| BlockBlock | 2.2.2 | `/Applications/Object See/BlockBlock Installer.app/Contents/Resources/BlockBlock.app` |
| BlockBlock Helper | 2.2.2 | `/Applications/Object See/BlockBlock Installer.app/Contents/Resources/BlockBlock Helper.app` |
| BlockBlock Installer | 2.2.2 | `/Applications/Object See/BlockBlock Installer.app` |
| BlockBlock Installer | 2.2.2 | `/Applications/Object See/BlockBlock Installer.app/Contents/Resources/BlockBlock Helper.app/Contents/Resources/BlockBlock Installer.app` |
| Brave | 145.1.87.192 | `/Applications/Brave Browser.app` |
| Brave Helper | 145.1.87.192 | `/Applications/Brave Browser.app/Contents/Frameworks/Brave Browser Framework.framework/Versions/145.1.87.192/Helpers/Brave Browser Helper.app` |
| Brave Helper (Alerts) | 145.1.87.192 | `/Applications/Brave Browser.app/Contents/Frameworks/Brave Browser Framework.framework/Versions/145.1.87.192/Helpers/Brave Browser Helper (Alerts).app` |
| Brave Helper (GPU) | 145.1.87.192 | `/Applications/Brave Browser.app/Contents/Frameworks/Brave Browser Framework.framework/Versions/145.1.87.192/Helpers/Brave Browser Helper (GPU).app` |
| Brave Helper (Plugin) | 145.1.87.192 | `/Applications/Brave Browser.app/Contents/Frameworks/Brave Browser Framework.framework/Versions/145.1.87.192/Helpers/Brave Browser Helper (Plugin).app` |
| Brave Helper (Renderer) | 145.1.87.192 | `/Applications/Brave Browser.app/Contents/Frameworks/Brave Browser Framework.framework/Versions/145.1.87.192/Helpers/Brave Browser Helper (Renderer).app` |
| BraveSoftwareUpdateAgent | — | `/Applications/Brave Browser.app/Contents/Frameworks/Brave Browser Framework.framework/Versions/145.1.87.192/Helpers/BraveUpdater.app/Contents/Helpers/BraveSoftwareUpdate.bundle/Contents/Resources/BraveSoftwareUpdateAgent.app` |
| BraveUpdater | 143.1.87.74 | `/Applications/Brave Browser.app/Contents/Frameworks/Brave Browser Framework.framework/Versions/145.1.87.192/Helpers/BraveUpdater.app` |
| c4dpy | 2025.3 | `/Applications/Maxon Cinema 4D 2025/c4dpy.app` |
| c4dpy | 2026.2 | `/Applications/Maxon Cinema 4D 2026/c4dpy.app` |
| CapCut | 8.6.0 | `/Applications/CapCut.app` |
| CapCut | 1.0.0 | `/Applications/CapCut.app/Contents/Frameworks/CapCut.app` |
| CapCut Helper | — | `/Applications/CapCut.app/Contents/Frameworks/CapCut Helper.app` |
| CapCut Helper (GPU) | — | `/Applications/CapCut.app/Contents/Frameworks/CapCut Helper (GPU).app` |
| CapCut Helper (Plugin) | — | `/Applications/CapCut.app/Contents/Frameworks/CapCut Helper (Plugin).app` |
| CapCut Helper (Renderer) | — | `/Applications/CapCut.app/Contents/Frameworks/CapCut Helper (Renderer).app` |
| caphost | 7.0.5 (81138) | `/Applications/zoom.us.app/Contents/Frameworks/caphost.app` |
| CCXProcess | 7.8.0-2 | `/Applications/Utilities/Adobe Creative Cloud Experience/CCXProcess/CCXProcess.app` |
| CEPHtmlEngine | 12.0.1.2 | `/Applications/Adobe After Effects 2026/Adobe After Effects 2026.app/Contents/MacOS/CEPHtmlEngine.app` |
| CEPHtmlEngine | 12.0.1.2 | `/Applications/Adobe Audition 2026/Adobe Audition 2026.app/Contents/MacOS/CEPHtmlEngine.app` |
| CEPHtmlEngine | 12.1.0.5 | `/Applications/Adobe Illustrator 2026/Adobe Illustrator.app/Contents/MacOS/CEPHtmlEngine/CEPHtmlEngine.app` |
| CEPHtmlEngine | 12.1.0.5 | `/Applications/Adobe InDesign 2026/Adobe InDesign 2026.app/Contents/MacOS/CEP/CEPHtmlEngine/CEPHtmlEngine.app` |
| CEPHtmlEngine | 12.0.1.2 | `/Applications/Adobe Media Encoder (Beta)/Adobe Media Encoder (Beta).app/Contents/MacOS/CEPHtmlEngine.app` |
| CEPHtmlEngine | 12.0.1.2 | `/Applications/Adobe Media Encoder 2026/Adobe Media Encoder 2026.app/Contents/MacOS/CEPHtmlEngine.app` |
| CEPHtmlEngine | 12.0.0.14 | `/Applications/Adobe Photoshop 2026/Adobe Photoshop 2026.app/Contents/MacOS/CEPHtmlEngine.app` |
| CEPHtmlEngine | 12.0.1.2 | `/Applications/Adobe Premiere Pro (Beta)/Adobe Premiere Pro (Beta).app/Contents/MacOS/CEPHtmlEngine.app` |
| CEPHtmlEngine | 12.0.1.2 | `/Applications/Adobe Premiere Pro 2026/Adobe Premiere Pro 2026.app/Contents/MacOS/CEPHtmlEngine.app` |
| CEPHtmlEngine Helper | 12.0.1.2 | `/Applications/Adobe After Effects 2026/Adobe After Effects 2026.app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper.app` |
| CEPHtmlEngine Helper | 12.0.1.2 | `/Applications/Adobe Audition 2026/Adobe Audition 2026.app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper.app` |
| CEPHtmlEngine Helper | 12.1.0.5 | `/Applications/Adobe Illustrator 2026/Adobe Illustrator.app/Contents/MacOS/CEPHtmlEngine/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper.app` |
| CEPHtmlEngine Helper | 12.1.0.5 | `/Applications/Adobe InDesign 2026/Adobe InDesign 2026.app/Contents/MacOS/CEP/CEPHtmlEngine/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper.app` |
| CEPHtmlEngine Helper | 12.0.1.2 | `/Applications/Adobe Media Encoder (Beta)/Adobe Media Encoder (Beta).app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper.app` |
| CEPHtmlEngine Helper | 12.0.1.2 | `/Applications/Adobe Media Encoder 2026/Adobe Media Encoder 2026.app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper.app` |
| CEPHtmlEngine Helper | 12.0.0.14 | `/Applications/Adobe Photoshop 2026/Adobe Photoshop 2026.app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper.app` |
| CEPHtmlEngine Helper | 12.0.1.2 | `/Applications/Adobe Premiere Pro (Beta)/Adobe Premiere Pro (Beta).app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper.app` |
| CEPHtmlEngine Helper | 12.0.1.2 | `/Applications/Adobe Premiere Pro 2026/Adobe Premiere Pro 2026.app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper.app` |
| CEPHtmlEngine Helper (GPU) | 12.0.1.2 | `/Applications/Adobe After Effects 2026/Adobe After Effects 2026.app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (GPU).app` |
| CEPHtmlEngine Helper (GPU) | 12.0.1.2 | `/Applications/Adobe Audition 2026/Adobe Audition 2026.app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (GPU).app` |
| CEPHtmlEngine Helper (GPU) | 12.1.0.5 | `/Applications/Adobe Illustrator 2026/Adobe Illustrator.app/Contents/MacOS/CEPHtmlEngine/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (GPU).app` |
| CEPHtmlEngine Helper (GPU) | 12.1.0.5 | `/Applications/Adobe InDesign 2026/Adobe InDesign 2026.app/Contents/MacOS/CEP/CEPHtmlEngine/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (GPU).app` |
| CEPHtmlEngine Helper (GPU) | 12.0.1.2 | `/Applications/Adobe Media Encoder (Beta)/Adobe Media Encoder (Beta).app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (GPU).app` |
| CEPHtmlEngine Helper (GPU) | 12.0.1.2 | `/Applications/Adobe Media Encoder 2026/Adobe Media Encoder 2026.app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (GPU).app` |
| CEPHtmlEngine Helper (GPU) | 12.0.0.14 | `/Applications/Adobe Photoshop 2026/Adobe Photoshop 2026.app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (GPU).app` |
| CEPHtmlEngine Helper (GPU) | 12.0.1.2 | `/Applications/Adobe Premiere Pro (Beta)/Adobe Premiere Pro (Beta).app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (GPU).app` |
| CEPHtmlEngine Helper (GPU) | 12.0.1.2 | `/Applications/Adobe Premiere Pro 2026/Adobe Premiere Pro 2026.app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (GPU).app` |
| CEPHtmlEngine Helper (Plugin) | 12.0.1.2 | `/Applications/Adobe After Effects 2026/Adobe After Effects 2026.app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (Plugin).app` |
| CEPHtmlEngine Helper (Plugin) | 12.0.1.2 | `/Applications/Adobe Audition 2026/Adobe Audition 2026.app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (Plugin).app` |
| CEPHtmlEngine Helper (Plugin) | 12.1.0.5 | `/Applications/Adobe Illustrator 2026/Adobe Illustrator.app/Contents/MacOS/CEPHtmlEngine/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (Plugin).app` |
| CEPHtmlEngine Helper (Plugin) | 12.1.0.5 | `/Applications/Adobe InDesign 2026/Adobe InDesign 2026.app/Contents/MacOS/CEP/CEPHtmlEngine/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (Plugin).app` |
| CEPHtmlEngine Helper (Plugin) | 12.0.1.2 | `/Applications/Adobe Media Encoder (Beta)/Adobe Media Encoder (Beta).app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (Plugin).app` |
| CEPHtmlEngine Helper (Plugin) | 12.0.1.2 | `/Applications/Adobe Media Encoder 2026/Adobe Media Encoder 2026.app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (Plugin).app` |
| CEPHtmlEngine Helper (Plugin) | 12.0.0.14 | `/Applications/Adobe Photoshop 2026/Adobe Photoshop 2026.app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (Plugin).app` |
| CEPHtmlEngine Helper (Plugin) | 12.0.1.2 | `/Applications/Adobe Premiere Pro (Beta)/Adobe Premiere Pro (Beta).app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (Plugin).app` |
| CEPHtmlEngine Helper (Plugin) | 12.0.1.2 | `/Applications/Adobe Premiere Pro 2026/Adobe Premiere Pro 2026.app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (Plugin).app` |
| CEPHtmlEngine Helper (Renderer) | 12.0.1.2 | `/Applications/Adobe After Effects 2026/Adobe After Effects 2026.app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (Renderer).app` |
| CEPHtmlEngine Helper (Renderer) | 12.0.1.2 | `/Applications/Adobe Audition 2026/Adobe Audition 2026.app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (Renderer).app` |
| CEPHtmlEngine Helper (Renderer) | 12.1.0.5 | `/Applications/Adobe Illustrator 2026/Adobe Illustrator.app/Contents/MacOS/CEPHtmlEngine/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (Renderer).app` |
| CEPHtmlEngine Helper (Renderer) | 12.1.0.5 | `/Applications/Adobe InDesign 2026/Adobe InDesign 2026.app/Contents/MacOS/CEP/CEPHtmlEngine/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (Renderer).app` |
| CEPHtmlEngine Helper (Renderer) | 12.0.1.2 | `/Applications/Adobe Media Encoder (Beta)/Adobe Media Encoder (Beta).app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (Renderer).app` |
| CEPHtmlEngine Helper (Renderer) | 12.0.1.2 | `/Applications/Adobe Media Encoder 2026/Adobe Media Encoder 2026.app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (Renderer).app` |
| CEPHtmlEngine Helper (Renderer) | 12.0.0.14 | `/Applications/Adobe Photoshop 2026/Adobe Photoshop 2026.app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (Renderer).app` |
| CEPHtmlEngine Helper (Renderer) | 12.0.1.2 | `/Applications/Adobe Premiere Pro (Beta)/Adobe Premiere Pro (Beta).app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (Renderer).app` |
| CEPHtmlEngine Helper (Renderer) | 12.0.1.2 | `/Applications/Adobe Premiere Pro 2026/Adobe Premiere Pro 2026.app/Contents/MacOS/CEPHtmlEngine.app/Contents/Frameworks/CEPHtmlEngine Helper (Renderer).app` |
| ChatGPT | 1.2026.160 | `/Applications/ChatGPT.app` |
| ChatGPT Atlas | 1.2026.126.0 | `/Applications/ChatGPT Atlas.app` |
| Chrome | 149.0.7827.201 | `/Applications/Google Chrome.app` |
| Chrome Helper | 149.0.7827.197 | `/Applications/Google Chrome.app/Contents/Frameworks/Google Chrome Framework.framework/Versions/149.0.7827.197/Helpers/Google Chrome Helper.app` |
| Chrome Helper | 149.0.7827.201 | `/Applications/Google Chrome.app/Contents/Frameworks/Google Chrome Framework.framework/Versions/149.0.7827.201/Helpers/Google Chrome Helper.app` |
| Chrome Helper (Alerts) | 149.0.7827.197 | `/Applications/Google Chrome.app/Contents/Frameworks/Google Chrome Framework.framework/Versions/149.0.7827.197/Helpers/Google Chrome Helper (Alerts).app` |
| Chrome Helper (Alerts) | 149.0.7827.201 | `/Applications/Google Chrome.app/Contents/Frameworks/Google Chrome Framework.framework/Versions/149.0.7827.201/Helpers/Google Chrome Helper (Alerts).app` |
| Chrome Helper (GPU) | 149.0.7827.197 | `/Applications/Google Chrome.app/Contents/Frameworks/Google Chrome Framework.framework/Versions/149.0.7827.197/Helpers/Google Chrome Helper (GPU).app` |
| Chrome Helper (GPU) | 149.0.7827.201 | `/Applications/Google Chrome.app/Contents/Frameworks/Google Chrome Framework.framework/Versions/149.0.7827.201/Helpers/Google Chrome Helper (GPU).app` |
| Chrome Helper (Renderer) | 149.0.7827.197 | `/Applications/Google Chrome.app/Contents/Frameworks/Google Chrome Framework.framework/Versions/149.0.7827.197/Helpers/Google Chrome Helper (Renderer).app` |
| Chrome Helper (Renderer) | 149.0.7827.201 | `/Applications/Google Chrome.app/Contents/Frameworks/Google Chrome Framework.framework/Versions/149.0.7827.201/Helpers/Google Chrome Helper (Renderer).app` |
| Cinema 4D | 2025.3 | `/Applications/Maxon Cinema 4D 2025/Cinema 4D.app` |
| Cinema 4D | 2026.2 | `/Applications/Maxon Cinema 4D 2026/Cinema 4D.app` |
| Cinema 4D Team Render Client | 2025.3 | `/Applications/Maxon Cinema 4D 2025/Cinema 4D Team Render Client.app` |
| Cinema 4D Team Render Client | 2026.2 | `/Applications/Maxon Cinema 4D 2026/Cinema 4D Team Render Client.app` |
| Cinema 4D Team Render Server | 2025.3 | `/Applications/Maxon Cinema 4D 2025/Cinema 4D Team Render Server.app` |
| Cinema 4D Team Render Server | 2026.2 | `/Applications/Maxon Cinema 4D 2026/Cinema 4D Team Render Server.app` |
| Claude | 1.12603.1 | `/Applications/Claude.app` |
| Claude | 1.12603.1 | `/Applications/Claude.app/Contents/Frameworks/Claude Helper.app` |
| Claude Code URL Handler | — | `/Users/tonymacbook2025/Applications/Claude Code URL Handler.app` |
| Claude Helper (GPU) | 1.12603.1 | `/Applications/Claude.app/Contents/Frameworks/Claude Helper (GPU).app` |
| Claude Helper (Plugin) | 1.12603.1 | `/Applications/Claude.app/Contents/Frameworks/Claude Helper (Plugin).app` |
| Claude Helper (Renderer) | 1.12603.1 | `/Applications/Claude.app/Contents/Frameworks/Claude Helper (Renderer).app` |
| Clocker - World Clock | 26.12 | `/Applications/Clocker.app` |
| Code | 1.124.2 | `/Applications/Visual Studio Code.app` |
| Code Helper | — | `/Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper.app` |
| Code Helper (GPU) | — | `/Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (GPU).app` |
| Code Helper (Plugin) | — | `/Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app` |
| Code Helper (Renderer) | — | `/Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Renderer).app` |
| Codex | 26.602.40724 | `/Applications/Codex.app` |
| Codex | 149.0.7827.54 | `/Applications/Codex.app/Contents/Frameworks/Codex Framework.framework/Versions/149.0.7827.54/Helpers/Codex (Alerts).app` |
| Codex | 149.0.7827.54 | `/Applications/Codex.app/Contents/Frameworks/Codex Framework.framework/Versions/149.0.7827.54/Helpers/Codex (GPU).app` |
| Codex | 149.0.7827.54 | `/Applications/Codex.app/Contents/Frameworks/Codex Framework.framework/Versions/149.0.7827.54/Helpers/Codex (Renderer).app` |
| Codex | 149.0.7827.54 | `/Applications/Codex.app/Contents/Frameworks/Codex Framework.framework/Versions/149.0.7827.54/Helpers/Codex (Service).app` |
| Codex Computer Use | 1.0 | `/Applications/Codex.app/Contents/Resources/plugins/openai-bundled/plugins/computer-use/Codex Computer Use.app` |
| Codex Computer Use Installer | 0.1.0 | `/Applications/Codex.app/Contents/Resources/plugins/openai-bundled/plugins/computer-use/Codex Computer Use.app/Contents/SharedSupport/Codex Computer Use Installer.app` |
| Comet | 149.0.7827.1093 | `/Applications/Comet.app` |
| Comet Helper | 149.0.7827.1093 | `/Applications/Comet.app/Contents/Frameworks/Comet Framework.framework/Versions/149.0.7827.1093/Helpers/Comet Helper.app` |
| Comet Helper | 149.0.7827.919 | `/Applications/Comet.app/Contents/Frameworks/Comet Framework.framework/Versions/149.0.7827.919/Helpers/Comet Helper.app` |
| Comet Helper (GPU) | 149.0.7827.1093 | `/Applications/Comet.app/Contents/Frameworks/Comet Framework.framework/Versions/149.0.7827.1093/Helpers/Comet Helper (GPU).app` |
| Comet Helper (GPU) | 149.0.7827.919 | `/Applications/Comet.app/Contents/Frameworks/Comet Framework.framework/Versions/149.0.7827.919/Helpers/Comet Helper (GPU).app` |
| Comet Helper (Renderer) | 149.0.7827.1093 | `/Applications/Comet.app/Contents/Frameworks/Comet Framework.framework/Versions/149.0.7827.1093/Helpers/Comet Helper (Renderer).app` |
| Comet Helper (Renderer) | 149.0.7827.919 | `/Applications/Comet.app/Contents/Frameworks/Comet Framework.framework/Versions/149.0.7827.919/Helpers/Comet Helper (Renderer).app` |
| CometSoftwareUpdateAgent | — | `/Applications/Comet.app/Contents/Frameworks/Comet Framework.framework/Versions/149.0.7827.1093/Helpers/CometUpdater.app/Contents/Helpers/CometSoftwareUpdate.bundle/Contents/Resources/CometSoftwareUpdateAgent.app` |
| CometSoftwareUpdateAgent | — | `/Applications/Comet.app/Contents/Frameworks/Comet Framework.framework/Versions/149.0.7827.919/Helpers/CometUpdater.app/Contents/Helpers/CometSoftwareUpdate.bundle/Contents/Resources/CometSoftwareUpdateAgent.app` |
| CometUpdater | 149.0.7827.1093 | `/Applications/Comet.app/Contents/Frameworks/Comet Framework.framework/Versions/149.0.7827.1093/Helpers/CometUpdater.app` |
| CometUpdater | 149.0.7827.919 | `/Applications/Comet.app/Contents/Frameworks/Comet Framework.framework/Versions/149.0.7827.919/Helpers/CometUpdater.app` |
| Commander One PRO | 3.17.2 | `/Applications/Commander One PRO.app` |
| Commandline | 2025.3 | `/Applications/Maxon Cinema 4D 2025/Commandline.app` |
| Commandline | 2026.2 | `/Applications/Maxon Cinema 4D 2026/Commandline.app` |
| Contact Sheets | — | `/Applications/Adobe Illustrator 2026/Scripting.localized/Sample Scripts.localized/AppleScript.localized/Contact Sheet Demo.localized/Contact Sheets.app` |
| Core Sync | 7.8.10.1 | `/Applications/Utilities/Adobe Sync/CoreSync/Core Sync.app` |
| CptHost | 7.0.5 (81138) | `/Applications/zoom.us.app/Contents/Frameworks/CptHost.app` |
| Creative Cloud | 6.10.0.253 | `/Applications/Utilities/Adobe Creative Cloud/ACC/Creative Cloud.app` |
| Creative Cloud Desktop App | 6.10.0.253 | `/Applications/Utilities/Adobe Creative Cloud/Utils/Creative Cloud Desktop App.app` |
| Creative Cloud Helper | 6.10.0.253 | `/Applications/Utilities/Adobe Creative Cloud/ACC/Creative Cloud Helper.app` |
| Creative Cloud Installer | 6.10.0.253 | `/Applications/Utilities/Adobe Creative Cloud/Utils/Creative Cloud Installer.app` |
| Creative Cloud UI Helper | 6.10.0.253 | `/Applications/Utilities/Adobe Creative Cloud/ACC/Creative Cloud.app/Contents/Frameworks/Creative Cloud UI Helper.app` |
| Creative Cloud UI Helper (GPU) | 6.10.0.253 | `/Applications/Utilities/Adobe Creative Cloud/ACC/Creative Cloud.app/Contents/Frameworks/Creative Cloud UI Helper (GPU).app` |
| Creative Cloud UI Helper (Renderer) | 6.10.0.253 | `/Applications/Utilities/Adobe Creative Cloud/ACC/Creative Cloud.app/Contents/Frameworks/Creative Cloud UI Helper (Renderer).app` |
| Creative Cloud Uninstaller | 6.10.0.253 | `/Applications/Utilities/Adobe Creative Cloud/Utils/Creative Cloud Uninstaller.app` |
| Cryptomator | 1.19.2 | `/Applications/Cryptomator.app` |
| CUALockScreenGuardian | 1.0 | `/Applications/Codex.app/Contents/Resources/plugins/openai-bundled/plugins/computer-use/Codex Computer Use.app/Contents/SharedSupport/CUALockScreenGuardian.app` |
| DaVinci Control Panels Setup |  | `/Applications/DaVinci Resolve/DaVinci Control Panels Setup.app` |
| DaVinci Resolve | 19.1.0 | `/Applications/DaVinci Resolve/DaVinci Resolve.app` |
| DaVinci Resolve Welcome |  | `/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Applications/DaVinci Resolve Welcome.app` |
| DDNotifier | 6.2 | `/Applications/Disk Drill.app/Contents/Helpers/DDNotifier.app` |
| DHS | 1.5.1 | `/Applications/Object See/DHS.app` |
| Dia | 1.9.1 | `/Applications/Dia.app` |
| Discord | 0.0.392 | `/Applications/Discord.app` |
| Discord Helper | — | `/Applications/Discord.app/Contents/Frameworks/Discord Helper.app` |
| Discord Helper (GPU) | — | `/Applications/Discord.app/Contents/Frameworks/Discord Helper (GPU).app` |
| Discord Helper (Plugin) | — | `/Applications/Discord.app/Contents/Frameworks/Discord Helper (Plugin).app` |
| Discord Helper (Renderer) | — | `/Applications/Discord.app/Contents/Frameworks/Discord Helper (Renderer).app` |
| Disk Drill | 6.2 | `/Applications/Disk Drill.app` |
| Disk Drill Service | — | `/Applications/Disk Drill.app/Contents/Resources/BackService.app` |
| Disk Drill Service | — | `/Applications/Disk Drill.app/Contents/Resources/BackService_11.app` |
| Distiller | 26.001.21691 | `/Applications/Adobe Acrobat DC/Acrobat Distiller.app` |
| Do Not Disturb | 1.3.0 | `/Applications/Object See/Do Not Disturb Installer.app/Contents/Resources/Do Not Disturb.app` |
| Do Not Disturb Helper | 1.3.0 | `/Applications/Object See/Do Not Disturb Installer.app/Contents/Resources/Do Not Disturb.app/Contents/Library/LoginItems/Do Not Disturb Helper.app` |
| Do Not Disturb Installer | 1.3.0 | `/Applications/Object See/Do Not Disturb Installer.app` |
| Docker | 4.68.0 | `/Applications/Docker.app` |
| Docker Desktop | 4.68.0 | `/Applications/Docker.app/Contents/MacOS/Docker Desktop.app` |
| docker-pass | — | `/Applications/Docker.app/Contents/Library/SecretsEngine/docker-pass.app` |
| DockerHelper | 1.0.1 | `/Applications/Docker.app/Contents/Library/LoginItems/DockerHelper.app` |
| Droplet | 1.0 | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Plugins/Preflight.acroplugin/Contents/Helpers/Droplet.app` |
| Droplet | 1.0.0 | `/Applications/Adobe Photoshop 2026/Adobe Photoshop 2026.app/Contents/MacOS/Droplet Template.app` |
| dynamiclinkmediaserver | 24.0.0 | `/Applications/Adobe Lightroom Classic/Adobe Lightroom Classic.app/Contents/Helpers/DynamicLinkMediaServer/dynamiclinkmediaserver.app` |
| dynamiclinkmediaserver | 25.2.0 | `/Applications/Adobe Photoshop 2026/Adobe Photoshop 2026.app/Contents/MacOS/DynamicLinkMediaServer/dynamiclinkmediaserver.app` |
| Electron | 31.3.1 | `/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Applications/Electron.app` |
| Electron Helper | — | `/Applications/1Password.app/Contents/Frameworks/1Password Helper.app` |
| Electron Helper | — | `/Applications/Adobe UXP Developer Tools/Adobe UXP Developer Tools.app/Contents/Frameworks/Adobe UXP Developer Tools Helper.app` |
| Electron Helper | — | `/Applications/Adobe UXP Developer Tools/Adobe UXP Developer Tools.app/Contents/Resources/app.asar.unpacked/node_modules/@adobe/uxp-inspect-frontend/dist/mac/Adobe UXP Developer Tools.app/Contents/Frameworks/Adobe UXP Developer Tools Helper.app` |
| Electron Helper | — | `/Applications/Antigravity.app/Contents/Frameworks/Antigravity Helper.app` |
| Electron Helper | — | `/Applications/Artlist Hub.app/Contents/Frameworks/Artlist Hub Helper.app` |
| Electron Helper | — | `/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Applications/Electron.app/Contents/Frameworks/Electron Helper.app` |
| Electron Helper | — | `/Applications/Docker.app/Contents/MacOS/Docker Desktop.app/Contents/Frameworks/Docker Desktop Helper.app` |
| Electron Helper | — | `/Applications/Neon Wallet.app/Contents/Frameworks/Neon Wallet Helper.app` |
| Electron Helper | — | `/Applications/Obsidian.app/Contents/Frameworks/Obsidian Helper.app` |
| Electron Helper | — | `/Applications/Pinokio.app/Contents/Frameworks/Pinokio Helper.app` |
| Electron Helper | — | `/Applications/TikTok LIVE Studio.app/Contents/Frameworks/TikTok LIVE Studio Helper.app` |
| Electron Helper | — | `/Applications/Upscayl.app/Contents/Frameworks/Upscayl Helper.app` |
| Electron Helper | — | `/Applications/Workpuls.app/Contents/Frameworks/Workpuls Helper.app` |
| Electron Helper | — | `/Applications/ZXPInstaller.app/Contents/Frameworks/ZXPInstaller Helper.app` |
| Electron Helper (GPU) | — | `/Applications/1Password.app/Contents/Frameworks/1Password Helper (GPU).app` |
| Electron Helper (GPU) | — | `/Applications/Adobe UXP Developer Tools/Adobe UXP Developer Tools.app/Contents/Frameworks/Adobe UXP Developer Tools Helper (GPU).app` |
| Electron Helper (GPU) | — | `/Applications/Adobe UXP Developer Tools/Adobe UXP Developer Tools.app/Contents/Resources/app.asar.unpacked/node_modules/@adobe/uxp-inspect-frontend/dist/mac/Adobe UXP Developer Tools.app/Contents/Frameworks/Adobe UXP Developer Tools Helper (GPU).app` |
| Electron Helper (GPU) | — | `/Applications/Antigravity.app/Contents/Frameworks/Antigravity Helper (GPU).app` |
| Electron Helper (GPU) | — | `/Applications/Artlist Hub.app/Contents/Frameworks/Artlist Hub Helper (GPU).app` |
| Electron Helper (GPU) | — | `/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Applications/Electron.app/Contents/Frameworks/Electron Helper (GPU).app` |
| Electron Helper (GPU) | — | `/Applications/Docker.app/Contents/MacOS/Docker Desktop.app/Contents/Frameworks/Docker Desktop Helper (GPU).app` |
| Electron Helper (GPU) | — | `/Applications/Neon Wallet.app/Contents/Frameworks/Neon Wallet Helper (GPU).app` |
| Electron Helper (GPU) | — | `/Applications/Obsidian.app/Contents/Frameworks/Obsidian Helper (GPU).app` |
| Electron Helper (GPU) | — | `/Applications/Pinokio.app/Contents/Frameworks/Pinokio Helper (GPU).app` |
| Electron Helper (GPU) | — | `/Applications/TikTok LIVE Studio.app/Contents/Frameworks/TikTok LIVE Studio Helper (GPU).app` |
| Electron Helper (GPU) | — | `/Applications/Upscayl.app/Contents/Frameworks/Upscayl Helper (GPU).app` |
| Electron Helper (GPU) | — | `/Applications/Workpuls.app/Contents/Frameworks/Workpuls Helper (GPU).app` |
| Electron Helper (GPU) | — | `/Applications/ZXPInstaller.app/Contents/Frameworks/ZXPInstaller Helper (GPU).app` |
| Electron Helper (Plugin) | — | `/Applications/1Password.app/Contents/Frameworks/1Password Helper (Plugin).app` |
| Electron Helper (Plugin) | — | `/Applications/Adobe UXP Developer Tools/Adobe UXP Developer Tools.app/Contents/Frameworks/Adobe UXP Developer Tools Helper (Plugin).app` |
| Electron Helper (Plugin) | — | `/Applications/Adobe UXP Developer Tools/Adobe UXP Developer Tools.app/Contents/Resources/app.asar.unpacked/node_modules/@adobe/uxp-inspect-frontend/dist/mac/Adobe UXP Developer Tools.app/Contents/Frameworks/Adobe UXP Developer Tools Helper (Plugin).app` |
| Electron Helper (Plugin) | — | `/Applications/Antigravity.app/Contents/Frameworks/Antigravity Helper (Plugin).app` |
| Electron Helper (Plugin) | — | `/Applications/Artlist Hub.app/Contents/Frameworks/Artlist Hub Helper (Plugin).app` |
| Electron Helper (Plugin) | — | `/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Applications/Electron.app/Contents/Frameworks/Electron Helper (Plugin).app` |
| Electron Helper (Plugin) | — | `/Applications/Docker.app/Contents/MacOS/Docker Desktop.app/Contents/Frameworks/Docker Desktop Helper (Plugin).app` |
| Electron Helper (Plugin) | — | `/Applications/Neon Wallet.app/Contents/Frameworks/Neon Wallet Helper (Plugin).app` |
| Electron Helper (Plugin) | — | `/Applications/Obsidian.app/Contents/Frameworks/Obsidian Helper (Plugin).app` |
| Electron Helper (Plugin) | — | `/Applications/Pinokio.app/Contents/Frameworks/Pinokio Helper (Plugin).app` |
| Electron Helper (Plugin) | — | `/Applications/TikTok LIVE Studio.app/Contents/Frameworks/TikTok LIVE Studio Helper (Plugin).app` |
| Electron Helper (Plugin) | — | `/Applications/Upscayl.app/Contents/Frameworks/Upscayl Helper (Plugin).app` |
| Electron Helper (Plugin) | — | `/Applications/Workpuls.app/Contents/Frameworks/Workpuls Helper (Plugin).app` |
| Electron Helper (Plugin) | — | `/Applications/ZXPInstaller.app/Contents/Frameworks/ZXPInstaller Helper (Plugin).app` |
| Electron Helper (Renderer) | — | `/Applications/1Password.app/Contents/Frameworks/1Password Helper (Renderer).app` |
| Electron Helper (Renderer) | — | `/Applications/Adobe UXP Developer Tools/Adobe UXP Developer Tools.app/Contents/Frameworks/Adobe UXP Developer Tools Helper (Renderer).app` |
| Electron Helper (Renderer) | — | `/Applications/Adobe UXP Developer Tools/Adobe UXP Developer Tools.app/Contents/Resources/app.asar.unpacked/node_modules/@adobe/uxp-inspect-frontend/dist/mac/Adobe UXP Developer Tools.app/Contents/Frameworks/Adobe UXP Developer Tools Helper (Renderer).app` |
| Electron Helper (Renderer) | — | `/Applications/Antigravity.app/Contents/Frameworks/Antigravity Helper (Renderer).app` |
| Electron Helper (Renderer) | — | `/Applications/Artlist Hub.app/Contents/Frameworks/Artlist Hub Helper (Renderer).app` |
| Electron Helper (Renderer) | — | `/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Applications/Electron.app/Contents/Frameworks/Electron Helper (Renderer).app` |
| Electron Helper (Renderer) | — | `/Applications/Docker.app/Contents/MacOS/Docker Desktop.app/Contents/Frameworks/Docker Desktop Helper (Renderer).app` |
| Electron Helper (Renderer) | — | `/Applications/Neon Wallet.app/Contents/Frameworks/Neon Wallet Helper (Renderer).app` |
| Electron Helper (Renderer) | — | `/Applications/Obsidian.app/Contents/Frameworks/Obsidian Helper (Renderer).app` |
| Electron Helper (Renderer) | — | `/Applications/Pinokio.app/Contents/Frameworks/Pinokio Helper (Renderer).app` |
| Electron Helper (Renderer) | — | `/Applications/TikTok LIVE Studio.app/Contents/Frameworks/TikTok LIVE Studio Helper (Renderer).app` |
| Electron Helper (Renderer) | — | `/Applications/Upscayl.app/Contents/Frameworks/Upscayl Helper (Renderer).app` |
| Electron Helper (Renderer) | — | `/Applications/Workpuls.app/Contents/Frameworks/Workpuls Helper (Renderer).app` |
| Electron Helper (Renderer) | — | `/Applications/ZXPInstaller.app/Contents/Frameworks/ZXPInstaller Helper (Renderer).app` |
| Electron Login Helper | — | `/Applications/Upscayl.app/Contents/Library/LoginItems/Upscayl Login Helper.app` |
| Elmedia Player | 8.24 | `/Applications/Elmedia Player.app` |
| Espanso | 2.2.1 | `/Applications/Espanso.app` |
| Excel | 16.110.2 | `/Applications/Microsoft Excel.app` |
| Exodus | 26.6.4 | `/Applications/Exodus.app` |
| Exodus | 26.6.4 | `/Applications/Exodus.app/Contents/Frameworks/Exodus Helper.app` |
| Exodus Helper (GPU) | 26.6.4 | `/Applications/Exodus.app/Contents/Frameworks/Exodus Helper (GPU).app` |
| Exodus Helper (Plugin) | 26.6.4 | `/Applications/Exodus.app/Contents/Frameworks/Exodus Helper (Plugin).app` |
| Exodus Helper (Renderer) | 26.6.4 | `/Applications/Exodus.app/Contents/Frameworks/Exodus Helper (Renderer).app` |
| Fairlight Studio Utility | — | `/Applications/DaVinci Resolve/Fairlight Studio Utility.app` |
| Figma | 126.2.9 | `/Applications/Figma.app` |
| Figma | — | `/Applications/Figma.app/Contents/Frameworks/Figma Helper.app` |
| Figma Helper (GPU) | — | `/Applications/Figma.app/Contents/Frameworks/Figma Helper (GPU).app` |
| Figma Helper (Plugin) | — | `/Applications/Figma.app/Contents/Frameworks/Figma Helper (Plugin).app` |
| Figma Helper (Renderer) | — | `/Applications/Figma.app/Contents/Frameworks/Figma Helper (Renderer).app` |
| FigmaAgent | 126.2.9 | `/Applications/Figma.app/Contents/Library/FigmaAgent.app` |
| FinderHelper | 127.0 | `/Applications/Google Drive.app/Contents/Applications/FinderHelper.app` |
| FrameioHelper | 1.0 | `/Applications/Adobe After Effects 2026/Adobe After Effects 2026.app/Contents/Resources/com.adobe.frameio/bin/FrameioHelper.app` |
| FrameioHelper | 1.0 | `/Applications/Adobe Premiere Pro (Beta)/Adobe Premiere Pro (Beta).app/Contents/CEP/extensions/com.adobe.frameio/bin/FrameioHelper.app` |
| FrameioHelper | 1.0 | `/Applications/Adobe Premiere Pro 2026/Adobe Premiere Pro 2026.app/Contents/CEP/extensions/com.adobe.frameio/bin/FrameioHelper.app` |
| GitHub Desktop | 3.5.6 | `/Applications/GitHub Desktop.app` |
| GitHub Desktop | 3.5.6 | `/Applications/GitHub Desktop.app/Contents/Frameworks/GitHub Desktop Helper.app` |
| GitHub Desktop Helper (GPU) | 3.5.6 | `/Applications/GitHub Desktop.app/Contents/Frameworks/GitHub Desktop Helper (GPU).app` |
| GitHub Desktop Helper (Plugin) | 3.5.6 | `/Applications/GitHub Desktop.app/Contents/Frameworks/GitHub Desktop Helper (Plugin).app` |
| GitHub Desktop Helper (Renderer) | 3.5.6 | `/Applications/GitHub Desktop.app/Contents/Frameworks/GitHub Desktop Helper (Renderer).app` |
| Google Docs | 127.0 | `/Applications/Google Docs.app` |
| Google Drive | 127.0 | `/Applications/Google Drive.app` |
| Google Sheets | 127.0 | `/Applications/Google Sheets.app` |
| Google Slides | 127.0 | `/Applications/Google Slides.app` |
| GoogleSoftwareUpdateAgent | — | `/Applications/Google Chrome.app/Contents/Frameworks/Google Chrome Framework.framework/Versions/149.0.7827.197/Helpers/GoogleUpdater.app/Contents/Helpers/GoogleSoftwareUpdate.bundle/Contents/Resources/GoogleSoftwareUpdateAgent.app` |
| GoogleSoftwareUpdateAgent | — | `/Applications/Google Chrome.app/Contents/Frameworks/Google Chrome Framework.framework/Versions/149.0.7827.201/Helpers/GoogleUpdater.app/Contents/Helpers/GoogleSoftwareUpdate.bundle/Contents/Resources/GoogleSoftwareUpdateAgent.app` |
| GoogleUpdater | 148.0.7730.0 | `/Applications/Google Chrome.app/Contents/Frameworks/Google Chrome Framework.framework/Versions/149.0.7827.197/Helpers/GoogleUpdater.app` |
| GoogleUpdater | 148.0.7730.0 | `/Applications/Google Chrome.app/Contents/Frameworks/Google Chrome Framework.framework/Versions/149.0.7827.201/Helpers/GoogleUpdater.app` |
| HLCrashProcessor | — | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Helpers/LogTransport2.app/Contents/MacOS/HLCrashProcessor.app` |
| HLCrashProcessor | — | `/Applications/Adobe Photoshop 2026/Adobe Photoshop 2026.app/Contents/MacOS/LogTransport2.app/Contents/MacOS/HLCrashProcessor.app` |
| HLCrashProcessor | — | `/Applications/Adobe XD/Adobe XD.app/Contents/MacOS/LogTransport2.app/Contents/MacOS/HLCrashProcessor.app` |
| Hubstaff | 1.9.2-1c4ae83b | `/Applications/Hubstaff.app` |
| IDLE | 3.13.2 | `/Applications/Python 3.13/IDLE.app` |
| Illustrator | 30.6.0 | `/Applications/Adobe Illustrator 2026/Adobe Illustrator.app` |
| IllustratorDiagnosys | 30.6.0 | `/Applications/Adobe Illustrator 2026/Adobe Illustrator.app/Contents/MacOS/IllustratorDiagnosys.app` |
| ImporterREDServer | 24.0.0 | `/Applications/Adobe Lightroom Classic/Adobe Lightroom Classic.app/Contents/Helpers/DynamicLinkMediaServer/dynamiclinkmediaserver.app/Contents/ImporterREDServer.app` |
| InDesign | 21.4.1.4 | `/Applications/Adobe InDesign 2026/Adobe InDesign 2026.app` |
| InDesignHelper | 21.4.1.4 | `/Applications/Adobe InDesign 2026/Adobe InDesign 2026.app/Contents/MacOS/Helpers/InDesignHelper.app` |
| Instagram |  | `/Users/tonymacbook2025/Applications/Chrome Apps.localized/Instagram.app` |
| KeepingYouAwake | 1.6.8 | `/Applications/KeepingYouAwake.app` |
| KeepingYouAwake Launcher | 1.6.8 | `/Applications/KeepingYouAwake.app/Contents/Library/LoginItems/KeepingYouAwake Launcher.app` |
| Keka | 1.5.0 | `/Applications/Keka.app` |
| KeyboardCleanTool | 6 | `/Applications/KeyboardCleanTool.app` |
| Keynote | 14.5 | `/Applications/Keynote.app` |
| KnockKnock | 3.1.0 | `/Applications/KnockKnock.app` |
| KnockKnock | 2.5.0 | `/Applications/Object See/KnockKnock.app` |
| LaunchAtLogin | 1.0 | `/Applications/Stats.app/Contents/Library/LoginItems/LaunchAtLogin.app` |
| launcher | — | `/Applications/Opera Air.app/Contents/Library/LoginItems/launcher.app` |
| Launcher Disabler | 26.106.0603 | `/Applications/OneDrive.app/Contents/Library/LoginItems/Launcher Disabler.app` |
| Log Collector tool | 6.0.0.61 | `/Applications/Utilities/Adobe Sync/CoreSync/Core Sync.app/Contents/Resources/Log Collector tool.app` |
| LogTransport | 26.10.0 | `/Applications/Adobe Acrobat DC/Acrobat Distiller.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/LogTransport.app` |
| LogTransport | 26.10.0 | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Frameworks/AcroCEF Helper (GPU).app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/LogTransport.app` |
| LogTransport | 26.10.0 | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Frameworks/AcroCEF Helper (Renderer).app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/LogTransport.app` |
| LogTransport | 26.10.0 | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Frameworks/AcroCEF Helper.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/LogTransport.app` |
| LogTransport | 26.10.0 | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/LogTransport.app` |
| LogTransport | 26.10.0 | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Helpers/AcroCEF/AcroCEF.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/LogTransport.app` |
| LogTransport | 26.10.0 | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Helpers/AdobeResourceSynchronizer.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/LogTransport.app` |
| LogTransport | 10.3.2 | `/Applications/Adobe After Effects 2026/Adobe After Effects 2026.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/LogTransport.app` |
| LogTransport | 10.3.2 | `/Applications/Adobe Audition 2026/Adobe Audition 2026.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/LogTransport.app` |
| LogTransport | 29.11.0 | `/Applications/Adobe Illustrator 2026/Adobe Illustrator.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/LogTransport.app` |
| LogTransport | 29.5.0 | `/Applications/Adobe InDesign 2026/Adobe InDesign 2026.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/LogTransport.app` |
| LogTransport | 29.5.0 | `/Applications/Adobe Lightroom CC/Adobe Lightroom.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/LogTransport.app` |
| LogTransport | 29.5.0 | `/Applications/Adobe Lightroom Classic/Adobe Lightroom Classic.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/LogTransport.app` |
| LogTransport | 10.3.2 | `/Applications/Adobe Media Encoder (Beta)/Adobe Media Encoder (Beta).app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/LogTransport.app` |
| LogTransport | 10.3.2 | `/Applications/Adobe Media Encoder 2026/Adobe Media Encoder 2026.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/LogTransport.app` |
| LogTransport | 26.5.0 | `/Applications/Adobe Photoshop 2026/Adobe Photoshop 2026.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/LogTransport.app` |
| LogTransport | 10.3.2 | `/Applications/Adobe Premiere Pro (Beta)/Adobe Premiere Pro (Beta).app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/LogTransport.app` |
| LogTransport | 10.3.2 | `/Applications/Adobe Premiere Pro 2026/Adobe Premiere Pro 2026.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/LogTransport.app` |
| LogTransport | 26.8.0 | `/Applications/Utilities/Adobe Creative Cloud/ACC/Creative Cloud Helper.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/LogTransport.app` |
| LogTransport | 26.8.0 | `/Applications/Utilities/Adobe Creative Cloud/ACC/Creative Cloud.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/LogTransport.app` |
| LogTransport | 26.8.0 | `/Applications/Utilities/Adobe Creative Cloud/ACC/Creative Cloud.app/Contents/Frameworks/Creative Cloud UI Helper (GPU).app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/LogTransport.app` |
| LogTransport | 26.8.0 | `/Applications/Utilities/Adobe Creative Cloud/ACC/Creative Cloud.app/Contents/Frameworks/Creative Cloud UI Helper (Renderer).app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/LogTransport.app` |
| LogTransport | 26.8.0 | `/Applications/Utilities/Adobe Creative Cloud/ACC/Creative Cloud.app/Contents/Frameworks/Creative Cloud UI Helper.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/LogTransport.app` |
| LogTransport | 26.8.0 | `/Applications/Utilities/Adobe Sync/CoreSync/Core Sync.app/Contents/Frameworks/AdobeCrashReporter.framework/Versions/A/LogTransport.app` |
| LogTransport2 | — | `/Applications/Adobe Acrobat DC/Adobe Acrobat.app/Contents/Helpers/LogTransport2.app` |
| LogTransport2 | — | `/Applications/Adobe Photoshop 2026/Adobe Photoshop 2026.app/Contents/MacOS/LogTransport2.app` |
| LogTransport2 | — | `/Applications/Adobe XD/Adobe XD.app/Contents/MacOS/LogTransport2.app` |
| LuLu | 4.3.1 | `/Applications/LuLu.app` |
| MacWhisper | 12.8 | `/Applications/MacWhisper.app` |
| maintenancetool | 4.2.0 | `/Applications/screenrec/maintenancetool.app` |
| Make Calendar | — | `/Applications/Adobe Illustrator 2026/Scripting.localized/Sample Scripts.localized/AppleScript.localized/Calendar.localized/Make Calendar.app` |
| Maono Link | — | `/Applications/Maono Link.app` |
| Media Encoder | 26.3.1 | `/Applications/Adobe Media Encoder 2026/Adobe Media Encoder 2026.app` |
| Media Encoder (Beta) | 26.5.0 | `/Applications/Adobe Media Encoder (Beta)/Adobe Media Encoder (Beta).app` |
| Microsoft Defender Shim | 101.26020.0000 | `/Applications/Microsoft Defender Shim.app` |
| Microsoft Defender Shim | 101.26020.0000 | `/Applications/Microsoft Defender Shim.app/Contents/MacOS/Microsoft Defender Shim.app` |
| Microsoft Error Reporting | 16.110.2 | `/Applications/Microsoft Excel.app/Contents/SharedSupport/Microsoft Error Reporting.app` |
| Microsoft Error Reporting | 16.110.2 | `/Applications/Microsoft OneNote.app/Contents/SharedSupport/Microsoft Error Reporting.app` |
| Microsoft Error Reporting | 16.110.2 | `/Applications/Microsoft Outlook.app/Contents/SharedSupport/Microsoft Error Reporting.app` |
| Microsoft Error Reporting | 16.110.2 | `/Applications/Microsoft PowerPoint.app/Contents/SharedSupport/Microsoft Error Reporting.app` |
| Microsoft Error Reporting | 16.110.2 | `/Applications/Microsoft Word.app/Contents/SharedSupport/Microsoft Error Reporting.app` |
| Microsoft Error Reporting | 16.102 | `/Applications/OneDrive.app/Contents/OneDrive Sync Service.app/Contents/SharedSupport/Microsoft Error Reporting.app` |
| Microsoft Error Reporting | 16.102 | `/Applications/OneDrive.app/Contents/SharedSupport/Microsoft Error Reporting.app` |
| Microsoft.Mashup.Container | 16.110.2 | `/Applications/Microsoft Excel.app/Contents/SharedSupport/Microsoft.Mashup.Container.app` |
| Mocha AE | 12.2.1 | `/Applications/Adobe After Effects 2026/Plug-ins/Effects/mochaAE/Resources/mochaui/Mocha AE.app` |
| Mocha AE | 12.2.1 | `/Applications/Adobe Media Encoder (Beta)/Adobe Media Encoder (Beta).app/Contents/PlugIns/(AfterEffectsLib)/Effects/mochaAE/Resources/mochaui/Mocha AE.app` |
| Mocha AE | 12.2.1 | `/Applications/Adobe Media Encoder 2026/Adobe Media Encoder 2026.app/Contents/PlugIns/(AfterEffectsLib)/Effects/mochaAE/Resources/mochaui/Mocha AE.app` |
| Mocha AE | 12.2.1 | `/Applications/Adobe Premiere Pro (Beta)/Adobe Premiere Pro (Beta).app/Contents/PlugIns/(AfterEffectsLib)/Effects/mochaAE/Resources/mochaui/Mocha AE.app` |
| Mocha AE | 12.2.1 | `/Applications/Adobe Premiere Pro 2026/Adobe Premiere Pro 2026.app/Contents/PlugIns/(AfterEffectsLib)/Effects/mochaAE/Resources/mochaui/Mocha AE.app` |
| MXAI_ImageSense | 1.0.0 | `/Applications/Maxon Cinema 4D 2025/resource/modules/c4d_assetbrowser/mxai/osx/MXAI_ImageSense.app` |
| MXAI_ImageSense | 1.0.0 | `/Applications/Maxon Cinema 4D 2026/resource/modules/c4d_assetbrowser/mxai/osx/MXAI_ImageSense.app` |
| Neon Wallet | 3.5.0 | `/Applications/Neon Wallet.app` |
| Netiquette | 2.3.0 | `/Applications/LuLu.app/Contents/Resources/Netiquette.app` |
| Netiquette | 2.2.0 | `/Applications/Object See/Netiquette.app` |
| Notion | 7.20.0 | `/Applications/Notion.app` |
| Notion | 7.20.0 | `/Applications/Notion.app/Contents/Frameworks/Notion Helper.app` |
| Notion Helper (GPU) | 7.20.0 | `/Applications/Notion.app/Contents/Frameworks/Notion Helper (GPU).app` |
| Notion Helper (Plugin) | 7.20.0 | `/Applications/Notion.app/Contents/Frameworks/Notion Helper (Plugin).app` |
| Notion Helper (Renderer) | 7.20.0 | `/Applications/Notion.app/Contents/Frameworks/Notion Helper (Renderer).app` |
| Numbers | 15.2.1 | `/Applications/Numbers Creator Studio.app` |
| Numbers | 14.5 | `/Applications/Numbers.app` |
| OBS | 32.0.4 | `/Applications/OBS.app` |
| OBS Helper | — | `/Applications/OBS.app/Contents/Frameworks/OBS Helper.app` |
| OBS Helper (GPU) | — | `/Applications/OBS.app/Contents/Frameworks/OBS Helper (GPU).app` |
| OBS Helper (Plugin) | — | `/Applications/OBS.app/Contents/Frameworks/OBS Helper (Plugin).app` |
| OBS Helper (Renderer) | — | `/Applications/OBS.app/Contents/Frameworks/OBS Helper (Renderer).app` |
| Obsidian | 1.12.4 | `/Applications/Obsidian.app` |
| Ollama | 0.6.7 | `/Applications/Ollama.app` |
| Ollama | 0.6.7 | `/Applications/Ollama.app/Contents/Frameworks/Ollama Helper.app` |
| Ollama Helper (GPU) | 0.6.7 | `/Applications/Ollama.app/Contents/Frameworks/Ollama Helper (GPU).app` |
| Ollama Helper (Plugin) | 0.6.7 | `/Applications/Ollama.app/Contents/Frameworks/Ollama Helper (Plugin).app` |
| Ollama Helper (Renderer) | 0.6.7 | `/Applications/Ollama.app/Contents/Frameworks/Ollama Helper (Renderer).app` |
| OneDrive | 26.106.0603 | `/Applications/OneDrive.app` |
| OneDrive File Handler | 26.106.0603 | `/Applications/OneDrive.app/Contents/OneDrive File Handler.app` |
| OneDrive Launcher | 26.106.0603 | `/Applications/OneDrive.app/Contents/Library/LoginItems/OneDrive Launcher.app` |
| OneDrive Sync Engine Worker | 26.106.0603 | `/Applications/OneDrive.app/Contents/Resources/SyncEngineWorker.app` |
| OneDrive Sync Engine Worker | 26.106.0603 | `/Applications/OneDrive.app/Contents/SyncEngineWorker.app` |
| OneDrive Sync Service | 26.106.0603 | `/Applications/OneDrive.app/Contents/OneDrive Sync Service.app` |
| OneDrive Updater | 26.106.0603 | `/Applications/OneDrive.app/Contents/OneDrive Updater.app` |
| OneNote | 16.110.2 | `/Applications/Microsoft OneNote.app` |
| OpenXMLConverter | 16.110.2 | `/Applications/Microsoft PowerPoint.app/Contents/SharedSupport/Open XML for Excel.app` |
| OpenXMLConverter | 16.110.2 | `/Applications/Microsoft Word.app/Contents/SharedSupport/Open XML for Excel.app` |
| Opera Air | 125.0 | `/Applications/Opera Air.app` |
| Opera Helper | — | `/Applications/Opera Air.app/Contents/Frameworks/Opera Framework.framework/Versions/124.0.5705.103/Helpers/Opera Helper.app` |
| Opera Helper | — | `/Applications/Opera Air.app/Contents/Frameworks/Opera Framework.framework/Versions/125.0.5729.39/Helpers/Opera Helper.app` |
| Opera Helper (Alerts) | 140.0.7339.249 | `/Applications/Opera Air.app/Contents/Frameworks/Opera Framework.framework/Versions/124.0.5705.103/Helpers/Opera Helper (Alerts).app` |
| Opera Helper (Alerts) | 141.0.7390.125 | `/Applications/Opera Air.app/Contents/Frameworks/Opera Framework.framework/Versions/125.0.5729.39/Helpers/Opera Helper (Alerts).app` |
| Opera Helper (GPU) | — | `/Applications/Opera Air.app/Contents/Frameworks/Opera Framework.framework/Versions/124.0.5705.103/Helpers/Opera Helper (GPU).app` |
| Opera Helper (GPU) | — | `/Applications/Opera Air.app/Contents/Frameworks/Opera Framework.framework/Versions/125.0.5729.39/Helpers/Opera Helper (GPU).app` |
| Opera Helper (Plugin) | — | `/Applications/Opera Air.app/Contents/Frameworks/Opera Framework.framework/Versions/124.0.5705.103/Helpers/Opera Helper (Plugin).app` |
| Opera Helper (Plugin) | — | `/Applications/Opera Air.app/Contents/Frameworks/Opera Framework.framework/Versions/125.0.5729.39/Helpers/Opera Helper (Plugin).app` |
| Opera Helper (Renderer) | — | `/Applications/Opera Air.app/Contents/Frameworks/Opera Framework.framework/Versions/124.0.5705.103/Helpers/Opera Helper (Renderer).app` |
| Opera Helper (Renderer) | — | `/Applications/Opera Air.app/Contents/Frameworks/Opera Framework.framework/Versions/125.0.5729.39/Helpers/Opera Helper (Renderer).app` |
| Outlook | 16.110.2 | `/Applications/Microsoft Outlook.app` |
| Outlook Profile Manager | 16.110.2 | `/Applications/Microsoft Outlook.app/Contents/SharedSupport/Outlook Profile Manager.app` |
| OverSight | 2.3.0 | `/Applications/Object See/OverSight Installer.app/Contents/Resources/OverSight.app` |
| OverSight | 2.4.0 | `/Applications/OverSight.app` |
| OverSight Installer | 2.3.0 | `/Applications/Object See/OverSight Installer.app` |
| OverSight Installer | 2.3.0 | `/Applications/Object See/OverSight Installer.app/Contents/Resources/OverSight.app/Contents/Resources/OverSight Installer.app` |
| OverSight Installer | 2.4.0 | `/Applications/OverSight.app/Contents/Resources/OverSight Installer.app` |
| Pages | 14.5 | `/Applications/Pages.app` |
| Photoshop 2026 | 27.8.0 | `/Applications/Adobe Photoshop 2026/Adobe Photoshop 2026.app` |
| Pinokio | 3.8.0 | `/Applications/Pinokio.app` |
| PlayerLocationCheck | 4.3.0.0 | `/Applications/PlayerLocationCheck.app` |
| Postman | 11.76.0 | `/Applications/Postman.app` |
| Postman Helper | — | `/Applications/Postman.app/Contents/Frameworks/Postman Helper.app` |
| Postman Helper (GPU) | — | `/Applications/Postman.app/Contents/Frameworks/Postman Helper (GPU).app` |
| Postman Helper (Plugin) | — | `/Applications/Postman.app/Contents/Frameworks/Postman Helper (Plugin).app` |
| Postman Helper (Renderer) | — | `/Applications/Postman.app/Contents/Frameworks/Postman Helper (Renderer).app` |
| PowerPoint | 16.110.2 | `/Applications/Microsoft PowerPoint.app` |
| Premiere | 26.3.0 | `/Applications/Adobe Premiere Pro 2026/Adobe Premiere Pro 2026.app` |
| Premiere (Beta) | 26.5.0 | `/Applications/Adobe Premiere Pro (Beta)/Adobe Premiere Pro (Beta).app` |
| Python Launcher | 3.13.2 | `/Applications/Python 3.13/Python Launcher.app` |
| QtWebEngineProcess |  | `/Applications/Elgato Wave Link.app/Contents/Frameworks/QtWebEngineCore.framework/Versions/A/Helpers/QtWebEngineProcess.app` |
| QtWebEngineProcess |  | `/Applications/screenrec/screenrec.app/Contents/Frameworks/QtWebEngineCore.framework/Versions/A/Helpers/QtWebEngineProcess.app` |
| RansomWhere_Installer | 1.2.5 | `/Applications/Object See/RansomWhere_Installer.app` |
| Raycast | 1.104.17 | `/Applications/Raycast.app` |
| RaycastLauncher | 1.0 | `/Applications/Raycast.app/Contents/Library/LoginItems/RaycastLauncher.app` |
| Recoverty | — | `/Applications/Xpiks.app/Contents/MacOS/Recoverty.app` |
| ReiKey | 1.4.2 | `/Applications/Object See/ReiKey Installer.app/Contents/Resources/ReiKey.app` |
| ReiKey | 1.4.2 | `/Applications/ReiKey.app` |
| ReiKey Helper | 1.4.2 | `/Applications/Object See/ReiKey Installer.app/Contents/Resources/ReiKey.app/Contents/Library/LoginItems/ReiKey Helper.app` |
| ReiKey Helper | 1.4.2 | `/Applications/ReiKey.app/Contents/Library/LoginItems/ReiKey Helper.app` |
| ReiKey Installer | 1.4.2 | `/Applications/Object See/ReiKey Installer.app` |
| Roblox | 0.714.0.7141083 | `/Applications/Roblox.app` |
| RobloxPlayerInstaller | 1.2.0.239 | `/Applications/Roblox.app/Contents/MacOS/RobloxPlayerInstaller.app` |
| Rogue Amoeba Track Title Helper | 1.0 | `/Applications/Audio Hijack.app/Contents/Frameworks/TrackTitles.framework/Versions/A/Resources/Rogue Amoeba Track Title Helper.app` |
| Safari | 26.3.1 | `/Applications/Safari.app` |
| Save as Adobe PDF | 26.001.21691 | `/Applications/Adobe Acrobat DC/Acrobat Distiller.app/Contents/Resources/SelfHealFiles/Library/PDF_Services/Save as Adobe PDF.app` |
| ScreenPal | 3 | `/Applications/ScreenPal.app` |
| ScreenPal | 3 | `/Applications/ScreenPal.app/Contents/app/NoSplashScreen/ScreenPal.app` |
| ScreenPal Launcher | 3 | `/Applications/ScreenPal.app/Contents/app/NoSplashScreen/ScreenPal.app/Contents/app/ScreenPal.app` |
| ScreenPal Launcher | 3 | `/Applications/ScreenPal.app/Contents/app/ScreenPal.app` |
| ScreenPal Launcher | 3 | `/Applications/ScreenPal.app/Contents/app/ScreenPalTray.app/Contents/app/ScreenPal.app` |
| ScreenPal Tray | 3 | `/Applications/ScreenPal.app/Contents/app/NoSplashScreen/ScreenPal.app/Contents/app/ScreenPalTray.app` |
| ScreenPal Tray | 3 | `/Applications/ScreenPal.app/Contents/app/ScreenPalTray.app` |
| ScreenPal Tray | 3 | `/Applications/ScreenPal.app/Contents/app/ScreenPalTray.app/Contents/app/ScreenPalTray.app` |
| screenrec | — | `/Applications/screenrec/screenrec.app` |
| screenrec | — | `/Applications/screenrec.app` |
| Silicio | 3.7.2 | `/Applications/Silicio.app` |
| SkyComputerUseClient | 1.0 | `/Applications/Codex.app/Contents/Resources/plugins/openai-bundled/plugins/computer-use/Codex Computer Use.app/Contents/SharedSupport/SkyComputerUseClient.app` |
| Slack | 4.50.143 | `/Applications/Slack.app` |
| Slack | 4.50.143 | `/Applications/Slack.app/Contents/Frameworks/Slack Helper.app` |
| Slack Helper (GPU) | 4.50.143 | `/Applications/Slack.app/Contents/Frameworks/Slack Helper (GPU).app` |
| Slack Helper (Plugin) | 4.50.143 | `/Applications/Slack.app/Contents/Frameworks/Slack Helper (Plugin).app` |
| Slack Helper (Renderer) | 4.50.143 | `/Applications/Slack.app/Contents/Frameworks/Slack Helper (Renderer).app` |
| SmartDaemon | 6.2 | `/Applications/Disk Drill.app/Contents/Library/LoginItems/SmartDaemon.app` |
| StandaloneUpdater | 25.137.0715 | `/Applications/OneDrive.app/Contents/StandaloneUpdater.app` |
| Stats | 2.11.58 | `/Applications/Stats.app` |
| SyncReporter | 26.106.0603 | `/Applications/OneDrive.app/Contents/SyncReporter.app` |
| TablePlus | 6.8.2 | `/Applications/TablePlus.app` |
| TaskExplorer | 2.0.2 | `/Applications/Object See/TaskExplorer.app` |
| TeamProjectsLocalHub | 26.3.0 | `/Applications/Adobe After Effects 2026/Adobe After Effects 2026.app/Contents/TeamProjectsLocalHub.app` |
| TeamProjectsLocalHub | 26.5.0 | `/Applications/Adobe Media Encoder (Beta)/Adobe Media Encoder (Beta).app/Contents/TeamProjectsLocalHub.app` |
| TeamProjectsLocalHub | 26.3.1 | `/Applications/Adobe Media Encoder 2026/Adobe Media Encoder 2026.app/Contents/TeamProjectsLocalHub.app` |
| The Unarchiver | 4.3.9 | `/Applications/The Unarchiver.app` |
| TikTok |  | `/Users/tonymacbook2025/Applications/Chrome Apps.localized/TikTok.app` |
| TikTok LIVE Studio | 0.16.2 | `/Applications/TikTok LIVE Studio.app` |
| Transcode | 7.0.5 (81138) | `/Applications/zoom.us.app/Contents/Frameworks/Transcode.app` |
| Tunnelblick | 8.0.1 (build 6301) | `/Applications/Tunnelblick.app` |
| Tunnelblick | 8.0 (build 6300) | `/Applications/Tunnelblick.old.app` |
| Tunnelblick Launcher | 1.0 | `/Applications/Tunnelblick.app/Contents/Library/LoginItems/Tunnelblick Launcher.app` |
| Tunnelblick Launcher | 1.0 | `/Applications/Tunnelblick.old.app/Contents/Library/LoginItems/Tunnelblick Launcher.app` |
| TunnelblickUpdater | 1.15.0 git-077c644 | `/Applications/Tunnelblick.app/Contents/Frameworks/Sparkle.framework/Versions/A/Resources/TunnelblickUpdater.app` |
| TunnelblickUpdater | 1.15.0 git-077c644 | `/Applications/Tunnelblick.old.app/Contents/Frameworks/Sparkle.framework/Versions/A/Resources/TunnelblickUpdater.app` |
| uninstall | 2026.2.0 | `/Applications/Maxon Cinema 4D 2026/uninstall.app` |
| Uninstall Resolve | — | `/Applications/DaVinci Resolve/Uninstall Resolve.app` |
| Updater | 2.8.0 | `/Applications/Arc.app/Contents/Frameworks/Sparkle.framework/Updater.app` |
| Updater | 2.8.0 | `/Applications/Arc.app/Contents/Frameworks/Sparkle.framework/Versions/B/Updater.app` |
| Updater | 2.8.1 | `/Applications/ChatGPT Atlas.app/Contents/Frameworks/Sparkle.framework/Updater.app` |
| Updater | 2.8.1 | `/Applications/ChatGPT Atlas.app/Contents/Frameworks/Sparkle.framework/Versions/B/Updater.app` |
| Updater | 2.8.1 | `/Applications/ChatGPT.app/Contents/Frameworks/Sparkle.framework/Updater.app` |
| Updater | 2.8.1 | `/Applications/ChatGPT.app/Contents/Frameworks/Sparkle.framework/Versions/B/Updater.app` |
| Updater | 2.9.1 | `/Applications/Codex.app/Contents/Frameworks/Sparkle.framework/Updater.app` |
| Updater | 2.9.1 | `/Applications/Codex.app/Contents/Frameworks/Sparkle.framework/Versions/B/Updater.app` |
| Updater | 2.8.1-bcny | `/Applications/Dia.app/Contents/Frameworks/Sparkle.framework/Updater.app` |
| Updater | 2.8.1-bcny | `/Applications/Dia.app/Contents/Frameworks/Sparkle.framework/Versions/B/Updater.app` |
| Updater | 2.8.1 | `/Applications/Disk Drill.app/Contents/Frameworks/Sparkle.framework/Updater.app` |
| Updater | 2.8.1 | `/Applications/Disk Drill.app/Contents/Frameworks/Sparkle.framework/Versions/B/Updater.app` |
| Updater | 2.8.1 | `/Applications/Hubstaff.app/Contents/Frameworks/Sparkle.framework/Updater.app` |
| Updater | 2.8.1 | `/Applications/Hubstaff.app/Contents/Frameworks/Sparkle.framework/Versions/B/Updater.app` |
| Updater | 2.6.4 | `/Applications/KeepingYouAwake.app/Contents/Frameworks/Sparkle.framework/Updater.app` |
| Updater | 2.6.4 | `/Applications/KeepingYouAwake.app/Contents/Frameworks/Sparkle.framework/Versions/B/Updater.app` |
| Updater | 2.0.0 | `/Applications/Keka.app/Contents/Frameworks/Sparkle.framework/Updater.app` |
| Updater | 2.0.0 | `/Applications/Keka.app/Contents/Frameworks/Sparkle.framework/Versions/B/Updater.app` |
| Updater | 2.7.0 | `/Applications/MacWhisper.app/Contents/Frameworks/Sparkle.framework/Updater.app` |
| Updater | 2.7.0 | `/Applications/MacWhisper.app/Contents/Frameworks/Sparkle.framework/Versions/B/Updater.app` |
| Updater | 2.6.4 | `/Applications/OBS.app/Contents/Frameworks/Sparkle.framework/Updater.app` |
| Updater | 2.6.4 | `/Applications/OBS.app/Contents/Frameworks/Sparkle.framework/Versions/B/Updater.app` |
| Updater | 2.8.1 | `/Applications/TablePlus.app/Contents/Frameworks/Sparkle.framework/Updater.app` |
| Updater | 2.8.1 | `/Applications/TablePlus.app/Contents/Frameworks/Sparkle.framework/Versions/B/Updater.app` |
| Updater | 2.3.0-beta.1 | `/Applications/WhatsApp.app/Contents/Frameworks/WAAppKitBridge.framework/Versions/A/PlugIns/MacPlugin.bundle/Contents/Frameworks/Sparkle.framework/Updater.app` |
| Updater | 2.3.0-beta.1 | `/Applications/WhatsApp.app/Contents/Frameworks/WAAppKitBridge.framework/Versions/A/PlugIns/MacPlugin.bundle/Contents/Frameworks/Sparkle.framework/Versions/B/Updater.app` |
| Upscayl | 2.15.0 | `/Applications/Upscayl.app` |
| UVR | 0.0.0 | `/Applications/Ultimate Vocal Remover.app` |
| VECrashHandler | 1.0.0 | `/Applications/CapCut.app/Contents/Frameworks/VECrashHandler.app` |
| VEHelper | 1.0.0 | `/Applications/CapCut.app/Contents/Frameworks/VEHelper.app` |
| Warp | 0.2026.05.13.09.15.01 | `/Applications/Warp.app` |
| Wave Link | 2.0.7 | `/Applications/Elgato Wave Link.app` |
| Web Gallery | — | `/Applications/Adobe Illustrator 2026/Scripting.localized/Sample Scripts.localized/AppleScript.localized/Web Gallery.localized/Web Gallery.app` |
| WhatsApp | 26.20.72 | `/Applications/WhatsApp.app` |
| WireGuard | 1.0.16 | `/Applications/WireGuard.app` |
| WireGuardLoginItemHelper | 1.0.16 | `/Applications/WireGuard.app/Contents/Library/LoginItems/WireGuardLoginItemHelper.app` |
| Wispr Flow | 1.5.980 | `/Applications/Wispr Flow.app` |
| Wispr Flow | 1.5.980 | `/Applications/Wispr Flow.app/Contents/Frameworks/Wispr Flow Helper.app` |
| Wispr Flow | 1.5.965 | `/Applications/Wispr Flow.app/Contents/Resources/swift-helper-app-dist/Wispr Flow.app` |
| Wispr Flow Helper (GPU) | 1.5.980 | `/Applications/Wispr Flow.app/Contents/Frameworks/Wispr Flow Helper (GPU).app` |
| Wispr Flow Helper (Plugin) | 1.5.980 | `/Applications/Wispr Flow.app/Contents/Frameworks/Wispr Flow Helper (Plugin).app` |
| Wispr Flow Helper (Renderer) | 1.5.980 | `/Applications/Wispr Flow.app/Contents/Frameworks/Wispr Flow Helper (Renderer).app` |
| Word | 16.110.2 | `/Applications/Microsoft Word.app` |
| Workpuls | 8.1.4 | `/Applications/Workpuls.app` |
| XD | 61.0.12.1 | `/Applications/Adobe XD/Adobe XD.app` |
| Xpiks | — | `/Applications/Xpiks.app` |
| zCCIMeetingHost | 7.0.5 (81138) | `/Applications/zoom.us.app/Contents/Frameworks/zCCIMeetingHost.app` |
| ZMScreenshot | 7.0.5 (81138) | `/Applications/zoom.us.app/Contents/Frameworks/ZMScreenshot.app` |
| zoom.us | 7.0.5 (81138) | `/Applications/zoom.us.app` |
| ZoomAutoUpdater | 7.0.5 (81138) | `/Applications/zoom.us.app/Contents/Frameworks/ZoomAutoUpdater.app` |
| ZoomClips | 7.0.5 (81138) | `/Applications/zoom.us.app/Contents/Frameworks/ZoomClips.app` |
| ZoomHybridConf | 7.0.5 (81138) | `/Applications/zoom.us.app/Contents/Frameworks/ZoomHybridConf.app` |
| ZoomPhone | 7.0.5 (81138) | `/Applications/zoom.us.app/Contents/Frameworks/ZoomPhone.app` |
| ZoomUninstaller | 7.0.5 (81138) | `/Applications/zoom.us.app/Contents/Frameworks/ZoomUninstaller.app` |
| ZoomUpdater | 7.0.5 (81138) | `/Applications/zoom.us.app/Contents/Library/LaunchAgents/ZoomUpdater.app` |
| ZXPInstaller | 1.8.2 | `/Applications/ZXPInstaller.app` |

## 2. Homebrew — Formulae & Casks

### Formulae

| Package | Version(s) |
|---|---|
| abseil | 20260107.1 |
| ada-url | 3.4.4 |
| aom | 3.12.1 |
| aribb24 | 1.0.4 |
| brotli | 1.1.0, 1.2.0 |
| c-ares | 1.34.6, 1.34.5 |
| ca-certificates | 2025-02-25, 2026-05-14, 2026-03-19 |
| cairo | 1.18.4 |
| certifi | 2026.2.25, 2026.5.20 |
| cjson | 1.7.18 |
| cloudflared | 2026.5.2 |
| dav1d | 1.5.3, 1.5.1 |
| eigen | 5.0.1 |
| fd | 10.2.0 |
| ffmpeg | 8.1.1 |
| flac | 1.5.0 |
| fmt | 12.1.0 |
| fontconfig | 2.17.1 |
| freetype | 2.14.1_1 |
| frei0r | 2.3.3 |
| fribidi | 1.0.16 |
| gcc | 15.2.0_1 |
| gdbm | 1.25 |
| gettext | 0.26 |
| gh | 2.93.0 |
| giflib | 5.2.2 |
| glib | 2.86.0 |
| gmp | 6.3.0 |
| gnutls | 3.8.9 |
| graphite2 | 1.3.14 |
| harfbuzz | 12.1.0 |
| hdrhistogram_c | 0.11.9 |
| highway | 1.2.0 |
| icu4c@77 | 77.1 |
| icu4c@78 | 78.3 |
| imath | 3.2.1 |
| isl | 0.27 |
| jpeg-turbo | 3.1.2 |
| jpeg-xl | 0.11.1_1 |
| lame | 3.100 |
| leptonica | 1.85.0 |
| libarchive | 3.7.9 |
| libass | 0.17.3 |
| libavif | 1.3.0 |
| libb2 | 0.98.1 |
| libbluray | 1.3.4 |
| libdeflate | 1.24 |
| libevent | 2.1.12_1 |
| libidn2 | 2.3.8 |
| libimagequant | 4.4.0 |
| libmicrohttpd | 1.0.1 |
| libmpc | 1.4.1, 1.4.0 |
| libnghttp2 | 1.69.0, 1.65.0 |
| libnghttp3 | 1.16.0 |
| libngtcp2 | 1.23.0 |
| libogg | 1.3.5 |
| libomp | 22.1.2, 22.1.7 |
| libpng | 1.6.50 |
| libraqm | 0.10.3 |
| librist | 0.2.11 |
| libsamplerate | 0.2.2 |
| libsndfile | 1.2.2_1 |
| libsodium | 1.0.20 |
| libsoxr | 0.1.3 |
| libssh | 0.11.1 |
| libtasn1 | 4.20.0 |
| libtiff | 4.7.1 |
| libtommath | 1.3.0 |
| libunibreak | 6.1 |
| libunistring | 1.4 |
| libuv | 1.51.0, 1.52.1 |
| libvidstab | 1.1.1 |
| libvmaf | 3.0.0, 3.1.0 |
| libvorbis | 1.3.7 |
| libvpx | 1.15.1, 1.16.0 |
| libx11 | 1.8.12 |
| libxau | 1.0.12 |
| libxcb | 1.17.0 |
| libxdmcp | 1.1.5 |
| libxext | 1.3.6 |
| libxrender | 0.9.12 |
| libyaml | 0.2.5 |
| little-cms2 | 2.17 |
| llhttp | 9.4.1 |
| llvm@20 | 20.1.8 |
| lz4 | 1.10.0 |
| lzo | 2.10 |
| mbedtls | 3.6.3 |
| mc | RELEASE.2025-08-13T08-35-41Z_1 |
| merve | 1.2.2_1 |
| mlx | 0.31.2 |
| mlx-c | 0.6.0_2 |
| mpdecimal | 4.0.1, 4.0.0 |
| mpfr | 4.2.2 |
| mpg123 | 1.32.10 |
| nbytes | 0.1.4 |
| nettle | 3.10.1 |
| node | 26.0.0 |
| numpy | 2.4.4 |
| ollama | 0.30.6 |
| onnx | 1.21.0 |
| openai-whisper | 20250625_5 |
| openblas | 0.3.32, 0.3.33 |
| opencore-amr | 0.1.6 |
| openexr | 3.4.0_2 |
| openjpeg | 2.5.3 |
| openjph | 0.24.1 |
| openssl@3 | 3.4.1, 3.6.2, 3.6.1 |
| opus | 1.5.2, 1.6.1 |
| p11-kit | 0.25.5 |
| pango | 1.56.3 |
| pcre2 | 10.46 |
| pillow | 11.3.0 |
| pipx | 1.7.1_1 |
| pixman | 0.46.4 |
| protobuf | 34.1 |
| pv | 1.9.31 |
| python-tk@3.11 | 3.11.11 |
| python-tk@3.13 | 3.13.3 |
| python@3.10 | 3.10.17 |
| python@3.11 | 3.11.12 |
| python@3.13 | 3.13.3 |
| python@3.14 | 3.14.3_1, 3.14.5 |
| pytorch | 2.11.0 |
| rav1e | 0.7.1 |
| readline | 8.3.3, 8.2.13 |
| rubberband | 4.0.0 |
| sdl2 | 2.32.10, 2.32.4_1 |
| simdjson | 4.6.4 |
| simdutf | 9.0.0 |
| sleef | 3.9.0 |
| snappy | 1.2.1 |
| speex | 1.2.1 |
| sqlite | 3.51.3, 3.49.1, 3.53.2 |
| srt | 1.5.4 |
| svt-av1 | 4.1.0, 3.0.2 |
| tcl-tk | 9.0.1 |
| tcl-tk@8 | 8.6.16 |
| tesseract | 5.5.0_1 |
| theora | 1.1.1 |
| tree | 2.2.1 |
| unbound | 1.22.0 |
| uvwasi | 0.0.23 |
| webp | 1.5.0 |
| x264 | r3222, r3108 |
| x265 | 4.2, 4.1 |
| xorgproto | 2024.1 |
| xvid | 1.3.7 |
| xz | 5.8.3, 5.8.1 |
| zeromq | 4.3.5_1 |
| zimg | 3.0.5 |
| zstd | 1.5.7, 1.5.7_1 |
| android-platform-tools | 36.0.0 |
| blackhole-2ch | 0.6.1 |
| espanso | 2.2.1 |
| fuse-t | 1.0.49 |
| fuse-t-sshfs | 1.0.2 |
| keepingyouawake | 1.6.8 |

### Casks

| Cask | Version(s) |
|---|---|
| android-platform-tools | 36.0.0 |
| blackhole-2ch | 0.6.1 |
| espanso | 2.2.1 |
| fuse-t | 1.0.49 |
| fuse-t-sshfs | 1.0.2 |
| keepingyouawake | 1.6.8 |

## 3. Python Installs & Virtual Environments

### Python Installations

- `python3` → `/opt/homebrew/bin/python3` — Python 3.14.5
- `python3.11` → `/opt/homebrew/bin/python3.11` — Python 3.11.12
- `python3.13` → `/opt/homebrew/bin/python3.13` — Python 3.13.3
- `python3.10` → `/opt/homebrew/bin/python3.10` — Python 3.10.17

### Virtual Environments

- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/excalidraw-diagram-skill/references/.venv`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Tool-Manager/.venv`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Video-Use/.venv`
- `/Users/tonymacbook2025/Documents/Automations/ComfyUI/venv`
- `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/venv`

## 4. Docker

### Containers

| Name | Image | Status | Ports |
|---|---|---|---|

### Images

| Repository | Tag | Size | ID |
|---|---|---|---|

### Volumes


### Networks


### Docker Compose Files

- `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/docker-compose.yml`
- `/Users/tonymacbook2025/Documents/Docker/backups/docker_backups/docker_config_backup_may_28_2025/docker-compose.yml`
- `/Users/tonymacbook2025/Documents/Docker/backups/docker_backups/docker_tunnel_Backups_nov_1_2025/docker-compose.yml`
- `/Users/tonymacbook2025/Documents/Docker/backups/n8n_data_backups/data_backup_do_not_use/docker-compose.yml`
- `/Users/tonymacbook2025/Documents/Docker/docker_config/docker-compose.yml`
- `/Users/tonymacbook2025/Documents/Docker/nca-toolkit/source/docker-compose.yml`

## 5. MCP Servers

### Config-Registered MCPs

**Config:** `/Users/tonymacbook2025/Library/Application Support/Claude/claude_desktop_config.json`

**Config:** `/Users/tonymacbook2025/.claude.json (global)`
- MCP_DOCKER
- cloudflare-api
- docker-mcp-toolkit
- magic
- n8n-mcp
- obsidian-mcp-server
- remotion-documentation
- stitch
- wikidata

**Config:** `/Users/tonymacbook2025/.claude.json (project: /Users/tonymacbook2025)`
- cloudflare-api
- n8n-mcp

**Config:** `/Users/tonymacbook2025/.claude.json (project: /Users/tonymacbook2025/Documents/App Building)`
- n8n-mcp

**Config:** `/Users/tonymacbook2025/.claude.json (project: /Users/tonymacbook2025/Documents/Agent-OS)`
- blotato

### Docker MCP Gateway Servers

_(Served via `MCP_DOCKER` gateway — `docker mcp gateway run`)_

- docker-mcp (catalog: Docker MCP Catalog)

### MCP Secret Keys (names only, no values)


## 6. CLIs

| CLI | Version | Path |
|---|---|---|
| `gh` | gh version 2.93.0 (2026-05-27) | `/opt/homebrew/bin/gh` |
| `git` | git version 2.50.1 (Apple Git-155) | `/usr/bin/git` |
| `node` | v26.0.0 | `/opt/homebrew/bin/node` |
| `npm` | 11.12.1 | `/opt/homebrew/bin/npm` |
| `npx` | 11.12.1 | `/opt/homebrew/bin/npx` |
| `bun` | 1.3.13 | `/Users/tonymacbook2025/.bun/bin/bun` |
| `firecrawl` | 1.19.0 | `/opt/homebrew/bin/firecrawl` |
| `docker` | Docker version 29.3.1, build c2be9cc | `/usr/local/bin/docker` |
| `docker-compose` | Docker Compose version v5.1.1 | `/usr/local/bin/docker-compose` |
| `ffmpeg` | — | `/opt/homebrew/bin/ffmpeg` |
| `ffprobe` | — | `/opt/homebrew/bin/ffprobe` |
| `graphify` | — | `/opt/homebrew/bin/graphify` |
| `obsidian` | — | `/Applications/Obsidian.app/Contents/MacOS/obsidian` |
| `claude` | 2.1.170 (Claude Code) | `/opt/homebrew/bin/claude` |
| `codex` | codex-cli 0.137.0 | `/opt/homebrew/bin/codex` |
| `gemini` | 0.45.2 | `/opt/homebrew/bin/gemini` |
| `kubectl` | Client Version: v1.34.1 | `/usr/local/bin/kubectl` |
| `jq` | jq-1.7.1-apple | `/usr/bin/jq` |
| `fd` | fd 10.2.0 | `/opt/homebrew/bin/fd` |
| `zsh` | zsh 5.9 (arm64-apple-darwin25.0) | `/bin/zsh` |
| `bash` | GNU bash, version 3.2.57(1)-release (arm64-apple-darwin25) | `/bin/bash` |
| `uv` | uv 0.10.12 (00d72dac7 2026-03-19 aarch64-apple-darwin) | `/Users/tonymacbook2025/.local/bin/uv` |
| `pip3` | pip 26.1.1 from /opt/homebrew/lib/python3.14/site-packages/pip (python 3.14) | `/opt/homebrew/bin/pip3` |
| `pip` | pip 25.2 from /Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/ | `/Library/Frameworks/Python.framework/Versions/3.13/bin/pip` |
| `yt-dlp` | 2026.03.17 | `/Library/Frameworks/Python.framework/Versions/3.13/bin/yt-dlp` |
| `curl` | curl 8.7.1 (x86_64-apple-darwin25.0) libcurl/8.7.1 (SecureTransport) LibreSSL/3. | `/usr/bin/curl` |
| `lame` | LAME 64bits version 3.100 (http://lame.sf.net) | `/opt/homebrew/bin/lame` |
| `vercel` | 54.9.1 | `/opt/homebrew/bin/vercel` |

## 7. Python Scripts

| Script | Description | Path |
|---|---|---|
| `01_Thumbnail_Rename_Filename.py` | 🟢 Load API key from .env | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/01_Thumbnail_Rename_Filename.py` |
| `03_Auto_Shorts_Editor_V2.5-SINGLE_MODE.py` | Auto-detect RAW or ASSETS | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/03_Auto_Shorts_Editor_V2.5-SINGLE_MODE.py` |
| `03_Auto_Shorts_Editor_V2.5-SINGLE_MODE.py` | Auto-detect RAW or ASSETS | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/backup_may_18_2025/03_Auto_Shorts_Editor_V2.5-SINGLE_MODE.py` |
| `03_Auto_Shorts_Editor_V2.py` | ✅ Ensures ffmpeg runs inside Shortcuts / limited shells | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/03_Auto_Shorts_Editor_V2.py` |
| `03_Auto_Shorts_Editor_V2.py` | ✅ Ensures ffmpeg runs inside Shortcuts / limited shells | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/backup_may_18_2025/03_Auto_Shorts_Editor_V2.py` |
| `03_Master_Editor_BATCH_MODE.py` | ✅ Ensures ffmpeg runs inside Shortcuts / limited shells | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Master_Controller_Script/03_Master_Editor_BATCH_MODE.py` |
| `03_Master_Editor_BATCH_MODE.py` | ✅ Ensures ffmpeg runs inside Shortcuts / limited shells | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Master_Controller_Script/archive/backup_may_18_2025/03_Master_Editor_BATCH_MODE.py` |
| `03_Master_Editor_SINGLE_MODE.py` | --- Folder Picker --- | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Master_Controller_Script/03_Master_Editor_SINGLE_MODE.py` |
| `03_Master_Editor_SINGLE_MODE.py` | --- Folder Picker --- | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Master_Controller_Script/archive/backup_may_18_2025/03_Master_Editor_SINGLE_MODE.py` |
| `04_Master_Transcibe_BATCH_MODE.py` | ✅ Ensure Apple Shortcut compatibility (ffmpeg path) | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Master_Controller_Script/04_Master_Transcibe_BATCH_MODE.py` |
| `04_Master_Transcibe_SINGLE_MODE.py` | --- Get Folder --- | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Master_Controller_Script/04_Master_Transcibe_SINGLE_MODE.py` |
| `04_Whisper_Transcribe_SRT_V1.5-SINGLE_MODE.py` | If it's a video file | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/04_Whisper_Transcribe_SRT_V1.5-SINGLE_MODE.py` |
| `04_Whisper_Transcribe_SRT_V1.py` | ✅ Ensure Apple Shortcut compatibility (ffmpeg path) | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/04_Whisper_Transcribe_SRT_V1.py` |
| `05_Brain_Master_TXT_BATCH.py` | ✅ Load environment | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Master_Controller_Script/archive/05_Brain_Master_TXT_BATCH.py` |
| `05_Brain_Master_TXT_BATCH_V2.py` | ✅ Load environment | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Master_Controller_Script/05_Brain_Master_TXT_BATCH_V2.py` |
| `05_Brain_Master_TXT_SINGLE.py` | ✅ ENV setup | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Master_Controller_Script/archive/05_Brain_Master_TXT_SINGLE.py` |
| `05_Brain_Master_TXT_SINGLE_V2.py` | ✅ ENV setup | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Master_Controller_Script/05_Brain_Master_TXT_SINGLE_V2.py` |
| `05_Brain_SRT_to_TXT_Description_V6.0._BATCH.py` | (no description) | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/05_Brain_SRT_to_TXT_Description_V6.0._BATCH.py` |
| `05_Brain_SRT_to_TXT_Description_V6.0._SINGLE.py` | ✅ ENV setup for Apple Shortcuts | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/05_Brain_SRT_to_TXT_Description_V6.0._SINGLE.py` |
| `05_Brain_SRT_to_TXT_Description_V7.0._BATCH.py` | (no description) | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/05_Brain_SRT_to_TXT_Description_V7.0._BATCH.py` |
| `05_Brain_SRT_to_TXT_Description_V7.0._SINGLE.py` | (no description) | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/05_Brain_SRT_to_TXT_Description_V7.0._SINGLE.py` |
| `05_Reimagined_Master_TXT_BATCH.py` | ✅ Load environment | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Master_Controller_Script/archive/05_Reimagined_Master_TXT_BATCH.py` |
| `05_Reimagined_Master_TXT_BATCH_V2.py` | ✅ Load environment | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Master_Controller_Script/05_Reimagined_Master_TXT_BATCH_V2.py` |
| `05_Reimagined_Master_TXT_SINGLE.py` | ✅ ENV setup | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Master_Controller_Script/archive/05_Reimagined_Master_TXT_SINGLE.py` |
| `05_Reimagined_Master_TXT_SINGLE_V2.py` | ✅ ENV setup | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Master_Controller_Script/05_Reimagined_Master_TXT_SINGLE_V2.py` |
| `05_Reimagined_SRT_to_TXT_Description_V6.0._BATCH.py` | (no description) | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/05_Reimagined_SRT_to_TXT_Description_V6.0._BATCH.py` |
| `05_Reimagined_SRT_to_TXT_Description_V6.0._SINGLE.py` | ✅ ENV setup for Apple Shortcuts | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/05_Reimagined_SRT_to_TXT_Description_V6.0._SINGLE.py` |
| `05_Reimagined_SRT_to_TXT_Description_V7.0._BATCH.py` | (no description) | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/05_Reimagined_SRT_to_TXT_Description_V7.0._BATCH.py` |
| `05_Reimagined_SRT_to_TXT_Description_V7.0._SINGLE.py` | (no description) | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/05_Reimagined_SRT_to_TXT_Description_V7.0._SINGLE.py` |
| `05_SRT_to_TXT_Description_V3.0-SINGLE-MODE-Alpha.py` | ✅ Use local .env inside whisper_env (safe zone) | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V3.0-SINGLE-MODE-Alpha.py` |
| `05_SRT_to_TXT_Description_V3.0-SINGLE-MODE.py` | Load API key from .env | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V3.0-SINGLE-MODE.py` |
| `05_SRT_to_TXT_Description_V3.0-SINGLE-MODE_FINAL_CLEANED.py` | Load API key from .env | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V3.0-SINGLE-MODE_FINAL_CLEANED.py` |
| `05_SRT_to_TXT_Description_V3.0-SINGLE-MODE_FINAL_LOCKED.py` | Load API key from .env | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V3.0-SINGLE-MODE_FINAL_LOCKED.py` |
| `05_SRT_to_TXT_Description_V3.0-SINGLE-MODE_FIXED.py` | Load API key from .env | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V3.0-SINGLE-MODE_FIXED.py` |
| `05_SRT_to_TXT_Description_V3.0-SINGLE-MODE_FIXED_FINAL.py` | Load API key from .env | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V3.0-SINGLE-MODE_FIXED_FINAL.py` |
| `05_SRT_to_TXT_Description_V3.0.py` | Load API Key | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V3.0.py` |
| `05_SRT_to_TXT_Description_V3.5-SINGLE-MODE.py` | ✅ Load API Key from .env | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V3.5-SINGLE-MODE.py` |
| `05_SRT_to_TXT_Description_V3.6-SINGLE-MODE.py` | ✅ Load API Key from .env | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V3.6-SINGLE-MODE.py` |
| `05_SRT_to_TXT_Description_V3.7-SINGLE-MODE.py` | ✅ Load API Key from .env | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V3.7-SINGLE-MODE.py` |
| `05_SRT_to_TXT_Description_V3.8-SINGLE-MODE.py` | ✅ Load API Key from .env | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V3.8-SINGLE-MODE.py` |
| `05_SRT_to_TXT_Description_V3.9-SINGLE-MODE.py` | ✅ Load API Key from .env | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V3.9-SINGLE-MODE.py` |
| `05_SRT_to_TXT_Description_V4.0-SINGLE-MODE.py` | ✅ Apple Shortcut Compatibility | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V4.0-SINGLE-MODE.py` |
| `05_SRT_to_TXT_Description_V4.0.py` | ✅ Apple Shortcut Compatibility | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V4.0.py` |
| `05_SRT_to_TXT_Description_V4.1-SINGLE-MODE.py` | Load API key from .env | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V4.1-SINGLE-MODE.py` |
| `05_SRT_to_TXT_Description_V4.1-SINGLE-MODE_FINAL.py` | Load API key from .env | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V4.1-SINGLE-MODE_FINAL.py` |
| `05_SRT_to_TXT_Description_V4.1-SINGLE-MODE_FINAL_FIXED.py` | Load API key from .env | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V4.1-SINGLE-MODE_FINAL_FIXED.py` |
| `05_SRT_to_TXT_Description_V4.1-SINGLE-MODE_FINAL_FIXED2.py` | Load API key from .env | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V4.1-SINGLE-MODE_FINAL_FIXED2.py` |
| `05_SRT_to_TXT_Description_V4.1-SINGLE-MODE_FINAL_FIXED3.py` | Load API key from .env | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V4.1-SINGLE-MODE_FINAL_FIXED3.py` |
| `05_SRT_to_TXT_Description_V4.1-SINGLE-MODE_FINAL_FIXED4.py` | Load API key from .env | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V4.1-SINGLE-MODE_FINAL_FIXED4.py` |
| `05_SRT_to_TXT_Description_V4.1-SINGLE-MODE_FINAL_FIXED5.py` | Load API key from .env | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V4.1-SINGLE-MODE_FINAL_FIXED5.py` |
| `05_SRT_to_TXT_Description_V4.1-SINGLE-MODE_FINAL_FIXED6.py` | Load API key from .env | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V4.1-SINGLE-MODE_FINAL_FIXED6.py` |
| `05_SRT_to_TXT_Description_V4.1-SINGLE-MODE_SAFE.py` | Load API key from .env | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V4.1-SINGLE-MODE_SAFE.py` |
| `05_SRT_to_TXT_Description_V5.0-LEGACY.py` | ✅ Apple Shortcut Compatibility | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V5.0-LEGACY.py` |
| `05_SRT_to_TXT_Description_V5.0.py` | ✅ Apple Shortcut Compatibility | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V5.0.py` |
| `05_SRT_to_TXT_Description_V5.1-LEGACY.py` | ✅ Apple Shortcut Compatibility | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V5.1-LEGACY.py` |
| `05_SRT_to_TXT_Description_V5.2-LEGACY.py` | Load environment variables | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/05_SRT_to_TXT_Description_V5.2-LEGACY.py` |
| `06_Extract_Keywords_From_SRT.py` | ✅ Environment setup for Apple Shortcuts compatibility | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/06_Extract_Keywords_From_SRT.py` |
| `__init__.py` | (no description) | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/skill-creator/scripts/__init__.py` |
| `__init__.py` | Web Asset Generator - Library Modules | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/web-asset-generator/scripts/lib/__init__.py` |
| `__init__.py` | Creative Content Engine - AI-powered visual content creation pipeline. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/__init__.py` |
| `__init__.py` | Provider registry and routing for image generation. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/providers/__init__.py` |
| `__init__.py` | Media feedback package | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/v1/media/feedback/__init__.py` |
| `__init__.py` | Creative Content Engine - AI-powered visual content creation pipeline. | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/App Building/002_Content-Creation/Video-Editor/004_Tools/__init__.py` |
| `__init__.py` | Provider registry and routing for image generation. | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/App Building/002_Content-Creation/Video-Editor/004_Tools/providers/__init__.py` |
| `__init__.py` | Creative Content Engine - AI-powered visual content creation pipeline. | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/OLD/Blotato/tools/__init__.py` |
| `__init__.py` | Provider registry and routing for image generation. | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/OLD/Blotato/tools/providers/__init__.py` |
| `agent-with-ui.py` | First, prompt the AI with the latest user message | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/3-agent-ui/agent-with-ui.py` |
| `agents.py` | (no description) | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/1-first-agent/agents.py` |
| `aggregate_benchmark.py` | Aggregate individual run results into benchmark summary statistics. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/skill-creator/scripts/aggregate_benchmark.py` |
| `airtable.py` | Airtable CRUD operations for Creative Content Engine. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Airtable/airtable.py` |
| `airtable.py` | (unreadable) | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/airtable.py` |
| `airtable.py` | Airtable CRUD operations for Creative Content Engine. | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/OLD/Blotato/tools/airtable.py` |
| `airtable.py` | Airtable CRUD operations for Creative Content Engine. | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/Obsidian-Vault/003_Tools/Airtable/airtable.py` |
| `analyze_audio.py` | FFmpeg paths | `/Users/tonymacbook2025/Documents/Docker/audio_analyzer/python_scripts/analyze_audio.py` |
| `analyze_clips.py` | Analyze video clips for editorial decisions. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/analyze_clips.py` |
| `analyze_stems.py` | analyze_stems.py — LUFS loudness analysis and gain correction for generated audio stems. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Audio/analyze_stems.py` |
| `app.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/app.py` |
| `app_utils.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/app_utils.py` |
| `asana_tools.py` | create an instance of the different Asana API classes | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/10-deploy-ai-agent-langserve/tools/asana_tools.py` |
| `asana_tools.py` | create an instance of the different Asana API classes | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/llm-agent-evaluation-framework/tools/asana_tools.py` |
| `assemble.py` | assemble.py — Reimagined Realms — Universal Assembly Pipeline | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Reimagined_Realms/assemble.py` |
| `assemble.py` | assemble.py — Pompeii: The Escape — Final Assembly Pipeline | `/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/002_Channels/003_Reimagined-Realms/Productions/0001_Pompeii_The_Escape/assemble.py` |
| `audio_mixing.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/audio_mixing.py` |
| `audio_mixing.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/audio_mixing.py` |
| `audio_tts.py` | tools/audio_tts.py | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Text-To-Speech/audio_tts.py` |
| `audio_tts.py` | (unreadable) | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/audio_tts.py` |
| `audio_tts.py` | tools/audio_tts.py | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/Obsidian-Vault/003_Tools/Text-To-Speech/audio_tts.py` |
| `authenticate.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/authenticate.py` |
| `authenticate.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/v1/toolkit/authenticate.py` |
| `authentication.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/authentication.py` |
| `Auto_Shorts_Editor_V2-SINGLE_MODE.py` | Auto-detect RAW or ASSETS | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/Auto_Shorts_Editor_V2-SINGLE_MODE.py` |
| `batch_generate_images.py` | Reimagined Realms — Batch Image Generation | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Reimagined_Realms/batch_generate_images.py` |
| `batch_generate_videos.py` | Reimagined Realms — Batch Video Generation (image-to-video) | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Reimagined_Realms/batch_generate_videos.py` |
| `caption_video.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/caption_video.py` |
| `caption_video.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/v1/video/caption_video.py` |
| `caption_video.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/caption_video.py` |
| `caption_video.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/v1/video/caption_video.py` |
| `case_study_generator.py` | Case Study Generator | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/case_study_generator.py` |
| `case_study_generator.py` | Case Study Generator | `/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/.agents/skills/case_study_generator.py` |
| `case_study_generator.py` | Case Study Generator | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/Obsidian-Vault/000_Skills/case_study_generator.py` |
| `catalog_refresh.py` | Model Catalog Refresh — runs monthly via cron (1st of month, 3am). | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Tool-Manager/catalog_refresh.py` |
| `check_dependencies.py` | Dependency checker for Web Asset Generator. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/web-asset-generator/scripts/check_dependencies.py` |
| `check_pipeline_status.py` | Quick status check — shows which clips are done, pending, or missing video_looped.mp4. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/check_pipeline_status.py` |
| `check_pipeline_status.py` | Quick status check — shows which clips are done, pending, or missing video_looped.mp4. | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/App Building/002_Content-Creation/Video-Editor/004_Tools/check_pipeline_status.py` |
| `check_vision_needed.py` | Filename stems that are non-descriptive — must be re-visioned regardless of asset note content | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/check_vision_needed.py` |
| `cleanup_bookmarks.py` | (no description) | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/cleanup_bookmarks.py` |
| `cloud_storage.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/cloud_storage.py` |
| `combine_videos.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/combine_videos.py` |
| `compose_audio.py` | compose_audio.py — Vision-based per-scene audio composer for Reimagined Realms productions. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Audio/compose_audio.py` |
| `concatenate.py` | (no description) | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/v1/audio/concatenate.py` |
| `concatenate.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/v1/video/concatenate.py` |
| `concatenate.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/v1/audio/concatenate.py` |
| `concatenate.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/v1/video/concatenate.py` |
| `config.py` | Load from centralized secrets file in home directory | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/config.py` |
| `config.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/config.py` |
| `config.py` | Load from centralized secrets file in home directory | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/App Building/002_Content-Creation/Video-Editor/004_Tools/config.py` |
| `config.py` | Configuration loader for Creative Content Engine. | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/OLD/Blotato/tools/config.py` |
| `core.py` | UI/UX Pro Max Core - BM25 search engine for UI/UX style guides | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/ui-ux-pro-max/scripts/core.py` |
| `cost-saving-task-agent.py` | create an instance of the different Asana API classes | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/cost-saving-ai-router/cost-saving-task-agent.py` |
| `create_basic_plugin.py` | Scaffold a plugin directory and optionally update marketplace.json. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/.system/plugin-creator/scripts/create_basic_plugin.py` |
| `cut.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/v1/video/cut.py` |
| `cut.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/v1/video/cut.py` |
| `design_system.py` | Design System Generator - Aggregates search results and applies reasoning | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/ui-ux-pro-max/scripts/design_system.py` |
| `download.py` | (no description) | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/v1/media/download.py` |
| `emoji_utils.py` | Emoji utilities for favicon generation. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/web-asset-generator/scripts/emoji_utils.py` |
| `enrich-notion-bookmarks.py` | Notion Bookmark Enrichment Script (Hybrid Strategy) | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/App Building/007_Tools-Systems/tools/enrich-notion-bookmarks.py` |
| `execute_python.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/v1/code/execute/execute_python.py` |
| `export_fcpxml.py` | tools/export_fcpxml.py | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Remotion/export_fcpxml.py` |
| `export_fcpxml.py` | tools/export_fcpxml.py | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/export_fcpxml.py` |
| `export_fcpxml.py` | tools/export_fcpxml.py | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/Obsidian-Vault/003_Tools/Remotion/export_fcpxml.py` |
| `extract_keyframes.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/extract_keyframes.py` |
| `extract_keyframes.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/extract_keyframes.py` |
| `feedback.py` | Ensure correct MIME types for Next.js assets | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/v1/media/feedback.py` |
| `feedback.py` | Define the path to the static feedback site files | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/v1/media/feedback/feedback.py` |
| `fetch_cc0_footage.py` | CC0/Public domain footage downloader for Anomalous Wild productions. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Asset-Sourcing/fetch_cc0_footage.py` |
| `fetch_cc0_footage.py` | (unreadable) | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/fetch_cc0_footage.py` |
| `fetch_cc0_footage.py` | CC0/Public domain footage downloader for Anomalous Wild productions. | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/Obsidian-Vault/003_Tools/Asset-Sourcing/fetch_cc0_footage.py` |
| `ffmpeg_compose.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/v1/ffmpeg/ffmpeg_compose.py` |
| `ffmpeg_compose.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/v1/ffmpeg/ffmpeg_compose.py` |
| `ffmpeg_toolkit.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/ffmpeg_toolkit.py` |
| `file_management.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/file_management.py` |
| `fix_embeds.py` | fix_embeds.py — Fix wrong-case ![[image]] embeds in 007_Resource_Library markdown notes. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/fix_embeds.py` |
| `fix_image_case.py` | fix_image_case.py — Convert lowercase kebab-case image filenames in Visual_Assets | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/fix_image_case.py` |
| `flask_crop_api.py` | Run multi_crop.py with arguments | `/Users/tonymacbook2025/Documents/Docker/scripts/flask_crop_api.py` |
| `gcp_toolkit.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/gcp_toolkit.py` |
| `gdrive_upload.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/gdrive_upload.py` |
| `gemini_scene_analysis.py` | gemini_scene_analysis.py — Second-by-second video analysis for audio stem design. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/AI-Analysis/gemini_scene_analysis.py` |
| `gemini_video_analysis.py` | 1. OVERALL STYLE & AESTHETIC | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/AI-Analysis/gemini_video_analysis.py` |
| `gemini_video_analysis.py` | (unreadable) | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/gemini_video_analysis.py` |
| `gemini_video_analysis.py` | 1. OVERALL STYLE & AESTHETIC | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/Obsidian-Vault/003_Tools/AI-Analysis/gemini_video_analysis.py` |
| `generate-lut-reference.py` | Regenerate the probe table that lives in alphaBlit.test.ts (paste over | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Hyperframes/packages/engine/scripts/generate-lut-reference.py` |
| `generate_docs.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/generate_docs.py` |
| `generate_favicons.py` | Generate favicon and app icon files from a source image or emoji. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/web-asset-generator/scripts/generate_favicons.py` |
| `generate_og_images.py` | Generate social media meta images (Open Graph images) for Facebook, Twitter, WhatsApp, etc. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/web-asset-generator/scripts/generate_og_images.py` |
| `generate_openai_yaml.py` | OpenAI YAML Generator - Creates agents/openai.yaml for a skill folder. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/.system/skill-creator/scripts/generate_openai_yaml.py` |
| `generate_report.py` | Generate an HTML report from run_loop.py output. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/skill-creator/scripts/generate_report.py` |
| `generate_review.py` | Generate and serve a review page for eval results. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/skill-creator/eval-viewer/generate_review.py` |
| `generate_shot.py` | Shot Generator — I Love/Hate Everything | `/Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/Love_Hate/generate_shot.py` |
| `generate_stems.py` | generate_stems.py — Audio stem generator for video productions. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Audio/generate_stems.py` |
| `generate_system_map.py` | generate_system_map.py | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/generate_system_map.py` |
| `get_transcript.py` | Extract transcript from a YouTube video. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/youtube-transcript/scripts/get_transcript.py` |
| `github_utils.py` | Shared GitHub helpers for skill install scripts. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/.system/skill-installer/scripts/github_utils.py` |
| `google.py` | Google AI Studio provider — image generation (Nano Banana / Nano Banana Pro) | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Image-Generation/google.py` |
| `google.py` | (unreadable) | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/providers/google.py` |
| `google.py` | Google AI Studio provider — image generation (Nano Banana / Nano Banana Pro) | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/App Building/002_Content-Creation/Video-Editor/004_Tools/providers/google.py` |
| `google.py` | Google AI Studio provider — image generation (Nano Banana / Nano Banana Pro) | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/OLD/Blotato/tools/providers/google.py` |
| `google_drive_tools.py` | If there are no (valid) credentials available, let the user log in. | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/10-deploy-ai-agent-langserve/tools/google_drive_tools.py` |
| `google_drive_tools.py` | If there are no (valid) credentials available, let the user log in. | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/llm-agent-evaluation-framework/tools/google_drive_tools.py` |
| `grade.py` | Apply a color grade to a video via ffmpeg filter chain. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Video-Use/helpers/grade.py` |
| `ikigai_cropper.py` | --- Define target crop ratios --- | `/Users/tonymacbook2025/Documents/Automations/IkigaiDigital/ikigai_cropper.py` |
| `ikigai_cropper_fixed.py` | Fixed output directory | `/Users/tonymacbook2025/Documents/Automations/IkigaiDigital/ikigai_cropper_fixed.py` |
| `Ikigai_detail_zoom_launcher.py` | (no description) | `/Users/tonymacbook2025/Documents/Automations/IkigaiDigital/Ikigai_detail_zoom_launcher.py` |
| `Ikigai_mockup_launcher.py` | Read the JSX source and pass as a string to avoid alias/8800 issues | `/Users/tonymacbook2025/Documents/Automations/IkigaiDigital/ARCHIVE/BACKUPS/Ikigai_mockup_launcher.py` |
| `Ikigai_mockup_launcher.py` | Read the JSX source and pass as a string to avoid alias/8800 issues | `/Users/tonymacbook2025/Documents/Automations/IkigaiDigital/Ikigai_mockup_launcher.py` |
| `ikigai_thumbnail.py` | Make Thumbnails folder | `/Users/tonymacbook2025/Documents/Automations/IkigaiDigital/ikigai_thumbnail.py` |
| `Ikigai_Video_Renderer.py` | First try with pyobjc to detect idle; otherwise fall back to UI-only flow | `/Users/tonymacbook2025/Documents/Automations/IkigaiDigital/ARCHIVE/BACKUPS/Ikigai_Video_Renderer.py` |
| `Ikigai_Video_Renderer.py` | First try with pyobjc to detect idle; otherwise fall back to UI-only flow | `/Users/tonymacbook2025/Documents/Automations/IkigaiDigital/ARCHIVE/Ikigai_Video_Renderer.py` |
| `image_gen.py` | Fallback CLI for explicit image generation or editing with GPT Image models. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/.system/imagegen/scripts/image_gen.py` |
| `image_gen.py` | Image generation module — multi-provider. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Image-Generation/image_gen.py` |
| `image_gen.py` | (unreadable) | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/providers/image_gen.py` |
| `image_gen.py` | Image generation module — multi-provider. | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/OLD/Blotato/tools/image_gen.py` |
| `image_gen.py` | Image generation module — multi-provider. | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/Obsidian-Vault/003_Tools/Image-Generation/image_gen.py` |
| `image_to_video.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/image_to_video.py` |
| `image_to_video.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/v1/image/convert/image_to_video.py` |
| `image_to_video.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/image_to_video.py` |
| `image_to_video.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/v1/image/convert/image_to_video.py` |
| `improve_description.py` | Improve a skill description based on eval results. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/skill-creator/scripts/improve_description.py` |
| `init_skill.py` | Skill Initializer - Creates a new skill from template | `/Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/Skills/Solo_Higgsfield_Agency/Cowork-Workspace-Template/.claude/skills/skill-creator/scripts/init_skill.py` |
| `init_skill.py` | Skill Initializer - Creates a new skill from template | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/.system/skill-creator/scripts/init_skill.py` |
| `install-skill-from-github.py` | Install a skill from a GitHub repo path into $CODEX_HOME/skills. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/.system/skill-installer/scripts/install-skill-from-github.py` |
| `job_status.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/v1/toolkit/job_status.py` |
| `jobs_status.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/v1/toolkit/jobs_status.py` |
| `kie_image_gen.py` | (no description) | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Image-Generation/kie_image_gen.py` |
| `kie_image_gen.py` | (unreadable) | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/providers/kie_image_gen.py` |
| `kie_image_gen.py` | (no description) | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/Obsidian-Vault/003_Tools/Image-Generation/kie_image_gen.py` |
| `kie_upload.py` | Kie AI file upload module. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Image-Generation/kie_upload.py` |
| `kie_upload.py` | (unreadable) | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/kie_upload.py` |
| `kie_upload.py` | Kie AI file upload module. | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/App Building/002_Content-Creation/Video-Editor/004_Tools/kie_upload.py` |
| `kie_upload.py` | Kie AI file upload module. | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/OLD/Blotato/tools/kie_upload.py` |
| `kie_video_gen.py` | Map the generic slugs to Veo3 exact model name | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/kie_video_gen.py` |
| `kie_video_gen.py` | (unreadable) | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/providers/kie_video_gen.py` |
| `kie_video_gen.py` | Map the generic slugs to Veo3 exact model name | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/Obsidian-Vault/003_Tools/Video-Generation/kie_video_gen.py` |
| `korvus_rag.py` | Initialize collection | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/korvus-simple-rag/korvus_rag.py` |
| `langchain-agent.py` | First, prompt the AI with the latest user message | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/2-langchain-agent/langchain-agent.py` |
| `langgraph-task-management-agent.py` | ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/7-langgraph-agent/langgraph-task-management-agent.py` |
| `langserve-chatbot.py` | ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/10-deploy-ai-agent-langserve/langserve-chatbot.py` |
| `langserve-endpoints.py` | Load .env file | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/10-deploy-ai-agent-langserve/langserve-endpoints.py` |
| `list-skills.py` | List skills from a GitHub repo path. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/.system/skill-installer/scripts/list-skills.py` |
| `llama3-task-agent.py` | create an instance of the different Asana API classes | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/llama3-function-calling-agent/llama3-task-agent.py` |
| `llm-eval-chatbot.py` | ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/llm-agent-evaluation-framework/llm-eval-chatbot.py` |
| `load_sql_data.py` | This script is used to create a SQLlite database, add tables | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-swarm-agent/load_sql_data.py` |
| `load_sql_data.py` | This script is used to create a SQLlite database, add tables | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/sql-ai-agent/load_sql_data.py` |
| `local-agent-with-ui.py` | (no description) | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-llm-tool-calling/local-agent-with-ui.py` |
| `local-rag-agent.py` | If you want to run the model absolutely locally - VERY resource intense! | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/5-rag-agent/local-rag-agent.py` |
| `love_hate_analyzer.py` | Love/Hate Reference Video Analyzer | `/Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/Love_Hate/love_hate_analyzer.py` |
| `madlibs.py` | Initialize the chat history with the initial system message | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/madlibs/madlibs.py` |
| `Master_Controller_V1.5.py` | ============================= | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Master_Controller_Script/archive/old_versions/Master_Controller_V1.5.py` |
| `Master_Controller_V1.6.py` | Suppress the Tkinter root window | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Master_Controller_Script/archive/old_versions/Master_Controller_V1.6.py` |
| `Master_Controller_V1.7.py` | Set up the Desktop logging | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Master_Controller_Script/archive/old_versions/Master_Controller_V1.7.py` |
| `Master_Controller_V1.8.py` | --- Load environment variables --- | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Master_Controller_Script/archive/Master_Controller_V1.8.py` |
| `Master_Controller_V1.9.py` | --- Load environment variables --- | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Master_Controller_Script/Master_Controller_V1.9.py` |
| `Master_Controller_V1.py` | ====== Master Controller Setup ====== | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Master_Controller_Script/archive/old_versions/Master_Controller_V1.py` |
| `media_convert.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/v1/media/convert/media_convert.py` |
| `media_convert.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/v1/media/convert/media_convert.py` |
| `media_to_mp3.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/media_to_mp3.py` |
| `media_to_mp3.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/v1/media/convert/media_to_mp3.py` |
| `media_to_mp3.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/v1/media/convert/media_to_mp3.py` |
| `media_transcribe.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/v1/media/media_transcribe.py` |
| `media_transcribe.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/v1/media/media_transcribe.py` |
| `metadata.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/v1/media/metadata.py` |
| `metadata.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/v1/media/metadata.py` |
| `mix_stems.py` | mix_stems.py — Mix generated audio stems onto the video timeline. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Audio/mix_stems.py` |
| `multi_crop.py` | Ensure 300 DPI and high quality | `/Users/tonymacbook2025/Documents/Docker/scripts/multi_crop.py` |
| `n8n-asana-agent.py` | This Python script is an example of how to use Streamlit with | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/8-n8n-asana-agent/n8n-asana-agent.py` |
| `n8n-langchain-agent.py` | ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/n8n-langchain-agent/n8n-langchain-agent.py` |
| `n8n-langchain-agent.py` | ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/n8n-langchain-agent-advanced/n8n-langchain-agent.py` |
| `n8n-streamlit-agent-basic-auth.py` | Constants | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/n8n-streamlit-agent/n8n-streamlit-agent-basic-auth.py` |
| `n8n-streamlit-agent.py` | Supabase setup | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/n8n-streamlit-agent/n8n-streamlit-agent.py` |
| `n8n_pipe.py` | title: n8n Pipe Function | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/n8n_pipe.py` |
| `new_video.py` | tools/new_video.py | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/new_video.py` |
| `new_video.py` | (unreadable) | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/new_video.py` |
| `new_video.py` | tools/new_video.py | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/Obsidian-Vault/003_Tools/Video-Generation/new_video.py` |
| `o1-ai-agent.py` | create an instance of the different Asana API classes | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/o1-ai-agent/o1-ai-agent.py` |
| `optimize-prompt.py` | Prompt Optimization Script | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/prompt-engineering-patterns/scripts/optimize-prompt.py` |
| `pack_transcripts.py` | Pack all Scribe transcripts in <edit>/transcripts/ into one readable markdown. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Video-Use/helpers/pack_transcripts.py` |
| `package_skill.py` | Skill Packager - Creates a distributable .skill file of a skill folder | `/Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/Skills/Solo_Higgsfield_Agency/Cowork-Workspace-Template/.claude/skills/skill-creator/scripts/package_skill.py` |
| `package_skill.py` | Skill Packager - Creates a distributable .skill file of a skill folder | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/skill-creator/scripts/package_skill.py` |
| `phase1_theme_discovery.py` | Scan ChatGPT export conversations and write a keyword-based theme report. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/phase1_theme_discovery.py` |
| `phase2_chatgpt_profile.py` | Distill approved ChatGPT themes into Tony profile notes. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/phase2_chatgpt_profile.py` |
| `phase3_chatgpt_structured_ingest.py` | Build a structured ChatGPT brain layer from the OpenAI export. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/phase3_chatgpt_structured_ingest.py` |
| `phase3_image_pipeline.py` | Copy OpenAI export images into OpenAI_Images and build an image map. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/phase3_image_pipeline.py` |
| `pipeline_supervisor.py` | Production Supervisor — bioluminescence_weapon video generation. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/pipeline_supervisor.py` |
| `pipeline_supervisor.py` | Production Supervisor — bioluminescence_weapon video generation. | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/App Building/002_Content-Creation/Video-Editor/004_Tools/pipeline_supervisor.py` |
| `preloop_new_clips.py` | Creates video_looped.mp4 for any new clip folder that has video.mp4 but not video_looped.mp4. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/preloop_new_clips.py` |
| `preloop_new_clips.py` | Creates video_looped.mp4 for any new clip folder that has video.mp4 but not video_looped.mp4. | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/App Building/002_Content-Creation/Video-Editor/004_Tools/preloop_new_clips.py` |
| `pricing_refresh.py` | Pricing Refresh — runs monthly via cron. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Tool-Manager/pricing_refresh.py` |
| `process_image_ingest.py` | Filename stems that are non-descriptive — AI sometimes produces these when it can't read an image | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/process_image_ingest.py` |
| `process_notion_edit.py` | (no description) | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/process_notion_edit.py` |
| `process_video_ingest.py` | 1. Create Directories | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/process_video_ingest.py` |
| `quick_validate.py` | Quick validation script for skills - minimal version | `/Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/Skills/Solo_Higgsfield_Agency/Cowork-Workspace-Template/.claude/skills/skill-creator/scripts/quick_validate.py` |
| `quick_validate.py` | Quick validation script for skills - minimal version | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/.system/skill-creator/scripts/quick_validate.py` |
| `quick_validate.py` | Quick validation script for skills - minimal version | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/skill-creator/scripts/quick_validate.py` |
| `rag-document-loader.py` | Load the PDF or txt documents from the directory | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/6-rag-task-agent/rag-document-loader.py` |
| `rag-task-agent.py` | create an instance of the different Asana API classes | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/6-rag-task-agent/rag-task-agent.py` |
| `read_marketplace_name.py` | Print the top-level marketplace name from any marketplace.json file. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/.system/plugin-creator/scripts/read_marketplace_name.py` |
| `regenerate-bookmarks-perplexity.py` | Notion Bookmark Regeneration via Perplexity API (4-Step Pipeline) | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/App Building/007_Tools-Systems/tools/regenerate-bookmarks-perplexity.py` |
| `remove_chroma_key.py` | Remove a solid chroma-key background from an image. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/.system/imagegen/scripts/remove_chroma_key.py` |
| `Remove_Text_From_Image.py` | --- CONFIG --- | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/Remove_Text_From_Image.py` |
| `rename_screenshots.py` | DEPRECATED — 2026-05-09 | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/rename_screenshots.py` |
| `render.py` | Render a video from an EDL. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Video-Use/helpers/render.py` |
| `render_excalidraw.py` | Render Excalidraw JSON to PNG using Playwright + headless Chromium. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/excalidraw-diagram/references/render_excalidraw.py` |
| `render_excalidraw.py` | Render Excalidraw JSON to PNG using Playwright + headless Chromium. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/excalidraw-diagram-skill/references/render_excalidraw.py` |
| `render_outputs.py` | render_outputs.py — Sound engineer render pipeline for video productions. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Audio/render_outputs.py` |
| `render_video.py` | render_video.py — Versioned video renderer for Reimagined Realms productions. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Audio/render_video.py` |
| `reroute_visual_assets.py` | Re-route images from Visual_Assets/ to correct subfolders based on filename classification. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/reroute_visual_assets.py` |
| `run.py` | print agent name in blue | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-swarm-agent/run.py` |
| `run.py` | (no description) | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/sql-ai-agent/run.py` |
| `run_eval.py` | Run trigger evaluation for a skill description. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/skill-creator/scripts/run_eval.py` |
| `run_loop.py` | Run the eval + improve loop until all pass or max iterations reached. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/skill-creator/scripts/run_loop.py` |
| `run_new_clips_batch.py` | Batch generator for new_clips_prompts.json — handles both video (Kie.ai) and image (Fal.ai Flux Pro). | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/run_new_clips_batch.py` |
| `run_new_clips_batch.py` | Batch generator for new_clips_prompts.json — handles both video (Kie.ai) and image (Fal.ai Flux Pro). | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/App Building/002_Content-Creation/Video-Editor/004_Tools/run_new_clips_batch.py` |
| `run_tts_batch.py` | Batch TTS runner — reads narration_tts.json, generates ElevenLabs audio for each scene. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/run_tts_batch.py` |
| `run_tts_batch.py` | Batch TTS runner — reads narration_tts.json, generates ElevenLabs audio for each scene. | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/App Building/002_Content-Creation/Video-Editor/004_Tools/run_tts_batch.py` |
| `run_video_gen_batch.py` | Batch AI video generator — reads ai_prompts.json, generates Kling/Veo videos for each scene. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/run_video_gen_batch.py` |
| `run_video_gen_batch.py` | Batch AI video generator — reads ai_prompts.json, generates Kling/Veo videos for each scene. | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/App Building/002_Content-Creation/Video-Editor/004_Tools/run_video_gen_batch.py` |
| `runnable.py` | from tools.google_drive_tools import available_drive_functions | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/10-deploy-ai-agent-langserve/runnable.py` |
| `runnable.py` | Invoke the chatbot with the binded tools | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/7-langgraph-agent/runnable.py` |
| `runnable.py` | Support for HuggingFace with local models coming soon! This function isn't used yet. | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/llm-agent-evaluation-framework/runnable.py` |
| `runnable.py` | Invoke the chatbot with the binded tools | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/n8n-langchain-agent-advanced/runnable.py` |
| `s3_toolkit.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/s3_toolkit.py` |
| `scrape_kieai.py` | Fetch all kie.ai model pricing via the undocumented JSON API. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Tool-Manager/scrape_kieai.py` |
| `search.py` | UI/UX Pro Max Search - BM25 search engine for UI/UX style guides | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/ui-ux-pro-max/scripts/search.py` |
| `silence.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/v1/media/silence.py` |
| `silence.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/v1/media/silence.py` |
| `split.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/v1/video/split.py` |
| `split.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/v1/video/split.py` |
| `sql_agents.py` | Get column names | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-swarm-agent/sql_agents.py` |
| `sql_agents.py` | Get column names | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/sql-ai-agent/sql_agents.py` |
| `SRT_to_TXT_Description_V2.0.py` | Load API Key | `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Archive Scripts/old_versions/SRT_to_TXT_Description_V2.0.py` |
| `streamlit-chatbot.py` | Initialize the chat history with the initial system message | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/streamlit-chatbot/streamlit-chatbot.py` |
| `streamlit_ui.py` | For now it appears Ollama doesn't support streaming with Pydantic AI so this is disabled | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/pydantic-ai/streamlit_ui.py` |
| `sync_skill_index.py` | (no description) | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/sync_skill_index.py` |
| `task-management-agent.py` | create an instance of the different Asana API classes | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/4-task-management-agent/task-management-agent.py` |
| `test.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/v1/toolkit/test.py` |
| `test_playwright_scraper.py` | Test Playwright web scraping vs current Firecrawl approach | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/App Building/007_Tools-Systems/tools/test_playwright_scraper.py` |
| `test_scraper_simple.py` | Simple test of scraping strategies for bookmark enrichment | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/App Building/007_Tools-Systems/tools/test_scraper_simple.py` |
| `test_specific_bookmarks.py` | Test specific bookmarks from AI Tools database | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/App Building/007_Tools-Systems/tools/test_specific_bookmarks.py` |
| `thumbnail.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/v1/video/thumbnail.py` |
| `thumbnail.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/v1/video/thumbnail.py` |
| `timeline_view.py` | Filmstrip + waveform composite PNG for a time range of a video. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Video-Use/helpers/timeline_view.py` |
| `Tokenized_Image_Compressor.py` | Tokenized Image Compressor | `/Users/tonymacbook2025/Documents/Automations/IkigaiDigital/Tokenized_Image_Compressor.py` |
| `tool_manager.py` | Tool Manager CLI — Agent-OS | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Tool-Manager/tool_manager.py` |
| `tools.py` | create an instance of the different Asana API classes | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/7-langgraph-agent/tools.py` |
| `tools.py` | ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/n8n-langchain-agent/tools.py` |
| `tools.py` | ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/n8n-langchain-agent-advanced/tools.py` |
| `transcribe.py` | Transcribe a video with ElevenLabs Scribe. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Video-Use/helpers/transcribe.py` |
| `transcribe_batch.py` | Batch-transcribe every video in a directory with 4 parallel workers. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Video-Use/helpers/transcribe_batch.py` |
| `transcribe_media.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/transcribe_media.py` |
| `transcription.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/transcription.py` |
| `trim.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/v1/video/trim.py` |
| `trim.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/v1/video/trim.py` |
| `update_asset_notes_vision.py` | Update Asset Notes with real vision-based descriptions using Gemini 2.5 Flash. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/update_asset_notes_vision.py` |
| `update_plugin_cachebuster.py` | Rewrite a local plugin version to a single Codex cachebuster suffix. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py` |
| `upload.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/routes/v1/s3/upload.py` |
| `upload.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/v1/s3/upload.py` |
| `utils.py` | Shared utilities for skill-creator scripts. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/skill-creator/scripts/utils.py` |
| `utils.py` | Shared utilities for Creative Content Engine. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/utils.py` |
| `utils.py` | Shared utilities for Creative Content Engine. | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/App Building/002_Content-Creation/Video-Editor/004_Tools/utils.py` |
| `utils.py` | Shared utilities for Creative Content Engine. | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/OLD/Blotato/tools/utils.py` |
| `validate_plugin.py` | Validate a generated plugin against the plugin ingestion contract. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/.system/plugin-creator/scripts/validate_plugin.py` |
| `validators.py` | Validation utilities for web assets. | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/web-asset-generator/scripts/lib/validators.py` |
| `vector_db_tools.py` | Create the open-source embedding function | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/10-deploy-ai-agent-langserve/tools/vector_db_tools.py` |
| `vector_db_tools.py` | Create the open-source embedding function | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/llm-agent-evaluation-framework/tools/vector_db_tools.py` |
| `version.py` | (no description) | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/version.py` |
| `video_stitcher.py` | Sort scene directories | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/video_stitcher.py` |
| `video_stitcher.py` | (unreadable) | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/providers/video_stitcher.py` |
| `video_stitcher.py` | Sort scene directories | `/Users/tonymacbook2025/Documents/Reconstruct/Migrated-App-Building/Obsidian-Vault/003_Tools/Video-Generation/video_stitcher.py` |
| `web_search_agent.py` | 'if-token-present' means nothing will be sent (and the example will work) if you don't have logfire configured | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/pydantic-ai/web_search_agent.py` |
| `web_search_agent_streamlit.py` | 'if-token-present' means nothing will be sent (and the example will work) if you don't have logfire configured | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/pydantic-ai/web_search_agent_streamlit.py` |
| `webhook.py` | Copyright (c) 2025 Stephen G. Pope | `/Users/tonymacbook2025/Documents/Docker/AI-Stacks/ai-agents-masterclass/local-ai-packaged/no-code-architects-toolkit/services/webhook.py` |

## 8. Claude Code Skills

- `cancel-ralph` — `/Users/tonymacbook2025/.claude/commands/cancel-ralph.md`
- `Case-Study-Analysis` — `/Users/tonymacbook2025/.claude/skills/Case-Study-Analysis.md`
- `Cinematic-Styles` — `/Users/tonymacbook2025/.claude/skills/Cinematic-Styles.md`
- `claudemd-audit` — `/Users/tonymacbook2025/.claude/commands/claudemd-audit.md`
- `claudemd-snapshot` — `/Users/tonymacbook2025/.claude/commands/claudemd-snapshot.md`
- `clean_gone` — `/Users/tonymacbook2025/.claude/commands/clean_gone.md`
- `code-review` — `/Users/tonymacbook2025/.claude/commands/code-review.md`
- `commit` — `/Users/tonymacbook2025/.claude/commands/commit.md`
- `commit-push-pr` — `/Users/tonymacbook2025/.claude/commands/commit-push-pr.md`
- `configure` — `/Users/tonymacbook2025/.claude/commands/configure.md`
- `Content-Strategy-Framework` — `/Users/tonymacbook2025/.claude/skills/Content-Strategy-Framework.md`
- `create-plugin` — `/Users/tonymacbook2025/.claude/commands/create-plugin.md`
- `DAIPBR-Storytelling` — `/Users/tonymacbook2025/.claude/skills/DAIPBR-Storytelling.md`
- `feature-dev` — `/Users/tonymacbook2025/.claude/commands/feature-dev.md`
- `help` — `/Users/tonymacbook2025/.claude/commands/help.md`
- `hookify` — `/Users/tonymacbook2025/.claude/commands/hookify.md`
- `list` — `/Users/tonymacbook2025/.claude/commands/list.md`
- `new-sdk-app` — `/Users/tonymacbook2025/.claude/commands/new-sdk-app.md`
- `NotebookLM-Protocol` — `/Users/tonymacbook2025/.claude/skills/NotebookLM-Protocol.md`
- `ralph-loop` — `/Users/tonymacbook2025/.claude/commands/ralph-loop.md`
- `review-pr` — `/Users/tonymacbook2025/.claude/commands/review-pr.md`
- `revise-claude-md` — `/Users/tonymacbook2025/.claude/commands/revise-claude-md.md`
- `Skill-Index` — `/Users/tonymacbook2025/.claude/skills/Skill-Index.md`
- `Video-Production-Workflow` — `/Users/tonymacbook2025/.claude/skills/Video-Production-Workflow.md`

## 9. Adobe & Creative App Plugins

**cep extensions:**
  - io.artlist.ai-assistant-extension

**plugins Photoshop 2025:**
  - Generator

## 10. Node.js Global Packages

**npm globals:**
```
/opt/homebrew/lib
├── @anthropic-ai/claude-code@2.1.170
├── @felores/kie-cli@0.2.0
├── @google/gemini-cli@0.45.2
├── @musistudio/claude-code-router@2.0.0
├── @openai/codex@0.137.0
├── @playwright/cli@0.1.13
├── @wavespeed/cli@0.2.3
├── corepack@0.35.0
├── firecrawl-cli@1.19.0
├── hyperframes@0.6.76
├── npm@11.12.1
├── pyright@1.1.410
├── typescript-language-server@5.3.0
├── typescript@5.9.3
├── uipro-cli@2.2.3
└── vercel@54.9.1
```

