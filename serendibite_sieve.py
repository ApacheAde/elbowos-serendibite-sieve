#!/usr/bin/env python3
"""Serendibite Sieve — wine-and-chartreuse gem sorter for ElbowOS. Python 3 + pygame."""
import math, os, random, subprocess, sys

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
PLAY = "--play" in sys.argv
if not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/workspace/artifacts/SERENDIBITE_SIEVE_ElbowOS.mp4")
TITLE, HANDLE = "SERENDIBITE SIEVE", "x.com/ElbowOS"
INK, WINE, GOLD = (16, 4, 12), (58, 12, 36), (255, 198, 84)
RAS, CRM, LIM = (236, 62, 128), (255, 226, 178), (190, 255, 70)
COLS = [RAS, CRM, LIM]
NAMES = ["RAS", "CRM", "LIM"]


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.big = pygame.font.Font(None, 92)
        self.mid = pygame.font.Font(None, 64)
        self.small = pygame.font.Font(None, 40)
        try:
            self.screen = pygame.display.set_mode((W, H), 0 if PLAY else pygame.HIDDEN)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.quit()
            pygame.display.init()
            self.screen = pygame.display.set_mode((W, H), pygame.HIDDEN)
        self.rng = random.Random(11)
        self.reset()

    def reset(self):
        self.t = 0
        self.score = 0
        self.combo = 0
        self.angle = 0.0
        self.gems = []
        self.sparks = []
        self.spawn = 0

    def chute(self, i):
        return 210 + i * 330

    def sieve_y(self, x):
        return 1120 + (x - 540) * math.tan(self.angle)

    def burst(self, x, y, col):
        for _ in range(12):
            self.sparks.append({
                "x": x, "y": y, "vx": self.rng.uniform(-7, 7),
                "vy": self.rng.uniform(-9, 1), "life": self.rng.randint(10, 20), "col": col,
            })

    def spawn_gem(self):
        k = self.rng.randrange(3)
        self.gems.append({
            "x": self.rng.uniform(360, 720), "y": 300.0,
            "vx": self.rng.uniform(-1.5, 1.5), "vy": self.rng.uniform(1.5, 3.5),
            "k": k, "on": False,
        })

    def step(self, steer):
        self.t += 1
        self.spawn += 1
        if self.spawn >= 16 and len(self.gems) < 7:
            self.spawn_gem()
            self.spawn = 0
        self.angle = max(-0.42, min(0.42, self.angle + steer * 0.05))
        self.angle *= 0.985
        keep = []
        for g in self.gems:
            if g["on"]:
                g["x"] += math.sin(self.angle) * 9.5
                g["y"] = self.sieve_y(g["x"]) - 26
                if g["x"] < 170 or g["x"] > 910:
                    g["on"] = False
                    g["vy"] = 6
                    g["vx"] = math.sin(self.angle) * 8
            else:
                g["vy"] += 0.42
                g["x"] += g["vx"]
                g["y"] += g["vy"]
                sy = self.sieve_y(g["x"])
                if 170 < g["x"] < 910 and g["y"] >= sy - 26 and g["y"] < sy + 30 and g["vy"] > 0:
                    g["on"] = True
                    g["y"] = sy - 26
                    self.burst(g["x"], g["y"], COLS[g["k"]])
            if g["y"] > 1580:
                hit = min(range(3), key=lambda i: abs(g["x"] - self.chute(i)))
                if hit == g["k"] and abs(g["x"] - self.chute(hit)) < 150:
                    self.combo += 1
                    self.score += 100 + self.combo * 15
                    self.burst(g["x"], 1620, COLS[g["k"]])
                else:
                    self.combo = 0
                    self.burst(g["x"], 1620, (90, 70, 80))
                continue
            keep.append(g)
        self.gems = keep
        for s in self.sparks:
            s["x"] += s["vx"]
            s["y"] += s["vy"]
            s["vy"] += 0.3
            s["life"] -= 1
        self.sparks = [s for s in self.sparks if s["life"] > 0]

    def auto(self):
        live = [g for g in self.gems if g["on"] or g["y"] > 700]
        if not live:
            return 0
        g = min(live, key=lambda q: abs(q["y"] - 1100))
        target = self.chute(g["k"])
        if target > g["x"] + 30:
            return 1
        if target < g["x"] - 30:
            return -1
        return 1 if self.angle < 0 else -1

    def draw(self, surf):
        surf.fill(INK)
        for i in range(16):
            pygame.draw.rect(surf, (28 + i, 6, 18 + i // 2), (0, i * 120, W, 120))
        # canopy ribs
        for i in range(7):
            x = 140 + i * 130
            pygame.draw.arc(surf, (90, 24, 52), (x - 80, 40, 200, 280), 0.2, 2.9, 6)
        pygame.draw.polygon(surf, (78, 18, 46), [(300, 210), (780, 210), (700, 340), (380, 340)])
        pygame.draw.polygon(surf, GOLD, [(300, 210), (780, 210), (700, 340), (380, 340)], 5)
        # sieve mesh
        x1, x2 = 150, 930
        y1, y2 = self.sieve_y(x1), self.sieve_y(x2)
        pygame.draw.line(surf, CRM, (x1, y1), (x2, y2), 22)
        pygame.draw.line(surf, GOLD, (x1, y1), (x2, y2), 4)
        for i in range(12):
            t = i / 11
            px = x1 + (x2 - x1) * t
            py = y1 + (y2 - y1) * t
            pygame.draw.circle(surf, INK, (int(px), int(py)), 7)
        pygame.draw.circle(surf, GOLD, (540, int(self.sieve_y(540))), 18)
        pygame.draw.line(surf, (120, 70, 40), (540, int(self.sieve_y(540))), (540, 1500), 8)
        # chutes
        for i in range(3):
            cx = self.chute(i)
            pygame.draw.rect(surf, COLS[i], (cx - 100, 1605, 200, 175), border_radius=22)
            pygame.draw.rect(surf, INK, (cx - 84, 1622, 168, 140), border_radius=16)
            lab = self.small.render(NAMES[i], True, COLS[i])
            surf.blit(lab, lab.get_rect(center=(cx, 1692)))
        for g in self.gems:
            c = COLS[g["k"]]
            pygame.draw.circle(surf, c, (int(g["x"]), int(g["y"])), 26)
            pygame.draw.circle(surf, (255, 255, 255), (int(g["x"]) - 8, int(g["y"]) - 8), 8)
        for s in self.sparks:
            pygame.draw.circle(surf, s["col"], (int(s["x"]), int(s["y"])), 5)
        surf.blit(self.big.render(TITLE, True, CRM), self.big.render(TITLE, True, CRM).get_rect(center=(W // 2, 96)))
        sc = self.mid.render(f"SCORE {self.score}   COMBO {self.combo}", True, GOLD)
        surf.blit(sc, sc.get_rect(center=(W // 2, 168)))
        hint = self.small.render("A / D tilt the sieve", True, LIM)
        surf.blit(hint, hint.get_rect(center=(W // 2, 1788)))
        hd = self.mid.render(HANDLE, True, LIM)
        surf.blit(hd, hd.get_rect(center=(W // 2, 1854)))

    def play_interactive(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            steer = 0
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
                    self.reset()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                steer -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                steer += 1
            self.step(steer)
            self.draw(self.screen)
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()

    def record(self):
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
            "-movflags", "+faststart", OUT,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            for _ in range(FPS * SECS):
                self.step(self.auto())
                self.draw(self.screen)
                proc.stdin.write(pygame.image.tostring(self.screen, "RGB"))
        finally:
            proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1200:]}")
        print("wrote", OUT)
        pygame.quit()


def main():
    g = Game()
    g.play_interactive() if PLAY else g.record()


if __name__ == "__main__":
    main()
