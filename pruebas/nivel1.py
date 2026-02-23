import pygame
import sys
import os
import math
import random

import config

# ------------------ CARGA DE RECURSOS ------------------

def load_skin():
    path = config.get_selected_skin_path()
    if path is None or not os.path.exists(path):
        return None
    try:
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, (config.PLAYER_SIZE, config.PLAYER_SIZE))
        return img
    except Exception:
        return None

def load_bg():
    # Usamos el mismo fondo que el menú
    if not os.path.exists(config.MENU_BACKGROUND):
        return None
    try:
        img = pygame.image.load(config.MENU_BACKGROUND).convert()
        img = pygame.transform.scale(img, (config.WIDTH, config.HEIGHT))
        return img
    except Exception:
        return None

skin_img = None
bg_image = None

# ------------------ CLASES ------------------

class ParallaxBackground:
    def __init__(self):
        self.use_image = bg_image is not None
        self.layers = [0, 0, 0]
        self.speeds = [1, 3, 5]

    def update(self, game_speed):
        for i in range(len(self.layers)):
            self.layers[i] -= game_speed * (self.speeds[i] * 0.1)
            limit = config.WIDTH if i == 0 else 200
            if self.layers[i] <= -limit:
                self.layers[i] += limit

    def draw(self, surface):
        if self.use_image:
            for i in range(2):
                x = int(self.layers[0] + i * config.WIDTH)
                surface.blit(bg_image, (x, 0))
        else:
            surface.fill(config.C_BG)

        for i, offset in enumerate(self.layers[1:], start=1):
            color = (20 + i*10, 20 + i*10, 40 + i*20)
            step = 120 - i*10
            for x in range(int(offset), config.WIDTH + step, step):
                pygame.draw.line(surface, color, (x, 0), (x, config.GROUND_Y), 2)
            for y in range(0, config.GROUND_Y, step):
                pygame.draw.line(surface, color, (0, y), (config.WIDTH, y), 2)

class Particle:
    def __init__(self, x, y, color, speed_mult=1.0):
        self.x, self.y = x, y
        self.vx = random.uniform(-4, 4) * speed_mult
        self.vy = random.uniform(-8, 2) * speed_mult
        self.life = random.randint(20, 50)
        self.max_life = self.life
        self.color = color
        self.size = random.randint(3, 7)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.4
        self.life -= 1

    def draw(self, surface):
        alpha = max(0, int(255 * (self.life / self.max_life)))
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        s.fill((*self.color, alpha))
        surface.blit(s, (self.x, self.y))

class Player:
    def __init__(self):
        self.rect = pygame.Rect(150, config.GROUND_Y - config.PLAYER_SIZE,
                                config.PLAYER_SIZE, config.PLAYER_SIZE)
        self.vel_y = 0
        self.rotation = 0
        self.gravity_dir = 1
        self.alive = True
        self.trail = []
        self.can_orb_jump = False
        self.current_orb = None

    def update(self):
        if not self.alive:
            return

        self.vel_y += config.GRAVITY * self.gravity_dir
        self.rect.y += self.vel_y

        if self.gravity_dir == 1 and self.rect.bottom >= config.GROUND_Y:
            self.rect.bottom = config.GROUND_Y
            self.vel_y = 0
            self.rotation = round(self.rotation / 90) * 90
        elif self.gravity_dir == -1 and self.rect.top <= 0:
            self.rect.top = 0
            self.vel_y = 0
            self.rotation = round(self.rotation / 90) * 90

        if self.vel_y != 0:
            self.rotation -= 6 * self.gravity_dir

        self.trail.append(self.rect.center)
        if len(self.trail) > 12:
            self.trail.pop(0)

    def jump(self):
        if self.can_orb_jump and self.current_orb:
            self.vel_y = config.JUMP_FORCE * 1.1 * self.gravity_dir
            self.current_orb.activate()
            self.can_orb_jump = False
            return True

        if self.gravity_dir == 1 and self.rect.bottom >= config.GROUND_Y:
            self.vel_y = config.JUMP_FORCE
            return True
        elif self.gravity_dir == -1 and self.rect.top <= 0:
            self.vel_y = -config.JUMP_FORCE
            return True
        return False

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            alpha = int(120 * (i / len(self.trail)))
            size = config.PLAYER_SIZE - (len(self.trail) - i) * 1.5
            s = pygame.Surface((size, size), pygame.SRCALPHA)
            s.fill((0, 255, 200, alpha))
            surface.blit(s, s.get_rect(center=pos))

        if skin_img:
            rotated = pygame.transform.rotate(skin_img, self.rotation)
        else:
            cube = pygame.Surface((config.PLAYER_SIZE, config.PLAYER_SIZE), pygame.SRCALPHA)
            cube.fill(config.C_LINE)
            pygame.draw.rect(cube, config.C_TEXT, cube.get_rect(), 3)
            rotated = pygame.transform.rotate(cube, self.rotation)

        surface.blit(rotated, rotated.get_rect(center=self.rect.center))

class GameObject:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.passed = False

    def update(self, speed):
        self.rect.x -= speed

    def draw(self, surface):
        pass

