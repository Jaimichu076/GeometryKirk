# boss_template.py
# Plantilla robusta para un boss. Usa math en lugar de pygame.math.
import pygame
import random
import os
import math
import config
from player import Player, PLAYER_MAX_HP
pygame.init()

# Cambia estas rutas por boss_0.png / boss_0.mp3 etc.
BOSS_IMAGE = os.path.join(config.ASSETS_IMG, "boss_X.png")
BOSS_MUSIC = os.path.join(config.ASSETS_AUDIO, "boss_X.mp3")

# Parámetros (ajusta por nivel)
BOSS_SIZE = 160
BOSS_MAX_HP = 600
PROJECTILE_SIZE = 14
FPS = config.FPS

def load_boss_image(path, size):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (size, size))
    except Exception:
        surf = pygame.Surface((size, size))
        surf.fill((200, 60, 60))
        return surf

class Boss:
    def __init__(self):
        self.w = BOSS_SIZE; self.h = BOSS_SIZE
        self.x = config.WIDTH - 260
        self.y = config.HEIGHT//2 - self.h//2
        self.img = load_boss_image(BOSS_IMAGE, BOSS_SIZE)
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.hp = BOSS_MAX_HP
        self.projectiles = []
        self.obstacles = []
        self.timers = {"shoot":0, "ob":0}

    def update(self, player):
        # Movimiento: mezcla de sinusoidal y seguimiento suave (usa math.sin)
        t = pygame.time.get_ticks() / 800.0
        self.y = int(config.HEIGHT//2 + 80 * math.sin(t)) - self.h//2

        # seguimiento suave
        if player.y + player.h//2 > self.y + self.h//2 + 6:
            self.y += 0.6
        elif player.y + player.h//2 < self.y + self.h//2 - 6:
            self.y -= 0.6
        self.rect.topleft = (self.x, self.y)

        # Timers
        self.timers["shoot"] += 1
        self.timers["ob"] += 1

        if self.timers["shoot"] >= 60:
            self.shoot_pattern(player)
            self.timers["shoot"] = 0

        if self.timers["ob"] >= 200:
            ox = random.randint(200, config.WIDTH - 300)
            rect = pygame.Rect(ox, -40, 40, 40)
            rect.vy = random.randint(2,5)
            self.obstacles.append(rect)
            self.timers["ob"] = 0

        # Update projectiles and obstacles
        for p in self.projectiles:
            p.x += getattr(p, "vx", -6)
            p.y += getattr(p, "vy", 0)
        self.projectiles = [p for p in self.projectiles if -100 < p.x < config.WIDTH + 100 and -100 < p.y < config.HEIGHT + 100]

        for o in self.obstacles:
            o.y += getattr(o, "vy", 3)
        self.obstacles = [o for o in self.obstacles if o.y < config.HEIGHT + 80]

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))
        for p in self.projectiles:
            pygame.draw.rect(screen, (255, 100, 80), p)
        for o in self.obstacles:
            pygame.draw.rect(screen, (200, 160, 0), o)

    def shoot_pattern(self, player):
        # ejemplo: fan de 5 proyectiles con ligera orientación al jugador
        center_y = self.y + self.h//2
        angles = [-0.4, -0.2, 0, 0.2, 0.4]
        speed = 6
        for a in angles:
            rect = pygame.Rect(self.x, center_y, PROJECTILE_SIZE, PROJECTILE_SIZE)
            rect.vx = -speed * math.cos(a)
            rect.vy = speed * math.sin(a)
            self.projectiles.append(rect)

def draw_hp_bar(screen, x, y, hp, max_hp, color):
    pygame.draw.rect(screen, (60,60,60), (x, y, 260, 20))
    ratio = max(0, hp/max_hp)
    pygame.draw.rect(screen, color, (x, y, int(260*ratio), 20))

def run_boss(screen, clock):
    # música (opcional)
    try:
        if os.path.exists(BOSS_MUSIC):
            pygame.mixer.music.load(BOSS_MUSIC)
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)
    except Exception:
        pass

    player = Player()
    boss = Boss()
    running = True

    while running:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                try: pygame.mixer.music.stop()
                except: pass
                pygame.quit(); raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE:
                    player.shoot()

        player.update(keys)
        boss.update(player)

        # collisions: player shots -> boss
        for shot in list(player.shots):
            if boss.rect.colliderect(shot):
                boss.hp -= 10
                try: player.shots.remove(shot)
                except: pass

        # boss projectiles -> player
        for p in list(boss.projectiles):
            if player.rect.colliderect(p):
                player.hp -= 16
                try: boss.projectiles.remove(p)
                except: pass

        # obstacles -> player
        for o in list(boss.obstacles):
            if player.rect.colliderect(o):
                player.hp -= 18
                try: boss.obstacles.remove(o)
                except: pass

        if player.hp <= 0 or boss.hp <= 0:
            running = False

        screen.fill(config.C_BG)
        player.draw(screen)
        boss.draw(screen)
        draw_hp_bar(screen, 20, 20, player.hp, PLAYER_MAX_HP, (0,255,0))
        draw_hp_bar(screen, config.WIDTH-300, 20, boss.hp, BOSS_MAX_HP, (255,80,60))
        pygame.display.flip()

    try: pygame.mixer.music.stop()
    except: pass
