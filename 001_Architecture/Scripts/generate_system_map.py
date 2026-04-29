#!/usr/bin/env python3
"""
generate_system_map.py

Scans the entire macOS system and generates System-Map.md in
001_Architecture/Install_Maps/. Run manually or via weekly cron.
No external dependencies — stdlib + subprocess only.
"""

import subprocess
import json
import plistlib
import re
from pathlib import Path
import datetime

# ── Config ────────────────────────────────────────────────────────────────────

HOME = Path.home()
WORKSPACE = Path("/Users/tonymacbook2025/Documents/Claude-Agent")
OUTPUT_DIR = WORKSPACE / "001_Architecture" / "Install_Maps"
OUTPUT_MD  = OUTPUT_DIR / "System-Map.md"
OUTPUT_JSON = OUTPUT_DIR / "system_map_data.json"

DOCKER_DOCS = HOME / "Documents" / "Docker"
PYTHON_DOCS = HOME / "Documents" / "Python"
AUTO_DOCS   = HOME / "Documents" / "Automations"

# Patterns applied only when scanning Python scripts
PY_SKIP_PATTERNS = [
    ".venv", "venv", "site-packages", "__pycache__", ".git",
    "node_modules", "dist", "build", ".tox",
    "ComfyUI",             # ComfyUI library tree
    "Google Drive Backup", # Backup copies only
    "backups",
    "docker_config",
    "baserow-data", "n8n-data", "flowise-data", "kokoro-data",
    "qdrant_storage", "postgres_storage", "minio-data",
    "openwebui-data", "nca-toolkit",
    "huggingface",
]

SKIP_PATTERNS = PY_SKIP_PATTERNS  # keep alias for other uses

# ── Helpers ───────────────────────────────────────────────────────────────────

