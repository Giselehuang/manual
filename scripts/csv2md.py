import csv, os, sys, textwrap

csv_path, out_root = sys.argv[1:]        # 無縮排

with open(csv_path, newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        slug = row["slug"].strip("/")
        for lang in ("en", "zh", "ja"):
            if not row.get(lang):        # 空白就跳過
                continue
            md_path = os.path.join(out_root, lang, f"{slug}.md")
            os.makedirs(os.path.dirname(md_path), exist_ok=True)
            with open(md_path, "w", encoding="utf-8") as md:
                md.write(textwrap.dedent(row[lang]).strip() + "\n")
