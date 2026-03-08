#!/usr/bin/env python3
"""
YellowJacket Theme — Asset Generator
WiFi Pineapple Pager (480x222 display)

High-contrast black and yellow theme. Clean, flat, candy-polished UI.
No glow, no scanlines, no animations beyond boot. Sharp edges, bold contrast.
Supersampled rendering at 3x with LANCZOS downscale for anti-aliased edges.

Usage: python3 generate_yellowjacket_assets.py
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont

# ─── Configuration ───────────────────────────────────────────────────────────

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
SS = 3  # Supersample factor

# ─── YellowJacket Palette ────────────────────────────────────────────────────
# Pure black and yellow. High contrast. Clean.

# Backgrounds — true black
BG        = (0, 0, 0)              # Pure black background
PANEL     = (14, 14, 10)           # Near-black panel — subtle warmth
PANEL_L   = (24, 22, 14)           # Lighter panel — hover/active areas

# Yellow — the accent (warm gold-yellow, not lemon)
YELLOW    = (255, 200, 0)          # Primary accent — bold yellow
YELLOW_L  = (255, 220, 60)         # Light yellow — highlights
YELLOW_D  = (140, 110, 0)          # Dark yellow — dimmed/inactive
YELLOW_DD = (70, 55, 0)            # Very dark yellow — subtle structural

# Neutrals
WHITE     = (245, 240, 230)        # Warm white — text
SOFT_W    = (200, 195, 185)        # Soft white — secondary text
GRAY      = (100, 95, 85)          # Disabled text
DARK_GRAY = (35, 33, 28)           # Borders / separators
DIM       = (45, 42, 32)           # Dimmed elements

# Functional colors (kept distinct for clarity — yellow theme doesn't mask errors)
RED       = (220, 55, 40)          # Alert / error
GREEN     = (75, 195, 75)          # Success / enabled
CYAN      = (0, 195, 215)          # Info readout

T = (0, 0, 0, 0)  # Transparent

# Section colors — all yellow (unified, theme.json maps everything to yellow)
SEC_ACCENT   = YELLOW
SEC_DIM      = YELLOW_D
SEC_DARK     = YELLOW_DD


# ─── Core Drawing Utilities ──────────────────────────────────────────────────

def _c(color, alpha=255):
    if len(color) == 4:
        return color
    return (*color, alpha)


def ensure_dir(path):
    os.makedirs(os.path.join(ASSETS_DIR, path), exist_ok=True)


def save(img, path):
    full = os.path.join(ASSETS_DIR, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    img.save(full, "PNG", optimize=True)


def new(w, h, bg=None):
    if bg is None:
        return Image.new("RGBA", (w, h), T)
    return Image.new("RGBA", (w, h), _c(bg))


def ss_start(w, h, bg=None):
    img = new(w * SS, h * SS, bg)
    return img, ImageDraw.Draw(img)


def ss_finish(img, w, h):
    return img.resize((w, h), Image.LANCZOS)


def rrect(d, xy, fill=None, outline=None, radius=4, width=1, s=SS):
    x0, y0, x1, y1 = [v * s for v in xy] if s > 1 else xy
    r = radius * s if s > 1 else radius
    w = width * s if s > 1 else width
    d.rounded_rectangle([x0, y0, x1, y1], radius=r,
                        fill=_c(fill) if fill else None,
                        outline=_c(outline) if outline else None,
                        width=w)


# ─── YellowJacket Background Templates ──────────────────────────────────────

def yj_frame_bg(w, h, top_h=26):
    """Clean black background with yellow-accented status bar."""
    img, d = ss_start(w, h, BG)
    s = SS

    # Status bar — dark panel
    d.rectangle([0, 0, w * s, top_h * s], fill=_c(PANEL))

    # 1px yellow separator below status bar
    d.rectangle([0, (top_h - 1) * s, w * s, top_h * s], fill=_c(YELLOW, 40))

    return img


def yj_section_bg(w, h, top_h=26, sidebar_w=4, bottom_h=3):
    """Section background — yellow left bar, yellow bottom strip."""
    img, d = ss_start(w, h, BG)
    s = SS

    # Status bar
    d.rectangle([0, 0, w * s, top_h * s], fill=_c(PANEL))
    d.rectangle([0, (top_h - 1) * s, w * s, top_h * s], fill=_c(YELLOW, 40))

    # Left sidebar bar — yellow structural accent
    bar_top = top_h * s
    bar_bot = (h - bottom_h) * s
    d.rectangle([0, bar_top, sidebar_w * s, bar_bot], fill=_c(YELLOW))

    # Bottom accent strip
    d.rectangle([0, (h - bottom_h) * s, w * s, h * s], fill=_c(YELLOW_DD, 50))
    d.rectangle([0, (h - bottom_h) * s, w * s, (h - bottom_h + 1) * s],
                fill=_c(YELLOW, 30))

    return img


# ─── Dashboard ───────────────────────────────────────────────────────────────

def gen_dashboard():
    """Main dashboard — 5 full-width horizontal bands.
    Unselected: black band with dim yellow icon/label.
    Selected: solid yellow band with black icon/label.
    """
    ensure_dir("dashboard")

    W, H = 480, 222
    TOP_BAR = 26
    BAND_H = 39       # (222 - 26) / 5 ≈ 39.2, use 39 with 1px gaps
    BAND_W = 480
    s = SS

    # ── Background: black base + status bar + faint band separators ──
    img, d = ss_start(W, H, BG)

    # Status bar
    d.rectangle([0, 0, W * s, TOP_BAR * s], fill=_c(PANEL))
    d.rectangle([0, (TOP_BAR - 1) * s, W * s, TOP_BAR * s], fill=_c(YELLOW, 35))

    # 5 bands with 1px yellow separator lines between them
    for i in range(1, 5):
        y = TOP_BAR + i * BAND_H
        d.rectangle([0, y * s, W * s, (y + 1) * s], fill=_c(YELLOW_DD, 40))

    result = ss_finish(img, W, H)
    save(result, "dashboard/yj_bg.png")

    # ── Band background (480x39) — transparent (bg shows through) ──
    img = new(BAND_W, BAND_H)
    save(img, "dashboard/band_bg.png")

    # ── Band highlight (480x47) — taller solid yellow fill for selected state ──
    SEL_BAND_H = 47
    img, d = ss_start(BAND_W, SEL_BAND_H)
    d.rectangle([0, 0, BAND_W * s, SEL_BAND_H * s], fill=_c(YELLOW))
    result = ss_finish(img, BAND_W, SEL_BAND_H)
    save(result, "dashboard/band_highlight.png")

    # ── Breadcrumb dots (8x8) ──
    dot_size = 8
    img, d = ss_start(dot_size, dot_size)
    d.ellipse([1 * s, 1 * s, (dot_size - 1) * s, (dot_size - 1) * s],
              outline=_c((255, 255, 255), 255), width=2 * s)
    save(ss_finish(img, dot_size, dot_size), "dashboard/dot_hollow.png")

    img, d = ss_start(dot_size, dot_size)
    d.ellipse([1 * s, 1 * s, (dot_size - 1) * s, (dot_size - 1) * s],
              fill=_c((255, 255, 255), 255))
    save(ss_finish(img, dot_size, dot_size), "dashboard/dot_filled.png")

    # ── Nav Icons — 30x30 (smaller for horizontal band layout) ──
    ICON_SIZE = 30

    # Alerts Icon — bell silhouette
    rw, rh = ICON_SIZE, ICON_SIZE
    img, d = ss_start(rw, rh)
    wc = _c((255, 255, 255), 255)
    wd = _c((255, 255, 255), 160)
    # Bell body
    d.arc([(4 * s, 3 * s), (26 * s, 20 * s)], 180, 360, fill=wc, width=2 * s)
    d.line([(4 * s, 12 * s), (4 * s, 22 * s)], fill=wc, width=2 * s)
    d.line([(26 * s, 12 * s), (26 * s, 22 * s)], fill=wc, width=2 * s)
    d.rectangle([2 * s, 21 * s, 28 * s, 23 * s], fill=wc)
    # Clapper
    d.ellipse([13 * s, 24 * s, 17 * s, 28 * s], fill=wc)
    # Top nub
    d.ellipse([13 * s, 1 * s, 17 * s, 5 * s], fill=wc)
    result = ss_finish(img, rw, rh)
    save(result, "dashboard/alerts.png")

    # Payloads Icon — rocket
    img, d = ss_start(rw, rh)
    wc = _c((255, 255, 255), 255)
    wd = _c((255, 255, 255), 140)
    # Rocket body
    d.polygon([(15 * s, 2 * s), (20 * s, 10 * s), (20 * s, 22 * s),
               (10 * s, 22 * s), (10 * s, 10 * s)], fill=_c((255, 255, 255), 40), outline=wc)
    # Nose cone
    d.polygon([(15 * s, 2 * s), (10 * s, 10 * s), (20 * s, 10 * s)],
              fill=_c((255, 255, 255), 60), outline=wc)
    # Fins
    d.polygon([(10 * s, 18 * s), (5 * s, 24 * s), (10 * s, 22 * s)], fill=wc)
    d.polygon([(20 * s, 18 * s), (25 * s, 24 * s), (20 * s, 22 * s)], fill=wc)
    # Exhaust
    d.line([(13 * s, 22 * s), (12 * s, 27 * s)], fill=wd, width=1 * s)
    d.line([(15 * s, 22 * s), (15 * s, 28 * s)], fill=wd, width=1 * s)
    d.line([(17 * s, 22 * s), (18 * s, 27 * s)], fill=wd, width=1 * s)
    # Window
    d.ellipse([13 * s, 12 * s, 17 * s, 16 * s], outline=wc, width=1 * s)
    result = ss_finish(img, rw, rh)
    save(result, "dashboard/payloads.png")

    # Recon Icon — radar sweep
    img, d = ss_start(rw, rh)
    wc = _c((255, 255, 255), 255)
    wd = _c((255, 255, 255), 120)
    cx, cy = 15, 18
    # Base arc
    d.arc([(2 * s, 5 * s), (28 * s, 28 * s)], 200, 340, fill=wc, width=2 * s)
    # Inner arc
    d.arc([(7 * s, 8 * s), (23 * s, 24 * s)], 210, 330, fill=wd, width=1 * s)
    # Sweep line
    d.line([(cx * s, cy * s), (23 * s, 5 * s)], fill=wc, width=2 * s)
    # Center dot
    d.ellipse([(cx - 2) * s, (cy - 2) * s, (cx + 2) * s, (cy + 2) * s], fill=wc)
    # Blips
    d.ellipse([21 * s, 8 * s, 24 * s, 11 * s], fill=_c((255, 255, 255), 180))
    d.ellipse([8 * s, 10 * s, 10 * s, 12 * s], fill=_c((255, 255, 255), 100))
    result = ss_finish(img, rw, rh)
    save(result, "dashboard/recon.png")

    # PineAP Icon — signal broadcast (concentric arcs)
    img, d = ss_start(rw, rh)
    wc = _c((255, 255, 255), 255)
    cx, cy = 15, 22
    # Antenna
    d.line([(cx * s, 8 * s), (cx * s, cy * s)], fill=wc, width=2 * s)
    d.ellipse([(cx - 2) * s, 5 * s, (cx + 2) * s, 9 * s], fill=wc)
    # Signal arcs
    for r, a in [(8, 200), (13, 150), (18, 100)]:
        d.arc([(cx - r) * s, (cy - r - 6) * s, (cx + r) * s, (cy + r - 6) * s],
              230, 310, fill=_c((255, 255, 255), a), width=2 * s)
    # Base
    d.rectangle([8 * s, 23 * s, 22 * s, 26 * s], fill=wc)
    result = ss_finish(img, rw, rh)
    save(result, "dashboard/pineap.png")

    # Settings Icon — gear
    img, d = ss_start(rw, rh)
    wc = _c((255, 255, 255), 255)
    cx, cy = 15, 15
    # Outer gear teeth
    num_teeth = 8
    for i in range(num_teeth):
        angle = (i * 360 / num_teeth) * math.pi / 180
        ox = cx + int(12 * math.cos(angle))
        oy = cy + int(12 * math.sin(angle))
        d.ellipse([(ox - 3) * s, (oy - 3) * s, (ox + 3) * s, (oy + 3) * s], fill=wc)
    # Outer ring
    d.ellipse([(cx - 10) * s, (cy - 10) * s, (cx + 10) * s, (cy + 10) * s],
              outline=wc, width=3 * s)
    # Inner hole
    d.ellipse([(cx - 4) * s, (cy - 4) * s, (cx + 4) * s, (cy + 4) * s],
              fill=_c(BG), outline=wc, width=2 * s)
    result = ss_finish(img, rw, rh)
    save(result, "dashboard/settings.png")

    # ── Labels — crisp text for band layout (2x bigger than original) ──
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font = ImageFont.truetype(font_path, 28)       # Unselected — was 16
    font_sel = ImageFont.truetype(font_path, 34)    # Selected — even bigger

    label_names = ["ALERTS", "PAYLOADS", "RECON", "PINEAP", "SETTINGS"]
    for label in label_names:
        # Normal size (28pt)
        bbox = font.getbbox(label)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        img = Image.new("RGBA", (tw + 4, th + 4), T)
        d = ImageDraw.Draw(img)
        d.text((2 - bbox[0], 2 - bbox[1]), label, fill=(255, 255, 255, 255), font=font)
        r, g, b, a = img.split()
        a = a.point(lambda p: 255 if p > 96 else 0)
        img = Image.merge("RGBA", (r, g, b, a))
        save(img, f"dashboard/label_{label.lower()}.png")

        # Selected size (34pt) — larger for active state
        bbox_s = font_sel.getbbox(label)
        tw_s = bbox_s[2] - bbox_s[0]
        th_s = bbox_s[3] - bbox_s[1]
        img_s = Image.new("RGBA", (tw_s + 4, th_s + 4), T)
        d_s = ImageDraw.Draw(img_s)
        d_s.text((2 - bbox_s[0], 2 - bbox_s[1]), label, fill=(255, 255, 255, 255), font=font_sel)
        r, g, b, a = img_s.split()
        a = a.point(lambda p: 255 if p > 96 else 0)
        img_s = Image.merge("RGBA", (r, g, b, a))
        save(img_s, f"dashboard/label_{label.lower()}_selected.png")

    # ── Selected Icons — 36x36 (larger for selected state) ──
    SEL_ICON = 36

    # Selected Alerts — bell (larger)
    rw, rh = SEL_ICON, SEL_ICON
    img, d = ss_start(rw, rh)
    wc = _c((255, 255, 255), 255)
    d.arc([(4 * s, 3 * s), (32 * s, 24 * s)], 180, 360, fill=wc, width=2 * s)
    d.line([(4 * s, 14 * s), (4 * s, 27 * s)], fill=wc, width=2 * s)
    d.line([(32 * s, 14 * s), (32 * s, 27 * s)], fill=wc, width=2 * s)
    d.rectangle([2 * s, 26 * s, 34 * s, 28 * s], fill=wc)
    d.ellipse([15 * s, 29 * s, 21 * s, 34 * s], fill=wc)
    d.ellipse([15 * s, 1 * s, 21 * s, 6 * s], fill=wc)
    save(ss_finish(img, rw, rh), "dashboard/alerts_selected.png")

    # Selected Payloads — rocket (larger)
    img, d = ss_start(rw, rh)
    wc = _c((255, 255, 255), 255)
    wd = _c((255, 255, 255), 140)
    d.polygon([(18 * s, 2 * s), (24 * s, 12 * s), (24 * s, 26 * s),
               (12 * s, 26 * s), (12 * s, 12 * s)], fill=_c((255, 255, 255), 40), outline=wc)
    d.polygon([(18 * s, 2 * s), (12 * s, 12 * s), (24 * s, 12 * s)],
              fill=_c((255, 255, 255), 60), outline=wc)
    d.polygon([(12 * s, 22 * s), (6 * s, 30 * s), (12 * s, 26 * s)], fill=wc)
    d.polygon([(24 * s, 22 * s), (30 * s, 30 * s), (24 * s, 26 * s)], fill=wc)
    d.line([(16 * s, 26 * s), (14 * s, 33 * s)], fill=wd, width=1 * s)
    d.line([(18 * s, 26 * s), (18 * s, 34 * s)], fill=wd, width=1 * s)
    d.line([(20 * s, 26 * s), (22 * s, 33 * s)], fill=wd, width=1 * s)
    d.ellipse([16 * s, 14 * s, 20 * s, 18 * s], outline=wc, width=1 * s)
    save(ss_finish(img, rw, rh), "dashboard/payloads_selected.png")

    # Selected Recon — radar (larger)
    img, d = ss_start(rw, rh)
    wc = _c((255, 255, 255), 255)
    wd = _c((255, 255, 255), 120)
    cx, cy = 18, 22
    d.arc([(2 * s, 6 * s), (34 * s, 34 * s)], 200, 340, fill=wc, width=2 * s)
    d.arc([(8 * s, 10 * s), (28 * s, 30 * s)], 210, 330, fill=wd, width=1 * s)
    d.line([(cx * s, cy * s), (28 * s, 6 * s)], fill=wc, width=2 * s)
    d.ellipse([(cx - 2) * s, (cy - 2) * s, (cx + 2) * s, (cy + 2) * s], fill=wc)
    d.ellipse([26 * s, 9 * s, 29 * s, 12 * s], fill=_c((255, 255, 255), 180))
    d.ellipse([9 * s, 12 * s, 12 * s, 15 * s], fill=_c((255, 255, 255), 100))
    save(ss_finish(img, rw, rh), "dashboard/recon_selected.png")

    # Selected PineAP — broadcast (larger)
    img, d = ss_start(rw, rh)
    wc = _c((255, 255, 255), 255)
    cx, cy = 18, 27
    d.line([(cx * s, 10 * s), (cx * s, cy * s)], fill=wc, width=2 * s)
    d.ellipse([(cx - 2) * s, 6 * s, (cx + 2) * s, 10 * s], fill=wc)
    for r, a in [(10, 200), (16, 150), (22, 100)]:
        d.arc([(cx - r) * s, (cy - r - 8) * s, (cx + r) * s, (cy + r - 8) * s],
              230, 310, fill=_c((255, 255, 255), a), width=2 * s)
    d.rectangle([10 * s, 28 * s, 26 * s, 31 * s], fill=wc)
    save(ss_finish(img, rw, rh), "dashboard/pineap_selected.png")

    # Selected Settings — gear (larger)
    img, d = ss_start(rw, rh)
    wc = _c((255, 255, 255), 255)
    cx, cy = 18, 18
    num_teeth = 8
    for i in range(num_teeth):
        angle = (i * 360 / num_teeth) * math.pi / 180
        ox = cx + int(14 * math.cos(angle))
        oy = cy + int(14 * math.sin(angle))
        d.ellipse([(ox - 3) * s, (oy - 3) * s, (ox + 3) * s, (oy + 3) * s], fill=wc)
    d.ellipse([(cx - 12) * s, (cy - 12) * s, (cx + 12) * s, (cy + 12) * s],
              outline=wc, width=3 * s)
    d.ellipse([(cx - 5) * s, (cy - 5) * s, (cx + 5) * s, (cy + 5) * s],
              fill=_c(BG), outline=wc, width=2 * s)
    save(ss_finish(img, rw, rh), "dashboard/settings_selected.png")


# ─── Status Bar ──────────────────────────────────────────────────────────────

def gen_statusbar():
    """Status bar icons — yellow accent system."""
    ensure_dir("statusbar")
    s = SS

    # ── Battery (38x20) ──
    bat_specs = [
        ("dashboard_battery_charge_25", 1, YELLOW),
        ("dashboard_battery_charge_50", 2, YELLOW),
        ("dashboard_battery_charge_75", 3, YELLOW_L),
        ("dashboard_battery_charge_100", 4, YELLOW_L),
        ("dashboard_battery_full", 4, YELLOW_L),
        ("dashboard_battery_text", 0, GRAY),
    ]
    for name, segs, color in bat_specs:
        img, d = ss_start(38, 20)
        rrect(d, (0, 2, 33, 18), outline=DARK_GRAY, radius=2, width=1)
        d.rectangle([34*s, 7*s, 37*s, 13*s], fill=_c(DARK_GRAY))
        for si in range(4):
            sx = (2 + si * 8) * s
            if si < segs:
                d.rectangle([sx, 4*s, sx + 6*s, 16*s], fill=_c(color))
            else:
                d.rectangle([sx, 4*s, sx + 6*s, 16*s], fill=_c(DARK_GRAY, 30))
        save(ss_finish(img, 38, 20), f"statusbar/{name}.png")

    # ── Brightness (20x20) ──
    for name, level in [("dashboard_brightness_2", 2), ("dashboard_brightness_3", 3),
                        ("dashboard_brightness_5", 5), ("dashboard_brightness_7", 7),
                        ("dashboard_brightness_8", 8)]:
        img, d = ss_start(20, 20)
        frac = level / 8.0
        col = _c((int(70 + frac * 185), int(55 + frac * 145), 0))
        d.ellipse([7*s, 7*s, 13*s, 13*s], fill=col)
        rays = min(level, 8)
        for r in range(rays):
            a = (r * 360 / 8) * math.pi / 180
            x1, y1 = 10*s + int(4*s * math.cos(a)), 10*s + int(4*s * math.sin(a))
            x2, y2 = 10*s + int(8*s * math.cos(a)), 10*s + int(8*s * math.sin(a))
            d.line([(x1, y1), (x2, y2)], fill=col, width=s)
        save(ss_finish(img, 20, 20), f"statusbar/{name}.png")

    # ── Bluetooth (20x20) ──
    img, d = ss_start(20, 20)
    pts = [(10, 2), (15, 6), (5, 14), (10, 18), (15, 14), (5, 6)]
    for i in range(len(pts) - 1):
        d.line([(pts[i][0]*s, pts[i][1]*s), (pts[i+1][0]*s, pts[i+1][1]*s)],
               fill=_c(YELLOW), width=s)
    d.line([(10*s, 2*s), (10*s, 18*s)], fill=_c(YELLOW), width=s)
    save(ss_finish(img, 20, 20), "statusbar/bluetooth.png")

    # ── Volume ──
    def speaker(d, color, s):
        d.polygon([(3*s, 7*s), (6*s, 7*s), (10*s, 3*s),
                   (10*s, 17*s), (6*s, 13*s), (3*s, 13*s)], fill=_c(color))

    for name, ww, waves in [("volume_low", 17, 1), ("volume_medium", 17, 2),
                            ("volume_high", 21, 3)]:
        img, d = ss_start(ww, 20)
        speaker(d, SOFT_W, s)
        for i in range(1, waves + 1):
            r = (3 + i * 3) * s
            d.arc([10*s, (10 - r // s)*s, 10*s + r*2, (10 + r // s)*s],
                  -50, 50, fill=_c(SOFT_W), width=s)
        save(ss_finish(img, ww, 20), f"statusbar/{name}.png")

    # ── Mute (20x20) ──
    img, d = ss_start(20, 20)
    speaker(d, GRAY, s)
    d.line([(2*s, 3*s), (17*s, 17*s)], fill=_c(RED), width=2*s)
    save(ss_finish(img, 20, 20), "statusbar/mute.png")

    # ── Vibrate (24x17) ──
    img, d = ss_start(24, 17)
    rrect(d, (7, 1, 17, 16), outline=SOFT_W, radius=2, width=1)
    d.arc([1*s, 4*s, 7*s, 13*s], 100, 260, fill=_c(SOFT_W), width=s)
    d.arc([17*s, 4*s, 23*s, 13*s], 280, 80, fill=_c(SOFT_W), width=s)
    save(ss_finish(img, 24, 17), "statusbar/vibrate.png")

    # ── GHz indicators (20x20 or 20x22) ──
    ghz = [("ghz_2", "2", YELLOW, 20), ("ghz_5", "5", YELLOW, 20),
           ("ghz_6", "6", YELLOW_D, 20), ("ghz_25", "25", YELLOW, 20),
           ("ghz_26", "26", YELLOW, 22), ("ghz_56", "56", YELLOW, 20),
           ("ghz_256", "A", YELLOW_L, 20), ("ghz_off", "-", GRAY, 20)]
    for name, _label, color, hh in ghz:
        img, d = ss_start(20, hh)
        rrect(d, (0, 0, 19, hh - 1), fill=(color[0], color[1], color[2], 30),
              outline=color, radius=3, width=1)
        save(ss_finish(img, 20, hh), f"statusbar/{name}.png")

    # ── GPS (21x21) ──
    img, d = ss_start(21, 21)
    cx, cy = 10*s, 10*s
    d.ellipse([cx-7*s, cy-7*s, cx+7*s, cy+7*s], outline=_c(YELLOW), width=s)
    d.ellipse([cx-3*s, cy-3*s, cx+3*s, cy+3*s], fill=_c(YELLOW))
    for dx, dy, dx2, dy2 in [(0, -9, 0, -4), (0, 4, 0, 9), (-9, 0, -4, 0), (4, 0, 9, 0)]:
        d.line([(cx+dx*s, cy+dy*s), (cx+dx2*s, cy+dy2*s)], fill=_c(YELLOW), width=s)
    save(ss_finish(img, 21, 21), "statusbar/gps.png")

    # ── Database (21x19) ──
    img, d = ss_start(21, 19)
    for cy in [3, 8, 13]:
        d.ellipse([3*s, cy*s, 18*s, (cy+5)*s], outline=_c(YELLOW_D), width=s)
    d.line([(3*s, 5*s), (3*s, 15*s)], fill=_c(YELLOW_D), width=s)
    d.line([(18*s, 5*s), (18*s, 15*s)], fill=_c(YELLOW_D), width=s)
    save(ss_finish(img, 21, 19), "statusbar/database.png")

    # ── PCAP (20x21) ──
    img, d = ss_start(20, 21)
    rrect(d, (2, 0, 17, 20), outline=YELLOW_D, radius=2, width=1)
    for ly in [5, 9, 13]:
        d.line([(5*s, ly*s), (14*s, ly*s)], fill=_c(YELLOW_D), width=s)
    save(ss_finish(img, 20, 21), "statusbar/pcap.png")

    # ── Wigle (28x21) ──
    img, d = ss_start(28, 21)
    d.ellipse([4*s, 1*s, 24*s, 20*s], outline=_c(YELLOW_D), width=s)
    d.ellipse([10*s, 1*s, 18*s, 20*s], outline=_c(YELLOW_D), width=s)
    d.line([(4*s, 10*s), (24*s, 10*s)], fill=_c(YELLOW_D), width=s)
    save(ss_finish(img, 28, 21), "statusbar/wigle.png")


# ─── Spinner ─────────────────────────────────────────────────────────────────

def gen_spinner():
    """Loading spinner — clean rotating yellow arc on black."""
    ensure_dir("spinner")
    s = SS
    W, H = 220, 156

    for frame in range(1, 5):
        img, d = ss_start(W, H)
        cx, cy = W * s // 2, H * s // 2
        ba = (frame - 1) * 90

        # Outer ring — dim
        r1 = min(cx, cy) - 6 * s
        d.arc([cx - r1, cy - r1, cx + r1, cy + r1],
              0, 360, fill=_c(DARK_GRAY, 60), width=2 * s)

        # Sweeping arc — yellow
        d.arc([cx - r1, cy - r1, cx + r1, cy + r1],
              ba, ba + 90, fill=_c(YELLOW, 220), width=3 * s)
        # Trail
        d.arc([cx - r1, cy - r1, cx + r1, cy + r1],
              ba - 30, ba, fill=_c(YELLOW, 80), width=2 * s)

        # Middle ring — subtle pulse
        r2 = r1 - 16 * s
        pulse_alpha = [100, 160, 200, 140][frame - 1]
        d.arc([cx - r2, cy - r2, cx + r2, cy + r2],
              0, 360, fill=_c(YELLOW_D, pulse_alpha), width=2 * s)

        # Inner arc — counter-rotating
        r3 = r2 - 14 * s
        ba2 = 360 - ba
        d.arc([cx - r3, cy - r3, cx + r3, cy + r3],
              ba2, ba2 + 60, fill=_c(YELLOW_L, 160), width=2 * s)

        # Center dot
        pr = (4 + frame) * s
        d.ellipse([cx - pr, cy - pr, cx + pr, cy + pr],
                  fill=_c(YELLOW, 60 + frame * 25))
        d.ellipse([cx - 3 * s, cy - 3 * s, cx + 3 * s, cy + 3 * s],
                  fill=_c(YELLOW, 200))

        save(ss_finish(img, W, H), f"spinner/spinner{frame}.png")


# ─── Boot Animation ──────────────────────────────────────────────────────────

def gen_boot():
    """Boot animation — clean dark boot with progressive yellow accent reveal.
    Black base, yellow elements fade in. No glow, no blur, just clean.
    16 frames (8 messages x 2 frames each).
    """
    ensure_dir("boot_animation")
    import random
    random.seed(42)

    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
    try:
        font_lg = ImageFont.truetype(bold_path, 20)
        font_sm = ImageFont.truetype(font_path, 12)
    except Exception:
        font_lg = ImageFont.load_default()
        font_sm = font_lg

    W, H = 480, 222

    status_pool = [
        "INITIALIZING SYSTEMS",
        "CALIBRATING RADIOS",
        "LOADING PAYLOAD ENGINE",
        "SCANNING FREQUENCIES",
        "PRIMING PINEAP CORE",
        "ARMING ATTACK VECTORS",
        "SYNCING MODULES",
        "CONFIGURING INTERFACES",
        "ESTABLISHING CHANNELS",
        "MAPPING NETWORK SPACE",
        "READING SENSOR DATA",
        "BUILDING ROUTE TABLES",
    ]
    diag_pool = [
        "YELLOWJACKET v1.0 // BOOT SEQUENCE",
        "MT7628AN 580MHz // CORE STABLE",
        "WLAN0 READY // TRI-BAND 6E",
        "PINEAP v8 // ENGINE ARMED",
        "RF SUBSYSTEMS NOMINAL",
        "NETWORK BRIDGE ACTIVE",
        "STORAGE MOUNTED // 4GB EMMC",
        "KERNEL 6.6 // OPENWRT 24.10",
        "DROPBEAR SSH // LISTENING",
        "PAYLOAD BANKS LOADED",
        "USB LINK ESTABLISHED",
        "ALL STATIONS REPORTING",
    ]
    random.shuffle(status_pool)
    random.shuffle(diag_pool)
    status_lines = status_pool[:8]
    diag_lines = diag_pool[:8]
    status_lines[7] = "ALL SYSTEMS OPERATIONAL"
    diag_lines[7] = "WIFI PINEAPPLE PAGER ONLINE"

    NUM_MSGS = 8
    FRAMES_PER_MSG = 2
    TOTAL_FRAMES = NUM_MSGS * FRAMES_PER_MSG

    frame_num = 0
    for msg_idx in range(NUM_MSGS):
        for sub in range(FRAMES_PER_MSG):
            frame_num += 1
            progress = frame_num / float(TOTAL_FRAMES)

            # Black background
            result = Image.new("RGBA", (W, H), (*BG, 255))
            td = ImageDraw.Draw(result)

            # Top accent line — gets brighter with progress
            top_alpha = int(30 + progress * 80)
            td.rectangle([0, 0, W, 2], fill=(*YELLOW, top_alpha))

            # Bottom accent line
            td.rectangle([0, H - 2, W, H], fill=(*YELLOW, top_alpha))

            # Progress bar — horizontal line, fills left to right
            bar_y = H // 2 + 32
            bar_x_start = 100
            bar_x_end = 380
            bar_fill = int(bar_x_start + (bar_x_end - bar_x_start) * progress)
            # Background track
            td.rectangle([bar_x_start, bar_y, bar_x_end, bar_y + 3],
                         fill=(*DARK_GRAY, 80))
            # Filled portion
            td.rectangle([bar_x_start, bar_y, bar_fill, bar_y + 3],
                         fill=(*YELLOW, 200))

            # Progress dots — 5 yellow dots
            dot_r = 4
            dot_spacing = 20
            dot_y = H // 2 - 40
            dot_start_x = W // 2 - (4 * dot_spacing) // 2
            dot_thresholds = [0, 1, 3, 4, 5]
            for di in range(5):
                dx = dot_start_x + di * dot_spacing
                if msg_idx >= dot_thresholds[di]:
                    td.ellipse([dx - dot_r, dot_y - dot_r,
                                dx + dot_r, dot_y + dot_r],
                               fill=(*YELLOW, 255))
                else:
                    td.ellipse([dx - dot_r, dot_y - dot_r,
                                dx + dot_r, dot_y + dot_r],
                               outline=(*DARK_GRAY, 120), width=1)

            # Main status — centered, yellow
            txt = status_lines[msg_idx]
            bbox = td.textbbox((0, 0), txt, font=font_lg)
            tw = bbox[2] - bbox[0]
            td.text(((W - tw) // 2, H // 2 - 18), txt,
                    fill=_c(YELLOW), font=font_lg)

            # Diagnostic — soft white
            diag = diag_lines[msg_idx]
            bbox = td.textbbox((0, 0), diag, font=font_sm)
            tw = bbox[2] - bbox[0]
            td.text(((W - tw) // 2, H // 2 + 8), diag,
                    fill=_c(SOFT_W), font=font_sm)

            # Frame counter
            counter = f"INIT {msg_idx + 1}/{NUM_MSGS}"
            bbox = td.textbbox((0, 0), counter, font=font_sm)
            tw = bbox[2] - bbox[0]
            td.text((W - tw - 8, H - 22), counter,
                    fill=_c(GRAY), font=font_sm)

            save(result, f"boot_animation/init-{frame_num}.png")


# ─── Keyboard ────────────────────────────────────────────────────────────────

def gen_keyboard():
    """Keyboard layouts — dark keys on black with yellow labels."""
    ensure_dir("keyboard")
    s = SS
    W, H = 480, 222

    try:
        kb_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 14 * s)
        kb_font_sm = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 10 * s)
    except Exception:
        kb_font = ImageFont.load_default()
        kb_font_sm = kb_font

    KEY_LABEL_COLOR = _c(YELLOW)

    SPECIAL = {
        "backspace": "\u2190", "capslock": "\u21e7", "done": "\u2713",
        "symbols_toggle": "#$", "space": "\u2423",
    }

    def draw_key_label(d, x, y, kw, kh, label):
        display = SPECIAL.get(label, label)
        font = kb_font_sm if len(display) > 1 else kb_font
        cx = (x + kw // 2) * s
        cy = (y + kh // 2) * s
        bbox = font.getbbox(display)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tx = cx - tw // 2
        ty = cy - th // 2 - bbox[1]
        d.text((tx, ty), display, fill=KEY_LABEL_COLOR, font=font)

    def draw_kb(d, rows, start_y=59, key_w=47, key_h=31, cols=None):
        max_cols = cols or max(len(row) for row in rows)
        total = max_cols * key_w
        x_off = (W - total) // 2
        for ri, row in enumerate(rows):
            y = start_y + ri * key_h
            for ci, key in enumerate(row):
                x = x_off + ci * key_w
                rrect(d, (x + 1, y + 1, x + key_w - 2, y + key_h - 2),
                       fill=PANEL, outline=DARK_GRAY, radius=3, width=1)
                draw_key_label(d, x, y, key_w, key_h, key)

    def draw_input_area(d):
        rrect(d, (8, 6, 472, 50), fill=PANEL, outline=DARK_GRAY, radius=3)
        d.rectangle([8*s, 6*s, 472*s, 8*s], fill=_c(YELLOW_D))

    def draw_fn_row(d):
        y, kh, kw = 183, 31, 47
        keys = [
            (7, kw, "symbols_toggle"),
            (54, kw, "-"),
            (101, kw, "'"),
            (148, 188, "space"),
            (336, kw, "/"),
            (383, kw, "?"),
            (430, kw, "done"),
        ]
        for x, w, label in keys:
            rrect(d, (x, y, x + w - 1, y + kh - 1),
                   fill=PANEL, outline=DARK_GRAY, radius=3, width=1)
            draw_key_label(d, x, y, w, kh, label)

    # QWERTY lowercase
    img, d = ss_start(W, H, BG)
    draw_input_area(d)
    draw_kb(d, [list("1234567890"), list("qwertyuiop"),
                list("asdfghjkl") + ["backspace"],
                ["capslock"] + list("zxcvbnm,.")])
    draw_fn_row(d)
    save(ss_finish(img, W, H), "keyboard/keyboard_layout_lower.png")

    # QWERTY uppercase
    img, d = ss_start(W, H, BG)
    draw_input_area(d)
    draw_kb(d, [list("1234567890"), list("QWERTYUIOP"),
                list("ASDFGHJKL") + ["backspace"],
                ["capslock"] + list("ZXCVBNM,.")])
    draw_fn_row(d)
    save(ss_finish(img, W, H), "keyboard/keyboard_layout_upper.png")

    # Symbols
    img, d = ss_start(W, H, BG)
    draw_input_area(d)
    draw_kb(d, [list("1234567890"), list("!@#$%^&*()"),
                list("~<>+=:;[]") + ["backspace"],
                ["capslock"] + list("_\"`{}|\\,.")])
    draw_fn_row(d)
    save(ss_finish(img, W, H), "keyboard/keyboard_layout_symbols.png")

    # Numeric
    img, d = ss_start(W, H, BG)
    draw_input_area(d)
    draw_kb(d, [list("789"), list("456"), list("123"),
                ["done", "0", "backspace"]],
            start_y=59, key_w=47, key_h=31)
    save(ss_finish(img, W, H), "keyboard/keyboard_layout_numeric.png")

    # IP
    img, d = ss_start(W, H, BG)
    draw_input_area(d)
    draw_kb(d, [["0", "1", "2", "3", "done"],
                ["/", "4", "5", "6", "backspace"],
                [".", "7", "8", "9"]],
            start_y=57, key_w=77, key_h=56, cols=5)
    save(ss_finish(img, W, H), "keyboard/keyboard_layout_ip.png")

    # Hex
    img, d = ss_start(W, H, BG)
    draw_input_area(d)
    draw_kb(d, [["0", "1", "2", "3", "4", "done"],
                ["5", "6", "7", "8", "9", "backspace"],
                list("ABCDEF")],
            start_y=57, key_w=77, key_h=56)
    save(ss_finish(img, W, H), "keyboard/keyboard_layout_hex.png")

    # Key highlight (47x31) — yellow outline, no glow
    img, d = ss_start(47, 31)
    rrect(d, (0, 0, 46, 30), fill=(YELLOW[0], YELLOW[1], YELLOW[2], 25),
          outline=YELLOW, radius=3, width=1)
    save(ss_finish(img, 47, 31), "keyboard/_key-bg.png")

    # Spacebar (188x31)
    img, d = ss_start(188, 31)
    rrect(d, (0, 0, 187, 30), fill=(YELLOW[0], YELLOW[1], YELLOW[2], 25),
          outline=YELLOW, radius=3, width=1)
    save(ss_finish(img, 188, 31), "keyboard/_spacebar-4x.png")

    # Hex key (75x54)
    img, d = ss_start(75, 54)
    rrect(d, (0, 0, 74, 53), fill=(YELLOW[0], YELLOW[1], YELLOW[2], 25),
          outline=YELLOW, radius=3, width=1)
    save(ss_finish(img, 75, 54), "keyboard/_hex-bg.png")


# ─── Dialogs ────────────────────────────────────────────────────────────────

def gen_dialogs():
    """Dialog backgrounds — clean black panels with yellow accent bars."""

    def make_dialog(w, h, accent=YELLOW):
        img, d = ss_start(w, h)
        s = SS
        # Main panel
        rrect(d, (0, 0, w-1, h-1), fill=BG, outline=DARK_GRAY, radius=5, width=1)

        # Top bar — yellow accent
        d.rectangle([0, 0, (w-1)*s, 3*s], fill=_c(accent, 180))

        # Bottom bar
        d.rectangle([0, (h-3)*s, (w-1)*s, (h-1)*s], fill=_c(accent, 80))

        return ss_finish(img, w, h)

    # Option dialogs (463x197)
    for name, color in [
        ("option_dialog_bg_windowed", YELLOW),
        ("option_dialog_bg_windowed_green", YELLOW),
        ("option_dialog_bg_windowed_purple", YELLOW),
        ("option_dialog_bg_windowed_red", RED),
        ("option_dialog_bg_narrow", YELLOW),
    ]:
        save(make_dialog(463, 197, accent=color), f"optiondialog/{name}.png")

    # Option button bg (59x71)
    img, d = ss_start(59, 71)
    rrect(d, (0, 0, 58, 70), fill=PANEL, outline=DARK_GRAY, radius=3)
    d.rectangle([0, 0, 3*SS, 70*SS], fill=_c(YELLOW_D))
    save(ss_finish(img, 59, 71), "optiondialog/button_bg.png")

    # Button outline (59x71) — yellow outline, no glow
    img, d = ss_start(59, 71)
    rrect(d, (0, 0, 58, 70), fill=(YELLOW[0], YELLOW[1], YELLOW[2], 10),
          outline=YELLOW, radius=3, width=2)
    save(ss_finish(img, 59, 71), "optiondialog/button_outline.png")

    # Check (24x19)
    img, d = ss_start(24, 19)
    d.line([(2*SS, 10*SS), (8*SS, 16*SS), (22*SS, 2*SS)], fill=_c(WHITE), width=2*SS)
    save(ss_finish(img, 24, 19), "optiondialog/check.png")

    # X (15x15)
    img, d = ss_start(15, 15)
    d.line([(2*SS, 2*SS), (12*SS, 12*SS)], fill=_c(RED), width=2*SS)
    d.line([(12*SS, 2*SS), (2*SS, 12*SS)], fill=_c(RED), width=2*SS)
    save(ss_finish(img, 15, 15), "optiondialog/x.png")

    # Alert dialog backgrounds
    for name, w, h, accent in [
        ("alert_dialog_bg_term", 398, 220, YELLOW),
        ("alert_dialog_bg_term_blue", 429, 222, YELLOW),
        ("alert_dialog_bg_term_error", 429, 222, RED),
        ("alert_dialog_bg_term_warning", 429, 222, YELLOW),
    ]:
        save(make_dialog(w, h, accent=accent), f"{name}.png")

    # Confirmation dialog bg (429x222)
    save(make_dialog(429, 222, accent=YELLOW), "confirmation_dialog_bg_term.png")

    # Confirmation buttons (121x41)
    for name, bg_c, out_c, accent in [
        ("generic_confirmation_button_deselected", PANEL, DARK_GRAY, None),
        ("generic_confirmation_button_selected", (YELLOW[0], YELLOW[1], YELLOW[2], 15), YELLOW, YELLOW),
    ]:
        img, d = ss_start(121, 41)
        rrect(d, (0, 0, 120, 40), fill=bg_c, outline=out_c, radius=3,
              width=1 if accent is None else 2)
        if accent:
            d.rectangle([0, 0, 120*SS, 2*SS], fill=_c(accent, 140))
        save(ss_finish(img, 121, 41), f"confirmation_dialog/{name}.png")

    # Edit string dialog bg (467x186)
    save(make_dialog(467, 186, accent=YELLOW), "edit_string_dialog_bg.png")

    # Dialog BG (480x222)
    save(make_dialog(480, 222, accent=YELLOW), "dialog_bg.png")

    # Messagebox (459x112)
    img, d = ss_start(459, 112)
    rrect(d, (0, 0, 458, 111), fill=BG, outline=DARK_GRAY, radius=3)
    d.rectangle([0, 0, 458*SS, 3*SS], fill=_c(YELLOW, 140))
    save(ss_finish(img, 459, 112), "messagebox.png")


# ─── Toggles / Radio / Checkbox ─────────────────────────────────────────────

def gen_toggles():
    """Toggle switches, radio buttons, checkbox — yellow accents."""
    s = SS

    # Toggle enabled bg (29x16)
    img, d = ss_start(29, 16)
    d.rounded_rectangle([0, 0, 28*s, 15*s], radius=8*s,
                        fill=_c(YELLOW, 35), outline=_c(YELLOW), width=s)
    save(ss_finish(img, 29, 16), "toggle/enabled/toggle_bg.png")

    # Toggle circle enabled (12x12)
    img, d = ss_start(12, 12)
    d.ellipse([0, 0, 11*s, 11*s], fill=_c(YELLOW))
    save(ss_finish(img, 12, 12), "toggle/enabled/circle.png")

    # Toggle check (10x5)
    img, d = ss_start(10, 5)
    d.line([(1*s, 3*s), (3*s, 4*s), (9*s, 0)], fill=_c(BG), width=s)
    save(ss_finish(img, 10, 5), "toggle/enabled/check.png")

    # Toggle disabled bg (29x16)
    img, d = ss_start(29, 16)
    d.rounded_rectangle([0, 0, 28*s, 15*s], radius=8*s,
                        fill=_c(DARK_GRAY, 50), outline=_c(GRAY), width=s)
    save(ss_finish(img, 29, 16), "toggle/disabled/toggle_disabled_bg.png")

    # Toggle circle disabled (12x12)
    img, d = ss_start(12, 12)
    d.ellipse([0, 0, 11*s, 11*s], fill=_c(GRAY))
    save(ss_finish(img, 12, 12), "toggle/disabled/circle.png")

    # Radio border (19x19)
    img, d = ss_start(19, 19)
    d.ellipse([s, s, 17*s, 17*s], outline=_c(SOFT_W), width=s)
    save(ss_finish(img, 19, 19), "radio/radio_border.png")

    # Radio selected (11x11)
    img, d = ss_start(11, 11)
    d.ellipse([0, 0, 10*s, 10*s], fill=_c(YELLOW))
    save(ss_finish(img, 11, 11), "radio/radio_selected.png")

    # Checkbox (20x20)
    img, d = ss_start(20, 20)
    rrect(d, (1, 1, 18, 18), outline=SOFT_W, radius=2, width=1)
    d.line([(5*s, 10*s), (8*s, 14*s), (15*s, 5*s)], fill=_c(YELLOW), width=2*s)
    save(ss_finish(img, 20, 20), "checkbox.png")


# ─── Recon ───────────────────────────────────────────────────────────────────

def gen_recon():
    """Recon screens and icons."""
    ensure_dir("recon")
    W, H = 480, 222

    # Recon dashboard (480x222)
    img = yj_frame_bg(W, H)
    save(ss_finish(img, W, H), "recon/recon_dashboard.png")

    # Recon list bg (480x222)
    img, d = ss_start(W, H, BG)
    s = SS
    # Top bar with yellow accent
    d.rectangle([0, 0, W*s, 10*s], fill=_c(PANEL))
    d.rectangle([0, 8*s, W*s, 10*s], fill=_c(YELLOW, 50))
    d.rectangle([120*s, 0, 122*s, 10*s], fill=_c(BG))
    d.rectangle([320*s, 0, 322*s, 10*s], fill=_c(BG))
    # Bottom bar
    d.rectangle([0, (H-10)*s, W*s, H*s], fill=_c(PANEL))
    d.rectangle([0, (H-10)*s, W*s, (H-8)*s], fill=_c(YELLOW, 35))
    # Row separators
    for y in range(42, 198, 34):
        d.line([(10*s, y*s), (470*s, y*s)], fill=_c(DARK_GRAY, 40), width=s)
    save(ss_finish(img, W, H), "recon/recon_list_bg.png")

    # Blank recon bg (480x222)
    img, d = ss_start(W, H, BG)
    d.rectangle([0, 0, W*s, 10*s], fill=_c(PANEL))
    d.rectangle([0, 8*s, W*s, 10*s], fill=_c(YELLOW, 50))
    d.rectangle([0, (H-10)*s, W*s, H*s], fill=_c(PANEL))
    rrect(d, (140, 80, 340, 140), fill=PANEL, outline=DARK_GRAY, radius=4)
    save(ss_finish(img, W, H), "blank_recon_bg.png")

    # RSSI bars (20x20)
    for level in range(4):
        img, d = ss_start(20, 20)
        for b in range(4):
            bh = (4 + b * 4) * s
            bx = b * 5 * s
            by = 19*s - bh
            if b <= level:
                c = [RED, YELLOW_D, YELLOW, YELLOW_L][level]
            else:
                c = (*DARK_GRAY, 40)
            d.rectangle([bx, by, bx + 3*s, 19*s], fill=_c(c))
        save(ss_finish(img, 20, 20), f"recon/rssi_{level}.png")

    # Encryption icons (20x20)
    def lock_icon(d, color, open_lock=False):
        s2 = SS
        if open_lock:
            d.arc([5*s2, 1*s2, 15*s2, 11*s2], 0, 180, fill=_c(color), width=2*s2)
        else:
            d.arc([5*s2, 1*s2, 15*s2, 11*s2], 0, 180, fill=_c(color), width=2*s2)
            d.line([(5*s2, 6*s2), (5*s2, 10*s2)], fill=_c(color), width=2*s2)
            d.line([(15*s2, 6*s2), (15*s2, 10*s2)], fill=_c(color), width=2*s2)
        rrect(d, (3, 9, 17, 19), fill=color, radius=1)

    for name, color, is_open in [
        ("enc_open", GREEN, True), ("enc_wep", RED, False),
        ("enc_wpa2", YELLOW, False), ("enc_wpa3", YELLOW_L, False)
    ]:
        img, d = ss_start(20, 20)
        lock_icon(d, color, is_open)
        save(ss_finish(img, 20, 20), f"recon/{name}.png")

    # Clients (20x20)
    img, d = ss_start(20, 20)
    s = SS
    d.ellipse([3*s, 2*s, 9*s, 8*s], fill=_c(SOFT_W))
    d.ellipse([11*s, 2*s, 17*s, 8*s], fill=_c(SOFT_W))
    d.pieslice([1*s, 6*s, 11*s, 18*s], 0, 180, fill=_c(SOFT_W))
    d.pieslice([9*s, 6*s, 19*s, 18*s], 0, 180, fill=_c(SOFT_W))
    save(ss_finish(img, 20, 20), "recon/clients.png")


# ─── Full-Screen Backgrounds ────────────────────────────────────────────────

def gen_backgrounds():
    """Section backgrounds + all full-screen assets."""
    W, H = 480, 222

    def framed():
        img = yj_frame_bg(W, H)
        return ss_finish(img, W, H)

    def section():
        return ss_finish(yj_section_bg(W, H), W, H)

    # All section backgrounds — unified yellow, no per-section variation
    save(section(), "settings_bg.png")
    save(section(), "pineap_bg.png")
    save(section(), "alerts_dashboard/alerts_bg.png")
    save(section(), "payloads_dashboard/payloads_bg.png")
    save(section(), "payloads_dashboard/recon_payloads_bg.png")
    save(section(), "power_menu_bg.png")
    save(section(), "launch_payload_dialog/launch_payload_bg.png")

    # Payload log backgrounds
    img, d = ss_start(W, H, BG)
    s = SS
    d.rectangle([0, 0, W*s, 10*s], fill=_c(PANEL))
    d.rectangle([0, 8*s, W*s, 10*s], fill=_c(YELLOW, 45))
    d.rectangle([200*s, 0, 202*s, 10*s], fill=_c(BG))
    d.rectangle([0, (H-10)*s, W*s, H*s], fill=_c(PANEL))
    d.rectangle([0, (H-10)*s, W*s, (H-8)*s], fill=_c(YELLOW, 30))
    result = ss_finish(img, W, H)
    save(result, "payloadlog/payload_log_bg.png")
    save(result, "payload_log_bg.png")

    # Lock screen
    img, d = ss_start(W, H, BG)
    s = SS
    d.rectangle([0, 0, W*s, 3*s], fill=_c(YELLOW))
    d.rectangle([0, (H-3)*s, W*s, H*s], fill=_c(YELLOW_DD))
    # Lock icon — yellow
    d.arc([215*s, 68*s, 265*s, 108*s], 180, 360, fill=_c(YELLOW), width=3*s)
    d.line([(215*s, 88*s), (215*s, 106*s)], fill=_c(YELLOW), width=3*s)
    d.line([(265*s, 88*s), (265*s, 106*s)], fill=_c(YELLOW), width=3*s)
    rrect(d, (205, 105, 275, 155), fill=YELLOW, radius=3)
    d.ellipse([234*s, 118*s, 246*s, 130*s], fill=_c(BG))
    d.rectangle([238*s, 128*s, 242*s, 143*s], fill=_c(BG))
    save(ss_finish(img, W, H), "lock_screen.png")

    # Buttons locked
    img, d = ss_start(W, H, BG)
    d.rectangle([0, 0, W*s, 3*s], fill=_c(YELLOW))
    d.rectangle([0, (H-3)*s, W*s, H*s], fill=_c(YELLOW_DD))
    rrect(d, (140, 80, 340, 142), fill=PANEL, outline=DARK_GRAY, radius=3)
    save(ss_finish(img, W, H), "buttons_locked.png")

    # QR screens
    _qr_screens = [
        ("help_qr", "https://hak5.org/pager-docs",
         ["Scan to open", "documentation"], "hak5.org/pager-docs", None),
        ("license_qr", "https://hak5.org/pager-license",
         ["Scan to view", "full license"], "hak5.org/pager-license",
         ["Access on device at", "/etc/LICENSES"]),
        ("virt_qr", "http://172.16.52.1:1471",
         ["Scan to open", "browser"], "http://172.16.52.1:1471",
         ["Your device must be", "connected via USB-C", "or Management AP"]),
    ]
    try:
        import subprocess, tempfile
        for qr_name, qr_url, title, url_text, extra in _qr_screens:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                subprocess.run(["qr", qr_url], stdout=tmp, check=True)
                tmp_path = tmp.name
            qr_raw = Image.open(tmp_path).convert("L")
            qr_sz = 160
            qr_raw = qr_raw.resize((qr_sz, qr_sz), Image.NEAREST)

            screen = Image.new("RGB", (W, H), BG)
            sd = ImageDraw.Draw(screen)
            sd.rectangle([0, 0, W, 2], fill=YELLOW)
            sd.rectangle([0, H - 2, W, H], fill=YELLOW_DD)

            qr_rgb = Image.new("RGB", (qr_sz, qr_sz), BG)
            qr_px = qr_raw.load()
            qr_rgb_px = qr_rgb.load()
            for qy in range(qr_sz):
                for qx in range(qr_sz):
                    qr_rgb_px[qx, qy] = WHITE if qr_px[qx, qy] < 128 else BG
            qr_x, qr_y = 20, (H - qr_sz) // 2 + 5
            screen.paste(qr_rgb, (qr_x, qr_y))
            sd.rectangle([qr_x - 2, qr_y - 2, qr_x + qr_sz + 1, qr_y + qr_sz + 1],
                         outline=DARK_GRAY)

            font_lg = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 18)
            font_md = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 13)
            font_sm = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 11)
            tx, ty = 200, 30
            for line in title:
                sd.text((tx, ty), line, fill=WHITE, font=font_lg)
                ty += 26
            ty += 15
            sd.text((tx, ty), url_text, fill=YELLOW, font=font_md)
            if extra:
                ty += 25
                for line in extra:
                    sd.text((tx, ty), line, fill=DARK_GRAY, font=font_sm)
                    ty += 16
            screen.save(os.path.join(ASSETS_DIR, f"{qr_name}.png"))
            os.unlink(tmp_path)
    except Exception:
        for qr_name, *_ in _qr_screens:
            base = framed()
            base_d = ImageDraw.Draw(base)
            base_d.rounded_rectangle([160, 28, 420, 194], radius=4, fill=_c(WHITE))
            save(base, f"{qr_name}.png")

    # Warning screens
    for name, accent in [("warn_device_too_hot", RED), ("warn_device_dimming_screen", YELLOW)]:
        img, d = ss_start(W, H, BG)
        s = SS
        d.rectangle([0, 0, W*s, 4*s], fill=_c(accent))
        d.rectangle([0, (H-4)*s, W*s, H*s], fill=_c(accent))
        d.polygon([(240*s, 50*s), (310*s, 170*s), (170*s, 170*s)],
                  outline=_c(accent), fill=_c(accent, 20))
        d.line([(240*s, 80*s), (240*s, 135*s)], fill=_c(BG), width=4*s)
        d.ellipse([235*s, 143*s, 245*s, 153*s], fill=_c(BG))
        save(ss_finish(img, W, H), f"{name}.png")

    # Battery alerts
    for name, color in [("low_battery_alert", YELLOW), ("critical_battery_alert", RED)]:
        img, d = ss_start(W, H, BG)
        s = SS
        d.rectangle([0, 0, W*s, 4*s], fill=_c(color))
        d.rectangle([0, (H-4)*s, W*s, H*s], fill=_c(color))
        rrect(d, (195, 55, 265, 160), outline=color, radius=3, width=2)
        d.rectangle([220*s, 48*s, 240*s, 55*s], fill=_c(color))
        fill_h = 35 if "low" in name else 12
        d.rectangle([199*s, (158-fill_h)*s, 261*s, 156*s], fill=_c(color))
        save(ss_finish(img, W, H), f"{name}.png")

    # Upgrade screens
    for name, color in [
        ("upgrade/checking_for_update-min", YELLOW),
        ("upgrade/downloading_upgrade", GREEN),
        ("upgrade/validating_upgrade", YELLOW_L),
    ]:
        base = framed()
        d = ImageDraw.Draw(base)
        d.rounded_rectangle([80, 118, 400, 138], radius=4,
                            fill=_c(PANEL), outline=_c(DARK_GRAY))
        d.rounded_rectangle([82, 120, 250, 136], radius=3, fill=_c(color))
        save(base, f"{name}.png")


# ─── Miscellaneous ───────────────────────────────────────────────────────────

def gen_misc():
    """All remaining small UI assets."""
    s = SS

    # Arrows (19x38)
    for name, flip in [("arrow_up", False), ("arrow_down", True)]:
        img, d = ss_start(19, 38)
        if not flip:
            d.polygon([(9*s, 2*s), (17*s, 18*s), (12*s, 18*s),
                       (12*s, 36*s), (6*s, 36*s), (6*s, 18*s), (1*s, 18*s)],
                      fill=_c(YELLOW))
        else:
            d.polygon([(9*s, 36*s), (17*s, 20*s), (12*s, 20*s),
                       (12*s, 2*s), (6*s, 2*s), (6*s, 20*s), (1*s, 20*s)],
                      fill=_c(YELLOW))
        save(ss_finish(img, 19, 38), f"{name}.png")

    # Small up/down (16x16)
    for name, pts in [("up", [(8, 2), (14, 13), (2, 13)]),
                      ("down", [(8, 13), (14, 2), (2, 2)])]:
        img, d = ss_start(16, 16)
        d.polygon([(p[0]*s, p[1]*s) for p in pts], fill=_c(SOFT_W))
        save(ss_finish(img, 16, 16), f"{name}.png")

    # Dividers (13x160) — yellow-tinted
    for name, color in [("divider", YELLOW_D), ("divleft", YELLOW_DD), ("divright", YELLOW_DD)]:
        img, d = ss_start(13, 160)
        d.rounded_rectangle([4*s, 0, 8*s, 159*s], radius=2*s, fill=_c(color))
        save(ss_finish(img, 13, 160), f"{name}.png")

    # Section-colored dividers — same yellow for all sections
    for sec in ['settings', 'pineap']:
        img, d = ss_start(13, 160)
        d.rounded_rectangle([4*s, 0, 8*s, 159*s], radius=2*s, fill=_c(YELLOW_DD))
        save(ss_finish(img, 13, 160), f"divleft_{sec}.png")
        img, d = ss_start(13, 160)
        d.rounded_rectangle([4*s, 0, 8*s, 159*s], radius=2*s, fill=_c(YELLOW_DD))
        save(ss_finish(img, 13, 160), f"divright_{sec}.png")

    # Menu icon (29x20) — three bars, yellow
    img, d = ss_start(29, 20)
    for y in [2, 8, 14]:
        d.rounded_rectangle([2*s, y*s, 26*s, (y + 4)*s], radius=2*s, fill=_c(YELLOW))
    save(ss_finish(img, 29, 20), "menu.png")

    # Menu disabled (29x20)
    img, d = ss_start(29, 20)
    for y in [2, 8, 14]:
        d.rounded_rectangle([2*s, y*s, 26*s, (y + 4)*s], radius=2*s, fill=_c(GRAY))
    save(ss_finish(img, 29, 20), "menu_disabled.png")

    # Info (29x20)
    img, d = ss_start(29, 20)
    rrect(d, (4, 0, 24, 19), outline=YELLOW, radius=3, width=1)
    d.ellipse([12*s, 3*s, 16*s, 7*s], fill=_c(YELLOW))
    d.rectangle([13*s, 9*s, 15*s, 16*s], fill=_c(YELLOW))
    save(ss_finish(img, 29, 20), "info.png")

    # Warning (29x20)
    img, d = ss_start(29, 20)
    d.polygon([(14*s, 1*s), (27*s, 18*s), (1*s, 18*s)],
              outline=_c(YELLOW), fill=_c(YELLOW, 20))
    d.line([(14*s, 6*s), (14*s, 13*s)], fill=_c(YELLOW), width=s)
    d.ellipse([13*s, 14*s, 15*s, 16*s], fill=_c(YELLOW))
    save(ss_finish(img, 29, 20), "warning.png")

    # Keyboard icon (29x20)
    img, d = ss_start(29, 20)
    rrect(d, (1, 3, 27, 17), outline=SOFT_W, radius=2, width=1)
    for x in [6, 11, 16, 21]:
        d.rectangle([x*s, 6*s, (x+2)*s, 8*s], fill=_c(SOFT_W))
    for x in [8, 13, 18]:
        d.rectangle([x*s, 11*s, (x+2)*s, 13*s], fill=_c(SOFT_W))
    save(ss_finish(img, 29, 20), "keyboard.png")

    # Wizard (29x20)
    img, d = ss_start(29, 20)
    d.polygon([(14*s, 1*s), (16*s, 7*s), (24*s, 7*s), (18*s, 11*s),
               (20*s, 18*s), (14*s, 14*s), (8*s, 18*s), (10*s, 11*s),
               (4*s, 7*s), (12*s, 7*s)], fill=_c(YELLOW), outline=_c(YELLOW_D))
    save(ss_finish(img, 29, 20), "wizard.png")

    # Disabled variants
    for name in ["info", "warning", "keyboard", "wizard"]:
        orig = Image.open(os.path.join(ASSETS_DIR, f"{name}.png")).convert("RGBA")
        px = orig.load()
        for y in range(orig.height):
            for x in range(orig.width):
                r, g, b, a = px[x, y]
                if a > 0:
                    gray = min(int(0.3 * r + 0.59 * g + 0.11 * b), 60)
                    px[x, y] = (gray, gray, gray, a)
        save(orig, f"disabled_{name}.png")

    # Client (23x14)
    img, d = ss_start(23, 14)
    rrect(d, (0, 0, 22, 13), outline=SOFT_W, radius=2, width=1)
    d.ellipse([9*s, 4*s, 13*s, 8*s], fill=_c(YELLOW))
    save(ss_finish(img, 23, 14), "client.png")

    # Disabled client (23x14)
    img, d = ss_start(23, 14)
    rrect(d, (0, 0, 22, 13), outline=GRAY, radius=2, width=1)
    d.ellipse([9*s, 4*s, 13*s, 8*s], fill=_c(GRAY))
    save(ss_finish(img, 23, 14), "disabled_client.png")

    # X (15x15)
    img, d = ss_start(15, 15)
    d.line([(2*s, 2*s), (12*s, 12*s)], fill=_c(RED), width=2*s)
    d.line([(12*s, 2*s), (2*s, 12*s)], fill=_c(RED), width=2*s)
    save(ss_finish(img, 15, 15), "x.png")

    # Triangle (13x15)
    img, d = ss_start(13, 15)
    d.polygon([(1*s, 14*s), (6*s, 1*s), (11*s, 14*s)], fill=_c(YELLOW))
    save(ss_finish(img, 13, 15), "triangle.png")

    # Start (20x20)
    img, d = ss_start(20, 20)
    d.polygon([(4*s, 2*s), (18*s, 10*s), (4*s, 18*s)], fill=_c(GREEN))
    save(ss_finish(img, 20, 20), "start.png")

    # Swap (20x20)
    img, d = ss_start(20, 20)
    d.polygon([(2*s, 5*s), (10*s, 1*s), (10*s, 9*s)], fill=_c(YELLOW))
    d.polygon([(18*s, 15*s), (10*s, 11*s), (10*s, 19*s)], fill=_c(YELLOW_D))
    save(ss_finish(img, 20, 20), "swap.png")

    # Autoplay (24x24)
    img, d = ss_start(24, 24)
    d.ellipse([2*s, 2*s, 21*s, 21*s], outline=_c(GREEN), width=s)
    d.polygon([(9*s, 6*s), (18*s, 12*s), (9*s, 18*s)], fill=_c(GREEN))
    save(ss_finish(img, 24, 24), "autoplay.png")

    # Autoplay stopped (24x24)
    img, d = ss_start(24, 24)
    d.ellipse([2*s, 2*s, 21*s, 21*s], outline=_c(RED), width=s)
    d.rectangle([8*s, 7*s, 16*s, 17*s], fill=_c(RED))
    save(ss_finish(img, 24, 24), "autoplay_stopped.png")

    # Flame (11x17)
    img, d = ss_start(11, 17)
    d.polygon([(5*s, 0), (10*s, 10*s), (8*s, 16*s),
               (5*s, 12*s), (2*s, 16*s), (0, 10*s)],
              fill=_c(YELLOW), outline=_c(YELLOW_D))
    save(ss_finish(img, 11, 17), "flame.png")

    # Folder (24x24)
    img, d = ss_start(24, 24)
    d.polygon([(1*s, 5*s), (10*s, 5*s), (12*s, 2*s), (22*s, 2*s), (22*s, 5*s)],
              fill=_c(YELLOW))
    rrect(d, (1, 5, 22, 21), fill=YELLOW, radius=2)
    save(ss_finish(img, 24, 24), "folder.png")

    # WiFi icon (25x25)
    img, d = ss_start(25, 25)
    d.arc([1*s, 1*s, 24*s, 24*s], 210, 330, fill=_c(YELLOW), width=2*s)
    d.arc([5*s, 5*s, 20*s, 20*s], 215, 325, fill=_c(YELLOW), width=2*s)
    d.arc([9*s, 9*s, 16*s, 16*s], 220, 320, fill=_c(YELLOW), width=s)
    d.ellipse([11*s, 18*s, 14*s, 21*s], fill=_c(YELLOW))
    save(ss_finish(img, 25, 25), "wifi_icon.png")

    # Alerts sub (26x9) — yellow pill
    img, d = ss_start(26, 9)
    d.rounded_rectangle([0, 0, 25*s, 8*s], radius=4*s, fill=_c(YELLOW))
    save(ss_finish(img, 26, 9), "alerts_dashboard/sub.png")

    # Payload dialog bg (135x70)
    img, d = ss_start(135, 70)
    rrect(d, (0, 0, 134, 69), fill=PANEL, outline=DARK_GRAY, radius=3)
    d.rectangle([0, 0, 3*s, 69*s], fill=_c(YELLOW_D))
    save(ss_finish(img, 135, 70), "payload_dialog_option_bg.png")

    # Payload dialog selected (136x71)
    img, d = ss_start(136, 71)
    rrect(d, (0, 0, 135, 70), fill=(YELLOW[0], YELLOW[1], YELLOW[2], 10),
          outline=YELLOW, radius=3, width=2)
    save(ss_finish(img, 136, 71), "payload_dialog_selected_box.png")

    # Pager device (88x62)
    img, d = ss_start(88, 62)
    rrect(d, (2, 2, 85, 59), fill=PANEL, outline=YELLOW_D, radius=3, width=1)
    rrect(d, (8, 8, 55, 38), fill=(YELLOW[0], YELLOW[1], YELLOW[2], 12),
          outline=YELLOW_DD, radius=2, width=1)
    d.ellipse([65*s, 15*s, 78*s, 28*s], outline=_c(SOFT_W), width=s)
    d.ellipse([65*s, 35*s, 78*s, 48*s], outline=_c(SOFT_W), width=s)
    save(ss_finish(img, 88, 62), "pager-16bit.png")

    # Payload log indicators
    for name, w, h, color in [
        ("payloadlog/payload_complete_indicator", 480, 43, GREEN),
        ("payloadlog/payload_error_indicator", 480, 44, RED),
        ("payloadlog/payload_running_indicator", 480, 43, YELLOW),
        ("payloadlog/payload_stopped_indicator", 480, 44, YELLOW_D),
    ]:
        img, d = ss_start(w, h)
        rrect(d, (0, 0, w-1, h-1), fill=(color[0], color[1], color[2], 8),
              outline=(color[0], color[1], color[2], 35), radius=2, width=1)
        d.rectangle([0, 0, 3*s, (h-1)*s], fill=_c(color))
        save(ss_finish(img, w, h), f"{name}.png")

    # Scroll indicators (12x15)
    for name, flip in [("payloadlog/scroll_up_indicator", False),
                       ("payloadlog/scroll_down_indicator", True)]:
        img, d = ss_start(12, 15)
        if not flip:
            d.polygon([(6*s, 1*s), (11*s, 14*s), (1*s, 14*s)], fill=_c(YELLOW))
        else:
            d.polygon([(6*s, 14*s), (11*s, 1*s), (1*s, 1*s)], fill=_c(YELLOW))
        save(ss_finish(img, 12, 15), f"{name}.png")

    # Scroll pause (16x16)
    img, d = ss_start(16, 16)
    d.rectangle([3*s, 2*s, 6*s, 13*s], fill=_c(YELLOW))
    d.rectangle([9*s, 2*s, 12*s, 13*s], fill=_c(YELLOW))
    save(ss_finish(img, 16, 16), "payloadlog/scroll_pause_indicator.png")

    # Payloads dashboard arrow (20x18)
    img, d = ss_start(20, 18)
    d.polygon([(2*s, 9*s), (16*s, 2*s), (16*s, 16*s)], fill=_c(SOFT_W))
    save(ss_finish(img, 20, 18), "payloads_dashboard/arrow.png")

    # Launch animation frames — simple yellow pulse rings, 4 frames
    for fi in range(4):
        w, h = 113, 106
        img, d = ss_start(w, h)
        cx, cy = w * SS // 2, h * SS // 2
        # Outer ring
        r1 = min(cx, cy) - 4 * SS
        alpha1 = [80, 120, 180, 220]
        d.ellipse([cx - r1, cy - r1, cx + r1, cy + r1],
                  outline=_c(YELLOW, alpha1[fi]), width=2 * SS)
        # Inner ring
        r2 = r1 - 10 * SS
        alpha2 = [60, 100, 140, 180]
        d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2],
                  outline=_c(YELLOW, alpha2[fi]), width=2 * SS)
        # Center dot
        r3 = (4 + fi) * SS
        d.ellipse([cx - r3, cy - r3, cx + r3, cy + r3],
                  fill=_c(YELLOW, 100 + fi * 35))
        d.ellipse([cx - 3 * SS, cy - 3 * SS, cx + 3 * SS, cy + 3 * SS],
                  fill=_c(YELLOW, 220))
        save(ss_finish(img, w, h), f"launch_payload_dialog/animation/anim_frame_{fi + 1}.png")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print(f"Generating YellowJacket assets → {ASSETS_DIR}")
    print(f"Supersample factor: {SS}x")
    os.makedirs(ASSETS_DIR, exist_ok=True)

    steps = [
        ("Status bar icons", gen_statusbar),
        ("Dashboard", gen_dashboard),
        ("Spinner", gen_spinner),
        ("Boot animation", gen_boot),
        ("Keyboards", gen_keyboard),
        ("Dialogs", gen_dialogs),
        ("Toggles/Radio/Checkbox", gen_toggles),
        ("Recon", gen_recon),
        ("Full-screen backgrounds", gen_backgrounds),
        ("Misc UI elements", gen_misc),
    ]

    for i, (label, fn) in enumerate(steps, 1):
        print(f"  [{i}/{len(steps)}] {label}...")
        fn()

    count = sum(1 for r, _, fs in os.walk(ASSETS_DIR) for f in fs if f.endswith(".png"))
    print(f"\nGenerated {count} PNG assets.")


if __name__ == "__main__":
    main()
