# player.py
import pygame
import config
import os
import math

# Constantes del jugador y armas
PLAYER_SIZE = config.PLAYER_SIZE if hasattr(config, "PLAYER_SIZE") else 64
PLAYER_SPEED = 7
PLAYER_MAX_HP = 180

# Pistola
PISTOL_COOLDOWN = 10
PISTOL_SPEED = 14
PISTOL_DAMAGE = 10
PISTOL_SIZE = 12

# Escopeta
SHOTGUN_COOLDOWN = 22
SHOTGUN_PELLETS = 7
SHOTGUN_SPREAD = 0.6
SHOTGUN_PELLET_SPEED = 12
SHOTGUN_BASE_DAMAGE = 6

# Lanzacohetes
ROCKET_COOLDOWN_SEC = 9.0
ROCKET_SPEED = 9
ROCKET_DAMAGE = 80
ROCKET_SIZE = 18

# HUD
SLOT_SIZE = 48

def load_image(path, size=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        return img
    except Exception:
        return None

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

        # Disparos: lista de dicts {"rect","vx","vy","life","damage","kind","img"}
        self.shots = []

        # Estado de armas
        self.weapon = "pistol"   # "pistol","shotgun","rocket"
        self.cooldowns = {"pistol":0, "shotgun":0}
        self.rocket_last_time = -999999

        # Cargar imágenes de proyectiles e iconos desde config
        self.proj_imgs = {
            "pistol": load_image(config.PROJ_PISTOL, (PISTOL_SIZE, PISTOL_SIZE)),
            "shotgun": load_image(config.PROJ_SHOTGUN, (PISTOL_SIZE, PISTOL_SIZE)),
            "rocket": load_image(config.PROJ_ROCKET, (ROCKET_SIZE, ROCKET_SIZE))
        }
        self.icons = {
            "pistol": load_image(config.ICON_PISTOL, (SLOT_SIZE, SLOT_SIZE)),
            "shotgun": load_image(config.ICON_SHOTGUN, (SLOT_SIZE, SLOT_SIZE)),
            "rocket": load_image(config.ICON_ROCKET, (SLOT_SIZE, SLOT_SIZE))
        }

        # Tutorial: armas desbloqueadas
        self.allowed_weapons = {"pistol": True, "shotgun": False, "rocket": False}

    def update(self, keys):
        # Movimiento
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.y -= PLAYER_SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.y += PLAYER_SPEED
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x -= PLAYER_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x += PLAYER_SPEED

        # Cambio de arma con 1/2/3 (solo si desbloqueada)
        if keys[pygame.K_1]:
            if self.allowed_weapons.get("pistol", True):
                self.weapon = "pistol"
        if keys[pygame.K_2]:
            if self.allowed_weapons.get("shotgun", False):
                self.weapon = "shotgun"
        if keys[pygame.K_3]:
            if self.allowed_weapons.get("rocket", False):
                self.weapon = "rocket"

        # Limitar a pantalla
        self.x = max(0, min(config.WIDTH - self.w, self.x))
        self.y = max(0, min(config.HEIGHT - self.h, self.y))
        self.rect.topleft = (self.x, self.y)

        # Actualizar disparos
        new_shots = []
        for s in self.shots:
            s["rect"].x += int(s["vx"])
            s["rect"].y += int(s["vy"])
            s["life"] -= 1
            if s["life"] > 0 and -200 < s["rect"].x < config.WIDTH + 200 and -200 < s["rect"].y < config.HEIGHT + 200:
                new_shots.append(s)
        self.shots = new_shots

        # Cooldowns
        for k in list(self.cooldowns.keys()):
            if self.cooldowns[k] > 0:
                self.cooldowns[k] -= 1

    def draw(self, screen):
        # Jugador
        screen.blit(self.img, (self.x, self.y))

        # Dibujar proyectiles (con imagen si existe)
        for s in self.shots:
            if s.get("img"):
                try:
                    screen.blit(s["img"], s["rect"])
                except:
                    pygame.draw.rect(screen, (0,220,140), s["rect"])
            else:
                pygame.draw.rect(screen, (0,220,140), s["rect"])

        # HUD inventario (esquina inferior izquierda)
        hud_x = 20
        hud_y = config.HEIGHT - 20 - SLOT_SIZE
        slot_gap = 12
        weapons_order = ["pistol","shotgun","rocket"]
        font = pygame.font.SysFont("Arial", 18)
        for i, w in enumerate(weapons_order):
            sx = hud_x + i * (SLOT_SIZE + slot_gap)
            srect = pygame.Rect(sx, hud_y, SLOT_SIZE, SLOT_SIZE)
            pygame.draw.rect(screen, (30,30,40), srect, border_radius=6)
            pygame.draw.rect(screen, (200,200,200), srect, 2, border_radius=6)
            icon = self.icons.get(w)
            if icon:
                screen.blit(icon, (sx + (SLOT_SIZE - icon.get_width())//2, hud_y + (SLOT_SIZE - icon.get_height())//2))
            else:
                pygame.draw.rect(screen, (120,120,120), (sx+8, hud_y+8, SLOT_SIZE-16, SLOT_SIZE-16))
            num_surf = font.render(str(i+1), True, config.C_TEXT)
            screen.blit(num_surf, (sx + 6, hud_y + 6))
            if self.weapon == w:
                pygame.draw.rect(screen, (0,255,0), srect.inflate(6,6), 3, border_radius=8)
            if not self.allowed_weapons.get(w, False):
                overlay = pygame.Surface((SLOT_SIZE, SLOT_SIZE), pygame.SRCALPHA)
                overlay.fill((0,0,0,160))
                screen.blit(overlay, (sx, hud_y))

    def shoot(self, target_rect=None):
        # Pistola
        if self.weapon == "pistol":
            if self.cooldowns["pistol"] == 0:
                rx = self.x + self.w
                ry = self.y + self.h//2 - PISTOL_SIZE//2
                rect = pygame.Rect(rx, ry, PISTOL_SIZE, PISTOL_SIZE)
                vx = PISTOL_SPEED
                vy = 0
                img = self.proj_imgs.get("pistol")
                self.shots.append({"rect":rect,"vx":vx,"vy":vy,"life":120,"damage":PISTOL_DAMAGE,"kind":"pistol","img":img})
                self.cooldowns["pistol"] = PISTOL_COOLDOWN

        # Escopeta
        elif self.weapon == "shotgun":
            if self.cooldowns["shotgun"] == 0:
                sx = self.x + self.w
                sy = self.y + self.h//2
                for i in range(SHOTGUN_PELLETS):
                    t = i / max(1, SHOTGUN_PELLETS-1)
                    angle = -SHOTGUN_SPREAD/2 + t * SHOTGUN_SPREAD
                    vx = SHOTGUN_PELLET_SPEED * math.cos(angle)
                    vy = SHOTGUN_PELLET_SPEED * math.sin(angle)
                    rect = pygame.Rect(int(sx), int(sy - 6), PISTOL_SIZE, PISTOL_SIZE)
                    img = self.proj_imgs.get("shotgun")
                    damage = SHOTGUN_BASE_DAMAGE
                    if target_rect:
                        dx = (target_rect.x + target_rect.w//2) - (self.x + self.w//2)
                        dy = (target_rect.y + target_rect.h//2) - (self.y + self.h//2)
                        dist = math.hypot(dx, dy)
                        factor = max(0.6, 1.6 - (dist / 400.0))
                        damage = int(damage * factor)
                    self.shots.append({"rect":rect,"vx":vx,"vy":vy,"life":80,"damage":damage,"kind":"shotgun","img":img})
                self.cooldowns["shotgun"] = SHOTGUN_COOLDOWN

        # Lanzacohetes
        elif self.weapon == "rocket":
            elapsed = (pygame.time.get_ticks() - self.rocket_last_time) / 1000.0
            if elapsed >= ROCKET_COOLDOWN_SEC:
                rx = self.x + self.w
                ry = self.y + self.h//2 - ROCKET_SIZE//2
                rect = pygame.Rect(rx, ry, ROCKET_SIZE, ROCKET_SIZE)
                vx = ROCKET_SPEED
                vy = 0
                img = self.proj_imgs.get("rocket")
                self.shots.append({"rect":rect,"vx":vx,"vy":vy,"life":200,"damage":ROCKET_DAMAGE,"kind":"rocket","img":img})
                self.rocket_last_time = pygame.time.get_ticks()

    def unlock_weapon(self, name):
        if name in self.allowed_weapons:
            self.allowed_weapons[name] = True
