"""Narrated guided tour for the Prudential Hong Kong competitive-intelligence report.

Records one clip per step into vercel_prudential_report/private/narration/pru/<step>.mp3 and injects the tour player
into the built report. Unchanged steps are not re-recorded. Steps without a recorded clip fall back to the browser's
own voice with timed captions, so the tour always works. Reuses the player from report_app/build_pa_tour.py.

    python -I report_app/prudential/build_tour.py --dry      # clips to record and the credit cost
    python -I report_app/prudential/build_tour.py            # record with ELEVENLABS_API_KEY, then inject
    python -I report_app/prudential/build_tour.py --key2     # record with ELEVENLABS_API_KEY2, then inject
    python -I report_app/prudential/build_tour.py --inject   # inject only (build.py runs this automatically)

The voice key is read from .env here only and never written into the app. Narration text must not contain personal
contact details, because it is sent to the voice service.
"""
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "report_app"))
import build_pa_tour as pa  # noqa: E402  (player markup and styles)

APP = ROOT / "vercel_prudential_report"
REPORTS = [APP / "private/report.html", ROOT / "Prudential/Prudential_HK_Competitive_Intelligence_Report.html"]
OUT = APP / "private/narration"
PERSONA = "pru"
VOICE = ("Alice", "Xb7hH8MSUJpSbSDYk0k2")  # default voice: British, female
MODEL = "eleven_multilingual_v2"
KBPS = 128
MAX_CREDITS = 6000

# id, element to bring into view (the player opens its view first), player label, caption (the voice reads the same text)
STEPS = [
    ("intro", "#one", "Introduction",
     "Welcome. This report compares Prudential Hong Kong with AIA, Manulife and AXA in Hong Kong, from November 2025 to October 2026. "
     "This tour takes about five minutes. You can pause, skip or close it at any time."),
    ("bottom-line", "#one .op-box", "The bottom line",
     "Start with the bottom line. Prudential is growing profit while its sales shrink. "
     "Profit from new policies rose eight percent in the first half of 2026, and its margin reached fifty-seven percent, but sales fell six percent."),
    ("strengths", "#one .grid.g2", "Strongest and weakest points",
     "Its strongest points are profit quality, sales through bank partners, which grew forty-eight percent, and cashless hospital billing. "
     "Its weakest points are slower agency growth, a customer app rated about one star in recent reviews, and the smallest Google ad and YouTube reach. "
     "Each point has a Read more button with its sources."),
    ("results", "#p1 .insight", "Hong Kong results",
     "Part one shows each insurer's Hong Kong results side by side. Manulife grew sales fastest, up forty-five percent in the third quarter, "
     "but at a lower margin. Each insurer measures new business differently, so compare growth, not size."),
    ("investors", "#inv", "Shares and capital",
     "Investors and capital. Over the year, Prudential's Hong Kong shares fell about twelve percent, close to the Hang Seng index, while Manulife's rose forty-one percent. "
     "Prudential's Hong Kong life company holds more than twice the capital the regulator requires."),
    ("awards", "#awards", "Industry awards",
     "Prudential won two of the seventeen Hong Kong Insurance Awards in 2026: excellence in digital transformation, and outstanding customer service in life insurance."),
    ("moves", "#tlBoard", "Competitor moves",
     "Part two is the board of competitor moves: one column per insurer, newest first. "
     "Use the type buttons to see only product launches, health network moves, partnerships or campaigns. Every card links to its source."),
    ("media", "#media", "Media coverage",
     "Media coverage. Prudential, AIA and Manulife each drew a little over a quarter of Hong Kong media stories. AXA drew less. "
     "Close to half of the coverage is in Chinese."),
    ("brand", "#socAll", "Brand and social",
     "Part three covers brand and campaigns. Prudential posts less than its rivals, but each Facebook post gets the highest engagement of the four. "
     "Offers and short stories work better for Prudential than general health tips."),
    ("detail", "#dpGlance", "Social, ads and search",
     "This page goes deeper on social media, ads and search. Two findings stand out. People search for Prudential by its Chinese name far more than its English one. "
     "And most of its Facebook and Instagram ads started only in October 2026, while AIA keeps ads running all year."),
    ("products", "#p4", "Products",
     "Part four tracks product launches. AIA and Manulife launched several wealth, legacy and retirement plans, each with its own announcement. "
     "Prudential launched for the same customers, but only one of its plans was publicised."),
    ("digital", "#apps", "Digital and apps",
     "Part five covers digital service. Prudential's customer app trails A I A's and Manulife's: many recent reviews mention slow loading or failed log-ins."),
    ("footprint", "#footprint", "Branches and service centres",
     "Branches and service centres. On Google Maps, Prudential shows five service points in four districts, against sixteen for AIA, "
     "and its locations draw more negative reviews than AIA's or AXA's. AIA and AXA also run wellness or partner health centres; "
     "the district maps show where each insurer can be found."),
    ("insights", "#insights", "Insights",
     "Part six brings it together in eight ranked insights. Each one shows what happened, how rivals compare, what it may mean, and what Prudential could do, "
     "with a Read more list of every source behind it."),
    ("explorer", "#explorer", "Evidence explorer",
     "The evidence explorer holds every record behind the report: releases, media stories, posts, ads, stock exchange filings and awards. "
     "Search in English or Chinese, and use the buttons to choose a record type."),
    ("filters", ".fbar", "Filters",
     "The filter bar at the top narrows every live panel by period, brand, module, category and platform. "
     "Each option shows how many records it leaves, and panels with no data are hidden with a note."),
    ("close", ".fab", "End of the tour",
     "That is the tour. Ask the report, at the bottom right, answers questions from this report's sources only. "
     "You can replay the tour from the Guided tour button at the top."),
]
SAY = [(r"\bAIA\b", "A I A"), (r"\bAXA\b", "Axa"), (r"\bAIA's\b", "A I A's"), (r"\bAXA's\b", "Axa's")]


