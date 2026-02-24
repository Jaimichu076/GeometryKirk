# player.py
import pygame
import config
import os

PLAYER_SIZE = 64
PLAYER_SPEED = 7
PLAYER_SHOT_SPEED = 14
PLAYER_MAX_HP = 180
SHOT_COOLDOWN = 12
PROJECTILE_SIZE = 12

def load_player_skin(size=PLAYER_SIZE):
    path = config.get_selected_skin_path()
    if not path:
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        surf.fill((180, 180, 180))
        return surf
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (size, size))
    except Exception:
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        surf.fill((180, 180, 180))
        return surf

class Player:
    def __init__(self, x=120, y=None):
        self.w = PLAYER_SIZE
        self.h = PLAYER_SIZE
        self.x = x
        self.y = y if y is not None else config.HEIGHT//2 - self.h//2
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.img = load_player_skin(self.w)
        self.hp = PLAYER_MAX_HP
        self.shots = []
        self.cooldown = 0

    def update(self, keys):
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.y -= PLAYER_SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.y += PLAYER_SPEED
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x -= PLAYER_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x += PLAYER_SPEED

        # Clamp to screen
        self.x = max(0, min(config.WIDTH - self.w, self.x))
        self.y = max(0, min(config.HEIGHT - self.h, self.y))
        self.rect.topleft = (self.x, self.y)

        # Update shots
        for s in self.shots:
            s.x += PLAYER_SHOT_SPEED
        self.shots = [s for s in self.shots if s.x < config.WIDTH + 50]

        if self.cooldown > 0:
            self.cooldown -= 1

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))
        for s in self.shots:
            pygame.draw.rect(screen, (0, 220, 140), s)

    def shoot(self):
        if self.cooldown == 0:
            rx = self.x + self.w
            ry = self.y + self.h//2 - PROJECTILE_SIZE//2
            rect = pygame.Rect(rx, ry, PROJECTILE_SIZE, PROJECTILE_SIZE)
            self.shots.append(rect)
            self.cooldown = SHOT_COOLDOWN

