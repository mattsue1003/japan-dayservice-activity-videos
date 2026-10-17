#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 rehashine_database.json 嵌入 template.html，產生 index.html（單一檔案，可直接放 GitHub Pages）"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DATE = "2026-10-17"

data = json.load(open(ROOT / "rehashine_database.json", encoding="utf-8"))
tpl = (Path(__file__).parent / "template.html").read_text(encoding="utf-8")
payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
html = tpl.replace("__DATA__", payload).replace("__DATA_DATE__", DATA_DATE)
(ROOT / "index.html").write_text(html, encoding="utf-8")
print("index.html 已產生，", len(data), "筆資料，", round(len(html.encode()) / 1024), "KB")
