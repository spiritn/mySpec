#!/usr/bin/env python3
"""Link the two review roles and three skills to this checkout (Python 3.11+)."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
import tomllib


SKILLS = ('project-requirements', 'project-research', 'project-adr')
ROLES = ('project_director', 'independent_reviewer')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skills-dir', type=Path, default=Path.home() / '.agents' / 'skills')
    codex_dir = Path(os.environ.get('CODEX_HOME') or Path.home() / '.codex')
    parser.add_argument('--agents-dir', type=Path, default=codex_dir / 'agents')
    parser.add_argument('--overwrite', action='store_true', help='先备份已有文件、目录或其他软链，再建立链接')
    parser.add_argument('--dry-run', action='store_true', help='只查看计划，不写文件')
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    skills_dir = args.skills_dir.expanduser().resolve()
    agents_dir = args.agents_dir.expanduser().resolve()
    if any(p == source or source in p.parents for p in (skills_dir, agents_dir)):
        raise ValueError('请选择仓库之外的安装目录')
    if skills_dir == agents_dir or skills_dir in agents_dir.parents or agents_dir in skills_dir.parents:
        raise ValueError('技能目录与角色目录不能相同或互相嵌套')
    links = []
    for name in SKILLS:
        folder = source / 'skills' / name
        if not (folder / 'SKILL.md').is_file():
            raise ValueError(f'缺少技能入口：{folder}')
        links.append((skills_dir / name, folder))
    for name in ROLES:
        path = source / 'agents' / f'{name}.toml'
        role = tomllib.loads(path.read_text(encoding='utf-8'))
        if role.get('name') != name or not role.get('developer_instructions'):
            raise ValueError(f'角色定义不完整：{path}')
        links.append((agents_dir / path.name, path))
    pending, conflicts = [], []
    for target, origin in links:
        if target.is_symlink() and target.resolve() == origin.resolve():
            print(f'已链接：{target} -> {origin}')
            continue
        pending.append((target, origin))
        if target.exists() or target.is_symlink():
            conflicts.append(target)
    for target, origin in pending:
        print(f'将链接：{target} -> {origin}')
    print(f'待链接 {len(pending)} 个；已有内容需备份 {len(conflicts)} 个')
    if args.dry_run:
        return 0
    if conflicts and not args.overwrite:
        print('目标已有内容，未修改；先查看 --dry-run，确认迁移时加 --overwrite。', file=sys.stderr)
        return 1
    # Preflight all target parents before moving any existing configuration.
    for target, _ in pending:
        for parent in target.parents:
            if (parent.exists() or parent.is_symlink()) and not parent.is_dir():
                raise ValueError(f'目标父路径不是目录：{parent}')
    moved, created = [], []
    try:
        if conflicts:
            backup_parent = agents_dir.parent / 'direction-review-backups'
            backup_parent.mkdir(parents=True, exist_ok=True)
            backup = Path(tempfile.mkdtemp(prefix='before-link-', dir=backup_parent))
            manifest = [{'original': str(t), 'backup': f'{i:03d}-{t.name}'}
                        for i, t in enumerate(conflicts)]
            (backup / 'manifest.json').write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
            for target, record in zip(conflicts, manifest):
                saved = backup / record['backup']
                target.rename(saved)
                moved.append((target, saved))
            print(f'原配置备份：{backup}')
        for target, origin in pending:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(origin, target_is_directory=origin.is_dir())
            created.append(target)
    except OSError:
        for target in reversed(created):
            target.unlink()
        for target, saved in reversed(moved):
            saved.rename(target)
        raise
    print('软链安装完成。编辑用户目录或仓库中的对应文件，修改都会落在仓库；请新开 Codex 聊天。')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(f'安装失败：{error}', file=sys.stderr)
        raise SystemExit(1)
