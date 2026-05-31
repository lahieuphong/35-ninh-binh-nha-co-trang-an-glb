from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEXTURE_DIR = PROJECT_ROOT / "assets" / "textures" / "nha_co_trang_an"
DOCS_DIR = PROJECT_ROOT / "docs"
SIZE = 512


def _clamp(v: float, lo: int = 0, hi: int = 255) -> int:
    return int(max(lo, min(hi, round(v))))


def _noise_l(size: int, seed: int, low_res: int = 96, blur: float = 1.2) -> Image.Image:
    rng = random.Random(seed)
    img = Image.new("L", (low_res, low_res))
    px = img.load()
    for y in range(low_res):
        for x in range(low_res):
            px[x, y] = rng.randrange(256)
    img = img.resize((size, size), Image.Resampling.BICUBIC)
    if blur:
        img = img.filter(ImageFilter.GaussianBlur(blur))
    return img


def _save_pair(name: str, base: Image.Image, height: Image.Image, *, normal_strength: float = 3.2) -> None:
    TEXTURE_DIR.mkdir(parents=True, exist_ok=True)
    base.save(TEXTURE_DIR / f"{name}_basecolor.png", optimize=True)
    _normal_from_height(height, strength=normal_strength).save(TEXTURE_DIR / f"{name}_normal.png", optimize=True)


def _normal_from_height(height: Image.Image, *, strength: float = 3.2) -> Image.Image:
    h = height.convert("L").filter(ImageFilter.GaussianBlur(0.45))
    src = h.load()
    w, hh = h.size
    out = Image.new("RGB", (w, hh), (128, 128, 255))
    dst = out.load()
    for y in range(hh):
        ym = (y - 1) % hh
        yp = (y + 1) % hh
        for x in range(w):
            xm = (x - 1) % w
            xp = (x + 1) % w
            dx = ((src[xp, y] - src[xm, y]) / 255.0) * strength
            dy = ((src[x, yp] - src[x, ym]) / 255.0) * strength
            nx, ny, nz = -dx, -dy, 1.0
            ln = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
            nx, ny, nz = nx / ln, ny / ln, nz / ln
            dst[x, y] = (_clamp((nx * 0.5 + 0.5) * 255), _clamp((ny * 0.5 + 0.5) * 255), _clamp((nz * 0.5 + 0.5) * 255))
    return out


def _jitter(color: tuple[int, int, int], amount: int, rng: random.Random) -> tuple[int, int, int]:
    return tuple(_clamp(c + rng.randint(-amount, amount)) for c in color)


