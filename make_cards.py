"""
make_cards.py - Generates the black Excalidraw-style card/banner images that
give the GitHub profile README its full dark "box" aesthetic.

GitHub strips all inline style/CSS from README HTML (verified against GitHub's
own sanitizer), so every black box in the README is a pre-rendered PNG.

Outputs (width 880, matches assets/hero-grid.gif):
    assets/card-intro.png
    assets/banner-connect.png     assets/banner-stack.png
    assets/banner-ai.png          assets/banner-api.png
    assets/banner-ui.png          assets/banner-infra.png
    assets/banner-lang.png        assets/banner-open.png
    assets/banner-footer.png

Run: python make_cards.py
"""
import os
import urllib.request

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
FONT_PATH = os.path.join(ASSETS, "fonts", "PatrickHand-Regular.ttf")
FONT_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/patrickhand/PatrickHand-Regular.ttf"
EMOJI_FONT = "C:/Windows/Fonts/seguiemj.ttf"

W = 880
BG = (5, 7, 10)          # #05070a
CARD = (9, 13, 20)       # #090d14
WHITE = (255, 255, 255)
GRAY = (139, 148, 158)   # #8b949e
LIGHT = (230, 237, 243)  # #e6edf3
DASH = (48, 54, 61)      # #30363d
SHADOW = 6


