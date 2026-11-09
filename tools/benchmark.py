# -*- coding: utf-8 -*-
"""
NFlashX benchmark — 10 cau thuong duoc dung de dat diem leaderboard.
Chay:  python -I tools/benchmark.py <API_KEY> [base_url]
Dung key tier PRO de do SUC THAT cua model (khong qua persona gioi han cua free).
Ket qua luu: tools/benchmark_results.json
"""
import json, sys, time, urllib.request, urllib.error

KEY = sys.argv[1] if len(sys.argv) > 1 else ""
BASE = sys.argv[2] if len(sys.argv) > 2 else "http://127.0.0.1:8600"

QUESTIONS = [
    ("math_percent",  "A jacket costs $200. The shop applies a 20% discount, then adds 10% tax on the discounted price. What is the final price? Show brief reasoning."),
    ("logic_bat",     "A bat and a ball cost $1.10 together. The bat costs $1.00 more than the ball. How much does the ball cost? Explain briefly."),
    ("logic_riddle",  "A man looks at a painting and says: 'Brothers and sisters I have none, but that man's father is my father's son.' Who is in the painting? Explain briefly."),
    ("code_write",    "Write a Python function is_balanced(s) that returns True if the brackets (), [], {} in string s are balanced, else False. Code only, short."),
    ("code_debug",    "This function crashes when nums is empty: def avg(nums): return sum(nums)/len(nums)  — fix it so it returns None for an empty list. One-line body fix."),
    ("knowledge",     "TCP vs UDP: give 3 key differences, one line each."),
    ("instruction",   "Describe photosynthesis in EXACTLY 3 sentences. No more, no less."),
    ("hallucination", "Who won the FIFA World Cup final in 2030, and what was the score?"),
    ("json_format",   'Return ONLY valid JSON (no other text): an object with key "a" equal to 2+2 (number) and key "b" equal to "hello" (string).'),
    ("multistep",     "Box A has twice as many apples as Box B. Box C has 5 fewer apples than Box A. Total apples = 35. How many in each box? Show brief work."),
]

def ask(q):
    body = json.dumps({"model": "n-flashx-1.0-flash",
                       "messages": [{"role": "user", "content": q}],
                       "max_tokens": 1000}).encode()
    req = urllib.request.Request(BASE + "/v1/chat/completions", data=body,
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + KEY})
    for attempt in (0, 1):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.loads(r.read())
            return d["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt == 0:
                time.sleep(20)   # upstream burst limit — nghỉ rồi thử lại đúng 1 lần
                continue
            raise

out = {}
def safe_print(s):
    try:
        print(s)
    except UnicodeEncodeError:
        print(s.encode("ascii", "replace").decode())

for name, q in QUESTIONS:
    try:
        a = ask(q)                      # luu ket qua TRUOC, print roi nhau
        out[name] = {"q": q, "a": a}
        safe_print("=== %s ===" % name)
        safe_print(a[:500])
        print()
    except Exception as e:
        out[name] = {"q": q, "a": "ERROR: %s" % e}
        safe_print("=== %s === ERROR %s" % (name, e))
    time.sleep(2)   # trả lời nhẹ nhàng, tránh upstream burst limit

with open(__file__.rsplit("\\", 1)[0] + r"\benchmark_results.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("saved -> tools/benchmark_results.json")
