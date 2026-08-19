import json
import re
from pathlib import Path
import requests

def load_manifest(manifestPath: Path) -> dict:
    with open(manifestPath, "r", encoding="utf-8") as f:
        return json.load(f)

def is_mod_enabled(mod_dir: Path) -> bool:
    return not mod_dir.name.endswith(".disabled")

def toggle_mod(mod_dir: Path, enable: bool) -> Path:
    if enable:
        if not mod_dir.name.endswith(".disabled"):
            return mod_dir
        new_name = mod_dir.name[:-9]
        new_path = mod_dir.with_name(new_name)
        mod_dir.rename(new_path)
        return new_path
    else:
        if mod_dir.name.endswith(".disabled"):
            return mod_dir
        new_path = mod_dir.with_name(mod_dir.name + ".disabled")
        mod_dir.rename(new_path)
        return new_path

def scan_mods(mods_dir: Path) -> list[dict]:
    results = []
    # TODO: handle subfolders containing multiple nested mods (e.g. expansion packs)
    for p in mods_dir.iterdir():
        if p.is_dir():
            # print(f"Scanning directory: {p.name}")
            manifest_file = p / "manifest.json"
            if manifest_file.exists():
                try:
                    data = load_manifest(manifest_file)
                    results.append({
                        "path": p,
                        "enabled": is_mod_enabled(p),
                        "manifest": data
                    })
                except (json.JSONDecodeError, OSError):
                    continue
    return results

def parse_version(ver_str: str) -> tuple:
    # SMAPI versions can be like 1.2.3 or 1.2.3-beta
    # We split into numeric parts and ignore release tags for simple checks
    match = re.match(r"^v?(\d+)(?:\.(\d+))?(?:\.(\d+))?", ver_str.strip())
    if not match:
        return (0, 0, 0)
    parts = []
    for group in match.groups():
        parts.append(int(group) if group is not None else 0)
    return tuple(parts)

def check_github_update(update_key: str) -> dict:
    """Queries GitHub releases API to find if there is a newer version available."""
    if not update_key.startswith("GitHub:"):
        return {"status": "skipped", "reason": "not a GitHub update key"}
    
    repo = update_key.split(":", 1)[1].strip()
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    
    try:
        response = requests.get(url, headers={"User-Agent": "modman-cli"}, timeout=8)
        if response.status_code == 404:
            return {"status": "error", "reason": "repository or release not found"}
        response.raise_for_status()
        data = response.json()
        
        tag_name = data.get("tag_name", "")
        html_url = data.get("html_url", "")
        return {
            "status": "success",
            "latest_version": tag_name,
            "url": html_url
        }
    except requests.RequestException as e:
        return {"status": "error", "reason": str(e)}
