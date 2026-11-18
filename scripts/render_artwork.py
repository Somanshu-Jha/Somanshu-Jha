"""Regenerate the profile artwork on Windows with Python and Pillow.

Run: python scripts/render_artwork.py
Uses the local Georgia and Cascadia Mono fonts. No network access is needed.
"""

from pathlib import Path
import math
import random
import re
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
SCALE = 2
PAPER = (239, 233, 220)
INK = '#252420'
MUTED = '#736E63'
ACCENT = '#BA6245'
RULE = '#C3BAA9'
FONTS = Path('C:/Windows/Fonts')


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), round(size * SCALE))


def paper(width, height):
    randomizer = random.Random(2718)
    image = Image.new('RGB', (width * SCALE, height * SCALE), PAPER)
    draw = ImageDraw.Draw(image)
    for _ in range(width * height // 5):
        x = randomizer.randrange(width * SCALE)
        y = randomizer.randrange(height * SCALE)
        tone = randomizer.choice([-5, -3, 3])
        draw.point((x, y), fill=tuple(channel + tone for channel in PAPER))
    return image


def text(draw, xy, value, face, size, fill=INK):
    draw.text(tuple(round(v * SCALE) for v in xy), value,
              font=font(face, size), fill=fill, stroke_width=0)


def line(draw, points, fill=RULE, width=1):
    draw.line([(round(x * SCALE), round(y * SCALE)) for x, y in points],
              fill=fill, width=max(1, round(width * SCALE)))


def circle(draw, x, y, radius, fill, outline=None, width=1):
    box = tuple(round(v * SCALE) for v in (x - radius, y - radius, x + radius, y + radius))
    draw.ellipse(box, fill=fill, outline=outline, width=round(width * SCALE))


def export_loop(frames, stem, duration):
    resized = [frame.resize((frame.width // SCALE, frame.height // SCALE), Image.Resampling.LANCZOS)
               for frame in frames]
    resized[0].save(ASSETS / f'{stem}.png', optimize=True)
    palette_source = resized[0].copy()
    # Give the small moving accent enough weight to retain its intended color.
    ImageDraw.Draw(palette_source).rectangle((0, 0, 180, 65), fill=ACCENT)
    palette = palette_source.quantize(colors=96, method=Image.Quantize.MEDIANCUT)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in resized]
    indexed[0].save(ASSETS / f'{stem}.gif', save_all=True, append_images=indexed[1:],
                    duration=duration, loop=0, optimize=True, disposal=1)
    return len(indexed)


def banner_frames():
    background = paper(1200, 420)
    draw = ImageDraw.Draw(background)
    text(draw, (54, 29), 'SOMANSHU-JHA  /  OPEN SOURCE', 'CascadiaMono.ttf', 13, MUTED)
    text(draw, (1054, 29), 'PROFILE 01', 'CascadiaMono.ttf', 13, MUTED)
    line(draw, [(54, 60), (1146, 60)])
    text(draw, (50, 69), 'Somanshu', 'georgia.ttf', 114)
    text(draw, (50, 185), 'Jha.', 'georgiai.ttf', 126)
    text(draw, (355, 224), 'Code, models,', 'georgia.ttf', 24, MUTED)
    text(draw, (355, 260), 'and things that work.', 'georgia.ttf', 24, MUTED)
    line(draw, [(54, 350), (1146, 350)])
    text(draw, (54, 371), 'AI / ML     SYSTEMS     WEB3', 'CascadiaMono.ttf', 16)
    text(draw, (867, 373), 'RESEARCH. BUILD. REPEAT.', 'CascadiaMono.ttf', 13, MUTED)
    frames = []
    for frame in range(60):
        image = background.copy()
        draw = ImageDraw.Draw(image)
        phase = frame / 60 * math.tau
        rotation = 0.16 * math.sin(phase)
        spread = 48 + 3 * math.sin(phase)
        cx, cy = 930, 207
        for index in range(30):
            orientation = index / 30 * math.tau + rotation
            points = []
            for sample in range(121):
                angle = sample / 120 * math.tau
                u, v = 82 * math.cos(angle), 27 * math.sin(angle)
                points.append((cx + spread * math.cos(orientation) + u * math.cos(orientation) - v * math.sin(orientation),
                               cy + spread * math.sin(orientation) + u * math.sin(orientation) + v * math.cos(orientation)))
            line(draw, points, INK, 0.75)
        orbit = phase - 0.85
        circle(draw, cx + 143 * math.cos(orbit), cy + 125 * math.sin(orbit), 11, ACCENT)
        circle(draw, cx, cy, 3, ACCENT)
        frames.append(image)
    return frames


def workbench_frames():
    background = paper(440, 300)
    draw = ImageDraw.Draw(background)
    text(draw, (25, 20), 'WORKBENCH / FIELD NOTES', 'CascadiaMono.ttf', 12, MUTED)
    line(draw, [(25, 47), (414, 47)])
    text(draw, (24, 61), 'Ideas into code.', 'georgiai.ttf', 30)
    notes = [('01', 'model.train(data)'), ('02', 'system.compile()'), ('03', 'contract.deploy()')]
    for row, (number, code) in enumerate(notes):
        text(draw, (26, 122 + row * 33), number, 'CascadiaMono.ttf', 12, MUTED)
        text(draw, (63, 117 + row * 33), code, 'CascadiaMono.ttf', 16)
    line(draw, [(26, 248), (414, 248)])
    text(draw, (26, 270), 'MODEL', 'CascadiaMono.ttf', 11, MUTED)
    text(draw, (196, 270), 'BUILD', 'CascadiaMono.ttf', 11, MUTED)
    text(draw, (370, 270), 'SHIP', 'CascadiaMono.ttf', 11, MUTED)
    frames = []
    for frame in range(60):
        image = background.copy()
        draw = ImageDraw.Draw(image)
        phase = frame / 60 * math.tau
        x = 220 - 188 * math.cos(phase)
        circle(draw, x, 248, 4, ACCENT)
        line(draw, [(49, 120 + 33 * (frame // 20)), (49, 136 + 33 * (frame // 20))], ACCENT, 2)
        frames.append(image)
    return frames


def update_readme():
    path = ROOT / 'README.md'
    readme = path.read_text(encoding='utf-8')
    hero = '''<p align="center">
  <picture>
    <source media="(prefers-reduced-motion: reduce)" srcset="./assets/banner.png" />
    <img src="./assets/banner.gif" alt="Somanshu Jha — an animated paper-and-ink banner with serif typography and kinetic line art" width="100%" />
  </picture>
</p>'''
    readme = re.sub(r'\A<p align="center">.*?</p>', lambda _: hero, readme, count=1, flags=re.S)
    workbench = '''<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="./assets/building.png" />
  <img align="right" src="./assets/building.gif" alt="Animated workbench notes with a moving progress marker" width="35%" />
</picture>'''
    readme = re.sub(r'(?:<picture>\s*<source[^>]*>\s*)?<img align="right" src="\./assets/building\.gif"[^>]*>(?:\s*</picture>)?',
                    lambda _: workbench, readme, count=1)
    readme = readme.replace('color=176F85', 'color=252420').replace('Explore_repositories-26374B', 'Explore_repositories-252420')
    stats = 'https://github-readme-stats.vercel.app/api?username=Somanshu-Jha&show_icons=true&hide_rank=true&title_color=D1876B&text_color=EDE8DE&icon_color=D1876B&bg_color=1C1C1A&hide_border=true'
    languages = 'https://github-readme-stats.vercel.app/api/top-langs/?username=Somanshu-Jha&layout=compact&title_color=D1876B&text_color=EDE8DE&bg_color=1C1C1A&hide_border=true'
    streak = 'https://streak-stats.demolab.com/?user=Somanshu-Jha&theme=dark&background=1C1C1A&ring=D1876B&fire=D1876B&currStreakLabel=D1876B&hide_border=true'
    for pattern, url in [
        (r'https://github-readme-stats\.vercel\.app/api\?[^"\s]+', stats),
        (r'https://github-readme-stats\.vercel\.app/api/top-langs/\?[^"\s]+', languages),
        (r'https://streak-stats\.demolab\.com/\?[^"\s]+', streak),
    ]:
        readme = re.sub(pattern, lambda _: url, readme)
    path.write_text(readme, encoding='utf-8')


def main():
    banner_count = export_loop(banner_frames(), 'banner', 100)
    workbench_count = export_loop(workbench_frames(), 'building', 100)
    for path in (ASSETS / 'badges').glob('*.svg'):
        svg = path.read_text(encoding='utf-8')
        svg = re.sub(r'(<rect\b[^>]*\bfill=")[^"]+("[^>]*>)', r'\g<1>#252420\2', svg, count=1)
        path.write_text(svg, encoding='utf-8')
    update_readme()
    obsolete = ASSETS / 'banner.svg'
    if obsolete.exists():
        obsolete.unlink()
    print(f'Created two {banner_count}/{workbench_count}-frame loops and static fallbacks.')
    print(f'Banner: {(ASSETS / "banner.gif").stat().st_size / 1024:.0f} KB')


if __name__ == '__main__':
    main()
