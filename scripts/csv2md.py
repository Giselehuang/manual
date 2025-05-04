#!/usr/bin/env python3
"""
csv2md.py
---------

從 CSV / Google Sheet 匯出的翻譯表，依 <ID -> 語言文字> 對應，
只替換 GitBook Markdown 檔中
<!-- sync:IDxxx:start --> ... <!-- sync:IDxxx:end --> 區塊。

用法：
    python scripts/csv2md.py translations.csv docs
"""
import csv
import pathlib
import re
import sys
import textwrap

# --- 參數 & 對應語言 ----------------------------
csv_path, out_root_str = sys.argv[1:]
out_root = pathlib.Path(out_root_str)             # ← 將字串轉 Path 物件
LANGS = ("zh", "ja")                              # 需要同步的語言目錄
PREFIX = "sync"                                   # 標籤前綴，可自行更改
# -----------------------------------------------

# 讀整張翻譯表成 dict: {ID: {zh: ..., ja: ...}}
with open(csv_path, newline="", encoding="utf-8") as f:
    table = {row["id"]: row for row in csv.DictReader(f)}

# 正則：抓 <!-- sync:ID:start --> 任意內容 <!-- sync:ID:end -->
pattern = re.compile(
    rf"<!-- {PREFIX}:([^:]+):start -->(.*?)<!-- {PREFIX}:\1:end -->",
    flags=re.S,
)

# 以英文檔為基準，確保其他語言 slug 結構一致
for md_path in (out_root / "en").rglob("*.md"):
    rel_path = md_path.relative_to(out_root / "en")       # ex: getting-started/intro.md
    en_text = md_path.read_text(encoding="utf-8")

    for lang in LANGS:
        target = out_root / lang / rel_path

        # 第一次若目標檔不存在→ 複製英文全文
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(en_text, encoding="utf-8")

        content = target.read_text(encoding="utf-8")

        # 取代函式：找到對應 ID ➜ 若有翻譯就換，沒有就保留原文
        def repl(match: re.Match) -> str:
            _id = match.group(1)
            new_text = table.get(_id, {}).get(lang, match.group(2))
            new_text = textwrap.dedent(new_text).strip()
            return f"<!-- {PREFIX}:{_id}:start -->\n{new_text}\n<!-- {PREFIX}:{_id}:end -->"

        content = pattern.sub(repl, content)
        target.write_text(content, encoding="utf-8")
