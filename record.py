"""
record.py — Automated capture pipeline for the dark-mode 3D hero.

GitHub README.md sanitizes <script>/<canvas>/WebGL, so this script renders
preview.html's interactive grid-warp into a GitHub-compatible looping GIF:
    python record.py  ->  assets/hero-grid.gif

Strategy:
  1. PRIMARY (pixel-faithful): if Playwright + Chromium is available, open
     preview.html, drive an organic mouse path via window.__setMouse,
     screenshot frames, and encode a GIF with PIL.
  2. FALLBACK (offline-safe): procedurally re-implement the exact canvas math
     (cosine spherical lens + radial spotlight) in PIL so the pipeline works
     with zero browser dependencies.

Both paths produce: dark-mode optimized, smooth looping, lightweight GIF.
"""
import math
import os
import sys

W, H = 880, 460
SPACING = 34
RADIUS = 160
STRENGTH = 40
FRAMES = 40
DURATION_MS = 70  # ~14fps, smooth + small file
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "hero-grid.gif")

BG = (5, 7, 10)
GRID = (27, 34, 45)

# ---------------------------------------------------------------- fallback renderer (PIL only)

def _load_fonts():
    from PIL import ImageFont
    candidates_bold = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    candidates_reg = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    def pick(cands, size):
        for p in cands:
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    continue
        return ImageFont.load_default()
    return {
        "title": pick(candidates_bold, 30),
        "sub": pick(candidates_reg, 15),
        "tag": pick(candidates_reg, 13),
        "small": pick(candidates_reg, 12),
        "pill": pick(candidates_bold, 12),
        "btn": pick(candidates_bold, 15),
    }


def mouse_path(t, cx=W / 2, cy=H / 2 + 10):
    """Organic figure-8 traversal across the card. Periodic in t->[0,1)."""
    x = cx + 200 * math.cos(2 * math.pi * t)
    y = cy + 95 * math.sin(4 * math.pi * t + 0.6) + 10 * math.sin(2 * math.pi * t * 3)
    return x, y


def draw_grid_fallback(draw, mx, my):
    # vertical distorted lines
    for gx in range(0, W + 1, SPACING):
        pts = []
        y = 0
        while y <= H:
            dx, dy = gx - mx, y - my
            dist = math.hypot(dx, dy)
            ox = 0.0
            if dist < RADIUS and dist > 0:
                ox = (dx / dist) * math.cos((dist / RADIUS) * (math.pi / 2)) * STRENGTH
            pts.append((gx + ox, y))
            y += 6
        draw.line(pts, fill=GRID)
    # horizontal distorted lines
    for gy in range(0, H + 1, SPACING):
        pts = []
        x = 0
        while x <= W:
            dx, dy = x - mx, gy - my
            dist = math.hypot(dx, dy)
            oy = 0.0
            if dist < RADIUS and dist > 0:
                oy = (dy / dist) * math.cos((dist / RADIUS) * (math.pi / 2)) * STRENGTH
            pts.append((x, gy + oy))
            x += 6
        draw.line(pts, fill=GRID)


def draw_spotlight(base, mx, my):
    """Radial white glow, alpha 0.15 -> 0 over RADIUS*1.1. Returns composited image."""
    from PIL import Image, ImageDraw
    glow_r = int(RADIUS * 1.1)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(layer)
    # concentric circles, outside-in, low alpha steps for smooth gradient
    steps = 24
    for i in range(steps, 0, -1):
        r = glow_r * i / steps
        # alpha peaks at center (0.15*255 ~= 38)
        a = int(38 * (1 - (r / glow_r)) ** 1.6) + 1
        g.ellipse([mx - r, my - r, mx + r, my + r], fill=(255, 255, 255, a))
    return Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")


