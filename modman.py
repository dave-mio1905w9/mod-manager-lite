import argparse
import sys
from pathlib import Path
from modman.modutils import find_mods, toggle_mod, run_audit, ModNotFoundError

# Standard Steam installation path on Windows as default fallback
DEFAULT_PATH = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Stardew Valley\Mods")


def main():
    parser = argparse.ArgumentParser(
        description="Manage Stardew Valley mods (SMAPI) directly from command line."
    )
    parser.add_argument(
        "-d", "--dir",
        type=Path,
        default=DEFAULT_PATH,
        help="Path to the Stardew Valley Mods directory"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # list command
    subparsers.add_parser("list", help="List installed mods and their status")

    # enable command
    enable_parser = subparsers.add_parser("enable", help="Enable a mod")
    enable_parser.add_argument("name", help="Folder name of the mod to enable")

    # disable command
    disable_parser = subparsers.add_parser("disable", help="Disable a mod")
    disable_parser.add_argument("name", help="Folder name of the mod to disable")

    # check command
    subparsers.add_parser("check", help="Audit active mods for missing or disabled dependencies")

    args = parser.parse_args()
    mods_dir = args.dir

    if not mods_dir.exists():
        print(f"Error: Mods directory does not exist at '{mods_dir}'", file=sys.stderr)
        print("Please specify the correct path using the -d/--dir option.", file=sys.stderr)
        sys.exit(1)

    # print(f"DEBUG: resolved mods directory to: {mods_dir}")

    try:
        if args.command == "list":
            mods = find_mods(mods_dir)
            if not mods:
                print("No mods found.")
                return
            
            print(f"{'STATUS':<10} {'NAME':<35} {'VERSION':<10} {'FOLDER'}")
            print("-" * 80)
            for mod in mods:
                status = "[ ACTIVE ]" if mod.enabled else "[DISABLED]"
                print(f"{status:<10} {mod.name:<35} {mod.version:<10} {mod.folder_name}")
            
            active_count = sum(1 for m in mods if m.enabled)
            print(f"\nSummary: {active_count} enabled, {len(mods) - active_count} disabled, {len(mods)} total.")
        
        elif args.command == "enable":
            # TODO: support fuzzy matching for mod names instead of exact folder names
            new_path = toggle_mod(mods_dir, args.name, enable=True)
            print(f"Enabled mod: {args.name} -> {new_path.name}")

        elif args.command == "disable":
            new_path = toggle_mod(mods_dir, args.name, enable=False)
            print(f"Disabled mod: {args.name} -> {new_path.name}")
            
        elif args.command == "check":
            results = run_audit(mods_dir)
            
            if not results["missing_dependencies"] and not results["disabled_dependencies"]:
                print("All enabled mods have their dependencies resolved and active!")
                return
                
            if results["missing_dependencies"]:
                print("Missing dependencies (not installed):")
                for mod_name, missing in results["missing_dependencies"].items():
                    print(f"  - {mod_name} requires:")
                    for dep in missing:
                        req_ver = f" (>= {dep['Version']})" if dep.get("Version") else ""
                        print(f"      * {dep['UniqueID']}{req_ver}")
                print()
                
            if results["disabled_dependencies"]:
                print("Disabled dependencies (installed but inactive):")
                for mod_name, disabled in results["disabled_dependencies"].items():
                    print(f"  - {mod_name} depends on disabled mods:")
                    for dep in disabled:
                        print(f"      * {dep.name} ({dep.folder_name})")
                print()

    except ModNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print("Error: Permission denied. Close Stardew Valley or SMAPI if they are running.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
