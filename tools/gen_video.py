"""Create + download a 5s AI video for the Motion slide.

Strategy:
  1. Try agnes-video-2.5-flash (free trial queue) every 2 minutes.
  2. Every 10th round also try agnes-video-2.5 (paid, needs >= $0.125 balance)
     — succeeds automatically once the account is topped up.
On success: poll GET /agnesapi until done, download to assets/motion-bg.mp4.
"""
import json, os, sys, time, urllib.request, urllib.error

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows cp1252 console fix

KEY = os.environ.get("AGNES_KEY", "")
BASE = "https://apihub.agnes-ai.com"
OUT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "assets", "motion-bg.mp4"))
PROMPT = ("Cinematic night city street, a motorcycle rider in black leather speeding past glowing neon "
          "signs, light trails, rain reflections on asphalt, camera tracking shot, moody blue tones")
BODY = {"mode": "text", "prompt": PROMPT, "seconds": "5", "size": "720P", "aspect_ratio": "16:9"}

def post(path, obj):
    req = urllib.request.Request(BASE + path, data=json.dumps(obj).encode(), headers={
        "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())

def get(path):
    req = urllib.request.Request(BASE + path, headers={"Authorization": f"Bearer {KEY}"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())

def try_create(model):
    try:
        r = post("/v1/videos", {"model": model, **BODY})
        vid = r.get("video_id")
        print(f"[{model}] task created: {vid}")
        return vid
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", "ignore")[:180]
        print(f"[{model}] HTTP {e.code}: {msg}")
        if e.code == 403:
            return "BLOCKED"  # rate-limited — back off
        if "insufficient_user_quota" in msg:
            print(">> Can nap it: video 5s 720P can $0.125 (nap tai platform.agnes-ai.com → Billing → Recharge)")
        return None
    except Exception as e:
        print(f"[{model}] err: {e}")
        return None

def poll_and_download(video_id, model):
    for _ in range(90):  # up to 45 min
        try:
            r = get(f"/agnesapi?video_id={video_id}&model_name={model}")
            d = r.get("data") or r
            status = str(d.get("status") or d.get("state") or "")
            url = d.get("video_url") or d.get("url") or d.get("output_url")
            print("poll:", status or str(r)[:120])
            if url:
                urllib.request.urlretrieve(url, OUT)
                print("OK saved:", os.path.getsize(OUT) // 1024, "KB")
                return True
            if "fail" in status.lower():
                print("TASK_FAILED"); return False
        except Exception as e:
            print("poll err:", e)
        time.sleep(30)
    print("POLL_TIMEOUT"); return False

rounds = 0
while rounds < 480:  # 15s per round ≈ 2h cap
    rounds += 1
    vid = try_create("agnes-video-2.5-flash")
    if vid and poll_and_download(vid, "agnes-video-2.5-flash"):
        raise SystemExit(0)
    wait = 15
    if vid == "BLOCKED":
        wait = 120  # rate-limited — cool down
    if rounds % 10 == 0:  # check paid model periodically (works once balance is topped up)
        vid = try_create("agnes-video-2.5")
        if vid and poll_and_download(vid, "agnes-video-2.5"):
            raise SystemExit(0)
        if vid == "BLOCKED":
            wait = max(wait, 120)
    time.sleep(wait)
print("GAVE_UP_AFTER_480_ROUNDS")
