import pygame
import sys
import os
import math
import random

# ==========================================
# CONFIGURACIÓN Y CONSTANTES
# ==========================================
WIDTH, HEIGHT = 1100, 600
GROUND_Y = HEIGHT - 100
FPS = 60

# Físicas
PLAYER_SIZE = 50
GRAVITY = 0.8
JUMP_FORCE = -14.5
SPEED = 8.5

# Colores
C_BG = (15, 15, 30)
C_GROUND = (25, 25, 50)
C_LINE = (0, 255, 200)
C_TEXT = (255, 255, 255)
C_BTN_IDLE = (40, 40, 80)
C_BTN_HOVER = (60, 60, 120)

# Rutas de assets
SKIN_PATH = os.path.join("assets", "images", "Epstein.jpg")
MUSIC_PATH = os.path.join("assets", "audio", "wearecharliekirk.mp3")

# AQUÍ PONES TU FONDO PERSONALIZADO
# Ejemplo: "mi_fondo.jpg" dentro de assets/images
BG_IMAGE_PATH = os.path.join("assets", "images", "mi_fondo.jpg")

# ==========================================
# INICIALIZACIÓN DE PYGAME
# ==========================================
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GEOMETRY DASH ULTRA - PRO EDITION")
clock = pygame.time.Clock()

font_title = pygame.font.SysFont("Arial Black", 80)
font_btn = pygame.font.SysFont("Arial Black", 40)
font_ui = pygame.font.SysFont("Arial", 25)

# Cargar skin
skin_img = None
if os.path.exists(SKIN_PATH):
    try:
        skin_img = pygame.image.load(SKIN_PATH).convert_alpha()
        skin_img = pygame.transform.scale(skin_img, (PLAYER_SIZE, PLAYER_SIZE))
    except Exception as e:
        print(f"Error cargando skin: {e}")

# Cargar música
if os.path.exists(MUSIC_PATH):
    try:
        pygame.mixer.music.load(MUSIC_PATH)
        pygame.mixer.music.set_volume(0.5)
    except Exception as e:
        print(f"Error cargando música: {e}")

# Cargar fondo personalizado
bg_image = None
if os.path.exists(BG_IMAGE_PATH):
    try:
        bg_image = pygame.image.load(BG_IMAGE_PATH).convert()
        bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
    except Exception as e:
        print(f"Error cargando fondo: {e}")
        bg_image = None

# ==========================================
# CLASES DE INTERFAZ Y SISTEMA
# ==========================================
class Button:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_hovered = False

    def draw(self, surface):
        color = C_BTN_HOVER if self.is_hovered else C_BTN_IDLE
        pygame.draw.rect(surface, color, self.rect, border_radius=15)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 3, border_radius=15)
        
        txt_surf = font_btn.render(self.text, True, C_TEXT)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            return self.action
        return None

class ParallaxBackground:
    def __init__(self):
        # Si hay imagen, la usamos como capa base
        self.use_image = bg_image is not None
        self.layers = [0, 0, 0]
        self.speeds = [1, 3, 5]

    def update(self, game_speed):
        for i in range(len(self.layers)):
            self.layers[i] -= game_speed * (self.speeds[i] * 0.1)
            if self.layers[i] <= -WIDTH:
                self.layers[i] += WIDTH

    def draw(self, surface):
        if self.use_image:
            # Fondo que se desplaza ligeramente para dar sensación de movimiento
            for i in range(2):
                x = int(self.layers[0] + i * WIDTH)
                surface.blit(bg_image, (x, 0))
        else:
            surface.fill(C_BG)

        # Capas extra de líneas para dar profundidad aunque haya imagen
        for i, offset in enumerate(self.layers[1:], start=1):
            color = (20 + i*10, 20 + i*10, 40 + i*20)
            step = 120 - i*10
            for x in range(int(offset), WIDTH + step, step):
                pygame.draw.line(surface, color, (x, 0), (x, GROUND_Y), 2)
            for y in range(0, GROUND_Y, step):
                pygame.draw.line(surface, color, (0, y), (WIDTH, y), 2)

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

# ==========================================
# ENTIDADES DEL JUEGO
# ==========================================
class Player:
    def __init__(self):
        self.rect = pygame.Rect(150, GROUND_Y - PLAYER_SIZE, PLAYER_SIZE, PLAYER_SIZE)
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

        self.vel_y += GRAVITY * self.gravity_dir
        self.rect.y += self.vel_y

        # Suelo / Techo
        if self.gravity_dir == 1 and self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
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
            self.vel_y = JUMP_FORCE * 1.1 * self.gravity_dir
            self.current_orb.activate()
            self.can_orb_jump = False
            return True

        if self.gravity_dir == 1 and self.rect.bottom >= GROUND_Y:
            self.vel_y = JUMP_FORCE
            return True
        elif self.gravity_dir == -1 and self.rect.top <= 0:
            self.vel_y = -JUMP_FORCE
            return True
        return False

    def draw(self, surface):
        # Estela
        for i, pos in enumerate(self.trail):
            alpha = int(120 * (i / len(self.trail)))
            size = PLAYER_SIZE - (len(self.trail) - i) * 1.5
            s = pygame.Surface((size, size), pygame.SRCALPHA)
            s.fill((0, 255, 200, alpha))
            surface.blit(s, s.get_rect(center=pos))

        # Cubo / Skin
        if skin_img:
            rotated = pygame.transform.rotate(skin_img, self.rotation)
        else:
            cube = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
            cube.fill(C_LINE)
            pygame.draw.rect(cube, C_TEXT, cube.get_rect(), 3)
            rotated = pygame.transform.rotate(cube, self.rotation)

        surface.blit(rotated, rotated.get_rect(center=self.rect.center))