def say(t):
    for a, b in SAY:
        t = re.sub(a, b, t)
    return t


def api_key():
    name = "ELEVENLABS_API_KEY2" if "--key2" in sys.argv else "ELEVENLABS_API_KEY"
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith(name + "="):
            return line.split("=", 1)[1].strip().strip("\"'")
    sys.exit(f"{name} is not set in .env")


def record(text, dest):
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE[1]}?output_format=mp3_44100_{KBPS}",
                                 data=json.dumps({"text": text, "model_id": MODEL}).encode(),
                                 headers={"xi-api-key": api_key(), "Content-Type": "application/json", "Accept": "audio/mpeg"})
    try:
        dest.write_bytes(urllib.request.urlopen(req, timeout=120).read())
        return True
    except urllib.error.HTTPError as e:
        print(f"  voice service refused {dest.name}: {e.code} {e.read()[:200]!r}")
        return False


def player():
    p = pa.PLAYER
    for a, b in [('($("#who") || {}).value || "nova"', '"pru"'), ('"pa-tour-', '"pru-tour-'),
                 ("the company, the person and the Palo Alto plays", "Prudential's position, its rivals' moves and what to do next"),
                 ("narration/<persona>/<step>.mp3, built by report_app/build_pa_tour.py", "narration/pru/<step>.mp3, built by report_app/prudential/build_tour.py"),
                 # this report has views: open the step's view before scrolling to it
                 ("clearHi(); const el = document.querySelector(S.to);",
                  "clearHi(); let el = document.querySelector(S.to); if (el && typeof viewOf === \"function\" && typeof showView === \"function\") { const v = viewOf(el); if (v && !document.getElementById(v).classList.contains(\"on\")) showView(v, null, false); el = document.querySelector(S.to); }")]:
        assert a in p, a
        p = p.replace(a, b)
    return p


def inject():
    rows = []
    for sid, to, label, text in STEPS:
        f = OUT / PERSONA / f"{sid}.mp3"
        rows.append({"id": sid, "tab": None, "to": to, "label": label, "text": text,
                     "sec": round(f.stat().st_size * 8 / (KBPS * 1000), 1) if f.exists() else None})
    data = {PERSONA: {"mins": max(1, round(sum(r["sec"] or len(r["text"]) / 15 for r in rows) / 60)), "steps": rows}}
    block = player().replace("__TOUR_DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    # the "9 of 16" label already shows the position; a half-filled line read as a fault
    block = block.replace("<!-- tour:end -->", "<style>#tourBar .tbar { display: none; }</style>\n<!-- tour:end -->", 1)
    btn = '<button type="button" class="btn" id="tourBtn" title="Narrated tour of this report">▶ <span class="lbl">Guided tour</span></button>\n  '
    for report in REPORTS:
        if not report.exists():
            continue
        s = report.read_text(encoding="utf-8")
        s = re.sub(r"<!-- tour:start -->.*?<!-- tour:end -->\n", "", s, flags=re.S)
        anchor = '<button class="fab" data-open-chat'
        assert s.count(anchor) == 1
        s = s.replace(anchor, block + anchor)
        if 'id="tourBtn"' not in s:
            ask = '<button class="btn primary" data-open-chat>✦ Ask the report</button>'
            assert s.count(ask) >= 1
            s = s.replace(ask, btn + ask, 1)
        report.write_text(s, encoding="utf-8", newline="")
    have = sum(1 for r in rows if r["sec"])
    print(f"tour injected: {len(rows)} steps, ~{data[PERSONA]['mins']} min, {have} with recorded voice")


def build(dry=False, inject_only=False):
    mpath = OUT / "manifest.json"
    manifest = json.loads(mpath.read_text(encoding="utf-8")) if mpath.exists() else {}
    todo = []
    for sid, _to, _label, text in STEPS:
        spoken = say(text)
        h = hashlib.sha256(f"{VOICE[1]}|{MODEL}|{spoken}".encode()).hexdigest()[:16]
        f = OUT / PERSONA / f"{sid}.mp3"
        if manifest.get(f"{PERSONA}/{sid}") != h or not f.exists():
            todo.append((sid, spoken, h, f))
    cost = sum(len(t[1]) for t in todo)
    print(f"{len(todo)} clip(s) to record, about {cost:,} credits")
    if dry:
        for sid, sp, *_ in todo:
            print(f"  {sid}: {len(sp)} chars")
        return
    if todo and not inject_only:
        if cost > MAX_CREDITS:
            sys.exit(f"Refusing: {cost:,} credits is over the {MAX_CREDITS:,} limit")
        for sid, spoken, h, f in todo:
            f.parent.mkdir(parents=True, exist_ok=True)
            if not record(spoken, f):
                break  # e.g. out of credits: clips recorded so far are kept; the rest use the browser voice
            manifest[f"{PERSONA}/{sid}"] = h
            mpath.write_text(json.dumps(manifest, indent=1), encoding="utf-8")
            print(f"  recorded {sid} ({f.stat().st_size // 1024} KB)")
    inject()


if __name__ == "__main__":
    build("--dry" in sys.argv, "--inject" in sys.argv)
