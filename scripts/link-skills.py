#!/usr/bin/env python3
"""Link shared Skills and the coding standard into a local Codex scope."""

import argparse
import sys
from pathlib import Path


def main():
    shared_root = Path(__file__).resolve().parents[1]
    skills_root = shared_root / "skills"
    available = {
        folder.name: folder
        for folder in sorted(skills_root.iterdir())
        if folder.is_dir() and (folder / "SKILL.md").is_file()
    }

    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--user", action="store_true", help="use ~/.agents")
    scope.add_argument("--project", type=Path, metavar="PATH", help="use PATH/.agents")
    parser.add_argument("--dry-run", action="store_true", help="preview links without writing")
    parser.add_argument("skills", nargs="*", help="skill names (default: all; workflow includes its stages)")
    args = parser.parse_args()

    requested = list(args.skills or available)
    if "workflow" in requested:
        requested.extend(("design", "task", "code", "review", "complete"))
    selected = list(dict.fromkeys(requested))
    unknown = [name for name in selected if name not in available]
    if unknown or not selected:
        parser.error(f"Unknown or missing skills: {', '.join(unknown)}. Available: {', '.join(available)}")

    target_root = Path.home() if args.user else args.project.expanduser()
    target_root = target_root.resolve()
    if not target_root.is_dir():
        parser.error(f"Target directory does not exist: {target_root}")
    agents = target_root / ".agents"

    standard = shared_root / "standards" / "coding.md"
    if not standard.is_file():
        parser.error(f"Coding standard is missing: {standard}")

    links = [(agents / "skills" / name, available[name]) for name in selected]
    links.append((agents / "standards" / "coding.md", standard))

    pending = []
    for target, source in links:
        if target.is_symlink() and target.resolve() == source.resolve():
            print(f"Already linked: {target}")
            continue
        if target.exists() or target.is_symlink():
            parser.error(f"Link destination already exists: {target}")
        for parent in (agents, target.parent):
            if (parent.exists() or parent.is_symlink()) and not parent.is_dir():
                parser.error(f"Link destination parent is not a directory: {parent}")
        pending.append((target, source))

    for target, source in pending:
        if not args.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(source, target_is_directory=source.is_dir())
        action = "Would link" if args.dry_run else "Linked"
        print(f"{action}: {target} -> {source}")

    print(f"Coding standard: {agents / 'standards' / 'coding.md'}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError) as error:
        sys.exit(f"Could not prepare links: {error}")
