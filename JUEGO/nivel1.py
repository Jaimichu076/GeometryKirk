# nivel1.py
# Nivel 1 — versión inspirada en Stereo Madness (Geometry Dash)
# - Fondo estático
# - Nivel largo (objetivo ~100-120s)
# - Secciones: tierra (cube), transición por portal -> fase ship (avión), salida a cube
# - No hay plataformas marrones decorativas: todos los objetos son funcionales
# - Portal convierte a ship; otro portal vuelve a cube
# - Controles: clic izquierdo o ESPACIO para saltar; mantener = salto automático
# - En ship: mantener = subir, soltar = bajar (simula nave)
# - Barra de progreso en tiempo real; pantalla de muerte y victoria limpias
# - No hay objetos detrás de la pared final (clear zone)
# - Código comentado y organizado

import pygame
import sys
import os
import math
import random

import config
skin_img = None
bg_image = None
SPIKE_IMG = None
SAW_IMG = None

# Cargar imagen del suelo


# ------------------ RECURSOS ------------------

def load_skin():
    """Carga la skin seleccionada desde config (si existe)."""
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
    """Carga fondo estático para el nivel (wallpaper.jpg por defecto)."""
    bg_path = os.path.join(config.ASSETS_IMG, "wallpaper.jpg")
    if not os.path.exists(bg_path):
        return None
    try:
        img = pygame.image.load(bg_path).convert()
        img = pygame.transform.scale(img, (config.WIDTH, config.HEIGHT))
        return img
    except Exception:
        return None

skin_img = None
bg_image = None


# ------------------ CLASES DE OBJETOS ------------------