class Spike(GameObject):
    def __init__(self, x, y_offset=0, inverted=False):
        super().__init__(x, config.GROUND_Y - 40 - y_offset, 40, 40)
        self.inverted = inverted
        if inverted:
            self.rect.y = y_offset

    def draw(self, surface):
        if self.inverted:
            pts = [
                (self.rect.left, self.rect.top),
                (self.rect.centerx, self.rect.bottom),
                (self.rect.right, self.rect.top),
            ]
        else:
            pts = [
                (self.rect.left, self.rect.bottom),
                (self.rect.centerx, self.rect.top),
                (self.rect.right, self.rect.bottom),
            ]
        pygame.draw.polygon(surface, (255, 50, 50), pts)
        pygame.draw.polygon(surface, (255, 150, 150), pts, 2)

class Saw(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 60, 60)
        self.angle = 0

    def update(self, speed):
        super().update(speed)
        self.angle += 10

    def draw(self, surface):
        surf = pygame.Surface((70, 70), pygame.SRCALPHA)
        pygame.draw.circle(surf, (150, 150, 150), (35, 35), 30)
        pygame.draw.circle(surf, (50, 50, 50), (35, 35), 25)
        for i in range(10):
            ang = math.radians(self.angle + i * 36)
            end_x = 35 + math.cos(ang) * 35
            end_y = 35 + math.sin(ang) * 35
            pygame.draw.line(surf, (200, 200, 200), (35, 35), (end_x, end_y), 4)
        surface.blit(surf, surf.get_rect(center=self.rect.center))

class JumpOrb(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40)
        self.active = False
        self.scale = 1.0

    def activate(self):
        self.active = True
        self.scale = 1.5

    def update(self, speed):
        super().update(speed)
        if self.scale > 1.0:
            self.scale -= 0.05

    def draw(self, surface):
        size = int(30 * self.scale)
        pygame.draw.circle(surface, (255, 255, 0), self.rect.center, size)
        pygame.draw.circle(surface, (255, 255, 255), self.rect.center, size - 5, 3)

class Portal(GameObject):
    def __init__(self, x, type_portal):
        super().__init__(x, config.GROUND_Y - 120, 50, 120)
        self.type = type_portal
        self.used = False

    def draw(self, surface):
        color = (150, 0, 255) if self.type == "gravity" else (0, 200, 255)
        if self.used:
            color = (70, 70, 100)
        pygame.draw.ellipse(surface, color, self.rect, 5)

# ------------------ NIVEL ------------------
# Más largo, con secciones: intro, orbes, sierras, gravedad, final

LEVEL_MAP = [
    #   0         1         2         3         4         5         6
    #   0123456789012345678901234567890123456789012345678901234567890123
    "............................................................................",
    "............................O...............................................",
    "...................................*...................v...v...v...........",
    "............O.............................G.........................O......",
    ".......^..^......^^...^.........^....***......^....^...........G..........",
    ".......................O....................v.............*................",
]

def load_level(level_data):
    objects = []
    block_w = 60
    start_x = 800
    
    for row_idx, row in enumerate(level_data):
        y_pos = config.GROUND_Y - ((len(level_data) - row_idx) * block_w) + 20
        
        for col_idx, char in enumerate(row):
            x_pos = start_x + (col_idx * block_w)
            
            if char == '^':
                objects.append(Spike(x_pos))
            elif char == 'v':
                objects.append(Spike(x_pos, 0, True))
            elif char == '*':
                objects.append(Saw(x_pos, y_pos))
            elif char == 'O':
                objects.append(JumpOrb(x_pos, y_pos - 20))
            elif char == 'G':
                objects.append(Portal(x_pos, "gravity"))
            
    objects.append(GameObject(start_x + (len(LEVEL_MAP[0]) * block_w), 0, 10, config.HEIGHT)) 
    return objects

# ------------------ LOOP DEL NIVEL ------------------

def spawn_particles(particles, x, y, color, count=30, speed=1.0):
    for _ in range(count):
        particles.append(Particle(x, y, color, speed))