def make_old_lim_wood() -> None:
    rng = random.Random(101)
    base = Image.new("RGB", (SIZE, SIZE), (220, 150, 82))
    height = Image.new("L", (SIZE, SIZE), 135)
    draw = ImageDraw.Draw(base)
    hdraw = ImageDraw.Draw(height)
    n = _noise_l(SIZE, 102, low_res=128, blur=1.0).load()
    px = base.load()
    hp = height.load()
    for y in range(SIZE):
        for x in range(SIZE):
            grain = math.sin(x * 0.055 + math.sin(y * 0.018) * 1.8) * 22
            fine = (n[x, y] - 128) * 0.22
            r = 216 + grain + fine
            g = 142 + grain * 0.42 + fine * 0.48
            b = 74 + grain * 0.18 + fine * 0.30
            px[x, y] = (_clamp(r), _clamp(g), _clamp(b))
            hp[x, y] = _clamp(126 + grain * 0.80 + fine * 0.65)

    # Thớ gỗ lim già: nhiều vân dọc, có vết nứt sẫm và mắt gỗ.
    for _ in range(80):
        x = rng.randrange(SIZE)
        color = _jitter((118, 55, 23), 18, rng)
        width = rng.choice([1, 1, 2, 3])
        wiggle = rng.uniform(0.012, 0.030)
        pts = []
        for y in range(-20, SIZE + 20, 16):
            pts.append((x + math.sin(y * wiggle + rng.random() * 2.0) * rng.uniform(6, 24), y))
        draw.line(pts, fill=color, width=width)
        hdraw.line(pts, fill=rng.randint(70, 105), width=width)

    for _ in range(16):
        cx, cy = rng.randrange(SIZE), rng.randrange(SIZE)
        rx, ry = rng.randint(10, 28), rng.randint(5, 13)
        box = (cx - rx, cy - ry, cx + rx, cy + ry)
        draw.ellipse(box, outline=_jitter((92, 43, 18), 12, rng), width=2)
        draw.ellipse((cx - rx // 2, cy - ry // 2, cx + rx // 2, cy + ry // 2), outline=_jitter((150, 78, 35), 12, rng), width=1)
        hdraw.ellipse(box, outline=84, width=2)
    _save_pair("old_lim_wood", base, height, normal_strength=3.4)


def make_fishscale_roof_tile() -> None:
    rng = random.Random(201)
    # Giảm độ cam/tươi rất nhẹ để mái ngói cũ hơn nhưng không bị tối đi quá rõ.
    base = Image.new("RGB", (SIZE, SIZE), (205, 108, 63))
    height = Image.new("L", (SIZE, SIZE), 110)
    draw = ImageDraw.Draw(base)
    hdraw = ImageDraw.Draw(height)
    tile_w, tile_h = 58, 48
    for row, y in enumerate(range(-tile_h, SIZE + tile_h, tile_h // 2)):
        offset = 0 if row % 2 == 0 else tile_w // 2
        for x in range(-tile_w, SIZE + tile_w, tile_w):
            x0 = x + offset
            col = _jitter((210, 112, 68), 30, rng)
            # Miếng ngói vảy: thân là ô cong, đáy có cung tròn nhô.
            rect = (x0, y, x0 + tile_w, y + tile_h)
            draw.rounded_rectangle(rect, radius=8, fill=col)
            draw.arc((x0, y + tile_h // 3, x0 + tile_w, y + tile_h + tile_h // 3), 180, 360, fill=_jitter((92, 36, 22), 10, rng), width=3)
            draw.line((x0, y, x0, y + tile_h), fill=_jitter((110, 44, 24), 12, rng), width=1)
            draw.line((x0 + tile_w, y, x0 + tile_w, y + tile_h), fill=_jitter((105, 42, 24), 12, rng), width=1)
            draw.line((x0 + 2, y + 2, x0 + tile_w - 3, y + 2), fill=_jitter((228, 142, 92), 14, rng), width=1)
            hdraw.rounded_rectangle(rect, radius=8, fill=150)
            hdraw.arc((x0, y + tile_h // 3, x0 + tile_w, y + tile_h + tile_h // 3), 180, 360, fill=205, width=5)
            hdraw.line((x0, y, x0, y + tile_h), fill=70, width=2)

    # Vết thâm, rêu và bạc màu trên mái cũ.
    for _ in range(340):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        r = rng.randint(1, 5)
        if rng.random() < 0.78:
            color = _jitter((82, 43, 28), 18, rng)
        else:
            color = _jitter((55, 88, 40), 16, rng)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color)
        hdraw.ellipse((x - r, y - r, x + r, y + r), fill=rng.randint(70, 125))
    _save_pair("fishscale_roof_tile", base, height, normal_strength=4.2)


def make_limestone_wall() -> None:
    rng = random.Random(301)
    noise = _noise_l(SIZE, 302, low_res=90, blur=1.8).load()
    base = Image.new("RGB", (SIZE, SIZE), (216, 213, 196))
    height = Image.new("L", (SIZE, SIZE), 142)
    px = base.load(); hp = height.load()
    for y in range(SIZE):
        for x in range(SIZE):
            v = noise[x, y] - 128
            warm = math.sin((x + y) * 0.018) * 9
            px[x, y] = (_clamp(216 + v * 0.25 + warm), _clamp(214 + v * 0.22 + warm * 0.4), _clamp(194 + v * 0.18),)
            hp[x, y] = _clamp(140 + v * 0.42)
    draw = ImageDraw.Draw(base); hdraw = ImageDraw.Draw(height)
    # Nứt đá vôi và rãnh tự nhiên.
    for _ in range(36):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        pts = [(x, y)]
        angle = rng.random() * math.tau
        for _ in range(rng.randint(5, 12)):
            angle += rng.uniform(-0.55, 0.55)
            x += math.cos(angle) * rng.randint(14, 34)
            y += math.sin(angle) * rng.randint(14, 34)
            pts.append((x, y))
        draw.line(pts, fill=_jitter((92, 94, 86), 16, rng), width=rng.choice([1, 1, 2]))
        hdraw.line(pts, fill=rng.randint(65, 95), width=2)
    for _ in range(120):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        if rng.random() < 0.35:
            col = _jitter((70, 114, 55), 18, rng)
            r = rng.randint(2, 8)
            draw.ellipse((x-r, y-r, x+r, y+r), fill=col)
            hdraw.ellipse((x-r, y-r, x+r, y+r), fill=118)
    _save_pair("limestone_wall", base, height, normal_strength=3.7)


def make_courtyard_brick() -> None:
    rng = random.Random(401)
    # Bản v6: đổi riêng sân sang cam đất nung.
    # Vẫn lấy họ màu từ mái ngói nhưng giảm độ đỏ/hồng: pha vàng đất + bụi vôi ấm,
    # giảm kênh xanh dương để sân ra cam gạch cũ thay vì hồng pastel.
    roof_path = TEXTURE_DIR / "fishscale_roof_tile_basecolor.png"
    if roof_path.exists():
        roof_src = Image.open(roof_path).convert("RGB").resize((SIZE, SIZE), Image.Resampling.BICUBIC)
        roof_src = roof_src.filter(ImageFilter.GaussianBlur(6.0))
    else:
        roof_src = Image.new("RGB", (SIZE, SIZE), (205, 108, 63))
    roof_px = roof_src.load()
    noise = _noise_l(SIZE, 404, low_res=120, blur=1.0).load()
    fine = _noise_l(SIZE, 405, low_res=180, blur=0.55).load()
    base = Image.new("RGB", (SIZE, SIZE), (205, 132, 77))
    draw = ImageDraw.Draw(base)
    px = base.load()
    orange_dust = (224, 163, 96)
    pale_lime_dust = (226, 202, 170)

    for y in range(SIZE):
        for x in range(SIZE):
            sx = (x + 31 + int(math.sin(y * 0.018) * 17)) % SIZE
            sy = (y + 67 + int(math.sin(x * 0.020) * 11)) % SIZE
            rr, gg, bb = roof_px[sx, sy]
            # Bắt đầu từ mái ngói, sau đó kéo về cam đất thay vì hồng nhạt.
            r = rr * 0.44 + orange_dust[0] * 0.42 + pale_lime_dust[0] * 0.14
            g = gg * 0.44 + orange_dust[1] * 0.42 + pale_lime_dust[1] * 0.14
            b = bb * 0.38 + orange_dust[2] * 0.48 + pale_lime_dust[2] * 0.14
            # Tăng sắc cam/vàng nhẹ: xanh dương xuống, đỏ giữ vừa phải để không quay lại đỏ mái.
            r = r * 1.02
            g = g * 0.98 + 4
            b = b * 0.78
            v = noise[x, y] - 128
            f = fine[x, y] - 128
            px[x, y] = (
                _clamp(r + v * 0.10 + f * 0.030),
                _clamp(g + v * 0.085 + f * 0.020),
                _clamp(b + v * 0.055 + f * 0.015),
            )

    bw, bh, gap = 92, 46, 5
    brick_palette = [
        (212, 133, 76),
        (198, 119, 67),
        (224, 151, 88),
        (188, 109, 62),
        (218, 143, 82),
        (203, 128, 72),
    ]
    for row, y in enumerate(range(-bh, SIZE + bh, bh)):
        offset = 0 if row % 2 == 0 else bw // 2
        for x in range(-bw, SIZE + bw, bw):
            x0 = x + offset
            rect = (x0 + gap, y + gap, x0 + bw - gap, y + bh - gap)
            col = _jitter(rng.choice(brick_palette), 11, rng)
            draw.rectangle(rect, fill=col)
            # Ron và mép gạch giữ sáng/ấm để thấy lát sân nhưng không bị trắng gắt.
            draw.line((rect[0], rect[1], rect[2], rect[1]), fill=_jitter((235, 196, 150), 8, rng), width=1)
            draw.line((rect[0], rect[3], rect[2], rect[3]), fill=_jitter((154, 91, 55), 8, rng), width=1)
            draw.line((rect[0], rect[1], rect[0], rect[3]), fill=_jitter((171, 103, 62), 7, rng), width=1)
            for _ in range(rng.randint(1, 3)):
                sx = rng.randint(int(rect[0]) + 4, int(rect[2]) - 4)
                sy = rng.randint(int(rect[1]) + 4, int(rect[3]) - 4)
                rr = rng.randint(2, 7)
                stain = _jitter(rng.choice([(184, 110, 66), (236, 179, 118), (207, 132, 76)]), 9, rng)
                draw.ellipse((sx - rr, sy - rr // 2, sx + rr, sy + rr // 2), fill=stain)
            if rng.random() < 0.22:
                cx = rng.randint(x0 + 16, x0 + bw - 16)
                cy = rng.randint(y + 12, y + bh - 10)
                pts = [(cx, cy), (cx + rng.randint(-12, 14), cy + rng.randint(-5, 6)), (cx + rng.randint(-16, 17), cy + rng.randint(-10, 10))]
                draw.line(pts, fill=_jitter((128, 79, 54), 7, rng), width=1)

    # Giữ nguyên normal/relief sân từ bản trước; chỉ đổi basecolor.
    base.save(TEXTURE_DIR / "courtyard_brick_basecolor.png", optimize=True)

def make_warm_earth() -> None:
    rng = random.Random(501)
    noise = _noise_l(SIZE, 502, low_res=128, blur=1.0).load()
    base = Image.new("RGB", (SIZE, SIZE))
    height = Image.new("L", (SIZE, SIZE))
    px = base.load(); hp = height.load()
    for y in range(SIZE):
        for x in range(SIZE):
            v = noise[x, y] - 128
            px[x, y] = (_clamp(168 + v * 0.32), _clamp(125 + v * 0.26), _clamp(82 + v * 0.18))
            hp[x, y] = _clamp(126 + v * 0.55)
    draw = ImageDraw.Draw(base); hdraw = ImageDraw.Draw(height)
    for _ in range(260):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        r = rng.randint(1, 4)
        col = _jitter((105, 74, 47), 25, rng)
        draw.ellipse((x-r, y-r, x+r, y+r), fill=col)
        hdraw.ellipse((x-r, y-r, x+r, y+r), fill=rng.randint(100, 170))
    _save_pair("warm_earth", base, height, normal_strength=3.0)


def make_moss() -> None:
    rng = random.Random(601)
    noise = _noise_l(SIZE, 602, low_res=90, blur=0.8).load()
    base = Image.new("RGB", (SIZE, SIZE))
    height = Image.new("L", (SIZE, SIZE))
    px = base.load(); hp = height.load()
    for y in range(SIZE):
        for x in range(SIZE):
            v = noise[x, y] - 128
            px[x, y] = (_clamp(65 + v * 0.16), _clamp(132 + v * 0.38), _clamp(48 + v * 0.18))
            hp[x, y] = _clamp(138 + v * 0.45)
    draw = ImageDraw.Draw(base); hdraw = ImageDraw.Draw(height)
    for _ in range(420):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        r = rng.randint(1, 5)
        col = _jitter((78, 153, 57), 25, rng)
        draw.ellipse((x-r, y-r, x+r, y+r), fill=col)
        hdraw.ellipse((x-r, y-r, x+r, y+r), fill=rng.randint(135, 205))
    _save_pair("moss", base, height, normal_strength=2.5)


def make_village_leaf() -> None:
    rng = random.Random(701)
    base = Image.new("RGB", (SIZE, SIZE), (58, 136, 48))
    height = Image.new("L", (SIZE, SIZE), 120)
    draw = ImageDraw.Draw(base); hdraw = ImageDraw.Draw(height)
    # Nền xanh sâu hơn để khi lên tán cây nhìn thật và dày hơn, không bị neon.
    noise = _noise_l(SIZE, 702, low_res=110, blur=1.2).load()
    px = base.load(); hp = height.load()
    for y in range(SIZE):
        for x in range(SIZE):
            v = noise[x, y] - 128
            px[x, y] = (_clamp(58 + v * 0.11), _clamp(136 + v * 0.28), _clamp(48 + v * 0.13))
            hp[x, y] = _clamp(120 + v * 0.22)
    for _ in range(340):
        cx, cy = rng.randrange(SIZE), rng.randrange(SIZE)
        length = rng.randint(22, 58)
        width = rng.randint(9, 22)
        angle = rng.random() * math.tau
        col = _jitter(rng.choice([(45, 112, 38), (78, 158, 55), (36, 92, 36), (118, 180, 68)]), 14, rng)
        leaf = Image.new("RGBA", (length + 8, width + 8), (0, 0, 0, 0))
        ld = ImageDraw.Draw(leaf)
        ld.ellipse((4, 4, length + 4, width + 4), fill=(*col, 165))
        ld.line((5, width // 2 + 4, length + 3, width // 2 + 4), fill=(168, 220, 110, 105), width=1)
        leaf = leaf.rotate(math.degrees(angle), expand=True, resample=Image.Resampling.BICUBIC)
        overlay = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        overlay.alpha_composite(leaf, (cx - leaf.width // 2, cy - leaf.height // 2))
        base = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(base)
        hdraw.ellipse((cx - width, cy - width, cx + width, cy + width), fill=rng.randint(132, 188))
    _save_pair("village_leaf", base, height, normal_strength=2.4)


def make_bamboo() -> None:
    rng = random.Random(801)
    base = Image.new("RGB", (SIZE, SIZE), (230, 185, 92))
    height = Image.new("L", (SIZE, SIZE), 128)
    draw = ImageDraw.Draw(base); hdraw = ImageDraw.Draw(height)
    for x in range(0, SIZE, 38):
        col = _jitter((226, 183, 91), 20, rng)
        draw.rectangle((x, 0, x + 37, SIZE), fill=col)
        draw.line((x, 0, x, SIZE), fill=_jitter((141, 105, 48), 10, rng), width=2)
        draw.line((x + 36, 0, x + 36, SIZE), fill=_jitter((245, 210, 120), 8, rng), width=1)
        hdraw.rectangle((x, 0, x + 37, SIZE), fill=rng.randint(132, 158))
        hdraw.line((x, 0, x, SIZE), fill=85, width=3)
    for y in range(20, SIZE, 62):
        yy = y + rng.randint(-8, 8)
        draw.line((0, yy, SIZE, yy), fill=_jitter((130, 94, 40), 13, rng), width=4)
        draw.line((0, yy + 3, SIZE, yy + 3), fill=_jitter((247, 215, 127), 8, rng), width=1)
        hdraw.line((0, yy, SIZE, yy), fill=202, width=4)
    _save_pair("bamboo", base, height, normal_strength=3.4)


def make_bamboo_fence() -> None:
    rng = random.Random(851)
    # Hàng rào dùng texture riêng, tối và nâu hơn tre cây/cọc gáo để nổi rõ trên sân cam.
    base = Image.new("RGB", (SIZE, SIZE), (178, 121, 48))
    height = Image.new("L", (SIZE, SIZE), 128)
    draw = ImageDraw.Draw(base); hdraw = ImageDraw.Draw(height)
    noise = _noise_l(SIZE, 852, low_res=120, blur=0.85).load()
    px = base.load(); hp = height.load()
    for y in range(SIZE):
        for x in range(SIZE):
            v = noise[x, y] - 128
            grain = math.sin(x * 0.075 + math.sin(y * 0.022) * 1.4) * 10
            px[x, y] = (
                _clamp(174 + v * 0.11 + grain),
                _clamp(116 + v * 0.08 + grain * 0.45),
                _clamp(45 + v * 0.05 + grain * 0.18),
            )
            hp[x, y] = _clamp(128 + v * 0.18 + grain * 0.55)

    for x in range(0, SIZE, 34):
        col = _jitter((184, 124, 48), 16, rng)
        draw.rectangle((x, 0, x + 33, SIZE), fill=col)
        draw.line((x, 0, x, SIZE), fill=_jitter((89, 59, 25), 10, rng), width=3)
        draw.line((x + 32, 0, x + 32, SIZE), fill=_jitter((229, 165, 73), 9, rng), width=1)
        hdraw.rectangle((x, 0, x + 33, SIZE), fill=rng.randint(132, 160))
        hdraw.line((x, 0, x, SIZE), fill=82, width=3)
    for y in range(18, SIZE, 56):
        yy = y + rng.randint(-7, 7)
        draw.line((0, yy, SIZE, yy), fill=_jitter((78, 51, 22), 11, rng), width=5)
        draw.line((0, yy + 3, SIZE, yy + 3), fill=_jitter((220, 156, 66), 9, rng), width=1)
        hdraw.line((0, yy, SIZE, yy), fill=202, width=5)

    # Vết buộc/dây khô tạo các điểm nhấn tối, giúp hàng rào tách khỏi nền sân.
    for _ in range(70):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        w, h = rng.randint(9, 20), rng.randint(2, 5)
        draw.ellipse((x - w, y - h, x + w, y + h), fill=_jitter((80, 50, 20), 12, rng))
        hdraw.ellipse((x - w, y - h, x + w, y + h), fill=rng.randint(78, 120))

    _save_pair("bamboo_fence", base, height, normal_strength=3.6)


def make_ceramic_jar() -> None:
    rng = random.Random(901)
    # Nâu sành/da lươn cũ: tối hơn bản trước, ít cam chói để hợp lu nước sân quê.
    base = Image.new("RGB", (SIZE, SIZE), (118, 64, 36))
    height = Image.new("L", (SIZE, SIZE), 132)
    draw = ImageDraw.Draw(base); hdraw = ImageDraw.Draw(height)
    noise = _noise_l(SIZE, 902, low_res=110, blur=1.15).load()
    fine = _noise_l(SIZE, 903, low_res=180, blur=0.55).load()
    px = base.load(); hp = height.load()
    for y in range(SIZE):
        for x in range(SIZE):
            v = noise[x, y] - 128
            f = fine[x, y] - 128
            vertical_glaze = math.sin(x * 0.038 + math.sin(y * 0.018) * 2.8) * 18
            slow_band = math.sin(y * 0.030) * 9
            r = 112 + v * 0.20 + f * 0.05 + vertical_glaze + slow_band
            g = 61 + v * 0.12 + f * 0.03 + vertical_glaze * 0.32 + slow_band * 0.30
            b = 34 + v * 0.08 + f * 0.02 + vertical_glaze * 0.12
            px[x, y] = (_clamp(r), _clamp(g), _clamp(b))
            hp[x, y] = _clamp(128 + v * 0.28 + vertical_glaze * 0.40 + slow_band * 0.35)

    # Vệt men chảy dọc và đốm nung không đều, tạo cảm giác gốm sành thủ công.
    for _ in range(105):
        x = rng.randrange(SIZE)
        length_bias = rng.randint(-18, 28)
        color = _jitter(rng.choice([(70, 34, 22), (146, 83, 44), (93, 49, 29)]), 18, rng)
        draw.line((x, -12, x + rng.randint(-22, 22), SIZE + 12 + length_bias), fill=color, width=rng.choice([1, 1, 2, 3]))
        hdraw.line((x, -12, x + rng.randint(-22, 22), SIZE + 12), fill=rng.randint(88, 138), width=2)

    for _ in range(70):
        cx, cy = rng.randrange(SIZE), rng.randrange(SIZE)
        rx, ry = rng.randint(6, 22), rng.randint(3, 10)
        if rng.random() < 0.58:
            col = _jitter((58, 31, 22), 12, rng)
            hv = rng.randint(70, 105)
        else:
            col = _jitter((166, 102, 55), 18, rng)
            hv = rng.randint(150, 190)
        draw.ellipse((cx-rx, cy-ry, cx+rx, cy+ry), fill=col)
        hdraw.ellipse((cx-rx, cy-ry, cx+rx, cy+ry), fill=hv)

    # Vài vòng men ngang nhẹ như vết quay bàn xoay.
    for y in range(34, SIZE, 58):
        yy = y + rng.randint(-8, 8)
        draw.line((0, yy, SIZE, yy), fill=_jitter((86, 45, 27), 14, rng), width=1)
        draw.line((0, yy + 2, SIZE, yy + 2), fill=_jitter((157, 94, 51), 12, rng), width=1)
        hdraw.line((0, yy, SIZE, yy), fill=115, width=2)
    _save_pair("ceramic_jar", base, height, normal_strength=2.9)


def make_dark_mortar() -> None:
    rng = random.Random(1001)
    noise = _noise_l(SIZE, 1002, low_res=80, blur=1.3).load()
    base = Image.new("RGB", (SIZE, SIZE))
    height = Image.new("L", (SIZE, SIZE))
    px = base.load(); hp = height.load()
    for y in range(SIZE):
        for x in range(SIZE):
            v = noise[x, y] - 128
            px[x, y] = (_clamp(96 + v * 0.20), _clamp(47 + v * 0.12), _clamp(37 + v * 0.10))
            hp[x, y] = _clamp(88 + v * 0.30)
    draw = ImageDraw.Draw(base); hdraw = ImageDraw.Draw(height)
    for _ in range(140):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        r = rng.randint(1, 3)
        draw.ellipse((x-r, y-r, x+r, y+r), fill=_jitter((58, 32, 27), 12, rng))
        hdraw.ellipse((x-r, y-r, x+r, y+r), fill=rng.randint(55, 105))
    _save_pair("dark_mortar", base, height, normal_strength=2.0)


def make_display_underside() -> None:
    rng = random.Random(1101)
    noise = _noise_l(SIZE, 1102, low_res=88, blur=1.7).load()
    fine = _noise_l(SIZE, 1103, low_res=160, blur=0.7).load()
    base = Image.new("RGB", (SIZE, SIZE))
    height = Image.new("L", (SIZE, SIZE))
    px = base.load(); hp = height.load()
    for y in range(SIZE):
        for x in range(SIZE):
            v = noise[x, y] - 128
            f = fine[x, y] - 128
            warm = math.sin((x * 0.020) + (y * 0.013)) * 5
            # Mặt đáy v6: đất nâu cam khô, pha khoáng sáng gợi vùng núi đá vôi Tràng An,
            # không còn sắc xám đá lạnh như bản trước.
            px[x, y] = (
                _clamp(174 + v * 0.22 + f * 0.045 + warm),
                _clamp(115 + v * 0.16 + f * 0.030 + warm * 0.38),
                _clamp(62 + v * 0.11 + f * 0.020),
            )
            hp[x, y] = _clamp(130 + v * 0.28 + f * 0.06)

    draw = ImageDraw.Draw(base); hdraw = ImageDraw.Draw(height)

    # Vết nứt đất mảnh, không quá nhiều; nét tối + nét sáng lệch để trông tự nhiên.
    for _ in range(20):
        x = rng.randint(-20, SIZE + 20)
        y = rng.randint(-20, SIZE + 20)
        angle = rng.random() * math.tau
        pts = [(x, y)]
        seg_count = rng.randint(4, 8)
        for _seg in range(seg_count):
            angle += rng.uniform(-0.42, 0.42)
            length = rng.randint(18, 44)
            x += math.cos(angle) * length
            y += math.sin(angle) * length
            pts.append((x, y))
        shade = _jitter((84, 58, 36), 9, rng)
        draw.line(pts, fill=shade, width=rng.choice([1, 1, 1, 2]))
        highlight = [(pxx + 1, pyy + 1) for pxx, pyy in pts]
        draw.line(highlight, fill=_jitter((210, 156, 100), 12, rng), width=1)
        hdraw.line(pts, fill=rng.randint(70, 94), width=1)

        if rng.random() < 0.46 and len(pts) > 3:
            root = rng.choice(pts[1:-1])
            branch_angle = angle + rng.choice([-1.0, 1.0]) * rng.uniform(0.55, 1.00)
            bx, by = root
            bpts = [(bx, by)]
            for _b in range(rng.randint(2, 4)):
                branch_angle += rng.uniform(-0.32, 0.32)
                bx += math.cos(branch_angle) * rng.randint(10, 24)
                by += math.sin(branch_angle) * rng.randint(10, 24)
                bpts.append((bx, by))
            draw.line(bpts, fill=_jitter((96, 65, 38), 9, rng), width=1)
            hdraw.line(bpts, fill=rng.randint(78, 100), width=1)

    # Lấm tấm khoáng/vôi và đất sét nung khô, không dùng đốm xanh/rêu.
    for _ in range(115):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        r = rng.randint(1, 4)
        col = _jitter(rng.choice([(126, 82, 45), (97, 66, 42), (198, 151, 98), (152, 104, 58)]), 10, rng)
        draw.ellipse((x-r, y-r, x+r, y+r), fill=col)
        hdraw.ellipse((x-r, y-r, x+r, y+r), fill=rng.randint(112, 150))

    _save_pair("display_underside", base, height, normal_strength=2.2)

def make_contact_sheet() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(TEXTURE_DIR.glob("*_basecolor.png"))
    if not files:
        return
    thumb_w, thumb_h = 128, 128
    label_h = 32
    cols = 5
    rows = math.ceil(len(files) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (238, 236, 228))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    for idx, path in enumerate(files):
        col = idx % cols
        row = idx // cols
        img = Image.open(path).convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x, y = col * thumb_w, row * (thumb_h + label_h)
        sheet.paste(img, (x, y))
        label = path.name.replace("_basecolor.png", "")[:22]
        draw.text((x + 4, y + thumb_h + 7), label, fill=(42, 40, 36), font=font)
    sheet.save(DOCS_DIR / "texture_preview_contact_sheet.png", optimize=True)


def main() -> None:
    TEXTURE_DIR.mkdir(parents=True, exist_ok=True)
    make_old_lim_wood()
    make_fishscale_roof_tile()
    make_limestone_wall()
    make_courtyard_brick()
    make_warm_earth()
    make_moss()
    make_village_leaf()
    make_bamboo()
    make_bamboo_fence()
    make_ceramic_jar()
    make_dark_mortar()
    make_display_underside()
    make_contact_sheet()
    print(f"Generated textures: {TEXTURE_DIR}")


if __name__ == "__main__":
    main()
