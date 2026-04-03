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
import math
import random
import config
import sys
import os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        # SUBIR UN NIVEL: de .../JUEGO/niveles/ → .../JUEGO/
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


skin_img = None
plane_skin_img = None
bg_image = None
SPIKE_IMG = None
SAW_IMG = None
saw_img = None
PORTAL_IMG = None
FINAL_IMG = None
FINAL_WALL_IMG = None
BLOCK_IMG = None
ROCKET_IMG = None
FIRE_FRAMES = []



# Cargar imagen del suelo


# ------------------ RECURSOS ------------------

def load_skin():
    path = config.get_selected_character_skin_path()
    if path is None or not os.path.exists(resource_path(path)):
        return None
    try:
        img = pygame.image.load(resource_path(path)).convert_alpha()
        img = pygame.transform.scale(img, (config.PLAYER_SIZE, config.PLAYER_SIZE))
        return img
    except Exception:
        return None

def load_plane_skin():
    path = config.get_selected_plane_skin_path()
    if path is None or not os.path.exists(resource_path(path)):
        return None
    try:
        img = pygame.image.load(resource_path(path)).convert_alpha()
        img = pygame.transform.scale(img, (config.PLAYER_SIZE + 20, config.PLAYER_SIZE))
        return img
    except Exception:
        return None


def load_bg():
    """Carga una imagen de fondo fija llamada fondo_level2.png."""
    bg_path = resource_path("assets/images/fondo_level2.png")

    if not os.path.exists(bg_path):
        print("⚠ No se encontró el fondo en:", bg_path)
        return None

    try:
        img = pygame.image.load(bg_path).convert()
        img = pygame.transform.smoothscale(img, (config.WIDTH, config.HEIGHT))

        return img
    except Exception as e:
        print("⚠ Error cargando fondo:", e)
        return None







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
        self.on_ground_flag = False

    def on_ground(self):
        return (
            self.mode == "cube"
            and (self.rect.bottom >= config.GROUND_Y or self.on_platform)
        )

    def update(self):
        if not self.alive:
            return

        # ------------------ CUBE ------------------
        if self.mode == "cube":

            self.vel_y += config.GRAVITY
            self.rect.y += self.vel_y

            if self.rect.bottom >= config.GROUND_Y:
                self.rect.bottom = config.GROUND_Y
                self.vel_y = 0
                self.on_ground_flag = True
                self.rotation = round(self.rotation / 90) * 90
            else:
                self.on_ground_flag = False

            if self.vel_y != 0:
                self.rotation -= 6

            if self.jump_held and self.on_ground_flag:
                self.jump()

        # ------------------ SHIP ------------------
        elif self.mode == "ship":

            if self.jump_held:
                self.rect.y -= self.ship_speed_y
                self.rotation = min(self.rotation + 4, 45)   # MORRO ARRIBA
            else:
                self.rect.y += self.ship_speed_y
                self.rotation = max(self.rotation - 4, -45)  # MORRO ABAJO

            # Suavizado
            if not self.jump_held:
                if self.rotation > 0:
                    self.rotation -= 1
                elif self.rotation < 0:
                    self.rotation += 1

            if self.rect.top < 0:
                self.rect.top = 0
            if self.rect.bottom > config.GROUND_Y:
                self.rect.bottom = config.GROUND_Y

        # ------------------ TRAIL (FUERA DE CUBE/SHIP) ------------------
        self.trail.append(self.rect.center)
        if len(self.trail) > 12:
            self.trail.pop(0)


    def jump(self):
        if self.mode != "cube":
            return False

        if self.rect.bottom >= config.GROUND_Y or self.on_platform:
            self.vel_y = -config.JUMP_FORCE
            return True

        return False

    def draw(self, surface):
    # ------------------ TRAIL ------------------
        for i, pos in enumerate(self.trail):
            alpha = int(120 * (i / len(self.trail)))
            size = config.PLAYER_SIZE - (len(self.trail) - i) * 1.5
            s = pygame.Surface((size, size), pygame.SRCALPHA)
            s.fill((0, 255, 200, alpha))
            surface.blit(s, s.get_rect(center=pos))

        # ------------------ SHIP ------------------
        if self.mode == "ship" and plane_skin_img:
            # Dibujar nave rotada
            rotated_plane = pygame.transform.rotate(plane_skin_img, self.rotation)
            plane_rect = rotated_plane.get_rect(center=self.rect.center)
            surface.blit(rotated_plane, plane_rect)

            # Dibujar el personaje encima de la nave
            if skin_img:
                rotated_player = pygame.transform.rotate(skin_img, self.rotation)
            else:
                cube = pygame.Surface((config.PLAYER_SIZE, config.PLAYER_SIZE), pygame.SRCALPHA)
                cube.fill((0, 255, 200))
                pygame.draw.rect(cube, config.C_TEXT, cube.get_rect(), 3)
                rotated_player = pygame.transform.rotate(cube, self.rotation)

            # Ajusta aquí la altura del personaje sobre la nave
            player_rect = rotated_player.get_rect(
                center=(self.rect.centerx, self.rect.centery - 25)
            )
            surface.blit(rotated_player, player_rect)
            return  # ya dibujamos todo en modo ship

        # ------------------ CUBE ------------------
        if skin_img:
            rotated = pygame.transform.rotate(skin_img, self.rotation)
        else:
            cube = pygame.Surface((config.PLAYER_SIZE, config.PLAYER_SIZE), pygame.SRCALPHA)
            cube.fill((0, 255, 200))
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

