#!/usr/bin/env python3
import os, sys, math, select, pygame

# Tekent via DRM/KMS op HDMI; toetsen lezen we uit stdin (SSH).
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

WIN_W, WIN_H = 1080, 1080  # wordt toch fullscreen; resolutie van je scherm telt
BG          = (10, 20, 15)
IRIS_COLOR  = (170, 230, 150)
PUPIL_COL   = (5, 8, 12)
EDGE_COL    = (0, 220, 120)

# Startwaarden
pupil_w   = 280
pupil_h   = 520
edge_px   = 8
taper_amt = 0.80   # 0..1   hoeveel de top/bottom “knijpen”
taper_pow = 2.2    # >=1    hoe steil de punt-curve is
side_round= 1.00   # 0.6..1.4 (1=ellipse; <1 platter aan de zijkant)

def build_pupil_points(cx, cy, w, h, taper_amt, taper_pow, side_round=1.0, samples=220):
    a, b = w/2.0, h/2.0
    left, right = [], []
    for i in range(samples+1):
        yy = (i/samples)*2.0 - 1.0            # -1..+1
        yshape    = (abs(yy)**side_round) * (1 if yy >= 0 else -1)
        x_extent  = math.sqrt(max(0.0, 1.0 - yshape*yshape))
        pinch     = 1.0 - taper_amt * (abs(yy)**taper_pow)
        pinch     = max(0.0, pinch)
        x = a * x_extent * pinch
        y = b * yy
        left.append((cx - x, cy + y))
        right.append((cx + x, cy + y))
    return left + right[::-1]

def draw(scene):
    scene.fill(BG)
    cx, cy = WIN_W//2, WIN_H//2
    r_iris = min(WIN_W, WIN_H)//2 - 30
    pygame.draw.circle(scene, IRIS_COLOR, (cx, cy), r_iris)
    pts = build_pupil_points(cx, cy, pupil_w, pupil_h, taper_amt, taper_pow, side_round)
    pygame.draw.polygon(scene, PUPIL_COL, pts)
    if edge_px > 0:
        pygame.draw.polygon(scene, EDGE_COL, pts, edge_px)

def nonblock_keys():
    """Lees 1 karakter uit stdin zonder te blokkeren; return '' als niets."""
    if select.select([sys.stdin], [], [], 0)[0]:
        ch = sys.stdin.read(1)
        return ch
    return ''

def main():
    global pupil_w, pupil_h, edge_px, taper_amt, taper_pow, side_round

    # KMSDRM fullscreen
    pygame.display.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H), pygame.FULLSCREEN | pygame.DOUBLEBUF)
    pygame.mouse.set_visible(False)

    clock = pygame.time.Clock()
    print("Bediening: a/d breedte, s/w hoogte, [/] rand, 1/2 taper_amt, 3/4 taper_pow, 5/6 side, r reset, q quit.")

    running = True
    while running:
        # Pygame events alleen voor netjes afsluiten via Ctrl+Alt+Backspace e.d.
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        # Toetsen via SSH (stdin)
        ch = nonblock_keys()
        if ch:
            if ch in ('q', '\x1b'):  # q of ESC
                running = False
            elif ch == 'a': pupil_w = max(40, pupil_w - 10)
            elif ch == 'd': pupil_w = min(WIN_W-80, pupil_w + 10)
            elif ch == 's': pupil_h = max(60, pupil_h - 10)
            elif ch == 'w': pupil_h = min(WIN_H-80, pupil_h + 10)
            elif ch == '[': edge_px = max(0, edge_px - 1)
            elif ch == ']': edge_px = min(40, edge_px + 1)
            elif ch == '1': taper_amt = max(0.0, taper_amt - 0.02)
            elif ch == '2': taper_amt = min(1.0, taper_amt + 0.02)
            elif ch == '3': taper_pow = max(1.0, taper_pow - 0.1)
            elif ch == '4': taper_pow = min(6.0, taper_pow + 0.1)
            elif ch == '5': side_round = max(0.6, side_round - 0.02)
            elif ch == '6': side_round = min(1.4, side_round + 0.02)
            elif ch == 'r':
                pupil_w, pupil_h, edge_px = 280, 520, 8
                taper_amt, taper_pow, side_round = 0.80, 2.2, 1.0

        draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
