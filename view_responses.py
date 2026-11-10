#!/usr/bin/env python3
"""Print stored responses. Usage: python view_responses.py [regex-on-prompt-id] [max-chars]"""
import re, sqlite3, sys

pat = sys.argv[1] if len(sys.argv) > 1 else "."
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 400
con = sqlite3.connect("audit.db")
for pid, s, resp, err in con.execute("SELECT prompt_id, sample, response, error FROM responses ORDER BY rowid"):
    if re.search(pat, pid):
        text = err if err else re.sub(r"\s+", " ", resp or "")[:limit]
        print(f"--- {pid} #{s}\n{text}\n")
