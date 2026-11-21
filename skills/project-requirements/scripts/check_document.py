#!/usr/bin/env python3
"""Check a review brief or an overview's opening summary and Mermaid limits."""
import argparse
import html
import json
import re
from pathlib import Path


def visible(text):
    literals = []
    def save_literal(match):
        literals.append(match.group(2))
        return f'\ue000{len(literals) - 1}\ue001'
    text = re.sub(r'(`+)(.*?)\1', save_literal, text)
    text = re.sub(r'!\[([^\]]*)\]\([^\n]*?\)', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^\n]*?\)', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\[[^\]]*\]', r'\1', text)
    text = re.sub(r'^\s*\[[^\]]+\]:\s*\S+.*$', '', text, flags=re.M)
    lines = []
    for line in text.splitlines():
        if re.fullmatch(r'\s*\|?[\s:|\-]+\|?\s*', line):
            continue
        line = re.sub(r'^\s{0,3}#{1,6}\s+', '', line)
        line = re.sub(r'^\s*(?:[-+*]|\d+[.)])\s+', '', line)
        line = re.sub(r'^\s*>\s?', '', line)
        line = re.sub(r'(\*\*|__)(.+?)\1', r'\2', line)
        line = re.sub(r'(?<!\w)([*_])([^\n]+?)\1(?!\w)', r'\2', line)
        if line.strip().startswith('|'):
            line = line.replace('|', '')
        lines.append(line)
    output = '\n'.join(lines)
    output = re.sub(r'\ue000(\d+)\ue001', lambda m: literals[int(m.group(1))], output)
    return re.sub(r'\s+', '', html.unescape(output))


def diagram_nodes(code):
    lines = [s.strip() for s in code.splitlines() if s.strip() and not s.lstrip().startswith('%%')]
    if not lines or not re.fullmatch(r'(?:flowchart|graph)\s+(?:TD|TB|BT|LR|RL);?', lines[0]):
        raise ValueError('只支持简单 flowchart/graph 主图')
    nodes = set()
    for line in lines[1:]:
        # Permit basic labeled nodes, labeled edges and chained edges only.
        line = re.sub(r'([A-Za-z][\w-]*)\s*(\[[^\]]*\]|\([^)]*\)|\{[^}]*\})', r'\1', line)
        line = re.sub(r'\|[^|]*\|', '', line)
        parts = re.split(r'\s*(?:-->|-\.->|==>|---)\s*|;', line)
        for part in filter(None, (p.strip() for p in parts)):
            if not re.fullmatch(r'[A-Za-z][\w-]*', part):
                raise ValueError('不支持的 Mermaid 语法：' + part)
            nodes.add(part)
    return len(nodes)


def check(text, brief=False, max_chars=300, first_chars=100, max_nodes=7):
    errors = []
    text = text.lstrip('\ufeff')
    if text.startswith('---\n'):
        end = text.find('\n---', 4)
        if end < 0:
            errors.append('frontmatter 未闭合')
        else:
            text = text[end + 4:].lstrip('\n')
    if re.search(r'<\/?[A-Za-z!][^>]*>', text):
        errors.append('不支持 HTML；请用普通 Markdown，避免隐藏正文')
    prose, block = [], []
    fence = None
    kind = ''
    diagrams = []
    code_chars = 0
    for line in text.splitlines():
        m = re.match(r'^\s{0,3}(`{3,}|~{3,})(.*)$', line)
        if fence is None and m:
            fence, kind, block = m.group(1), m.group(2).strip().lower(), []
        elif fence is not None and m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) and not m.group(2).strip():
            code = '\n'.join(block)
            if kind == 'mermaid':
                try:
                    diagrams.append(diagram_nodes(code))
                except ValueError as exc:
                    errors.append(str(exc))
            else:
                code_chars += len(re.sub(r'\s+', '', code))
            fence = None
        elif fence is not None:
            block.append(line)
        else:
            prose.append(line)
    if fence is not None:
        errors.append('代码块未闭合')
        prose.extend(block)
    body = '\n'.join(prose)
    chars = len(visible(body)) + code_chars
    paragraph = []
    for line in prose:
        if not paragraph and (not line.strip() or re.match(r'^\s*#{1,6}\s', line)):
            continue
        if paragraph and not line.strip():
            break
        paragraph.append(line)
    first = len(visible('\n'.join(paragraph)))
    if brief:
        if chars > max_chars:
            errors.append(f'正文 {chars} > {max_chars}')
        if first > first_chars:
            errors.append(f'首段 {first} > {first_chars}')
        if not first:
            errors.append('缺少首段结论')
        if len(diagrams) > 1:
            errors.append('审阅页最多一张主图')
    if any(n > max_nodes for n in diagrams):
        errors.append(f'主图节点超限：{diagrams}，每图最多 {max_nodes}')
    return {'ok': not errors, 'body_chars': chars, 'first_paragraph_chars': first,
            'diagram_nodes': diagrams, 'errors': errors}


