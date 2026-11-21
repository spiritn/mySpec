#!/usr/bin/env python3
"""Install the two roles and three skills; requires Python 3.11 or newer."""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import tomllib


SKILLS = ('project-requirements', 'project-research', 'project-adr')
ROLES = ('project_director', 'independent_reviewer')
TOKEN = '{{SKILLS_DIR}}'


def plan_install(source, skills_dir, agents_dir):
    plan = []
    for name in SKILLS:
        folder = source / 'skills' / name
        if not (folder / 'SKILL.md').is_file():
            raise ValueError(f'缺少技能入口：{folder / "SKILL.md"}')
        for path in sorted(folder.rglob('*')):
            if '__pycache__' in path.parts or path.name.startswith('.'):
                continue
            if path.is_symlink():
                raise ValueError(f'源文件不能是符号链接：{path}')
            if path.is_file():
                text = path.read_text(encoding='utf-8').replace(TOKEN, skills_dir.as_posix())
                plan.append((skills_dir / name / path.relative_to(folder), text.encode('utf-8')))
    for name in ROLES:
        path = source / 'agents' / f'{name}.toml'
        replacement = skills_dir.as_posix().replace('\\', '\\\\').replace('"', '\\"')
        text = path.read_text(encoding='utf-8').replace(TOKEN, replacement)
        role = tomllib.loads(text)
        if role.get('name') != name or not role.get('developer_instructions'):
            raise ValueError(f'角色定义不完整：{path}')
        plan.append((agents_dir / path.name, text.encode('utf-8')))
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skills-dir', type=Path, default=Path.home() / '.agents' / 'skills')
    codex_dir = Path(os.environ.get('CODEX_HOME') or Path.home() / '.codex')
    parser.add_argument('--agents-dir', type=Path, default=codex_dir / 'agents')
    parser.add_argument('--overwrite', action='store_true', help='先备份，再更新内容不同的文件')
    parser.add_argument('--dry-run', action='store_true', help='只查看计划，不写文件')
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    skills_dir = args.skills_dir.expanduser().resolve()
    agents_dir = args.agents_dir.expanduser().resolve()
    if any(c in str(p) for p in (skills_dir, agents_dir) for c in ('\n', '\r')):
        raise ValueError('安装路径不能含换行')
    if any(p == source or source in p.parents for p in (skills_dir, agents_dir)):
        raise ValueError('请选择仓库之外的安装目录，避免修改源模板')
    if skills_dir == agents_dir or skills_dir in agents_dir.parents or agents_dir in skills_dir.parents:
        raise ValueError('技能目录与角色目录不能相同或互相嵌套')
    plan = plan_install(source, skills_dir, agents_dir)
    changes, conflicts = [], []
    for target, data in plan:
        if target.is_symlink() or (target.exists() and not target.is_file()):
            raise ValueError(f'目标不是普通文件：{target}')
        if target.exists() and target.read_bytes() == data:
            continue
        changes.append((target, data))
        if target.exists():
            conflicts.append(target)
    print(f'技能目录：{skills_dir}\n角色目录：{agents_dir}')
    print(f'待写入 {len(changes)} 个文件；内容相同 {len(plan) - len(changes)} 个；冲突 {len(conflicts)} 个')
    if conflicts and not args.overwrite:
        print('已有不同内容，未写入任何文件；确认更新时加 --overwrite。', file=sys.stderr)
        for target in conflicts:
            print(f'  {target}', file=sys.stderr)
        return 1
    if args.dry_run:
        for target, _ in changes:
            print(f'将写入：{target}')
        return 0
    # Finish all conflict checks before making any changes.
    if conflicts:
        backup_parent = agents_dir.parent / 'direction-review-backups'
        backup_parent.mkdir(parents=True, exist_ok=True)
        backup = Path(tempfile.mkdtemp(prefix='before-update-', dir=backup_parent))
        index = []
        for i, target in enumerate(conflicts):
            saved = backup / f'{i:03d}-{target.name}'
            shutil.copy2(target, saved)
            index.append({'original': str(target), 'backup': saved.name})
        (backup / 'manifest.json').write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'旧文件备份：{backup}')
    for target, data in changes:
        target.parent.mkdir(parents=True, exist_ok=True)
        # Atomic replacement avoids leaving a half-written role or skill.
        handle, temporary = tempfile.mkstemp(prefix='.direction-review-', dir=target.parent)
        try:
            with os.fdopen(handle, 'wb') as stream:
                stream.write(data)
            os.replace(temporary, target)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    print('安装完成。请新开 Codex 聊天，加载这两个角色和三个技能。')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(f'安装失败：{error}', file=sys.stderr)
        raise SystemExit(1)
