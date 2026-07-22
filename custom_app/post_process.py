import json, re, sys

def punct(t: str) -> str:
    t = t.strip()
    # 若末尾无标点，则补句号
    if not re.search(r'[。！？…]$', t):
        t += '。'
    return t

with open(sys.argv[1], "r", encoding="utf-8") as f:
    data = json.load(f)

for seg in data["segments"]:
    start = f"{seg['start']:.2f}"
    end   = f"{seg['end']:.2f}"
    text  = punct(seg["text"])
    print(f"{start} --> {end}\t{text}")

