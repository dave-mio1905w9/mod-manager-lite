# mod-manager-lite

A quick CLI tool to manage my Stardew Valley mods. It parses SMAPI manifests, toggles mods by adding/removing a `.disabled` suffix, and checks for updates.

I built this because I play on Windows, dislike heavy electron managers, and wanted a quick way to audit my 40+ mods.

## Setup

Clone this repo and install requirements:

```cmd
pip install -r requirements.txt
```

You can set the `MOD_DIR` environment variable to avoid passing the path every time:

```cmd
set MOD_DIR=C:\Program Files (x86)\Steam\steamapps\common\Stardew Valley\Mods
```

## Commands

List all mods, their status, and versions:
```cmd
python modman.py list
```

Disable a mod:
```cmd
python modman.py disable "UI Info Suite 2"
```

Enable a mod:
```cmd
python modman.py enable "UI Info Suite 2"
```

Check GitHub updates for mods that have an UpdateKeys entry pointing to GitHub:
```cmd
python modman.py check
```

<!-- last-checked: 2026-09-18 -->