def run_level(screen, clock):
    global skin_img, bg_image
    skin_img = load_skin()
    bg_image = load_bg()

    font_title = pygame.font.SysFont("Arial Black", 60)
    font_ui = pygame.font.SysFont("Arial", 24)

    bg = ParallaxBackground()
    particles = []
    player = Player()
    objects = load_level(LEVEL_MAP)
    score = 0
    camera_shake = 0
    death_timer = 0
    state = "PLAY"   # PLAY, GAMEOVER, WIN, PAUSE

    # Música del nivel (independiente de la del menú)
    if os.path.exists(config.LEVEL_MUSIC):
        try:
            pygame.mixer.music.load(config.LEVEL_MUSIC)
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

    running = True
    while running:
        clock.tick(config.FPS)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if state == "PLAY":
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_SPACE, pygame.K_UP):
                        if player.jump():
                            spawn_particles(particles, player.rect.centerx,
                                            player.rect.bottom, (200, 200, 200), 5, 0.5)
                    if event.key == pygame.K_ESCAPE:
                        state = "PAUSE"
                        pygame.mixer.music.pause()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if player.jump():
                        spawn_particles(particles, player.rect.centerx,
                                        player.rect.bottom, (200, 200, 200), 5, 0.5)

            elif state == "PAUSE":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        state = "PLAY"
                        pygame.mixer.music.unpause()
                    if event.key == pygame.K_BACKSPACE:
                        running = False

            elif state in ("GAMEOVER", "WIN"):
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return run_level(screen, clock)
                    if event.key == pygame.K_ESCAPE:
                        running = False

        bg.update(config.SPEED if state == "PLAY" else 1)

        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)

        if state == "PLAY":
            if player.alive:
                player.update()
                player.can_orb_jump = False
                player.current_orb = None

                for obj in objects[:]:
                    obj.update(config.SPEED)

                    if (not obj.passed and obj.rect.right < player.rect.left
                            and not type(obj) is GameObject):
                        obj.passed = True
                        score += 10

                    if type(obj) is GameObject and player.rect.colliderect(obj.rect):
                        state = "WIN"
                        spawn_particles(particles, player.rect.centerx,
                                        player.rect.centery, (0, 255, 0), 100, 2.0)

                    hitbox = player.rect.inflate(-12, -12)

                    if isinstance(obj, (Spike, Saw)) and hitbox.colliderect(obj.rect):
                        player.alive = False
                        camera_shake = 25
                        death_timer = 90
                        spawn_particles(particles, player.rect.centerx,
                                        player.rect.centery, (255, 50, 50), 60, 2.0)
                        pygame.mixer.music.stop()

                    elif isinstance(obj, JumpOrb) and hitbox.colliderect(obj.rect.inflate(40, 40)):
                        player.can_orb_jump = True
                        player.current_orb = obj

                    elif isinstance(obj, Portal) and player.rect.colliderect(obj.rect):
                        if not obj.used:
                            if obj.type == "gravity":
                                player.gravity_dir *= -1
                            obj.used = True

                    if obj.rect.right < -200:
                        objects.remove(obj)

            else:
                if camera_shake > 0:
                    camera_shake -= 1
                death_timer -= 1
                if death_timer <= 0:
                    state = "GAMEOVER"

        ox = random.randint(-camera_shake, camera_shake) if camera_shake > 0 else 0
        oy = random.randint(-camera_shake, camera_shake) if camera_shake > 0 else 0

        temp_surf = pygame.Surface((config.WIDTH, config.HEIGHT))
        bg.draw(temp_surf)

        pygame.draw.rect(temp_surf, config.C_GROUND,
                         (0, config.GROUND_Y, config.WIDTH, config.HEIGHT - config.GROUND_Y))
        pygame.draw.line(temp_surf, config.C_LINE,
                         (0, config.GROUND_Y), (config.WIDTH, config.GROUND_Y), 3)

        for obj in objects:
            obj.draw(temp_surf)
        for p in particles:
            p.draw(temp_surf)
        if player.alive:
            player.draw(temp_surf)

        score_txt = font_ui.render(f"PUNTOS: {score}", True, config.C_TEXT)
        temp_surf.blit(score_txt, (20, 20))

        if state == "PAUSE":
            overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            temp_surf.blit(overlay, (0, 0))
            txt = font_title.render("PAUSA", True, config.C_TEXT)
            temp_surf.blit(txt, (config.WIDTH//2 - txt.get_width()//2, config.HEIGHT//2 - 60))
            txt2 = font_ui.render("ESC: continuar  |  BACKSPACE: salir al menú de niveles",
                                  True, config.C_TEXT)
            temp_surf.blit(txt2, (config.WIDTH//2 - txt2.get_width()//2, config.HEIGHT//2 + 10))

        if state == "GAMEOVER":
            overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            temp_surf.blit(overlay, (0, 0))
            txt = font_title.render("¡TE ESTRELLASTE!", True, (255, 50, 50))
            temp_surf.blit(txt, (config.WIDTH//2 - txt.get_width()//2, config.HEIGHT//2 - 60))
            txt2 = font_ui.render("ENTER: reintentar  |  ESC: volver al menú de niveles",
                                  True, config.C_TEXT)
            temp_surf.blit(txt2, (config.WIDTH//2 - txt2.get_width()//2, config.HEIGHT//2 + 10))

        if state == "WIN":
            overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            temp_surf.blit(overlay, (0, 0))
            txt = font_title.render("¡NIVEL COMPLETADO!", True, (50, 255, 50))
            temp_surf.blit(txt, (config.WIDTH//2 - txt.get_width()//2, config.HEIGHT//2 - 60))
            txt2 = font_ui.render("ENTER: volver a jugar  |  ESC: volver al menú de niveles",
                                  True, config.C_TEXT)
            temp_surf.blit(txt2, (config.WIDTH//2 - txt2.get_width()//2, config.HEIGHT//2 + 10))

        screen.blit(temp_surf, (ox, oy))
        pygame.display.flip()

    # Al salir del nivel, restaurar música de menú
    if os.path.exists(config.MENU_MUSIC):
        try:
            pygame.mixer.music.load(config.MENU_MUSIC)
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)
        except Exception:
            pass