class FinalWall(GameObject):
    def __init__(self, x):
        super().__init__(x, 0, 1000, config.GROUND_Y, kind="final_wall")

    def draw(self, surface):
        if FINAL_WALL_IMG:
            surface.blit(FINAL_WALL_IMG, self.rect)
        else:
            pygame.draw.rect(surface, (0, 0, 0), self.rect)






class Saw(GameObject):
    """Sierra giratoria fija."""
    def __init__(self, x, y):
        super().__init__(x, y, 60, 60, kind="saw")
        self.angle = random.randint(0, 360)

    def update(self, speed):
        super().update(speed)
        self.angle += 12

    def draw(self, surface):
        
        rotated = pygame.transform.rotate(saw_img, self.angle)
        rect = rotated.get_rect(center=self.rect.center)
        surface.blit(rotated, rect)


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
    
    
    def __init__(self, x, y, portal_type="in"): 
            super().__init__(x, y - 40, 50, 160, kind="portal") 
            self.portal_type = portal_type 
            self.used = False

    def draw(self, surface):
        rect = PORTAL_IMG.get_rect(center=self.rect.center) 
        surface.blit(PORTAL_IMG, rect)

class Rocket(GameObject):
    """Cohete que cae hacia el jugador en diagonal cuando llega a trigger_x."""
    def __init__(self, x, y, trigger_x, speed=8):
        super().__init__(x, y, 50, 20, kind="rocket")
        self.speed = speed
        self.trigger_x = trigger_x
        self.active = False
        self.image = ROCKET_IMG
        self.fire_index = 0
        self.fire_speed = 0.25

        # Puedes dejar esto aunque no lo usemos ya
        self.dx = math.cos(math.radians(45))
        self.dy = math.sin(math.radians(45))

    def update(self, scroll_speed):
        # El cohete se mueve con el scroll aunque no esté activo
        self.rect.x -= scroll_speed

        # Animación del fuego SIEMPRE activa
        self.fire_index += self.fire_speed
        if self.fire_index >= len(FIRE_FRAMES):
            self.fire_index = 0

        # Si aún no está activo, no cae
        if not self.active:
            return

        # --- CAÍDA A 45 GRADOS ---
        # dx y dy ya los tienes definidos en __init__:
        # self.dx = cos(45°)
        # self.dy = sin(45°)
        self.rect.x -= self.speed * self.dx   # hacia la izquierda
        self.rect.y += self.speed * self.dy   # hacia abajo

        # IMPACTO CONTRA EL SUELO
        if self.rect.bottom >= config.GROUND_Y:
            self.rect.bottom = config.GROUND_Y
            self.active = False



    def draw(self, surface):
        if self.image:
            surface.blit(self.image, self.rect)

            # --- DIBUJAR FUEGO ---
            if FIRE_FRAMES:
                fire_img = FIRE_FRAMES[int(self.fire_index)]

                # Ajusta la posición del fuego según tu sprite
                fire_x = self.rect.x + 60   # detrás del cohete
                fire_y = self.rect.y - 40   # centrado verticalmente

                surface.blit(fire_img, (fire_x, fire_y))

        else:
            pygame.draw.rect(surface, (255, 80, 0), self.rect)
            pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)