def run(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception:
        return ""

def safe_json_lines(text):
    out = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out

# ── Scanners ──────────────────────────────────────────────────────────────────

def scan_apps():
    apps = []
    for search_dir in [Path("/Applications"), HOME / "Applications"]:
        if not search_dir.exists():
            continue
        for app in sorted(search_dir.glob("**/*.app")):
            plist_path = app / "Contents" / "Info.plist"
            entry = {"name": app.stem, "version": "—", "bundle_id": "", "path": str(app)}
            if plist_path.exists():
                try:
                    with open(plist_path, "rb") as f:
                        p = plistlib.load(f)
                    entry["name"]      = p.get("CFBundleName") or app.stem
                    entry["version"]   = p.get("CFBundleShortVersionString", "—")
                    entry["bundle_id"] = p.get("CFBundleIdentifier", "")
                except Exception:
                    pass
            apps.append(entry)
    return sorted(apps, key=lambda x: x["name"].lower())


def scan_homebrew():
    formulae, casks = [], []
    for line in run(["brew", "list", "--versions"]).splitlines():
        parts = line.split()
        if parts:
            formulae.append({"name": parts[0], "versions": parts[1:]})
    for line in run(["brew", "list", "--cask", "--versions"]).splitlines():
        parts = line.split()
        if parts:
            casks.append({"name": parts[0], "versions": parts[1:]})
    return formulae, casks


def scan_python():
    installs = []
    seen_paths = set()
    for cmd in ["python3", "python", "python3.11", "python3.12", "python3.13", "python3.10"]:
        path = run(["which", cmd])
        if path and path not in seen_paths:
            seen_paths.add(path)
            version = run([cmd, "--version"])
            installs.append({"command": cmd, "version": version, "path": path})

    pyenv_out = run(["pyenv", "versions"])
    if pyenv_out:
        installs.append({"pyenv_versions": pyenv_out})

    conda_out = run(["conda", "env", "list"])
    if conda_out:
        installs.append({"conda_envs": conda_out})

    return installs


def scan_venvs():
    venvs, seen = [], set()
    search_roots = [HOME / "Documents", HOME / "Desktop", WORKSPACE]
    for root in search_roots:
        if not root.exists():
            continue
        for cfg in root.glob("**/.venv/pyvenv.cfg"):
            p = str(cfg.parent)
            if p not in seen:
                seen.add(p); venvs.append(p)
        for cfg in root.glob("**/venv/pyvenv.cfg"):
            p = str(cfg.parent)
            if p not in seen:
                seen.add(p); venvs.append(p)
    return venvs


def scan_docker():
    info = {"containers": [], "images": [], "volumes": [], "networks": [], "compose_files": []}

    info["containers"] = safe_json_lines(run(["docker", "ps", "-a", "--format", "{{json .}}"]))
    info["images"]     = safe_json_lines(run(["docker", "images", "--format", "{{json .}}"]))
    info["volumes"]    = safe_json_lines(run(["docker", "volume", "ls", "--format", "{{json .}}"]))
    info["networks"]   = safe_json_lines(run(["docker", "network", "ls", "--format", "{{json .}}"]))

    compose_skip = [".git", "node_modules", "Google Drive Backup"]
    compose_files = []
    for search_root in [HOME / "Documents", WORKSPACE]:
        if not search_root.exists():
            continue
        for pattern in ["**/docker-compose.yml", "**/docker-compose.yaml", "**/compose.yml", "**/compose.yaml"]:
            for cf in search_root.glob(pattern):
                if not any(s in str(cf) for s in compose_skip):
                    compose_files.append(str(cf))
    info["compose_files"] = sorted(set(compose_files))
    return info


def scan_mcps():
    mcps = {}
    paths_to_check = [
        HOME / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json",
        HOME / ".claude" / "claude_desktop_config.json",
        WORKSPACE / ".claude" / "settings.json",
        HOME / ".claude" / "settings.json",
    ]
    for p in paths_to_check:
        if p.exists():
            try:
                with open(p) as f:
                    config = json.load(f)
                if "mcpServers" in config:
                    mcps[str(p)] = list(config["mcpServers"].keys())
            except Exception:
                pass
    return mcps


def scan_docker_mcp_servers():
    """
    Identify MCP servers available via Docker MCP Gateway.
    Docker Desktop manages these via its UI; no CLI list command exists.
    We extract candidates from: docker catalog, running containers, and TOOLBOX.md.
    """
    servers = []

    # Docker MCP catalog lists available servers (not necessarily enabled)
    catalog = HOME / ".docker" / "mcp" / "catalog.json"
    if catalog.exists():
        try:
            with open(catalog) as f:
                d = json.load(f)
            for name, meta in d.get("catalogs", {}).items():
                servers.append(f"{name} (catalog: {meta.get('displayName', '')})")
        except Exception:
            pass

    # Running containers that look like MCP tools
    container_names = run(["docker", "ps", "--format", "{{.Names}}"]).splitlines()
    mcp_keywords = ["mcp", "obsidian", "wikidata", "cloudflare", "google", "notion",
                    "github", "slack", "figma", "linear", "blotato"]
    for name in container_names:
        if any(k in name.lower() for k in mcp_keywords):
            servers.append(f"container:{name}")

    # Extract from TOOLBOX.md if it documents MCPs
    toolbox = WORKSPACE / "TOOLBOX.md"
    if toolbox.exists():
        content = toolbox.read_text(errors="ignore")
        mcp_section = re.search(r"(?:## MCP|## MCP Servers)(.*?)(?:\n## |\Z)", content, re.DOTALL)
        if mcp_section:
            for line in mcp_section.group(1).splitlines():
                line = line.strip()
                if line.startswith("-") or line.startswith("*"):
                    servers.append(f"toolbox:{line.lstrip('-* ').strip()}")

    seen = set()
    return [s for s in servers if not (s in seen or seen.add(s))]


def scan_mcp_secrets():
    secrets_file = HOME / ".mcp-secrets.env"
    if not secrets_file.exists():
        return []
    names = []
    with open(secrets_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                names.append(line.split("=")[0])
    return names


def scan_clis():
    known = [
        "gh", "git", "node", "npm", "npx", "bun", "deno",
        "firecrawl", "docker", "docker-compose",
        "ffmpeg", "ffprobe", "imagemagick", "convert", "magick",
        "graphify", "obsidian", "claude", "codex",
        "terraform", "kubectl", "helm",
        "aws", "gcloud", "az",
        "jq", "yq", "fd", "rg", "fzf", "tmux", "zsh", "bash",
        "poetry", "uv", "pip3", "pip",
        "yt-dlp", "youtube-dl", "wget", "curl",
        "exiftool", "sox", "lame",
        "supabase", "vercel", "netlify",
        "blotato", "n8n",
    ]
    clis = []
    for cli in known:
        path = run(["which", cli])
        if path:
            for flag in ["--version", "version", "-v", "-V"]:
                version = run([cli, flag], timeout=5)
                if version:
                    version = version.split("\n")[0][:100]
                    break
            else:
                version = "—"
            clis.append({"name": cli, "version": version, "path": path})
    return clis


def extract_description(py_path: Path) -> str:
    try:
        content = py_path.read_text(errors="ignore")[:2000]
    except Exception:
        return "(unreadable)"

    # Module-level docstring
    m = re.search(r'^"""(.*?)"""', content, re.DOTALL | re.MULTILINE)
    if m:
        first_line = m.group(1).strip().split("\n")[0].strip()
        if len(first_line) > 8:
            return first_line

    m = re.search(r"^'''(.*?)'''", content, re.DOTALL | re.MULTILINE)
    if m:
        first_line = m.group(1).strip().split("\n")[0].strip()
        if len(first_line) > 8:
            return first_line

    # First non-shebang comment line
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("#") and not line.startswith("#!/") and not line.startswith("# -*-"):
            desc = line.lstrip("#").strip()
            if len(desc) > 8:
                return desc

    return "(no description)"


def scan_python_scripts():
    scripts, seen = [], set()
    search_dirs = [
        HOME / "Documents",
        WORKSPACE,
    ]
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        for py_file in sorted(search_dir.glob("**/*.py")):
            if any(pat in str(py_file) for pat in PY_SKIP_PATTERNS):
                continue
            if str(py_file) in seen:
                continue
            seen.add(str(py_file))
            scripts.append({
                "name": py_file.name,
                "path": str(py_file),
                "description": extract_description(py_file),
            })
    return sorted(scripts, key=lambda x: x["name"].lower())


def scan_skills():
    # Direct skill dirs: ~/.claude/skills/, ~/.claude/commands/, project-local equivalents
    # Plugin cache: only the top-level skill .md files inside each plugin's skills/ subdir
    skill_dirs = [
        HOME / ".claude" / "skills",
        HOME / ".claude" / "commands",
        WORKSPACE / ".claude" / "skills",
        WORKSPACE / ".claude" / "commands",
    ]
    skills, seen = [], set()

    # Direct dirs: one level deep only (each file IS a skill)
    for d in skill_dirs:
        if d.exists():
            for f in d.glob("*.md"):
                if str(f) not in seen:
                    seen.add(str(f))
                    skills.append({"name": f.stem, "path": str(f)})

    # Plugin cache: skills live at <plugin>/skills/<name>.md
    plugin_cache = HOME / ".claude" / "plugins" / "cache"
    if plugin_cache.exists():
        for skill_file in plugin_cache.glob("*/*/skills/*.md"):
            if str(skill_file) not in seen:
                seen.add(str(skill_file))
                skills.append({"name": skill_file.stem, "path": str(skill_file)})
        # Also versioned: <vendor>/<plugin>/<version>/skills/<name>.md
        for skill_file in plugin_cache.glob("*/*/*/skills/*.md"):
            if str(skill_file) not in seen:
                seen.add(str(skill_file))
                skills.append({"name": skill_file.stem, "path": str(skill_file)})

    return sorted(skills, key=lambda x: x["name"].lower())


def scan_node_globals():
    npm_out  = run(["npm", "list", "-g", "--depth=0"])
    bun_path = run(["which", "bun"])
    bun_out  = run(["bun", "pm", "ls", "-g"]) if bun_path else ""
    return {"npm_globals": npm_out, "bun_globals": bun_out}


def scan_adobe_plugins():
    plugins = {}

    for cep_dir in [
        Path("/Library/Application Support/Adobe/CEP/extensions"),
        HOME / "Library" / "Application Support" / "Adobe" / "CEP" / "extensions",
    ]:
        key = "cep_extensions" if "/Library/" not in str(cep_dir) or "home" not in str(cep_dir).lower() else "user_cep_extensions"
        if cep_dir.exists():
            plugins[key] = [d.name for d in sorted(cep_dir.iterdir()) if d.is_dir()]

    adobe_apps = [
        "Photoshop 2025", "Photoshop 2024",
        "After Effects 2025", "After Effects 2024",
        "Premiere Pro 2025", "Premiere Pro 2024",
        "Illustrator 2025", "Illustrator 2024",
        "Lightroom Classic",
        "DaVinci Resolve",
    ]
    for app_name in adobe_apps:
        plugin_dir = Path(f"/Applications/Adobe {app_name}/Plug-ins")
        if not plugin_dir.exists():
            plugin_dir = Path(f"/Applications/{app_name}/Plug-ins")
        if plugin_dir.exists():
            key = f"plugins_{app_name.replace(' ', '_')}"
            plugins[key] = [p.name for p in sorted(plugin_dir.iterdir())]

    return plugins


# ── Markdown Generator ────────────────────────────────────────────────────────

def md_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")
    for row in rows:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(lines)


def generate_markdown(data):
    ts = data["generated_at"]
    out = [
        "---",
        "title: System Map",
        "type: install-map",
        "tags: [system-map, install-map, tools, assets]",
        "---",
        "",
        "# System Map",
        "",
        f"> **Auto-generated:** {ts}  ",
        "> Do not edit manually. Refresh by running:",
        "> `python3 /Users/tonymacbook2025/Documents/Claude-Agent/001_Architecture/Scripts/generate_system_map.py`",
        "",
        "**When Tony says 'look at the system map' — this is that file.**",
        "",
        "---",
        "",
        "## Table of Contents",
        "1. [Installed Applications](#1-installed-applications)",
        "2. [Homebrew — Formulae & Casks](#2-homebrew--formulae--casks)",
        "3. [Python Installs & Virtual Environments](#3-python-installs--virtual-environments)",
        "4. [Docker](#4-docker)",
        "5. [MCP Servers](#5-mcp-servers)",
        "6. [CLIs](#6-clis)",
        "7. [Python Scripts](#7-python-scripts)",
        "8. [Claude Code Skills](#8-claude-code-skills)",
        "9. [Adobe & Creative App Plugins](#9-adobe--creative-app-plugins)",
        "10. [Node.js Global Packages](#10-nodejs-global-packages)",
        "",
        "---",
        "",
    ]

    # 1. Apps
    out += ["## 1. Installed Applications", ""]
    rows = [(a["name"], a["version"], f"`{a['path']}`") for a in data["apps"]]
    out += [md_table(["App", "Version", "Path"], rows), ""]

    # 2. Homebrew
    out += ["## 2. Homebrew — Formulae & Casks", "", "### Formulae", ""]
    formulae_rows = [(p["name"], ", ".join(p["versions"])) for p in data["homebrew"]["formulae"]]
    out += [md_table(["Package", "Version(s)"], formulae_rows), ""]
    out += ["### Casks", ""]
    cask_rows = [(c["name"], ", ".join(c["versions"])) for c in data["homebrew"]["casks"]]
    out += [md_table(["Cask", "Version(s)"], cask_rows), ""]

    # 3. Python
    out += ["## 3. Python Installs & Virtual Environments", "", "### Python Installations", ""]
    for p in data["python"]["installs"]:
        if "pyenv_versions" in p:
            out += [f"**pyenv:**", "```", p["pyenv_versions"], "```", ""]
        elif "conda_envs" in p:
            out += [f"**conda:**", "```", p["conda_envs"], "```", ""]
        else:
            out.append(f"- `{p['command']}` → `{p['path']}` — {p['version']}")
    out += ["", "### Virtual Environments", ""]
    for v in data["python"]["venvs"]:
        out.append(f"- `{v}`")
    out += [""]

    # 4. Docker
    out += ["## 4. Docker", ""]
    d = data["docker"]

    out += ["### Containers", ""]
    container_rows = []
    for c in d["containers"]:
        name   = c.get("Names") or c.get("Name", "—")
        image  = c.get("Image", "—")
        status = c.get("Status", "—")
        ports  = c.get("Ports", "—")
        container_rows.append((name, image, status, ports))
    out += [md_table(["Name", "Image", "Status", "Ports"], container_rows), ""]

    out += ["### Images", ""]
    image_rows = [
        (img.get("Repository", "—"), img.get("Tag", "—"), img.get("Size", "—"), str(img.get("ID", "—"))[:12])
        for img in d["images"]
    ]
    out += [md_table(["Repository", "Tag", "Size", "ID"], image_rows), ""]

    out += ["### Volumes", ""]
    for v in d["volumes"]:
        out.append(f"- `{v.get('Name', v)}`")
    out += [""]

    out += ["### Networks", ""]
    for n in d["networks"]:
        out.append(f"- `{n.get('Name', n)}` (driver: {n.get('Driver', '—')})")
    out += [""]

    out += ["### Docker Compose Files", ""]
    for cf in d["compose_files"]:
        out.append(f"- `{cf}`")
    out += [""]

    # 5. MCPs
    out += ["## 5. MCP Servers", ""]
    out += ["### Config-Registered MCPs", ""]
    for config_path, server_list in data["mcps"].items():
        out.append(f"**Config:** `{config_path}`")
        for s in sorted(server_list):
            out.append(f"- {s}")
        out.append("")
    docker_mcps = data.get("docker_mcp_servers", [])
    if docker_mcps:
        out += ["### Docker MCP Gateway Servers", ""]
        out.append("_(Served via `MCP_DOCKER` gateway — `docker mcp gateway run`)_")
        out.append("")
        for s in docker_mcps:
            out.append(f"- {s}")
        out.append("")
    out += ["### MCP Secret Keys (names only, no values)", ""]
    for k in data.get("mcp_secret_keys", []):
        out.append(f"- `{k}`")
    out += [""]

    # 6. CLIs
    out += ["## 6. CLIs", ""]
    cli_rows = [(f"`{c['name']}`", c["version"].split("\n")[0][:80], f"`{c['path']}`") for c in data["clis"]]
    out += [md_table(["CLI", "Version", "Path"], cli_rows), ""]

    # 7. Python Scripts
    out += ["## 7. Python Scripts", ""]
    script_rows = [(f"`{s['name']}`", s["description"], f"`{s['path']}`") for s in data["python_scripts"]]
    out += [md_table(["Script", "Description", "Path"], script_rows), ""]

    # 8. Skills
    out += ["## 8. Claude Code Skills", ""]
    for s in data["skills"]:
        out.append(f"- `{s['name']}` — `{s['path']}`")
    out += [""]

    # 9. Adobe plugins
    out += ["## 9. Adobe & Creative App Plugins", ""]
    for key, val in data.get("adobe_plugins", {}).items():
        out.append(f"**{key.replace('_', ' ')}:**")
        if val:
            for plugin in val:
                out.append(f"  - {plugin}")
        else:
            out.append("  _(none found)_")
        out.append("")

    # 10. Node globals
    out += ["## 10. Node.js Global Packages", ""]
    npm_out = data.get("node", {}).get("npm_globals", "")
    bun_out = data.get("node", {}).get("bun_globals", "")
    if npm_out:
        out += ["**npm globals:**", "```", npm_out, "```", ""]
    if bun_out:
        out += ["**bun globals:**", "```", bun_out, "```", ""]

    return "\n".join(out) + "\n"


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Scanning apps...")
    apps = scan_apps()

    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Scanning Homebrew...")
    formulae, casks = scan_homebrew()

    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Scanning Python...")
    py_installs = scan_python()
    venvs       = scan_venvs()

    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Scanning Docker...")
    docker = scan_docker()

    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Scanning MCPs...")
    mcps                = scan_mcps()
    mcp_secret_keys     = scan_mcp_secrets()
    docker_mcp_servers  = scan_docker_mcp_servers()

    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Scanning CLIs...")
    clis = scan_clis()

    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Scanning Python scripts...")
    py_scripts = scan_python_scripts()

    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Scanning skills...")
    skills = scan_skills()

    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Scanning Node globals...")
    node = scan_node_globals()

    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Scanning Adobe plugins...")
    adobe = scan_adobe_plugins()

    data = {
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "apps": apps,
        "homebrew": {"formulae": formulae, "casks": casks},
        "python": {"installs": py_installs, "venvs": venvs},
        "docker": docker,
        "mcps": mcps,
        "mcp_secret_keys": mcp_secret_keys,
        "docker_mcp_servers": docker_mcp_servers,
        "clis": clis,
        "python_scripts": py_scripts,
        "skills": skills,
        "adobe_plugins": adobe,
        "node": node,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_JSON, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"JSON  → {OUTPUT_JSON}")

    md = generate_markdown(data)
    with open(OUTPUT_MD, "w") as f:
        f.write(md)
    print(f"Map   → {OUTPUT_MD}")
    print("Done.")


if __name__ == "__main__":
    main()