# --- OBSTÁCULOS ---
class GameObject:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.passed = False

    def update(self, speed):
        self.rect.x -= speed

    def draw(self, surface):
        pass

class Spike(GameObject):
    def __init__(self, x, y_offset=0, inverted=False):
        super().__init__(x, GROUND_Y - 40 - y_offset, 40, 40)
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
        for i in range(8):
            ang = math.radians(self.angle + i * 45)
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
        super().__init__(x, GROUND_Y - 120, 50, 120)
        self.type = type_portal
        self.used = False

    def draw(self, surface):
        color = (150, 0, 255) if self.type == "gravity" else (0, 200, 255)
        if self.used:
            color = (70, 70, 100)
        pygame.draw.ellipse(surface, color, self.rect, 5)

# ==========================================
# PARSEADOR DE NIVELES
# ==========================================
LEVEL_MAP = [
    "....................................................................",
    "............................O.......................................",
    "...................................*...................v...v...v....",
    "............O.............................G.........................",
    ".......^..........^...^.........^.............^....^................",
]

def load_level(level_data):
    objects = []
    block_w = 60
    start_x = 800
    
    for row_idx, row in enumerate(level_data):
        y_pos = GROUND_Y - ((len(level_data) - row_idx) * block_w) + 20
        
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
            
    # Bloque final invisible para ganar
    objects.append(GameObject(start_x + (len(LEVEL_MAP[0]) * block_w), 0, 10, HEIGHT)) 
    return objects