def check_overview(text, max_chars=300, first_chars=100, max_nodes=7):
    """Budget only the opening '当前判断'; check format and diagrams everywhere."""
    full = check(text, max_chars=max_chars, first_chars=first_chars, max_nodes=max_nodes)
    errors = list(full['errors'])
    body = text.lstrip('\ufeff')
    metadata = re.match(r'\A---\n.*?\n---(?:\n|\Z)', body, re.S)
    if metadata:
        body = body[metadata.end():]
    lines = body.splitlines()
    headings = []
    fence = None
    for index, line in enumerate(lines):
        marker = re.match(r'^\s{0,3}(`{3,}|~{3,})(.*)$', line)
        if fence is not None:
            if (marker and marker.group(1)[0] == fence[0]
                    and len(marker.group(1)) >= len(fence)
                    and not marker.group(2).strip()):
                fence = None
            continue
        if marker:
            fence = marker.group(1)
            continue
        heading = re.match(r'^ {0,3}(#{1,6})[ \t]+(.+?)[ \t]*$', line)
        if heading:
            title = re.sub(r'[ \t]+#+$', '', heading.group(2))
            headings.append((index, len(heading.group(1)), title))
    starts = [index for index, level, title in headings
              if level == 2 and title == '当前判断']
    summary = None
    if not starts:
        errors.append('缺少二级章节：## 当前判断')
    else:
        if len(starts) != 1:
            errors.append('当前判断章节重复；只保留一个')
        start = starts[0]
        prefix = [index for index in range(start) if lines[index].strip()]
        if prefix and (len(prefix) != 1 or not any(
                index == prefix[0] and level == 1 for index, level, _ in headings)):
            errors.append('当前判断必须位于正文开头，之前只允许一个一级标题及空行')
        end = next((index for index, level, _ in headings
                    if index > start and level <= 2), len(lines))
        summary = check('\n'.join(lines[start:end]), brief=True,
                        max_chars=max_chars, first_chars=first_chars, max_nodes=max_nodes)
        errors.extend('当前判断：' + error for error in summary['errors'])
    return {
        'ok': not errors,
        'mode': 'overview',
        'full_document_chars': full['body_chars'],
        'summary_chars': summary['body_chars'] if summary else None,
        'summary_first_paragraph_chars': summary['first_paragraph_chars'] if summary else None,
        'diagram_nodes': full['diagram_nodes'],
        'errors': errors,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--brief', action='store_true', help='整份文件按300字审阅检查')
    mode.add_argument('--overview', action='store_true', help='仅开头的当前判断按300字检查')
    parser.add_argument('--max-chars', type=int, default=300)
    parser.add_argument('--first-chars', type=int, default=100)
    parser.add_argument('--max-nodes', type=int, default=7)
    args = parser.parse_args()
    text = args.file.read_text(encoding='utf-8')
    if args.overview:
        result = check_overview(text, args.max_chars, args.first_chars, args.max_nodes)
    else:
        result = check(text, args.brief, args.max_chars, args.first_chars, args.max_nodes)
    print(json.dumps({'file': str(args.file), **result}, ensure_ascii=False))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
