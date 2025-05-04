import csv, os, sys, re, textwrap, pathlib

csv_path, out_root = sys.argv[1:]

# 把整張翻譯表轉成 dict: {ID: {zh: ..., ja: ...}}
table = {row['id']: row for row in csv.DictReader(open(csv_path, newline='', encoding='utf-8'))}

for md_path in pathlib.Path(out_root, "en").rglob("*.md"):          # 以英文目錄為基準
    rel = md_path.relative_to(out_root / "en")                      # ex: getting-started/intro.md
    en_text = md_path.read_text(encoding="utf-8")

    for lang in ("zh", "ja"):
        target = pathlib.Path(out_root, lang, rel)
        if not target.exists():                                     # 第一次複製整檔
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(en_text, encoding="utf-8")

        txt = target.read_text(encoding="utf-8")

        def repl(match):
            _id = match.group(1)
            new = table.get(_id, {}).get(lang, match.group(2))      # 若翻譯缺漏就保留舊文
            return f"<!-- sync:{_id}:start -->\n{new}\n<!-- sync:{_id}:end -->"

        # ⬇️ 正則前綴從 i18n: 改成 sync:
        pattern = r"<!-- sync:([^:]+):start -->(.*?)<!-- sync:\1:end -->"
        txt = re.sub(pattern, repl, txt, flags=re.S)
        target.write_text(txt, encoding="utf-8")