# ==========================================
# MOTOR PRINCIPAL DEL JUEGO
# ==========================================
class GameManager:
    def __init__(self):
        self.state = "MENU"  # MENU, PLAY, GAMEOVER, PAUSE, WIN
        self.bg = ParallaxBackground()
        self.particles = []
        
        # Botones del Menú
        btn_w, btn_h = 300, 80
        center_x = WIDTH // 2 - btn_w // 2
        self.btn_play = Button(center_x, 250, btn_w, btn_h, "JUGAR", "PLAY")
        self.btn_quit = Button(center_x, 360, btn_w, btn_h, "SALIR", "QUIT")
        
        # Variables de Juego
        self.player = None
        self.objects = []
        self.score = 0
        self.camera_shake = 0
        self.death_timer = 0
        
    def reset_game(self):
        self.player = Player()
        self.objects = load_level(LEVEL_MAP)
        self.particles.clear()
        self.score = 0
        self.camera_shake = 0
        if not pygame.mixer.music.get_busy() and os.path.exists(MUSIC_PATH):
            pygame.mixer.music.play(-1)

    def spawn_particles(self, x, y, color, count=30, speed=1.0):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, speed))

    def run(self):
        while True:
            clock.tick(FPS)
            mouse_pos = pygame.mouse.get_pos()
            
            # --- EVENTOS ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if self.state == "MENU":
                    self.btn_play.check_hover(mouse_pos)
                    self.btn_quit.check_hover(mouse_pos)
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.btn_play.handle_click(mouse_pos) == "PLAY":
                            self.reset_game()
                            self.state = "PLAY"
                        elif self.btn_quit.handle_click(mouse_pos) == "QUIT":
                            pygame.quit()
                            sys.exit()
                            
                elif self.state == "PLAY":
                    if event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_SPACE, pygame.K_UP):
                            if self.player.jump():
                                self.spawn_particles(
                                    self.player.rect.centerx,
                                    self.player.rect.bottom,
                                    (200, 200, 200),
                                    5,
                                    0.5,
                                )
                        if event.key == pygame.K_ESCAPE:
                            self.state = "PAUSE"
                            pygame.mixer.music.pause()
                            
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.player.jump():
                            self.spawn_particles(
                                self.player.rect.centerx,
                                self.player.rect.bottom,
                                (200, 200, 200),
                                5,
                                0.5,
                            )

                elif self.state == "PAUSE":
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.state = "PLAY"
                        pygame.mixer.music.unpause()

            # --- LÓGICA ---
            self.bg.update(SPEED if self.state == "PLAY" else 1)
            
            for p in self.particles[:]:
                p.update()
                if p.life <= 0:
                    self.particles.remove(p)

            if self.state == "PLAY":
                if self.player.alive:
                    self.player.update()
                    self.player.can_orb_jump = False
                    self.player.current_orb = None

                    for obj in self.objects[:]:
                        obj.update(SPEED)
                        
                        # Score
                        if (
                            not obj.passed
                            and obj.rect.right < self.player.rect.left
                            and not type(obj) is GameObject
                        ):
                            obj.passed = True
                            self.score += 10
                            
                        # Fin de nivel
                        if type(obj) is GameObject and self.player.rect.colliderect(obj.rect):
                            self.state = "WIN"
                            self.spawn_particles(
                                self.player.rect.centerx,
                                self.player.rect.centery,
                                (0, 255, 0),
                                100,
                                2.0,
                            )

                        # Hitbox reducida
                        hitbox = self.player.rect.inflate(-12, -12)
                        
                        if isinstance(obj, (Spike, Saw)) and hitbox.colliderect(obj.rect):
                            self.player.alive = False
                            self.camera_shake = 25
                            self.death_timer = 90
                            self.spawn_particles(
                                self.player.rect.centerx,
                                self.player.rect.centery,
                                (255, 50, 50),
                                60,
                                2.0,
                            )
                            pygame.mixer.music.stop()

                        elif isinstance(obj, JumpOrb) and hitbox.colliderect(obj.rect.inflate(40, 40)):
                            self.player.can_orb_jump = True
                            self.player.current_orb = obj

                        elif isinstance(obj, Portal) and self.player.rect.colliderect(obj.rect):
                            if not obj.used:
                                if obj.type == "gravity":
                                    self.player.gravity_dir *= -1
                                obj.used = True

                        if obj.rect.right < -200:
                            self.objects.remove(obj)

                else:
                    if self.camera_shake > 0:
                        self.camera_shake -= 1
                    self.death_timer -= 1
                    if self.death_timer <= 0:
                        self.state = "GAMEOVER"

            # --- DIBUJADO ---
            ox = random.randint(-self.camera_shake, self.camera_shake) if self.camera_shake > 0 else 0
            oy = random.randint(-self.camera_shake, self.camera_shake) if self.camera_shake > 0 else 0
            
            temp_surf = pygame.Surface((WIDTH, HEIGHT))
            self.bg.draw(temp_surf)

            if self.state in ("PLAY", "GAMEOVER", "PAUSE", "WIN"):
                pygame.draw.rect(temp_surf, C_GROUND, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
                pygame.draw.line(temp_surf, C_LINE, (0, GROUND_Y), (WIDTH, GROUND_Y), 3)

                for obj in self.objects:
                    obj.draw(temp_surf)
                for p in self.particles:
                    p.draw(temp_surf)
                if self.player and self.player.alive:
                    self.player.draw(temp_surf)

                score_txt = font_ui.render(f"PUNTOS: {self.score}", True, C_TEXT)
                temp_surf.blit(score_txt, (20, 20))

            # Interfaces
            if self.state == "MENU":
                t = font_title.render("ULTRA DASH", True, C_TEXT)
                t_shadow = font_title.render("ULTRA DASH", True, (0, 0, 0))
                temp_surf.blit(t_shadow, (WIDTH//2 - t.get_width()//2 + 5, 85))
                temp_surf.blit(t, (WIDTH//2 - t.get_width()//2, 80))
                
                self.btn_play.draw(temp_surf)
                self.btn_quit.draw(temp_surf)

            elif self.state == "PAUSE":
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                temp_surf.blit(overlay, (0, 0))
                txt = font_title.render("PAUSA", True, C_TEXT)
                temp_surf.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 50))
                txt2 = font_ui.render("Presiona ESC para continuar", True, C_TEXT)
                temp_surf.blit(txt2, (WIDTH//2 - txt2.get_width()//2, HEIGHT//2 + 50))

            elif self.state == "GAMEOVER":
                txt = font_title.render("¡TE ESTRELLASTE!", True, (255, 50, 50))
                temp_surf.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 100))
                self.btn_play.rect.y = HEIGHT//2 + 50
                self.btn_play.text = "REINTENTAR"
                self.btn_play.check_hover(mouse_pos)
                if pygame.mouse.get_pressed()[0] and self.btn_play.handle_click(mouse_pos):
                    self.reset_game()
                    self.state = "PLAY"
                self.btn_play.draw(temp_surf)
                
            elif self.state == "WIN":
                txt = font_title.render("¡NIVEL COMPLETADO!", True, (50, 255, 50))
                temp_surf.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 100))
                self.btn_quit.rect.y = HEIGHT//2 + 50
                self.btn_quit.text = "MENÚ PRINCIPAL"
                self.btn_quit.check_hover(mouse_pos)
                if pygame.mouse.get_pressed()[0] and self.btn_quit.handle_click(mouse_pos):
                    self.state = "MENU"
                self.btn_quit.draw(temp_surf)

            screen.blit(temp_surf, (ox, oy))
            pygame.display.flip()

# ==========================================
# INICIO DE LA APLICACIÓN
# ==========================================
if __name__ == "__main__":
    game = GameManager()
    game.run()
