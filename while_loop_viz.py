from PIL import Image, ImageDraw, ImageFont
import os

# ── Fonts ──────────────────────────────────────────────────────────────────
MONO_BOLD = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"
MONO      = "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"
SANS      = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

fnt_kw   = ImageFont.truetype(MONO_BOLD, 22)   # keywords  (purple)
fnt_code = ImageFont.truetype(MONO,      22)   # plain code
fnt_big  = ImageFont.truetype(SANS_BOLD, 52)   # big countdown
fnt_lbl  = ImageFont.truetype(SANS,      15)   # small labels

# ── Palette ────────────────────────────────────────────────────────────────
BG       = (15,  17,  26)   # near-black navy
PANEL_BG = (24,  27,  40)   # slightly lighter panel
BORDER   = (55,  60,  90)   # subtle border
GREEN    = (80, 220, 130)   # "running" accent
RED      = (255, 85,  85)   # "done" accent
YELLOW   = (255, 210, 60)   # variable highlight
PURPLE   = (180, 130, 255)  # keyword
CYAN     = (90, 210, 255)   # number literal
WHITE    = (230, 232, 240)
GRAY     = (110, 115, 145)
ARROW    = (255, 140,  50)  # execution arrow

W, H = 640, 400

# ── Code lines ─────────────────────────────────────────────────────────────
# We'll draw the code manually with colour tokens
CODE_X = 52   # left margin for code
CODE_Y = 60   # top of first code line
LINE_H = 32   # line height

def draw_rounded_rect(draw, xy, radius=10, fill=None, outline=None, width=1):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)

def make_frame(count, active_line, done=False):
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # ── Background panel ──
    draw_rounded_rect(draw, (18, 18, W-18, H-18), radius=14,
                      fill=PANEL_BG, outline=BORDER, width=2)

    # ── Title bar ──
    draw_rounded_rect(draw, (18, 18, W-18, 50), radius=14, fill=(30, 34, 52))
    draw.text((30, 25), "🚀  while_loop_demo.py", font=fnt_lbl, fill=GRAY)

    # ── Execution arrow ──
    arrow_y = CODE_Y + active_line * LINE_H + 10
    draw.text((28, arrow_y), "▶", font=fnt_code, fill=ARROW if not done else BG)

    # helper: draw a coloured token and return next x
    def tok(x, y, text, color, fnt=fnt_code):
        draw.text((x, y), text, font=fnt, fill=color)
        return x + fnt.getlength(text)

    # ── Line 0: count = 5 ──
    y = CODE_Y
    x = CODE_X
    x = tok(x, y, "count", YELLOW)
    x = tok(x, y, " = ", WHITE)
    x = tok(x, y, "5", CYAN)

    # ── Line 1: while count > 0: ──
    y = CODE_Y + LINE_H
    x = CODE_X
    x = tok(x, y, "while ", PURPLE, fnt_kw)
    x = tok(x, y, "count", YELLOW)
    x = tok(x, y, " > ", WHITE)
    x = tok(x, y, "0", CYAN)
    x = tok(x, y, ":", WHITE)

    # ── Line 2: print(f"…") ──
    y = CODE_Y + 2*LINE_H
    x = CODE_X + 36   # indent
    x = tok(x, y, "print", PURPLE, fnt_kw)
    x = tok(x, y, '(f"Blast off in ', WHITE)
    x = tok(x, y, str(count) if not done else "...", CYAN)
    x = tok(x, y, '!")', WHITE)

    # ── Line 3: count -= 1 ──
    y = CODE_Y + 3*LINE_H
    x = CODE_X + 36
    x = tok(x, y, "count", YELLOW)
    x = tok(x, y, " -= ", WHITE)
    x = tok(x, y, "1", CYAN)

    # ── Line 4: print("🚀 LAUNCH!") ──
    y = CODE_Y + 4*LINE_H
    x = CODE_X
    x = tok(x, y, "print", PURPLE, fnt_kw)
    x = tok(x, y, '("', WHITE)
    x = tok(x, y, "🚀 LAUNCH!" if done else "🚀 LAUNCH!", GREEN if done else GRAY)
    x = tok(x, y, '")', WHITE)

    # ── Divider ──
    div_y = CODE_Y + 5*LINE_H + 6
    draw.line([(28, div_y), (W-28, div_y)], fill=BORDER, width=1)

    # ── Variable inspector ──
    var_y = div_y + 12
    draw.text((CODE_X, var_y), "variables", font=fnt_lbl, fill=GRAY)

    # count badge
    badge_x = CODE_X + 90
    badge_col = RED if done else (GREEN if count > 0 else RED)
    draw_rounded_rect(draw, (badge_x, var_y - 2, badge_x + 130, var_y + 22),
                      radius=6, fill=badge_col + (40,) if False else badge_col)
    cval = "0 ✗" if done and count == 0 else str(count)
    draw.text((badge_x + 8, var_y), f"count = {cval}", font=fnt_lbl, fill=WHITE)

    # ── Big countdown display ──
    big_x = W - 160
    big_y = div_y + 8

    if done:
        label = "LAUNCH!"
        col   = GREEN
        draw.text((big_x - 10, big_y), label, font=fnt_lbl, fill=GREEN)
        # rocket emoji big
        draw.text((big_x + 10, big_y + 18), "🚀", font=fnt_big, fill=GREEN)
    else:
        draw.text((big_x + 20, big_y), "T-minus", font=fnt_lbl, fill=GRAY)
        num_str = str(count)
        nw = fnt_big.getlength(num_str)
        draw.text((big_x + (100 - nw)//2, big_y + 16), num_str, font=fnt_big, fill=YELLOW)

    # ── Status strip ──
    status_y = H - 38
    status_col = GREEN if not done else RED
    status_txt = "● CONDITION TRUE — looping…" if not done else "● CONDITION FALSE — loop exits"
    if done:
        status_col = RED
    draw.text((CODE_X, status_y), status_txt, font=fnt_lbl, fill=status_col)

    return img


# ── Build frames ───────────────────────────────────────────────────────────
frames = []
durations = []

def add(img, ms):
    frames.append(img)
    durations.append(ms)

# Pause on initial state (line 0 highlighted, count=5)
for _ in range(3):
    add(make_frame(5, active_line=0), 350)

# Loop iterations: count 5 → 4 → 3 → 2 → 1
for count in [5, 4, 3, 2, 1]:
    # check condition line
    add(make_frame(count, active_line=1), 500)
    # print line
    add(make_frame(count, active_line=2), 600)
    # decrement line
    add(make_frame(count, active_line=3), 500)

# Check condition with count=0 → false → exit
add(make_frame(0, active_line=1, done=True), 700)
# final print line
for _ in range(6):
    add(make_frame(0, active_line=4, done=True), 400)

# ── Save ──────────────────────────────────────────────────────────────────
out = "/mnt/user-data/outputs/while_loop_countdown.gif"
frames[0].save(
    out,
    save_all=True,
    append_images=frames[1:],
    duration=durations,
    loop=0,
    optimize=False,
)
print(f"Saved {len(frames)} frames → {out}")
print(f"Size: {os.path.getsize(out) / 1024:.1f} KB")
