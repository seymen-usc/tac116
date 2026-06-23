from PIL import Image, ImageDraw, ImageFont
import os, math, random, subprocess, sys

# ── Config ─────────────────────────────────────────────────────────────────
START_COUNT = 5         # <- change this to adjust starting number
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

    fnt_kw   = load_font(mono_bold_paths, 20)
    fnt_code = load_font(mono_paths,      20)
    fnt_big  = load_font(sans_bold_paths, 48)
    fnt_lbl  = load_font(sans_paths,      14)
    fnt_out  = load_font(mono_paths,      13)   # output console font

    # ── Palette ────────────────────────────────────────────────────────────
    BG         = (15,  17,  26)
    PANEL_BG   = (24,  27,  40)
    BORDER     = (55,  60,  90)
    GREEN      = (80, 220, 130)
    RED        = (255, 85,  85)
    ORANGE     = (255, 140,  50)
    YELLOW     = (255, 210, 60)
    PURPLE     = (180, 130, 255)
    CYAN       = (90, 210, 255)
    WHITE      = (230, 232, 240)
    GRAY       = (110, 115, 145)
    ARROW      = (255, 140,  50)
    OUT_BG     = (10,  12,  20)   # darker console background
    OUT_TEXT   = (140, 220, 140)  # classic green terminal text
    OUT_BORDER = (40,  50,  80)

    W, H    = 720, 440
    CODE_X  = 52
    CODE_Y  = 62
    LINE_H  = 30

    # Layout: code panel on left, output panel on right
    SPLIT_X = 430   # x where right panel starts
    OUT_X   = SPLIT_X + 16
    OUT_Y   = CODE_Y + LINE_H  # aligns with line 1

    # ── Helpers ────────────────────────────────────────────────────────────
    def draw_rounded_rect(draw, xy, radius=10, fill=None, outline=None, width=1):
        draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

    def tok(draw, x, y, text, color, fnt=fnt_code):
        draw.text((x, y), text, font=fnt, fill=color)
        return x + fnt.getlength(text)

    def draw_rocket(draw, cx, cy, size=1.0, color=WHITE):
        s = size
        body = [
            (cx,              cy - int(20*s)),
            (cx + int(8*s),   cy - int(4*s)),
            (cx + int(8*s),   cy + int(11*s)),
            (cx - int(8*s),   cy + int(11*s)),
            (cx - int(8*s),   cy - int(4*s)),
        ]
        draw.polygon(body, fill=color)
        draw.ellipse([cx-int(4*s), cy-int(3*s), cx+int(4*s), cy+int(4*s)], fill=CYAN)
        draw.polygon([
            (cx - int(8*s),  cy + int(3*s)),
            (cx - int(15*s), cy + int(13*s)),
            (cx - int(8*s),  cy + int(11*s)),
        ], fill=ORANGE)
        draw.polygon([
            (cx + int(8*s),  cy + int(3*s)),
            (cx + int(15*s), cy + int(13*s)),
            (cx + int(8*s),  cy + int(11*s)),
        ], fill=ORANGE)
        draw.polygon([
            (cx - int(5*s), cy + int(11*s)),
            (cx,             cy + int(20*s)),
            (cx + int(5*s), cy + int(11*s)),
        ], fill=YELLOW)

    def base_panel(draw, boom=False):
        draw_rounded_rect(draw, (18, 18, W-18, H-18), radius=14, fill=PANEL_BG, outline=BORDER, width=2)
        # title bar
        draw_rounded_rect(draw, (18, 18, W-18, 52), radius=14, fill=(30, 34, 52))
        prefix = "[!!]" if boom else "[>]"
        col    = RED   if boom else GRAY
        draw.text((30, 30), f"{prefix}  while_loop_demo.py", font=fnt_lbl, fill=col)
        # vertical divider between code and output panels
        draw.line([(SPLIT_X, 52), (SPLIT_X, H-18)], fill=BORDER, width=1)
        # output panel header
        draw.text((OUT_X, 58), "output", font=fnt_lbl, fill=GRAY)

    # ── Explosion particles ────────────────────────────────────────────────
    random.seed(42)
    particles = [
        {"angle": random.uniform(0, 2*math.pi),
         "speed": random.uniform(30, 110),
         "color": random.choice([RED, ORANGE, YELLOW, WHITE]),
         "size":  random.randint(3, 9)}
        for _ in range(60)
    ]

    def make_explosion_frame(t, output_lines):
        img = Image.new("RGB", (W, H), BG)
        if t < 0.15:
            alpha = int(180 * (1 - t / 0.15))
            flash = Image.new("RGB", (W, H), (255, 200, 80))
            img   = Image.blend(img, flash, alpha / 255)
        draw = ImageDraw.Draw(img)
        base_panel(draw, boom=True)

        # explosion centred in the code panel area
        cx, cy = SPLIT_X // 2 + 18, H // 2 + 30
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
                r  = int(ring_t * 160)
                rc = (255, int(140 * (1 - ring_t)), 0)
                draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=rc, width=max(1, 3-ring))
        if 0.1 < t < 0.85:
            boom_alpha = min(1.0, (t-0.1)/0.2) * max(0, (0.85-t)/0.3)
            bc = (int(255*boom_alpha), int(80*boom_alpha), int(80*boom_alpha))
            bw = fnt_big.getlength("WEEEE!")
            draw.text((cx - bw//2, cy - 30), "WEEEE!", font=fnt_big, fill=bc)

        # output panel: show all accumulated output lines + BOOM
        all_lines = output_lines + ["** WEEEE! **"]
        for i, line in enumerate(all_lines):
            col = RED if line == "** WEEEE! **" else OUT_TEXT
            draw.text((OUT_X, OUT_Y + i * 18), line, font=fnt_out, fill=col)

        draw.text((CODE_X, H-32), "● count = 0  —  loop exits!", font=fnt_lbl, fill=RED)
        return img

    def make_frame(count, active_line, output_lines, done=False):
        img  = Image.new("RGB", (W, H), BG)
        draw = ImageDraw.Draw(img)
        base_panel(draw)

        # execution arrow (highlighted line background)
        arrow_y = CODE_Y + active_line * LINE_H
        if not done:
            draw_rounded_rect(draw, (26, arrow_y - 3, SPLIT_X - 8, arrow_y + LINE_H - 6),
                              radius=4, fill=(40, 45, 65))
        draw.text((30, arrow_y), ">", font=fnt_code, fill=ARROW if not done else BG)

        # ── Code lines ──

        # Line 0: count = 5
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

        # Line 2:     print("T-minus", count, "!")
        y = CODE_Y + 2*LINE_H; x = CODE_X + 30
        x = tok(draw, x, y, "print", PURPLE, fnt_kw)
        x = tok(draw, x, y, '(', WHITE)
        x = tok(draw, x, y, '"T-minus"', CYAN)
        x = tok(draw, x, y, ', ', WHITE)
        x = tok(draw, x, y, 'count', YELLOW)
        x = tok(draw, x, y, ', ', WHITE)
        x = tok(draw, x, y, '"!"', CYAN)
        x = tok(draw, x, y, ')', WHITE)

        # Line 3:     count -= 1
        y = CODE_Y + 3*LINE_H; x = CODE_X + 30
        x = tok(draw, x, y, "count", YELLOW)
        x = tok(draw, x, y, " -= ", WHITE)
        x = tok(draw, x, y, "1", CYAN)

        # Line 4: print("** WEEEE! **")
        y = CODE_Y + 4*LINE_H; x = CODE_X
        x = tok(draw, x, y, "print", PURPLE, fnt_kw)
        x = tok(draw, x, y, '(', WHITE)
        x = tok(draw, x, y, '"** WEEEE! **"', RED if done else GRAY)
        x = tok(draw, x, y, ')', WHITE)

        # ── Divider below code ──
        div_y = CODE_Y + 5*LINE_H + 4
        draw.line([(26, div_y), (SPLIT_X - 8, div_y)], fill=BORDER, width=1)

        # ── Variable inspector ──
        var_y = div_y + 10
        draw.text((CODE_X, var_y), "variables:", font=fnt_lbl, fill=GRAY)
        badge_x   = CODE_X + 85
        badge_col = RED if (done or count == 0) else GREEN
        draw_rounded_rect(draw, (badge_x, var_y-2, badge_x+150, var_y+20), radius=5, fill=badge_col)
        cval = "0  (exits!)" if (done and count == 0) else str(count)
        draw.text((badge_x + 8, var_y), f"count = {cval}", font=fnt_lbl, fill=WHITE)

        # ── Rocket panel (bottom right) ──
        rocket_cx = SPLIT_X + (W - SPLIT_X) // 2
        rocket_cy = H - 100
        if done:
            for angle in range(0, 360, 30):
                rad = math.radians(angle)
                ex  = rocket_cx + int(math.cos(rad) * 20)
                ey  = rocket_cy + int(math.sin(rad) * 20)
                draw.line([(rocket_cx, rocket_cy), (ex, ey)], fill=ORANGE, width=2)
            draw.ellipse([rocket_cx-8, rocket_cy-8, rocket_cx+8, rocket_cy+8], fill=RED)
        else:
            draw_rocket(draw, rocket_cx, rocket_cy, size=0.9, color=WHITE)

        # ── Output console panel ──
        for i, line in enumerate(output_lines):
            draw.text((OUT_X, OUT_Y + i * 18), line, font=fnt_out, fill=OUT_TEXT)

        # ── Status strip ──
        if done:
            draw.text((CODE_X, H-32), "● CONDITION FALSE — loop exits", font=fnt_lbl, fill=RED)
        else:
            draw.text((CODE_X, H-32), "● CONDITION TRUE — looping...", font=fnt_lbl, fill=GREEN)

        return img

    # ── Build frames ───────────────────────────────────────────────────────
    frames, durations = [], []

    def add(img, ms):
        frames.append(img)
        durations.append(ms)

    output_lines = []   # accumulates printed output as loop runs

    # Initial assignment line — pause here so viewer can read
    for _ in range(5):
        add(make_frame(START_COUNT, active_line=0, output_lines=[]), 300)

    for count in range(START_COUNT, 0, -1):
        # Step 1: check condition — hold long so viewer can read
        for _ in range(4):
            add(make_frame(count, active_line=1, output_lines=output_lines), 300)

        # Step 2: print line — show the new output appearing
        new_line = f"T-minus {count} !"
        for _ in range(4):
            add(make_frame(count, active_line=2, output_lines=output_lines), 300)
        output_lines.append(new_line)
        # hold a beat after output appears
        for _ in range(3):
            add(make_frame(count, active_line=2, output_lines=output_lines), 300)

        # Step 3: decrement — hold so viewer sees count change
        for _ in range(4):
            add(make_frame(count - 1, active_line=3, output_lines=output_lines), 300)

    # Condition false at count=0
    for _ in range(5):
        add(make_frame(0, active_line=1, output_lines=output_lines, done=True), 300)

    # Explosion
    N_EXPLODE = 22
    for i in range(N_EXPLODE):
        add(make_explosion_frame(i / (N_EXPLODE - 1), output_lines), 70)
    for _ in range(10):
        add(make_explosion_frame(1.0, output_lines), 200)

    # ── Save & open ────────────────────────────────────────────────────────
    frames[0].save(OUTPUT_FILE, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=False)
    print(f"Saved {len(frames)} frames -> {OUTPUT_FILE}  ({os.path.getsize(OUTPUT_FILE)//1024} KB)")

    if sys.platform == "darwin":
        subprocess.run(["open", OUTPUT_FILE])
    elif sys.platform.startswith("linux"):
        subprocess.run(["xdg-open", OUTPUT_FILE])
    elif sys.platform == "win32":
        os.startfile(OUTPUT_FILE)


generate_gif()