def draw_card(draw, fonts):
    # --- top pill ---
    pill = [W / 2 - 190, 22, W / 2 + 190, 48]
    draw.rounded_rectangle([p + 5 for p in pill], radius=12, fill=(255, 255, 255))
    draw.rounded_rectangle(pill, radius=12, fill=(13, 17, 23), outline=(255, 255, 255), width=2)
    draw.ellipse([pill[0] + 14, 31, pill[0] + 22, 39], fill=(255, 255, 255))
    draw.text((pill[0] + 30, 29), "AUTONOMOUS AI  •  GRAPHRAG ACTIVE", font=fonts["pill"], fill=(255, 255, 255))

    # --- main card + hard offset shadow (excalidraw) ---
    card = [W / 2 - 235, 62, W / 2 + 235, 432]
    shadow = [c + 6 for c in card]
    draw.rounded_rectangle(shadow, radius=14, fill=(255, 255, 255))
    draw.rounded_rectangle(card, radius=14, fill=(9, 13, 20), outline=(255, 255, 255), width=3)

    cx0 = card[0] + 24
    # header
    draw.rounded_rectangle([cx0, 86, cx0 + 44, 122], radius=6, fill=(22, 27, 34),
                           outline=(255, 255, 255), width=2)
    draw.text((cx0 + 8, 94), "</>", font=fonts["tag"], fill=(255, 255, 255))
    draw.text((cx0 + 56, 86), "PARTH VASTAVIK", font=fonts["title"], fill=(255, 255, 255))
    draw.text((cx0 + 58, 118), "GenAI Engineer & Full-Stack Architect", font=fonts["sub"], fill=(139, 148, 158))
    draw.line([(cx0, 140), (card[2] - 24, 140)], fill=(48, 54, 61), width=2)

    # notice box
    nb = [cx0, 152, card[2] - 24, 196]
    draw.rounded_rectangle(nb, radius=8, fill=(17, 22, 32), outline=(255, 255, 255), width=2)
    draw.text((nb[0] + 10, 158), "LLM orchestration  •  GraphRAG  •  FastAPI", font=fonts["tag"], fill=(230, 237, 243))
    draw.text((nb[0] + 10, 176), "microservices.", font=fonts["tag"], fill=(230, 237, 243))

    # tags
    tags = ["FastAPI", "LangChain", "Langbase", "Neo4j", "Vector DB", "RAG", "Next.js", "Linux"]
    tx, ty = cx0, 206
    for tag in tags:
        tw = len(tag) * 8 + 22
        if tx + tw > card[2] - 24:
            tx, ty = cx0, ty + 30
        draw.rounded_rectangle([tx + 2, ty + 2, tx + tw + 2, ty + 24], radius=10, fill=(255, 255, 255))
        draw.rounded_rectangle([tx, ty, tx + tw, ty + 22], radius=10, fill=(22, 27, 34),
                               outline=(255, 255, 255), width=1)
        draw.text((tx + 11, ty + 4), tag, font=fonts["tag"], fill=(255, 255, 255))
        tx += tw + 8

    # spec rows
    for i, (k, v) in enumerate([("BACKEND:", "Python Async • FastAPI"),
                                ("ENGINE:", "Neo4j + Hybrid RAG")]):
        y = 272 + i * 32
        draw.rounded_rectangle([cx0, y, card[2] - 24, y + 26], radius=12,
                               fill=(13, 17, 23), outline=(255, 255, 255), width=2)
        draw.text((cx0 + 12, y + 6), k, font=fonts["small"], fill=(139, 148, 158))
        draw.text((cx0 + 110, y + 6), v, font=fonts["small"], fill=(255, 255, 255))

    # CTA button
    btn = [cx0, 342, card[2] - 24, 372]
    draw.rounded_rectangle([b + 3 for b in btn], radius=12, fill=(90, 90, 90))
    draw.rounded_rectangle(btn, radius=12, fill=(255, 255, 255))
    draw.text((cx0 + 108, 349), "CONNECT ON LINKEDIN  →", font=fonts["btn"], fill=(5, 7, 10))

    # footer
    draw.text((cx0, 384), "Kolkata, India", font=fonts["small"], fill=(110, 118, 129))
    draw.text((card[2] - 190, 384), "GITHUB: @parthasdey2304", font=fonts["small"], fill=(110, 118, 129))
    # location footer strip
    draw.text((cx0, 404), "preview.html  •  interactive canvas demo", font=fonts["small"], fill=(70, 76, 85))