class Block(GameObject):
    """Bloque sólido apilable. Se puede pisar, pero chocar de frente mata."""
    def __init__(self, x, y, w=60, h=60):
        super().__init__(x, y, w, h, kind="block")
        self.image = BLOCK_IMG

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, self.rect)
        else:
            pygame.draw.rect(surface, (150, 100, 50), self.rect)
            pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)





  

        
       



    
class Platform(GameObject):
    """Plataforma sólida donde el jugador puede subirse."""
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h, kind="platform")

    def draw(self, surface):
        pygame.draw.rect(surface, (180, 180, 180), self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)


# ------------------ GENERACIÓN DEL NIVEL (LARGO + FASE SHIP) ------------------


try:
    BLOCK_IMG = pygame.image.load(resource_path("assets/images/block.png")).convert_alpha()
    BLOCK_IMG = pygame.transform.scale(BLOCK_IMG, (60, 60))
except:
    BLOCK_IMG = None


def generate_level():
    """
    Genera un nivel largo con varias secciones y una fase 'ship'.
    - Objetivo: duración entre 100 y 130 segundos.
    - end_x colocado de forma que no haya objetos detrás de la pared final.
    - No se generan plataformas marrones decorativas; todo es funcional.
    """

    
    

    objects = []

    objects.append(Rocket(3000, 100, trigger_x=2800))
    objects.append(Rocket(4500, 150, trigger_x=4300))
    objects.append(Rocket(6000, 50, trigger_x=5800))



        

    # Bloque final de victoria
    objects.append(FinalWall(34000))

    

    

    



    # --- FINAL DEL NIVEL ---
    end_x = 34000
    

    total_distance_real = end_x - 200
    return objects, end_x, total_distance_real


# ------------------ UTILIDADES ------------------

def spawn_particles(particles, x, y, color, count=30, speed=1.0):
    for _ in range(count):
        particles.append(Particle(x + random.uniform(-12, 12), y + random.uniform(-12, 12), color, speed))



# ------------------ BUCLE PRINCIPAL DEL NIVEL ------------------

