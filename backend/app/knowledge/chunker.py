"""Markdown 分块：按标题与段落切分，便于向量检索。"""
from __future__ import annotations

import re

_HEADING_RE = re.compile(r"^(#{1,4})\s+(.+)$", re.MULTILINE)


def chunk_markdown(text: str, *, max_chars: int = 480) -> list[tuple[str, str]]:
    """返回 (section_title, chunk_text) 列表。"""
    text = text.strip()
    if not text:
        return []

    sections: list[tuple[str, str]] = []
    current_title = "概述"
    current_lines: list[str] = []

    for line in text.splitlines():
        m = _HEADING_RE.match(line.strip())
        if m:
            if current_lines:
                sections.append((current_title, "\n".join(current_lines).strip()))
            current_title = m.group(2).strip()
            current_lines = []
            continue
        current_lines.append(line)

    if current_lines:
        sections.append((current_title, "\n".join(current_lines).strip()))

    if not sections:
        sections = [("概述", text)]

    out: list[tuple[str, str]] = []
    for title, body in sections:
        body = body.strip()
        if not body:
            continue
        if len(body) <= max_chars:
            out.append((title, body))
            continue
        paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
        buf = ""
        for para in paras:
            candidate = f"{buf}\n\n{para}".strip() if buf else para
            if len(candidate) <= max_chars:
                buf = candidate
                continue
            if buf:
                out.append((title, buf))
            if len(para) <= max_chars:
                buf = para
            else:
                for i in range(0, len(para), max_chars):
                    out.append((title, para[i : i + max_chars]))
                buf = ""
        if buf:
            out.append((title, buf))
    return out