class Particle:
    """Partícula para efectos visuales (muerte/ganar)."""
    def __init__(self, x, y, color, speed_mult=1.0):
        self.x, self.y = x, y
        self.vx = random.uniform(-3, 3) * speed_mult
        self.vy = random.uniform(-6, -1) * speed_mult
        self.life = random.randint(30, 70)
        self.max_life = self.life
        self.color = color
        self.size = random.randint(3, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.25
        self.life -= 1

    def draw(self, surface):
        alpha = max(0, int(255 * (self.life / self.max_life)))
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        s.fill((*self.color, alpha))
        surface.blit(s, (self.x, self.y))

class Player:
    """
    Jugador principal.
    - mode: "cube" o "ship"
    - cube: física con gravedad y salto
    - ship: control vertical (mantener = subir)
    """
    def __init__(self, start_x):
        self.start_x = start_x
        self.rect = pygame.Rect(start_x, config.GROUND_Y - config.PLAYER_SIZE,
                                config.PLAYER_SIZE, config.PLAYER_SIZE)
        self.vel_y = 0.0
        self.rotation = 0.0
        self.gravity_dir = 1
        self.alive = True
        self.trail = []
        self.jump_held = False
        self.mode = "cube"
        self.ship_speed_y = 4.0
        self.on_platform = False


    def on_ground(self):
        return (
            self.mode == "cube"
            and (
                (self.gravity_dir == 1 and self.rect.bottom >= config.GROUND_Y)
                or (self.gravity_dir == -1 and self.rect.top <= 0)
                or self.on_platform
            )

        )
        

    def update(self):
        if not self.alive:
            return

        if self.mode == "cube":
            if self.jump_held and self.on_ground():
                self.jump()

            
            #auto-jump
            if not self.on_platform:
                self.vel_y += config.GRAVITY * self.gravity_dir
                self.rect.y += self.vel_y

            else:
                self.vel_y = 0

            if self.gravity_dir == 1 and self.rect.bottom >=config.GROUND_Y:
                self.rect.bottom = config.GROUND_Y
                self.vel_y = 0
                self.rotacion = round(self.rotation / 90) * 90
            
            elif self.gravity_dir == -1 and self.rect.top <= 0:
                self.rect.top = 0
                self.vel_y = 0
                self.rotacion = round(self.rotacion / 90) * 90

            if self.vel_y != 0:
                self.rotation -= 6 * self.gravity_dir

            



        elif self.mode == "ship":
            # ship vertical control: hold -> up, release -> down
            if self.jump_held:
                self.rect.y -= self.ship_speed_y
            else:
                self.rect.y += self.ship_speed_y
            # clamp inside screen (ship limited to play area)
            if self.rect.top < 0:
                self.rect.top = 0
            if self.rect.bottom > config.GROUND_Y:
                self.rect.bottom = config.GROUND_Y

        # trail visual
        self.trail.append(self.rect.center)
        if len(self.trail) > 12:
            self.trail.pop(0)

    def jump(self):
        """Salto en modo cube."""
        if self.mode == "cube":
            if self.gravity_dir == 1 and (self.rect.bottom >= config.GROUND_Y or self.on_platform):

                self.vel_y = config.JUMP_FORCE
                return True
            elif self.gravity_dir == -1 and self.rect.top <= 0:
                self.vel_y = -config.JUMP_FORCE
                return True
        return False

    def draw(self, surface):
        # trail
        for i, pos in enumerate(self.trail):
            alpha = int(120 * (i / len(self.trail)))
            size = config.PLAYER_SIZE - (len(self.trail) - i) * 1.5
            s = pygame.Surface((size, size), pygame.SRCALPHA)
            s.fill((0, 255, 200, alpha))
            surface.blit(s, s.get_rect(center=pos))

        # sprite o cubo
        if skin_img:
            rotated = pygame.transform.rotate(skin_img, self.rotation)
        else:
            cube = pygame.Surface((config.PLAYER_SIZE, config.PLAYER_SIZE), pygame.SRCALPHA)
            if self.mode == "cube":
                cube.fill(config.C_LINE)
            else:
                cube.fill((80, 200, 255))  # color distinto para ship
            pygame.draw.rect(cube, config.C_TEXT, cube.get_rect(), 3)
            rotated = pygame.transform.rotate(cube, self.rotation)
        surface.blit(rotated, rotated.get_rect(center=self.rect.center))

class GameObject:
    """Objeto genérico (end, portal, jump pad, etc.)."""
    def __init__(self, x, y, w, h, kind="generic"):
        self.rect = pygame.Rect(x, y, w, h)
        self.kind = kind
        self.passed = False
        # movimiento opcional
        self.move_axis = None
        self.move_range = 0
        self.move_origin = (self.rect.x, self.rect.y)
        self.move_speed = 0.002 * random.uniform(0.8, 1.2)

    def update(self, speed):
        # scroll del mundo
        self.rect.x -= speed
        # movimiento oscilante si aplica
        if self.move_axis == 'y':
            offset = math.sin(pygame.time.get_ticks() * self.move_speed + self.rect.x * 0.01) * self.move_range
            self.rect.y = int(self.move_origin[1] + offset)
        elif self.move_axis == 'x':
            offset = math.sin(pygame.time.get_ticks() * self.move_speed + self.rect.y * 0.01) * self.move_range
            self.rect.x = int(self.move_origin[0] + offset) - speed

    def draw(self, surface):
        if self.kind == "end":
            pygame.draw.rect(surface, (0, 200, 0), self.rect)
            pygame.draw.rect(surface, (0, 0, 0), self.rect, 3)
        elif self.kind == "jump_pad":
            pygame.draw.rect(surface, (0, 180, 255), self.rect, border_radius=6)
            pygame.draw.rect(surface, (0, 0, 0), self.rect, 2, border_radius=6)
            cx, cy = self.rect.center
            pygame.draw.polygon(surface, (255, 255, 255), [(cx-6, cy+6), (cx+6, cy+6), (cx, cy-6)])
        elif self.kind == "portal":
            color = (200, 80, 255)
            pygame.draw.ellipse(surface, color, self.rect, 5)
        else:
            # genérico (bloque utilitario)
            pygame.draw.rect(surface, (120, 120, 120), self.rect)
            pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)

class Spike(GameObject):
    """Pico que mata al tocarlo."""
    def __init__(self, x, y_offset=0, inverted=False):
        y = config.GROUND_Y - 40 - y_offset if not inverted else y_offset
        super().__init__(x, y, 40, 40, kind="spike")
        self.inverted = inverted

    def draw(self, surface):
        if self.inverted:
            img = pygame.transform.flip(SPIKE_IMG, False, True)
        else:
            img = SPIKE_IMG
        surface.blit(img, self.rect)

class Saw(GameObject):
    """Sierra giratoria fija."""
    def __init__(self, x, y):
        super().__init__(x, y, 60, 60, kind="saw")
        self.angle = random.randint(0, 360)

    def update(self, speed):
        super().update(speed)
        self.angle += 12

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