def run_level(screen, clock):
    global skin_img, plane_skin_img, bg_image
    global SPIKE_IMG, SAW_IMG, saw_img, PORTAL_IMG, FINAL_IMG, FINAL_WALL_IMG, BLOCK_IMG, ROCKET_IMG

    

    # ------------------ CARGA DE RECURSOS ------------------
    skin_img = load_skin()
    plane_skin_img = load_plane_skin()
    bg_image = load_bg()

    try:
        ROCKET_IMG = pygame.image.load(resource_path("assets/images/rocket_level2.png")).convert_alpha()
        ROCKET_IMG = pygame.transform.scale(ROCKET_IMG, (120, 60))
    except:
        print("⚠ No se encontró rocket_level2.png, usando cohete por defecto")
        ROCKET_IMG = None

    # --- FUEGO DEL COHETE ---
    global FIRE_FRAMES
    FIRE_FRAMES = []
    for i in range(4):
        img = pygame.image.load(resource_path(f"assets/images/fire_{i}.png")).convert_alpha()
        img = pygame.transform.scale(img, (60, 60))  # tamaño del fuego
        FIRE_FRAMES.append(img)


    font_title = pygame.font.SysFont("Arial Black", 60)
    font_ui = pygame.font.SysFont("Arial", 24)
    font_pct = pygame.font.SysFont("Arial Black", 28)

    SPIKE_IMG = pygame.image.load(resource_path("assets/images/level1_spike.png")).convert_alpha()
    SPIKE_IMG = pygame.transform.scale(SPIKE_IMG, (70, 70))

    GROUND_IMG = pygame.image.load(resource_path("assets/images/level2_floor.png")).convert_alpha()

    # Escalado doble para suavizar bordes y textura
    GROUND_IMG = pygame.transform.smoothscale(
        GROUND_IMG,
        (config.WIDTH * 2, (config.HEIGHT - config.GROUND_Y) * 2)
    )

    # Downscale final para máxima nitidez
    GROUND_IMG = pygame.transform.smoothscale(
        GROUND_IMG,
        (config.WIDTH, config.HEIGHT - config.GROUND_Y)
    )



    SAW_IMG = pygame.image.load(resource_path("assets/images/level1_motioncirclespike.png")).convert_alpha()
    SAW_IMG = pygame.transform.scale(SAW_IMG, (70, 70))

    saw_img = pygame.image.load(resource_path("assets/images/level1_circlespike.gif")).convert_alpha()
    saw_img = pygame.transform.scale(saw_img, (70, 70))

    PORTAL_IMG = pygame.image.load(resource_path("assets/images/netherportal.gif")).convert_alpha()
    PORTAL_IMG = pygame.transform.scale(PORTAL_IMG, (90, 120))

    FINAL_IMG = pygame.image.load(resource_path("assets/images/final_level1-removebg.png")).convert_alpha()
    FINAL_IMG = pygame.transform.scale(FINAL_IMG, (180, 260))

    FINAL_WALL_IMG = pygame.image.load(resource_path("assets/images/final_wall.jpg")).convert_alpha()
    FINAL_WALL_IMG = pygame.transform.scale(FINAL_WALL_IMG, (1000, config.GROUND_Y))

  

    # ------------------ ESTADO INICIAL ------------------
    player = Player(start_x=150)
    objects, end_x, total_distance = generate_level()

    final_rect = FINAL_IMG.get_rect()
    final_rect.midbottom = (end_x, config.GROUND_Y)

    distance_traveled = 0
    progress = 0
    state = "PLAY"

    SCROLL_SPEED = getattr(config, "SCROLL_SPEED", 400)

    # ------------------ MÚSICA ------------------
    music_path = resource_path(config.LEVEL2_MUSIC)

    if os.path.exists(music_path):
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)
        except:
            pass

    # ------------------ BUCLE PRINCIPAL ------------------
    running = True
    while running:
        dt = clock.tick(config.FPS) / 1000.0
        scroll_speed = SCROLL_SPEED * dt

        # ------------------ EVENTOS ------------------
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            # ------------------ PLAY ------------------
            if state == "PLAY":

                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_SPACE, pygame.K_UP):
                        player.jump_held = True
                        player.jump()

                    if event.key == pygame.K_ESCAPE:
                        pygame.mixer.music.pause()
                        state = "PAUSA"

                if event.type == pygame.KEYUP:
                    if event.key in (pygame.K_SPACE, pygame.K_UP):
                        player.jump_held = False

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    player.jump_held = True
                    player.jump()

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    player.jump_held = False

            # ------------------ PAUSA ------------------
            elif state == "PAUSA":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        pygame.mixer.music.unpause()
                        state = "PLAY"

                    if event.key == pygame.K_ESCAPE:
                        pygame.mixer.music.stop()
                        return

            # ------------------ GAMEOVER ------------------
            elif state == "GAMEOVER":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return run_level(screen, clock)
                    if event.key == pygame.K_ESCAPE:
                        running = False

            # ------------------ WIN ------------------
            elif state == "WIN":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return run_level(screen, clock)
                    if event.key == pygame.K_ESCAPE:
                        running = False

        # ------------------ ACTUALIZACIÓN ------------------
        if state == "PLAY":

            player.update()

            for obj in objects:
                # 🔥 ÚNICO CAMBIO REAL:
                # Los cohetes necesitan el jugador para perseguirlo
                if getattr(obj, "kind", None) == "rocket":
                    obj.update(scroll_speed)
                else:
                    obj.update(scroll_speed)

            distance_traveled = min(distance_traveled + scroll_speed, total_distance)
            progress = min(100, (distance_traveled / total_distance) * 100)

            player.on_platform = False

            for obj in objects:

                # ------------------ PLATAFORMAS ------------------
                if getattr(obj, "kind", None) == "platform":
                    if player.rect.colliderect(obj.rect):
                        if player.vel_y >= 0 and player.rect.bottom <= obj.rect.bottom:
                            player.rect.bottom = obj.rect.top
                            player.vel_y = 0
                            player.on_platform = True

                # ------------------ BLOQUES ------------------
                if getattr(obj, "kind", None) == "block":
                    if player.rect.colliderect(obj.rect):

                        # Si está encima → plataforma
                        if player.vel_y >= 0 and player.rect.bottom <= obj.rect.top + 10:
                            player.rect.bottom = obj.rect.top
                            player.vel_y = 0
                            player.on_platform = True

                        # Si choca de frente → muerte
                        elif player.rect.right > obj.rect.left and player.rect.left < obj.rect.left:
                            state = "GAMEOVER"
                            pygame.mixer.music.stop()
                            SCROLL_SPEED = 0
                            player.vel_y = 0

                # ------------------ PORTALES ------------------
                if getattr(obj, "kind", None) == "portal":
                    if player.rect.colliderect(obj.rect) and not getattr(obj, "used", False):
                        obj.used = True
                        if obj.portal_type == "in":
                            player.mode = "ship"
                            player.vel_y = 0
                            player.rotation = 0
                        elif obj.portal_type == "out":
                            player.mode = "cube"
                            player.vel_y = 0
                            player.rotation = 0

                # ------------------ COHETE ------------------
                if getattr(obj, "kind", None) == "rocket":

                    # Activación por distancia
                    if not obj.active and player.rect.x >= obj.trigger_x:
                        obj.active = True

                    # Colisión
                    if player.rect.colliderect(obj.rect):
                        state = "GAMEOVER"
                        pygame.mixer.music.stop()
                        SCROLL_SPEED = 0
                        player.vel_y = 0

                # ------------------ MUERTE ------------------
                if getattr(obj, "kind", None) in ("spike", "saw", "movingsaw"):
                    if player.rect.colliderect(obj.rect):
                        state = "GAMEOVER"
                        pygame.mixer.music.stop()
                        SCROLL_SPEED = 0
                        player.vel_y = 0

                # ------------------ GANAR ------------------
                if getattr(obj, "kind", None) == "final_wall":
                    if progress >= 100 and player.rect.colliderect(obj.rect):
                        state = "WIN"
                        pygame.mixer.music.stop()
                        SCROLL_SPEED = 0
                        player.vel_y = 0

        # ------------------ DIBUJO ------------------
        screen.blit(bg_image, (0, 0))
        screen.blit(GROUND_IMG, (0, config.GROUND_Y))

        for obj in objects:
            obj.draw(screen)

        player.draw(screen)
        screen.blit(FINAL_IMG, final_rect)

        # ------------------ BARRA DE PROGRESO ------------------
        bar_total_width = 400
        bar_height = 25
        bar_x = config.WIDTH // 2 - bar_total_width // 2
        bar_y = 20

        pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_total_width, bar_height), 3)
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, int((progress / 100) * bar_total_width), bar_height))

        pct_text = font_pct.render(f"{int(progress)}%", True, (255, 255, 255))
        screen.blit(pct_text, (config.WIDTH // 2 - pct_text.get_width() // 2,
                            bar_y + bar_height // 2 - pct_text.get_height() // 2))

        # ------------------ PAUSA ------------------
        if state == "PAUSA":
            overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            font_big = pygame.font.SysFont(None, 80)
            text = font_big.render("PAUSA", True, (255, 255, 255))
            screen.blit(text, (config.WIDTH//2 - text.get_width()//2,
                            config.HEIGHT//2 - 150))

            font_small = pygame.font.SysFont(None, 40)
            msg1 = font_small.render("ENTER - Continuar", True, (255, 255, 255))
            msg2 = font_small.render("ESC - Salir al menú", True, (255, 255, 255))

            screen.blit(msg1, (config.WIDTH//2 - msg1.get_width()//2,
                            config.HEIGHT//2 - 20))
            screen.blit(msg2, (config.WIDTH//2 - msg2.get_width()//2,
                            config.HEIGHT//2 + 40))

        # ------------------ WIN ------------------
        if state == "WIN":
            overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            font_big = pygame.font.SysFont(None, 90)
            text = font_big.render("¡HAS GANADO!", True, (0, 255, 0))
            screen.blit(text, (config.WIDTH//2 - text.get_width()//2,
                            config.HEIGHT//2 - text.get_height()//2))

            font_small = pygame.font.SysFont(None, 40)
            msg = font_small.render("ENTER para reiniciar   |   ESC para salir", True, (255, 255, 255))
            screen.blit(msg, (config.WIDTH//2 - msg.get_width()//2,
                            config.HEIGHT//2 + 60))

        # ------------------ GAMEOVER ------------------
        if state == "GAMEOVER":
            overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            font_big = pygame.font.SysFont(None, 90)
            text = font_big.render("HAS PERDIDO", True, (255, 0, 0))
            screen.blit(text, (config.WIDTH//2 - text.get_width()//2,
                            config.HEIGHT//2 - text.get_height()//2))

            font_small = pygame.font.SysFont(None, 40)
            msg = font_small.render("ENTER para reintentar   |   ESC para salir", True, (255, 255, 255))
            screen.blit(msg, (config.WIDTH//2 - msg.get_width()//2,
                            config.HEIGHT//2 + 60))

        pygame.display.flip()


















