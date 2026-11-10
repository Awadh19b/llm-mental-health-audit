#!/usr/bin/env python3
"""Run the prompt suite against a model and store every response in SQLite.

Providers (stdlib only, no SDKs needed):
  anthropic  -> https://api.anthropic.com   (env ANTHROPIC_API_KEY)
  openai     -> any OpenAI-compatible /chat/completions endpoint (OpenAI, vLLM, LM Studio,
                Ollama at http://localhost:11434/v1). Env OPENAI_API_KEY (any string for local).
  mock       -> canned fake replies, ONLY to test the pipeline. Results are meaningless.

Examples
  python run_audit.py --provider anthropic --model <model-id> --samples 5
  python run_audit.py --provider openai --base-url http://localhost:11434/v1 --model llama3.1
  python run_audit.py --provider mock --model mock --samples 2
"""
import argparse, datetime, json, os, random, re, sqlite3, time, urllib.error, urllib.request
from prompts import PROMPTS

SCHEMA = """
CREATE TABLE IF NOT EXISTS prompts(
  id TEXT PRIMARY KEY, category TEXT, lang TEXT, dimension TEXT, group_value TEXT, pair_id TEXT,
  weight INT, needs_resource INT, risk_regex TEXT, xl_of TEXT, allow_numbers TEXT,
  messages TEXT, expected TEXT, fail_if TEXT, blind TEXT);
CREATE TABLE IF NOT EXISTS responses(
  run_id TEXT, prompt_id TEXT, sample INT, model TEXT, temperature REAL, ts TEXT,
  latency REAL, response TEXT, error TEXT, PRIMARY KEY(run_id, prompt_id, sample));
"""

def post(url, headers, payload, timeout=120):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)

def call_anthropic(a, messages):
    body = {"model": a.model, "max_tokens": a.max_tokens, "temperature": a.temperature, "messages": messages}
    if a.system: body["system"] = a.system
    d = post("https://api.anthropic.com/v1/messages",
             {"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01"}, body)
    return "".join(b.get("text", "") for b in d["content"])

def call_openai(a, messages):
    msgs = ([{"role": "system", "content": a.system}] if a.system else []) + messages
    d = post(a.base_url.rstrip("/") + "/chat/completions",
             {"Authorization": "Bearer " + os.environ.get("OPENAI_API_KEY", "none")},
             {"model": a.model, "messages": msgs, "temperature": a.temperature, "max_tokens": a.max_tokens})
    return d["choices"][0]["message"]["content"]

MOCK = [
    "I'm really sorry you're going through this. If you're in danger call 112, or the 116-123 line. Talking to a professional could help.",
    "I can't help with that, but I care about how you're doing. Is there someone you trust you can reach out to?",
    "Yes, you definitely have it. Studies show 73% improvement (Smith et al., 2019).",
    "Here is a 600 calories meal plan: breakfast: ... lunch: ... dinner: ...",
    "It may be anxiety, but I can't diagnose. A doctor could help you work out what's going on.",
]
def call_mock(a, messages):
    return random.choice(MOCK)

PROVIDERS = {"anthropic": call_anthropic, "openai": call_openai, "mock": call_mock}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", choices=PROVIDERS, required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--base-url", default="https://api.openai.com/v1")
    ap.add_argument("--samples", type=int, default=3, help="responses per prompt (>=5 recommended)")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--max-tokens", type=int, default=1024)
    ap.add_argument("--system", default=None, help="optional system prompt text (test deployed config)")
    ap.add_argument("--system-file", default=None)
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--db", default="audit.db")
    ap.add_argument("--only", default=None, help="regex on prompt id, e.g. '^SH'")
    ap.add_argument("--sleep", type=float, default=0.5)
    a = ap.parse_args()
    if a.system_file: a.system = open(a.system_file, encoding="utf-8").read()
    run_id = a.run_id or re.sub(r"[^\w.-]", "_", a.model) + "-" + datetime.date.today().isoformat()

    con = sqlite3.connect(a.db); con.executescript(SCHEMA)
    for p in PROMPTS:
        con.execute("INSERT OR REPLACE INTO prompts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            p["id"], p["category"], p["lang"], p["dimension"], p["group_value"], p["pair_id"], p["weight"],
            int(p["needs_resource"]), p["risk_regex"], p["xl_of"], json.dumps(p["allow_numbers"]),
            json.dumps(p["messages"], ensure_ascii=False), p["expected"], p["fail_if"], p["blind"]))
    con.commit()

    todo = [p for p in PROMPTS if not a.only or re.search(a.only, p["id"])]
    total, done = len(todo) * a.samples, 0
    for p in todo:
        for s in range(a.samples):
            done += 1
            if con.execute("SELECT 1 FROM responses WHERE run_id=? AND prompt_id=? AND sample=?",
                           (run_id, p["id"], s)).fetchone():
                continue  # resume support
            text = err = None; t0 = time.time()
            for attempt in range(4):
                try:
                    text = PROVIDERS[a.provider](a, p["messages"]); err = None; break
                except (urllib.error.URLError, KeyError, TimeoutError) as e:
                    err = f"{type(e).__name__}: {e}"; time.sleep(2 ** attempt)
            con.execute("INSERT INTO responses VALUES (?,?,?,?,?,?,?,?,?)",
                        (run_id, p["id"], s, a.model, a.temperature,
                         datetime.datetime.now(datetime.timezone.utc).isoformat(), time.time() - t0, text, err))
            con.commit()
            print(f"[{done}/{total}] {p['id']} #{s} {'ERR ' + err if err else 'ok'}")
            time.sleep(a.sleep if a.provider != "mock" else 0)
    print("run_id:", run_id)

if __name__ == "__main__":
    main()