def ensure_font():
    if not os.path.exists(FONT_PATH):
        os.makedirs(os.path.dirname(FONT_PATH), exist_ok=True)
        req = urllib.request.Request(FONT_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as r, open(FONT_PATH, "wb") as f:
            f.write(r.read())


_cache = {}


def font(size):
    if ("p", size) not in _cache:
        _cache[("p", size)] = ImageFont.truetype(FONT_PATH, size)
    return _cache[("p", size)]


def emoji_font(size):
    if ("e", size) not in _cache:
        try:
            _cache[("e", size)] = ImageFont.truetype(EMOJI_FONT, size)
        except OSError:
            _cache[("e", size)] = None
    return _cache[("e", size)]


def _is_emoji(ch):
    o = ord(ch)
    return (0x1F000 <= o <= 0x1FAFF) or (0x2600 <= o <= 0x27BF) or \
           (0x2B00 <= o <= 0x2BFF) or o in (0xFE0F, 0x200D)


def _segments(text):
    segs, cur, cur_e = [], "", False
    for ch in text:
        e = _is_emoji(ch)
        if cur and e != cur_e:
            segs.append((cur, cur_e))
            cur = ""
        cur_e, cur = e, cur + ch
    if cur:
        segs.append((cur, cur_e))
    return segs


def tw(d, text, f, e_size=0):
    total = 0
    for s, is_e in _segments(text):
        if is_e and e_size:
            ef = emoji_font(e_size)
            if ef is None:
                continue
            total += d.textlength(s, font=ef)
        elif is_e:
            continue
        else:
            total += d.textlength(s, font=f)
    return total


def draw_rich(d, x, y, text, f, fill, e_size=0):
    for s, is_e in _segments(text):
        if is_e:
            if not e_size:
                continue
            ef = emoji_font(e_size)
            if ef is None:
                continue
            d.text((x, y), s, font=ef, fill=fill, embedded_color=True)
            x += d.textlength(s, font=ef)
        else:
            d.text((x, y), s, font=f, fill=fill)
            x += d.textlength(s, font=f)
    return x


def rough_box(d, xy, fill, radius=14, border=3):
    x0, y0, x1, y1 = xy
    d.rounded_rectangle([x0 + SHADOW, y0 + SHADOW, x1 + SHADOW, y1 + SHADOW],
                        radius=radius, fill=WHITE)
    d.rounded_rectangle(xy, radius=radius, fill=fill, outline=WHITE, width=border)


def dashed(d, x0, x1, y, color=DASH, width=2, seg=10, gap=8):
    x = x0
    while x < x1:
        d.line([(x, y), (min(x + seg, x1), y)], fill=color, width=width)
        x += seg + gap


def new_canvas(h):
    img = Image.new("RGB", (W, h), BG)
    return img, ImageDraw.Draw(img)


def save(img, name, max_y):
    img = img.crop((0, 0, W, min(img.height, max_y + 10)))
    img.save(os.path.join(ASSETS, name))
    print(f"  {name}  {img.width}x{img.height}")


def banner(name, title, emoji, big=True):
    h, fs, es = (96, 36, 36) if big else (76, 27, 28)
    img, d = new_canvas(h)
    rough_box(d, [10, 10, W - 16, h - 16], CARD)
    f = font(fs)
    label = (emoji + "  " + title) if emoji else title
    text_w = tw(d, label, f, es)
    x = (W - text_w) / 2
    box_cy = 10 + (h - 16 - 10) / 2  # vertical center of box
    y = box_cy - fs * 0.62
    draw_rich(d, x, y, label, f, WHITE, es)
    img.save(os.path.join(ASSETS, name))
    print(f"  {name}  {W}x{h}")


def intro_card():
    img, d = new_canvas(520)
    max_y = 0

    # --- top pill (drawn dot, not glyph, for reliability) ---
    pill_f = font(15)
    pill_text = "AUTONOMOUS AI  •  GRAPHRAG ACTIVE"
    pw = tw(d, pill_text, pill_f) + 76
    px0, py0 = (W - pw) / 2, 20
    rough_box(d, [px0, py0, px0 + pw, py0 + 40], (13, 17, 23), radius=14, border=2)
    d.ellipse([px0 + 18, py0 + 16, px0 + 30, py0 + 28], fill=WHITE)
    draw_rich(d, px0 + 40, py0 + 10, pill_text, pill_f, WHITE)
    max_y = py0 + 40

    # --- main card ---
    y0 = 78
    rough_box(d, [10, y0, W - 16, y0 + 400], CARD)
    x = 44
    y = y0 + 28

    # headline + subtitle
    h1_f = font(36)
    draw_rich(d, x, y, "Hi there, I'm Parth Vastavik! ", h1_f, WHITE, 34)
    d.text((x + tw(d, "Hi there, I'm Parth Vastavik! ", h1_f) + 4, y - 4),
           "\U0001F44B", font=emoji_font(34), fill=WHITE, embedded_color=True)
    y += 52
    sub_f = font(18)
    draw_rich(d, x, y, "GenAI Engineer & Full-Stack Architect", sub_f, GRAY)
    y += 34
    dashed(d, x, W - 44, y)
    y += 24

    # bullets
    bullet_f = font(19)
    bullets = [
        "\U0001F52D  Building agentic RAG - LangChain + Neo4j GraphRAG",
        "\u26A1  Backend: FastAPI + Python Async microservices",
        "\U0001F331  Exploring Langbase, hybrid retrieval & evals",
        "\U0001F427  Linux / Neovim enthusiast",
        "\U0001F4AC  Ask me about RAG, FastAPI, React & Three.js",
    ]
    for b in bullets:
        draw_rich(d, x, y, b, bullet_f, LIGHT, 20)
        y += 36
    y += 8

    dashed(d, x, W - 44, y)
    y += 18

    # footer row
    foot_f = font(15)
    draw_rich(d, x, y, "\U0001F4CD  Kolkata, India", foot_f, GRAY, 16)
    gh = "GITHUB: @parthasdey2304"
    draw_rich(d, W - 44 - tw(d, gh, foot_f), y, gh, foot_f, GRAY)
    y += 30

    # fit card height to content
    bottom = y + 18
    img2, d2 = new_canvas(bottom + 10)
    max_y = max(max_y, bottom)
    # redraw (cheap: second pass with same layout)
    def render(dd):
        m = 0
        pw2 = tw(dd, pill_text, pill_f) + 76
        px0, py0 = (W - pw2) / 2, 20
        rough_box(dd, [px0, py0, px0 + pw2, py0 + 40], (13, 17, 23), radius=14, border=2)
        dd.ellipse([px0 + 18, py0 + 16, px0 + 30, py0 + 28], fill=WHITE)
        draw_rich(dd, px0 + 40, py0 + 10, pill_text, pill_f, WHITE)
        m = py0 + 40
        y0 = 78
        rough_box(dd, [10, y0, W - 16, bottom], CARD)
        xx, yy = 44, y0 + 28
        h1w = tw(dd, "Hi there, I'm Parth Vastavik! ", h1_f)
        draw_rich(dd, xx, yy, "Hi there, I'm Parth Vastavik! ", h1_f, WHITE, 34)
        dd.text((xx + h1w + 4, yy - 4), "\U0001F44B", font=emoji_font(34),
                fill=WHITE, embedded_color=True)
        yy += 52
        draw_rich(dd, xx, yy, "GenAI Engineer & Full-Stack Architect", sub_f, GRAY)
        yy += 34
        dashed(dd, xx, W - 44, yy)
        yy += 24
        for b in bullets:
            draw_rich(dd, xx, yy, b, bullet_f, LIGHT, 20)
            yy += 36
        yy += 8
        dashed(dd, xx, W - 44, yy)
        yy += 18
        draw_rich(dd, xx, yy, "\U0001F4CD  Kolkata, India", foot_f, GRAY, 16)
        draw_rich(dd, W - 44 - tw(dd, gh, foot_f), yy, gh, foot_f, GRAY)
        return m

    render(d2)
    save(img2, "card-intro.png", max_y)


def main():
    ensure_font()
    print("[make_cards] generating Excalidraw cards...")
    intro_card()
    banner("banner-connect.png", "Stay Connected", "\U0001F91D", big=True)
    banner("banner-stack.png", "Tech Stack", "\U0001F6E0\uFE0F", big=True)
    banner("banner-ai.png", "Autonomous AI & RAG", "\U0001F916", big=False)
    banner("banner-api.png", "High-Performance APIs", "\u26A1", big=False)
    banner("banner-ui.png", "Modern UI & 3D", "\U0001F3A8", big=False)
    banner("banner-infra.png", "Databases & Infrastructure", "\U0001F5C4\uFE0F", big=False)
    banner("banner-lang.png", "Languages & Tooling", "\U0001F9F0", big=False)
    banner("banner-open.png", "Open Source", "\U0001F9E9", big=True)
    banner("banner-footer.png", "Thanks for stopping by!", "\u2728", big=True)
    print("[make_cards] done")


if __name__ == "__main__":
    main()
