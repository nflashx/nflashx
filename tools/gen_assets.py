"""Generate landing-page artwork with the Agnes image API (run once at build time)."""
import json, os, time, urllib.request

KEY = os.environ.get("AGNES_API_KEY", "sk-44kFggy5oV4nksiZkLnzFuNB5loRZlywK6FqjCfDKnSia81g")
BASE = "https://apihub.agnes-ai.com/v1/images/generations"
OUT = os.path.join(os.path.dirname(__file__), "..", "assets")

JOBS = [
    # slide 2 — brand mascot scene (like the original's generated "i" logo hero)
    ("hero-brand.jpg", 1024, 1024,
     "A glossy chrome 3D letter N logo floating above a dark rocky alien landscape at night, "
     "a huge glowing circular ring of light behind it, vertical beam of light, nebula and starfield sky, "
     "cinematic lighting, dark blue and silver palette, ultra detailed, centered composition"),
    # slide 3 — cinematic still (Ken Burns fallback if video queue is full)
    ("motion-bg.jpg", 1280, 720,
     "Cinematic film still, a rider in black leather gear on a futuristic motorcycle speeding through a "
     "dark gothic city street at night, motion blur, warm street lamps and blue neon, rain haze, moody tones, "
     "wide shot, photorealistic"),
    # slide 4 — gallery of five distinct images (like the original)
    ("gallery-1.jpg", 768, 832, "epic desert adventure movie poster, two travellers riding a giant white cat through clouds, warm golden sunset light, fantasy"),
    ("gallery-2.jpg", 768, 832, "neon cyberpunk girl portrait with glowing katana, rain, purple and blue neon lights, cinematic"),
    ("gallery-3.jpg", 768, 832, "moody film noir portrait of a man in a neon-lit alley at night, teal and orange, cinematic bokeh"),
    ("gallery-4.jpg", 768, 832, "stylish young man in an open black suit standing on a mediterranean street, golden hour sun flare, old dome cathedral behind, photorealistic"),
    ("gallery-5.jpg", 768, 832, "vintage golden palace hall interior, luxury baroque architecture, warm candle light, cinematic wide shot"),
    # studio placeholder samples
    ("sample-street.jpg", 1024, 640, "a neon cyberpunk street at night, rain, cinematic lighting, reflections, ultra detailed"),
]

def gen(name, w, h, prompt):
    body = json.dumps({"model": "agnes-image-2.5-flash", "prompt": prompt,
                       "size": f"{w}x{h}", "n": 1}).encode()
    req = urllib.request.Request(BASE, data=body, headers={
        "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.loads(r.read())
    url = data["data"][0]["url"]
    path = os.path.normpath(os.path.join(OUT, name))
    urllib.request.urlretrieve(url, path)
    print(f"OK {name} <- {url[:80]}... ({os.path.getsize(path)//1024} KB)")

for name, w, h, p in JOBS:
    for attempt in range(3):
        try:
            gen(name, w, h, p)
            break
        except Exception as e:
            print(f"retry {name} ({attempt+1}): {e}")
            time.sleep(8)
    time.sleep(3)
print("DONE")