def render_fallback():
    from PIL import Image, ImageDraw
    fonts = _load_fonts()
    # warmup easing so the loop is seamless (avoid sweep from off-screen)
    sx, sy = mouse_path(0)
    for k in range(40):
        t = k / 40
        mx, my = mouse_path(t)
        sx += (mx - sx) * 0.15
        sy += (my - sy) * 0.15
    frames = []
    for i in range(FRAMES):
        t = i / FRAMES
        mx, my = mouse_path(t)
        sx += (mx - sx) * 0.15
        sy += (my - sy) * 0.15
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        draw_grid_fallback(d, sx, sy)
        img = draw_spotlight(img, sx, sy)
        d = ImageDraw.Draw(img)
        draw_card(d, fonts)
        # quantize per-frame for small file; keep dark palette clean
        frames.append(img.convert("P", palette=Image.ADAPTIVE, colors=128))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    frames[0].save(OUT, save_all=True, append_images=frames[1:],
                   duration=DURATION_MS, loop=0, optimize=True)
    return OUT


# ---------------------------------------------------------------- primary: Playwright screenshots
def render_playwright():
    """Drive preview.html in headless Chromium, screenshot frames, encode GIF."""
    from PIL import Image
    from playwright.sync_api import sync_playwright
    import pathlib
    html = pathlib.Path(__file__).parent.joinpath("preview.html").as_uri()
    frames = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H})
        page.goto(html)
        page.wait_for_function("window.__heroReady === true", timeout=15000)
        page.wait_for_timeout(800)  # let Virgil font + layout settle
        # warmup: ease the in-page smoother onto the path start
        for k in range(20):
            t = k / 20
            import math as m
            x = W / 2 + 200 * m.cos(2 * m.pi * t)
            y = H / 2 + 10 + 95 * m.sin(4 * m.pi * t + 0.6)
            page.evaluate(f"window.__setMouse({x}, {y})")
            page.wait_for_timeout(30)
        for i in range(FRAMES):
            import math as m
            t = i / FRAMES
            x = W / 2 + 200 * m.cos(2 * m.pi * t)
            y = H / 2 + 10 + 95 * m.sin(4 * m.pi * t + 0.6)
            page.evaluate(f"window.__setMouse({x}, {y})")
            page.wait_for_timeout(DURATION_MS)
            shot = page.screenshot()
            import io
            img = Image.open(io.BytesIO(shot)).convert("RGB").resize((W, H))
            frames.append(img.convert("P", palette=Image.ADAPTIVE, colors=128))
        browser.close()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    frames[0].save(OUT, save_all=True, append_images=frames[1:],
                   duration=DURATION_MS, loop=0, optimize=True)
    return OUT


def main():
    try:
        # Prefer pixel-faithful browser capture when deps exist
        import importlib.util
        if importlib.util.find_spec("playwright") is not None:
            try:
                path = render_playwright()
                print(f"[record] browser capture -> {path}")
                return
            except Exception as e:
                print(f"[record] playwright failed ({e}); using PIL fallback")
        else:
            print("[record] playwright not installed; using PIL fallback")
    except Exception as e:
        print(f"[record] capture check failed ({e}); using PIL fallback")
    path = render_fallback()
    size_kb = os.path.getsize(path) / 1024
    print(f"[record] fallback render -> {path} ({size_kb:.0f} KB, {FRAMES} frames)")


if __name__ == "__main__":
    sys.exit(main())