class MovingSaw(GameObject):
    """Sierra que se mueve verticalmente (peligrosa)."""
    def __init__(self, x, y, range_y=80):
        super().__init__(x, y, 60, 60, kind="movingsaw")
        self.angle = 0
        self.move_range = range_y
        self.move_origin = (self.rect.x, self.rect.y)

        

    def update(self, speed):
        super().update(speed)
        self.angle += 14  # velocidad de giro

        # movimiento predecible
        t = pygame.time.get_ticks() / 300
        offset = math.sin(t) * self.move_range

        self.rect.y = self.move_origin[1] + offset

    def draw(self, surface):
        rotated = pygame.transform.rotate(SAW_IMG, self.angle)
        rect = rotated.get_rect(center=self.rect.center)
        surface.blit(rotated, rect)


class JumpPad(GameObject):
    """Pad que impulsa al jugador hacia arriba (útil)."""
    def __init__(self, x, y, power=1.4):
        super().__init__(x, y, 40, 20, kind="jump_pad")
        self.power = power

    def draw(self, surface):
        pygame.draw.rect(surface, (0, 180, 255), self.rect, border_radius=6)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2, border_radius=6)
        cx, cy = self.rect.center
        pygame.draw.polygon(surface, (255, 255, 255), [(cx-6, cy+6), (cx+6, cy+6), (cx, cy-6)])

class Portal(GameObject):
    """Portal que cambia el modo (cube <-> ship)."""
    def __init__(self, x, y):
        super().__init__(x, y, 50, 120, kind="portal")
        self.used = False

    def draw(self, surface):
        color = (200, 80, 255) if not self.used else (70, 70, 100)
        pygame.draw.ellipse(surface, color, self.rect, 5)

class Platform(GameObject):
    """Plataforma sólida donde el jugador puede subirse."""
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h, kind="platform")

    def draw(self, surface):
        pygame.draw.rect(surface, (180, 180, 180), self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)


# ------------------ GENERACIÓN DEL NIVEL (LARGO + FASE SHIP) ------------------

def generate_level():
    """
    Genera un nivel largo con varias secciones y una fase 'ship'.
    - Objetivo: duración entre 100 y 130 segundos.
    - end_x colocado de forma que no haya objetos detrás de la pared final.
    - No se generan plataformas marrones decorativas; todo es funcional.
    """

    objects = []

    objects.append(MovingSaw(800, config.GROUND_Y - 80))
    objects.append(MovingSaw(1100, config.GROUND_Y - 80))
    objects.append(Spike(1600, config.GROUND_Y -500))
    objects.append(Spike(1650, config.GROUND_Y -500))
    objects.append(Spike(1800, config.GROUND_Y -500))
    objects.append(Spike(1850, config.GROUND_Y -500))
    objects.append(Platform(2400, config.GROUND_Y - 30, 200, 40))
    objects.append(Spike(2600, config.GROUND_Y -500))
    objects.append(Spike(2650, config.GROUND_Y -500))
    objects.append(Spike(2700, config.GROUND_Y -500))
    objects.append(Platform(2800, config.GROUND_Y - 30, 200, 40))

    




    

    
    x = 900
    margin_final = 700
    end_x = 15000
    max_x = end_x - margin_final

    
    objects.append(GameObject(end_x, 0, 10, config.HEIGHT, kind="end"))

    total_distance_real = end_x - 150
    return objects, end_x, total_distance_real

# ------------------ UTILIDADES ------------------

def spawn_particles(particles, x, y, color, count=30, speed=1.0):
    for _ in range(count):
        particles.append(Particle(x + random.uniform(-12, 12), y + random.uniform(-12, 12), color, speed))



# ------------------ BUCLE PRINCIPAL DEL NIVEL ------------------

