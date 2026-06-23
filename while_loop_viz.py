from PIL import Image, ImageDraw, ImageFont
import os, math, random, subprocess, sys

# ── Config ─────────────────────────────────────────────────────────────────
START_COUNT = 10        # ← change this to adjust starting number
OUTPUT_FILE = "while_loop_countdown.gif"

def generate_gif():
    # ── Fonts ──────────────────────────────────────────────────────────────
    def load_font(paths, size):
        for path in paths:
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
        return ImageFont.load_default()

    mono_bold_paths = [
        "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
        "/System/Library/Fonts/Courier New Bold.ttf",
        "/Library/Fonts/CourierNewPSBoldMT.ttf",
    ]
    mono_paths = [
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "/System/Library/Fonts/Courier New.ttf",
        "/Library/Fonts/CourierNewPSMT.ttf",
    ]
    sans_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    sans_bold_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf",
    ]

    fnt_kw   = load_font(mono_bold_paths, 22)
    fnt_code = load_font(mono_paths,      22)
    fnt_big  = load_font(sans_bold_paths, 52)
    fnt_lbl  = load_font(sans_paths,      15)
    fnt_med  = load_font(sans_bold_paths, 22)

    # ── Palette ────────────────────────────────────────────────────────────
    BG       = (15,  17,  26)
    PANEL_BG = (24,  27,  40)
    BORDER   = (55,  60,  90)
    GREEN    = (80, 220, 130)
    RED      = (255, 85,  85)
    ORANGE   = (255, 140,  50)
    YELLOW   = (255, 210, 60)
    PURPLE   = (180, 130, 255)
    CYAN     = (90, 210, 255)
    WHITE    = (230, 232, 240)
    GRAY     = (110, 115, 145)
    ARROW    = (255, 140,  50)

    W, H   = 640, 400
    CODE_X = 52
    CODE_Y = 60
    LINE_H = 32

    # ── Helpers ────────────────────────────────────────────────────────────
    def draw_rounded_rect(draw, xy, radius=10, fill=None, outline=None, width=1):
        draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

    def tok(draw, x, y, text, color, fnt=fnt_code):
        draw.text((x, y), text, font=fnt, fill=color)
        return x + fnt.getlength(text)

    def base_panel(title="🚀  while_loop_demo.py"):
        img  = Image.new("RGB", (W, H), BG)
        draw = ImageDraw.Draw(img)
        draw_rounded_rect(draw, (18, 18, W-18, H-18), radius=14, fill=PANEL_BG, outline=BORDER, width=2)
        draw_rounded_rect(draw, (18, 18, W-18, 50),   radius=14, fill=(30, 34, 52))
        draw.text((30, 25), title, font=fnt_lbl, fill=GRAY)
        return img, draw

    # ── Explosion particles (seeded so they're consistent) ─────────────────
    random.seed(42)
    particles = [
        {"angle": random.uniform(0, 2*math.pi),
         "speed": random.uniform(30, 120),
         "color": random.choice([RED, ORANGE, YELLOW, WHITE]),
         "size":  random.randint(3, 9)}
        for _ in range(60)
    ]

    def make_explosion_frame(t):
        """t = 0.0 → 1.0, explosion progress"""
        img, draw = base_panel("💥  while_loop_demo.py")
        cx, cy = W // 2, H // 2 + 20

        if t < 0.15:
            alpha = int(180 * (1 - t / 0.15))
            flash = Image.new("RGB", (W, H), (255, 200, 80))
            img   = Image.blend(img, flash, alpha / 255)
            draw  = ImageDraw.Draw(img)

        for p in particles:
            dist = p["speed"] * t * 3
            px   = int(cx + math.cos(p["angle"]) * dist)
            py   = int(cy + math.sin(p["angle"]) * dist)
            fade = max(0, 1 - t * 1.4)
            r, g, b = p["color"]
            col  = (int(r*fade), int(g*fade), int(b*fade))
            sz   = max(1, int(p["size"] * (1 - t * 0.7)))
            draw.ellipse([px-sz, py-sz, px+sz, py+sz], fill=col)

        for ring in range(3):
            ring_t = t - ring * 0.12
            if 0 < ring_t < 0.8:
                r  = int(ring_t * 200)
                rc = (255, int(140 * (1 - ring_t)), 0)
                draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=rc, width=max(1, 3-ring))

        if 0.1 < t < 0.85:
            boom_alpha = min(1.0, (t - 0.1) / 0.2) * max(0, (0.85 - t) / 0.3)
            bc = (int(255*boom_alpha), int(80*boom_alpha), int(80*boom_alpha))
            bw = fnt_big.getlength("BOOM!")
            draw.text((cx - bw//2, cy - 34), "BOOM!", font=fnt_big, fill=bc)

        draw.text((CODE_X, H-38), "● count = 0  —  loop exits  💥", font=fnt_lbl, fill=RED)
        return img

    def make_frame(count, active_line, done=False):
        img, draw = base_panel()

        arrow_y = CODE_Y + active_line * LINE_H + 10
        draw.text((28, arrow_y), "▶", font=fnt_code, fill=ARROW if not done else BG)

        # Line 0: count = START_COUNT
        y, x = CODE_Y, CODE_X
        x = tok(draw, x, y, "count", YELLOW)
        x = tok(draw, x, y, " = ", WHITE)
        x = tok(draw, x, y, str(START_COUNT), CYAN)

        # Line 1: while count > 0:
        y = CODE_Y + LINE_H; x = CODE_X
        x = tok(draw, x, y, "while ", PURPLE, fnt_kw)
        x = tok(draw, x, y, "count", YELLOW)
        x = tok(draw, x, y, " > ", WHITE)
        x = tok(draw, x, y, "0", CYAN)
        x = tok(draw, x, y, ":", WHITE)

        # Line 2: print(f"🚀 T-minus {count}!")
        y = CODE_Y + 2*LINE_H; x = CODE_X + 36
        x = tok(draw, x, y, "print", PURPLE, fnt_kw)
        cv = str(count) if not done else "..."
        x = tok(draw, x, y, '(f"🚀 T-minus ', WHITE)
        x = tok(draw, x, y, cv, CYAN)
        x = tok(draw, x, y, '!")', WHITE)

        # Line 3: count -= 1
        y = CODE_Y + 3*LINE_H; x = CODE_X + 36
        x = tok(draw, x, y, "count", YELLOW)
        x = tok(draw, x, y, " -= ", WHITE)
        x = tok(draw, x, y, "1", CYAN)

        # Line 4: print("💥 BOOM!")
        y = CODE_Y + 4*LINE_H; x = CODE_X
        x = tok(draw, x, y, "print", PURPLE, fnt_kw)
        x = tok(draw, x, y, '("', WHITE)
        x = tok(draw, x, y, "💥 BOOM!", RED if done else GRAY)
        x = tok(draw, x, y, '")', WHITE)

        # Divider
        div_y = CODE_Y + 5*LINE_H + 6
        draw.line([(28, div_y), (W-28, div_y)], fill=BORDER, width=1)

        # Variable inspector
        var_y = div_y + 12
        draw.text((CODE_X, var_y), "variables", font=fnt_lbl, fill=GRAY)
        badge_x   = CODE_X + 90
        badge_col = RED if (done or count == 0) else GREEN
        draw_rounded_rect(draw, (badge_x, var_y-2, badge_x+145, var_y+22), radius=6, fill=badge_col)
        cval = "0  ✗ exits!" if (done and count == 0) else str(count)
        draw.text((badge_x + 8, var_y), f"count = {cval}", font=fnt_lbl, fill=WHITE)

        # Right panel: spaceship + countdown number
        big_x = W - 155
        big_y = div_y + 6
        if done:
            draw.text((big_x, big_y), "BOOM!", font=fnt_med, fill=RED)
            draw.text((big_x + 12, big_y + 26), "💥", font=fnt_big, fill=RED)
        else:
            draw.text((big_x + 18, big_y), "T-minus", font=fnt_lbl, fill=GRAY)
            draw.text((big_x + 48, big_y + 14), "🚀", font=fnt_med, fill=WHITE)
            num_str = str(count)
            nw      = fnt_big.getlength(num_str)
            ratio   = count / START_COUNT
            draw.text((big_x + (110 - nw)//2, big_y + 38), num_str,
                      font=fnt_big, fill=(255, int(210*ratio), int(60*ratio)))

        # Status strip
        if done:
            draw.text((CODE_X, H-38), "● CONDITION FALSE — loop exits", font=fnt_lbl, fill=RED)
        else:
            draw.text((CODE_X, H-38), "● CONDITION TRUE — looping…",   font=fnt_lbl, fill=GREEN)

        return img

    # ── Build frames ───────────────────────────────────────────────────────
    frames, durations = [], []

    def add(img, ms):
        frames.append(img)
        durations.append(ms)

    for _ in range(3):
        add(make_frame(START_COUNT, active_line=0), 350)

    for count in range(START_COUNT, 0, -1):
        add(make_frame(count, active_line=1), 420)
        add(make_frame(count, active_line=2), 520)
        add(make_frame(count, active_line=3), 420)

    add(make_frame(0, active_line=1, done=True), 600)

    N_EXPLODE = 20
    for i in range(N_EXPLODE):
        add(make_explosion_frame(i / (N_EXPLODE - 1)), 75)
    for _ in range(8):
        add(make_explosion_frame(1.0), 200)

    # ── Save & open ────────────────────────────────────────────────────────
    out = OUTPUT_FILE
    frames[0].save(out, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=False)
    print(f"✅ Saved {len(frames)} frames → {out}  ({os.path.getsize(out)//1024} KB)")

    # Open the GIF automatically
    if sys.platform == "darwin":
        subprocess.run(["open", out])
    elif sys.platform.startswith("linux"):
        subprocess.run(["xdg-open", out])
    elif sys.platform == "win32":
        os.startfile(out)


generate_gif()