def run_level(screen, clock):
    """
    Bucle principal del nivel:
    - Maneja entrada (espacio/clic y mantener)
    - Cambia entre modos cube/ship con portals
    - Actualiza progreso y muestra barra superior
    - Muestra pantallas de muerte y victoria
    """
    global skin_img, bg_image, SPIKE_IMG, SAW_IMG
    skin_img = load_skin()
    bg_image = load_bg()


    # Fuentes
    font_title = pygame.font.SysFont("Arial Black", 60)
    font_ui = pygame.font.SysFont("Arial", 24)
    font_pct = pygame.font.SysFont("Arial Black", 28)

    bg_static = bg_image  # fondo estático
    # Cargar imagen del spike (correcto)
    SPIKE_IMG = pygame.image.load("Juego/assets/images/obunga.png").convert_alpha()
    SPIKE_IMG = pygame.transform.scale(SPIKE_IMG, (70, 70))
    # Cargar imagen del suelo (correcto)
    GROUND_IMG = pygame.image.load("Juego/assets/images/suelo.png").convert_alpha()
    GROUND_IMG = pygame.transform.scale(
        GROUND_IMG,
        (config.WIDTH, config.HEIGHT - config.GROUND_Y)
    )
    # cargar imagen del suelo
    SAW_IMG = pygame.image.load("Juego/assets/images/israel.png").convert_alpha()
    SAW_IMG = pygame.transform.scale(SAW_IMG, (70, 70))

    

    particles = []
    player = Player(start_x=150)
    objects, end_x, total_distance = generate_level()

    distance_traveled = 0.0
    progress = 0

    camera_shake = 0
    death_timer = 0
    state = "PLAY"   # PLAY, GAMEOVER, WIN, PAUSE

    # reproducir música del nivel
    if os.path.exists(config.LEVEL_MUSIC):
        try:
            pygame.mixer.music.load(config.LEVEL_MUSIC)
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)
        except:
            pass

    running = True
    while running:
        dt = clock.tick(config.FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        # ------------------ EVENTOS ------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if state == "PLAY":
                # teclado
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_SPACE, pygame.K_UP):
                        player.jump_held = True
                        if player.mode == "cube":
                            player.jump()
                    if event.key == pygame.K_ESCAPE:
                        state = "PAUSE"
                        pygame.mixer.music.pause()

                if event.type == pygame.KEYUP:
                    if event.key in (pygame.K_SPACE, pygame.K_UP):
                        player.jump_held = False

                # ratón
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    player.jump_held = True
                    if player.mode == "cube":
                        player.jump()
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    player.jump_held = False

            elif state == "PAUSE":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        state = "PLAY"
                        pygame.mixer.music.unpause()
                    if event.key == pygame.K_BACKSPACE:
                        running = False

            elif state == "GAMEOVER":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return run_level(screen, clock)
                    if event.key == pygame.K_ESCAPE:
                        running = False

            elif state == "WIN":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return run_level(screen, clock)
                    if event.key == pygame.K_ESCAPE:
                        running = False

        # ------------------ UPDATE ------------------
        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)

        if state == "PLAY":
            if player.alive:
                player.update()
                # colisiones y lógica de objetos

                hitbox = player.rect.inflate(-12, -12)

                # actualizar objetos (scroll)
                player.on_platform = False

                for obj in objects[:]:
                    if isinstance(obj, Platform) and player.mode == "cube":
                        if hitbox.colliderect(obj.rect):
                            if player.rect.bottom <= obj.rect.top + 15:

                                player.rect.bottom = obj.rect.top
                                player.vel_y = 0
                                player.rotation = round(player.rotation / 90) * 90
                                player.on_platform = True


                                
                                    

                        
                    obj.update(config.SPEED)

                # incrementar distancia recorrida
                distance_traveled += config.SPEED
                progress = max(0, min(100, int((distance_traveled / total_distance) * 100)))

                
                

                for obj in objects[:]:
                    # end -> WIN
                    if obj.kind == "end" and player.rect.colliderect(obj.rect):
                        state = "WIN"
                        spawn_particles(particles, player.rect.centerx, player.rect.centery, (0, 255, 0), 260, 3.0)
                        try:
                            pygame.mixer.music.stop()
                        except:
                            pass
                        break

                    # portal -> alterna modos (solo si no usado)
                    if isinstance(obj, Portal) and player.rect.colliderect(obj.rect):
                        if not obj.used:
                            obj.used = True
                            if player.mode == "cube":
                                player.mode = "ship"
                                # ajustar posición vertical para ship
                                player.rect.y = max(20, min(config.GROUND_Y - 60, player.rect.y))
                            else:
                                player.mode = "cube"
                                player.vel_y = 0

                    # jump pads -> impulso
                    if isinstance(obj, JumpPad) and player.mode == "cube" and hitbox.colliderect(obj.rect):
                        player.vel_y = config.JUMP_FORCE * obj.power
                        spawn_particles(particles, player.rect.centerx, player.rect.bottom, (0, 200, 255), 12, 1.2)

                    # obstáculos que matan (aplican en ambos modos)
                    if isinstance(obj, (Spike, Saw, MovingSaw)) and hitbox.colliderect(obj.rect):
                        player.alive = False
                        camera_shake = 28
                        death_timer = 120
                        spawn_particles(particles, player.rect.centerx, player.rect.centery, (255, 50, 50), 220, 3.0)
                        try:
                            pygame.mixer.music.stop()
                        except:
                            pass
                        break

                # limpiar objetos fuera de pantalla
                for obj in objects[:]:
                    if obj.rect.right < -600:
                        objects.remove(obj)

            else:
                # jugador muerto -> esperar a GAMEOVER
                if camera_shake > 0:
                    camera_shake -= 1
                death_timer -= 1
                if death_timer <= 0:
                    state = "GAMEOVER"

        
                # ------------------ DRAW ------------------
        ox = random.randint(-camera_shake, camera_shake) if camera_shake > 0 else 0
        oy = random.randint(-camera_shake, camera_shake) if camera_shake > 0 else 0

        temp_surf = pygame.Surface((config.WIDTH, config.HEIGHT))

        # fondo estático o color
        if bg_static:
            temp_surf.blit(bg_static, (0, 0))
        else:
            temp_surf.fill(config.C_BG)

        # suelo con imagen
        temp_surf.blit(GROUND_IMG, (0, config.GROUND_Y))

        # línea negra del borde del suelo
        pygame.draw.line(
            temp_surf,
            (0, 0, 0),  # negro
            (0, config.GROUND_Y),
            (config.WIDTH, config.GROUND_Y),
            3
        )

        # dibujar objetos
        for obj in objects:
            obj.draw(temp_surf)

        # partículas
        for p in particles:
            p.draw(temp_surf)

        # dibujar jugador
        player.draw(temp_surf)

        

        # barra superior de progreso
        bar_w = int(config.WIDTH * 0.72)
        bar_x = config.WIDTH // 2 - bar_w // 2
        bar_y = 18
        pygame.draw.rect(temp_surf, (30, 30, 30), (bar_x, bar_y, bar_w, 28), border_radius=8)
        pygame.draw.rect(temp_surf, (0, 200, 0), (bar_x, bar_y, int(bar_w * (progress / 100)), 28), border_radius=8)
        pygame.draw.rect(temp_surf, (0, 0, 0), (bar_x, bar_y, bar_w, 28), 3, border_radius=8)

        # porcentaje centrado
        pct_text = font_pct.render(f"{progress}%", True, config.C_TEXT)
        temp_surf.blit(pct_text, (config.WIDTH // 2 - pct_text.get_width() // 2, bar_y + 34))

        # indicador de modo (cube / ship)
        mode_text = font_ui.render(f"MODO: {player.mode.upper()}", True, config.C_TEXT)
        temp_surf.blit(mode_text, (20, 20))

        # mensajes de estado
        if state == "PAUSE":
            overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            temp_surf.blit(overlay, (0, 0))
            txt = font_title.render("PAUSA", True, config.C_TEXT)
            temp_surf.blit(txt, (config.WIDTH//2 - txt.get_width()//2, config.HEIGHT//2 - 60))
            txt2 = font_ui.render("ESC: continuar  |  BACKSPACE: salir al menú de niveles", True, config.C_TEXT)
            temp_surf.blit(txt2, (config.WIDTH//2 - txt2.get_width()//2, config.HEIGHT//2 + 10))

        if state == "GAMEOVER":
            overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 230))
            temp_surf.blit(overlay, (0, 0))
            txt = font_title.render("HAS MUERTO", True, (255, 50, 50))
            temp_surf.blit(txt, (config.WIDTH//2 - txt.get_width()//2, config.HEIGHT//2 - 80))
            hint = font_ui.render("ENTER: reintentar  |  ESC: volver al menú de niveles", True, config.C_TEXT)
            temp_surf.blit(hint, (config.WIDTH//2 - hint.get_width()//2, config.HEIGHT//2 + 10))

        if state == "WIN":
            overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            temp_surf.blit(overlay, (0, 0))
            txt = font_title.render("¡NIVEL COMPLETADO!", True, (50, 255, 50))
            temp_surf.blit(txt, (config.WIDTH//2 - txt.get_width()//2, config.HEIGHT//2 - 80))
            hint = font_ui.render("ENTER: volver a jugar  |  ESC: volver al menú de niveles", True, config.C_TEXT)
            temp_surf.blit(hint, (config.WIDTH//2 - hint.get_width()//2, config.HEIGHT//2 + 10))

        # blit final con shake
        screen.blit(temp_surf, (ox, oy))
        pygame.display.flip()

    # restaurar música del menú al salir
    if os.path.exists(config.MENU_MUSIC):
        try:
            pygame.mixer.music.load(config.MENU_MUSIC)
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)
        except:
            pass




