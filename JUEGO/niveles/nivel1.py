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
    """Carga una imagen de fondo fija llamada fondo_lvl1.png."""
    bg_path = resource_path("assets/images/fondo_lvl1.png")

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

        # ------------------ MODO CUBE ------------------
        if self.mode == "cube":
            # gravedad
            if not self.on_platform:
                self.vel_y += config.GRAVITY * self.gravity_dir
            else:
                self.vel_y = 0

            self.rect.y += self.vel_y

            # colisión con suelo
            if self.rect.bottom >= config.GROUND_Y:
                self.rect.bottom = config.GROUND_Y
                self.vel_y = 0
                self.rotation = round(self.rotation / 90) * 90

            # rotación mientras cae
            if self.vel_y != 0:
                self.rotation -= 6 * self.gravity_dir

        # ------------------ MODO SHIP ------------------
        elif self.mode == "ship":
            # subir si mantienes pulsado
            if self.jump_held:
                self.rect.y -= self.ship_speed_y
            else:
                self.rect.y += self.ship_speed_y

            # límites verticales
            if self.rect.top < 0:
                self.rect.top = 0
            if self.rect.bottom > config.GROUND_Y:
                self.rect.bottom = config.GROUND_Y

        # ------------------ TRAIL ------------------
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

        # --- AVIÓN DEBAJO EN MODO SHIP ---
        if self.mode == "ship" and plane_skin_img:
            plane_rect = plane_skin_img.get_rect(center=(self.rect.centerx, self.rect.centery + 30))
            surface.blit(plane_skin_img, plane_rect)

        # --- PERSONAJE ENCIMA ---
        if skin_img:
            rotated = pygame.transform.rotate(skin_img, self.rotation)
        else:
            cube = pygame.Surface((config.PLAYER_SIZE, config.PLAYER_SIZE), pygame.SRCALPHA)
            if self.mode == "cube":
                cube.fill((0, 255, 200))
            else:
                cube.fill((80, 200, 255))
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

        # --- SECCIÓN INICIAL (muy fácil) ---
    objects.append(Spike(1200, 0))
    objects.append(Spike(1400, 0))
    objects.append(Spike(1600, 0))

    objects.append(Saw(2000, config.GROUND_Y - 90))
    objects.append(Spike(2400, 0))

        # --- PORTAL A SHIP ---
    portal1_x = 2800
    portal1_y = config.GROUND_Y - 90
    objects.append(Portal(portal1_x, portal1_y, "in"))

    objects.append(Saw(portal1_x, portal1_y - 80))
    objects.append(Saw(portal1_x, portal1_y - 160))
    objects.append(Saw(portal1_x, portal1_y - 240))
    objects.append(Saw(portal1_x, portal1_y - 320))
    objects.append(Saw(portal1_x, portal1_y - 400))
    objects.append(Saw(portal1_x, portal1_y - 480))

    objects.append(Spike(3000, 0))
    objects.append(Spike(3050, 0))
    objects.append(Spike(3100, 0))
    objects.append(Spike(3150, 0))
    objects.append(Spike(3200, 0))
    objects.append(Spike(3250, 0))
    objects.append(Spike(3300, 0))

    objects.append(Saw(3200, config.GROUND_Y - 130))
    objects.append(Saw(3300, config.GROUND_Y - 170))
    objects.append(Saw(3500, config.GROUND_Y - 110))

    objects.append(Spike(3350, 0))
    objects.append(Spike(3400, 0))
    objects.append(Spike(3450, 0))
    objects.append(Spike(3500, 0))
    objects.append(Spike(3550, 0))
    objects.append(Spike(3600, 0))
    objects.append(Spike(3650, 0))
    objects.append(Spike(3700, 0))
    objects.append(Spike(3750, 0))
    objects.append(Spike(3800, 0))
    objects.append(Spike(3850, 0))
    objects.append(Spike(3900, 0))
    objects.append(Spike(3950, 0))
    objects.append(Spike(4000, 0))
    objects.append(Spike(4050, 0))
    objects.append(Spike(4100, 0))
    objects.append(Spike(4150, 0))
    objects.append(Spike(4200, 0))
    objects.append(Spike(4250, 0))
    objects.append(Spike(4300, 0))
    objects.append(Spike(4350, 0))
    objects.append(Spike(4400, 0))
    objects.append(Spike(4450, 0))
    objects.append(Spike(4500, 0))
    objects.append(Spike(4550, 0))
    objects.append(Spike(4600, 0))
    objects.append(Spike(4650, 0))
    objects.append(Spike(4700, 0))
    objects.append(Spike(4750, 0))
    objects.append(Spike(4800, 0))
    objects.append(Spike(4850, 0))
    objects.append(Spike(4900, 0))
    objects.append(Spike(4850, 0))
    objects.append(Spike(4900, 0))
    objects.append(Spike(4950, 0))
    objects.append(Spike(5000, 0))
    objects.append(Spike(5050, 0))
    objects.append(Spike(5100, 0))
    objects.append(Spike(5150, 0))
    objects.append(Spike(5200, 0))
    objects.append(Spike(5250, 0))
    objects.append(Spike(5300, 0))

    objects.append(Saw(3700, config.GROUND_Y - 190))
    objects.append(Saw(3850, config.GROUND_Y - 350))
    objects.append(Saw(4000, config.GROUND_Y - 450))
    objects.append(Saw(3900, config.GROUND_Y - 290))
    objects.append(MovingSaw(4200, config.GROUND_Y - 350))
    objects.append(Saw(4500, config.GROUND_Y - 120))
    objects.append(Saw(4700, config.GROUND_Y - 320))
    objects.append(Saw(4900, config.GROUND_Y - 390))
    objects.append(Saw(5200, config.GROUND_Y - 250))

        # --- PORTAL A CUBE ---
    portal2_x = 5500
    portal2_y = config.GROUND_Y - 90
    objects.append(Portal(portal2_x, portal2_y, "out"))

    objects.append(Saw(portal2_x, portal2_y - 80))
    objects.append(Saw(portal2_x, portal2_y - 160))
    objects.append(Saw(portal2_x, portal2_y - 240))
    objects.append(Saw(portal2_x, portal2_y - 320))
    objects.append(Saw(portal2_x, portal2_y - 400))
    objects.append(Saw(portal2_x, portal2_y - 480))

    objects.append(Spike(5800, 0))
    objects.append(Spike(5850, 0))
    objects.append(MovingSaw(6200, config.GROUND_Y - 120))
    objects.append(MovingSaw(6600, config.GROUND_Y - 120))
    

    objects.append(Spike(7000, 0))
    objects.append(Spike(7050, 0))
    objects.append(Spike(7300, 0))
    objects.append(Spike(7350, 0))

    

    


    objects.append(Spike(8000, 0))
    objects.append(Spike(8050, 0))

    objects.append(Saw(8300, config.GROUND_Y - 110))
    




    


    objects.append(MovingSaw(9100, config.GROUND_Y - 120))


    


    objects.append(Spike(9800, 0))
    objects.append(Spike(9950, 0))
    

    
    

    








    














    









        # --- SEGUNDA SECCIÓN SHIP ---
    portal3_x = 11300
    portal3_y = config.GROUND_Y - 90
    objects.append(Portal(portal3_x, portal3_y, "in"))

    objects.append(Saw(portal3_x, portal3_y - 80))
    objects.append(Saw(portal3_x, portal3_y - 160))
    objects.append(Saw(portal3_x, portal3_y - 240))
    objects.append(Saw(portal3_x, portal3_y - 320))
    objects.append(Saw(portal3_x, portal3_y - 400))
    objects.append(Saw(portal3_x, portal3_y - 480))


    objects.append(Spike(1, 0))

    objects.append(Saw(11400, config.GROUND_Y - 500))
    objects.append(Saw(11450, config.GROUND_Y - 500))

    objects.append(Spike(11500, 0))
    objects.append(Spike(11550, 0))
    objects.append(Spike(11600, 0))
    objects.append(Spike(11650, 0))
    objects.append(Spike(11700, 0))
    objects.append(Spike(11750, 0))
    objects.append(Spike(11800, 0))
    objects.append(Spike(11850, 0))
    objects.append(Spike(11900, 0))
    objects.append(Spike(11950, 0))
    objects.append(Spike(12000, 0))
    objects.append(Spike(12050, 0))
    objects.append(Spike(12100, 0))
    objects.append(Spike(12150, 0))
    objects.append(Spike(12200, 0))
    objects.append(Spike(12250, 0))
    objects.append(Spike(12300, 0))
    objects.append(Spike(12350, 0))
    objects.append(Spike(12400, 0))
    objects.append(Spike(12450, 0))
    objects.append(Spike(12500, 0))
    objects.append(Spike(12550, 0))
    objects.append(Spike(12600, 0))
    objects.append(Spike(12650, 0))
    objects.append(Spike(12700, 0))
    objects.append(Spike(12750, 0))
    objects.append(Spike(12800, 0))
    objects.append(Spike(12850, 0))
    objects.append(Spike(12900, 0))
    objects.append(Spike(12950, 0))
    objects.append(Spike(13000, 0))
    objects.append(Spike(13050, 0))
    objects.append(Spike(13100, 0))
    objects.append(Spike(13150, 0))
    objects.append(Spike(13200, 0))
    objects.append(Spike(13250, 0))
    objects.append(Spike(13300, 0))
    objects.append(Spike(13350, 0))
    objects.append(Spike(13400, 0))
    objects.append(Spike(13450, 0))
    objects.append(Spike(13500, 0))
    objects.append(Spike(13550, 0))
    objects.append(Spike(13600, 0))
    objects.append(Spike(13650, 0))
    objects.append(Spike(13700, 0))
    objects.append(Spike(13750, 0))
    objects.append(Spike(13800, 0))
    objects.append(Spike(13850, 0))
    objects.append(Spike(13900, 0))
    objects.append(Spike(13950, 0))
    objects.append(Spike(14000, 0))
    objects.append(Spike(14050, 0))
    objects.append(Spike(14100, 0))
    objects.append(Spike(14150, 0))
    objects.append(Spike(14200, 0))
    objects.append(Spike(14250, 0))
    objects.append(Spike(14300, 0))
    objects.append(Spike(14350, 0))
    objects.append(Spike(14400, 0))
    objects.append(Spike(14450, 0))
    objects.append(Spike(14500, 0))
    objects.append(Spike(14550, 0))
    objects.append(Spike(14600, 0))
    objects.append(Spike(14650, 0))
    objects.append(Spike(14700, 0))
    objects.append(Spike(14750, 0))
    objects.append(Spike(14800, 0))
    objects.append(Spike(14850, 0))
    objects.append(Spike(14900, 0))
    objects.append(Spike(14950, 0))
    objects.append(Spike(15000, 0))
    objects.append(Spike(15050, 0))
    objects.append(Spike(15100, 0))
    objects.append(Spike(15150, 0))
    objects.append(Spike(15200, 0))
    objects.append(Spike(15250, 0))
    objects.append(Spike(15300, 0))
    objects.append(Spike(15350, 0))
    objects.append(Spike(15400, 0))
    objects.append(Spike(15450, 0))
    objects.append(Spike(15500, 0))
    objects.append(Spike(15550, 0))
    objects.append(Spike(15600, 0))
    objects.append(Spike(15650, 0))
    objects.append(Spike(15700, 0))
    objects.append(Spike(15750, 0))
    objects.append(Spike(15800, 0))
    objects.append(Spike(15850, 0))
    objects.append(Spike(15900, 0))
    objects.append(Spike(15950, 0))
    objects.append(Spike(16000, 0))
    objects.append(Spike(16050, 0))
    objects.append(Spike(16100, 0))
    objects.append(Spike(16150, 0))
    objects.append(Spike(16200, 0))
    objects.append(Spike(16250, 0))
    objects.append(Spike(16300, 0))
    objects.append(Spike(16350, 0))
    objects.append(Spike(16400, 0))
    objects.append(Spike(16450, 0))
    objects.append(Spike(16500, 0))
    objects.append(Spike(16550, 0))
    objects.append(Spike(16600, 0))
    objects.append(Spike(16650, 0))
    objects.append(Spike(16700, 0))
    objects.append(Spike(16750, 0))
    objects.append(Spike(16800, 0))
    objects.append(Spike(16850, 0))
    objects.append(Spike(16900, 0))
    objects.append(Spike(16950, 0))
    objects.append(Spike(17000, 0))
    objects.append(Spike(17050, 0))
    objects.append(Spike(17100, 0))
    objects.append(Spike(17150, 0))
    objects.append(Spike(17200, 0))
    objects.append(Spike(17250, 0))
    objects.append(Spike(17300, 0))
    objects.append(Spike(17350, 0))
    objects.append(Spike(17400, 0))
    objects.append(Saw(12000, config.GROUND_Y - 300))
    




    




    



        # --- PORTAL FINAL A CUBE ---
    portal4_x = 17600
    portal4_y = config.GROUND_Y - 90
    objects.append(Portal(portal4_x, portal4_y, "out"))

    objects.append(Saw(portal4_x, portal4_y - 80))
    objects.append(Saw(portal4_x, portal4_y - 160))
    objects.append(Saw(portal4_x, portal4_y - 240))
    objects.append(Saw(portal4_x, portal4_y - 320))
    objects.append(Saw(portal4_x, portal4_y - 400))
    objects.append(Saw(portal4_x, portal4_y - 480))

        # --- CUBE FINAL ---
    

        # --- FINAL DEL NIVEL ---
    end_x = 19000
    objects.append(GameObject(end_x, 0, 10, config.HEIGHT, kind="end"))

    total_distance_real = end_x - 150
    return objects, end_x, total_distance_real


# ------------------ UTILIDADES ------------------

def spawn_particles(particles, x, y, color, count=30, speed=1.0):
    for _ in range(count):
        particles.append(Particle(x + random.uniform(-12, 12), y + random.uniform(-12, 12), color, speed))



# ------------------ BUCLE PRINCIPAL DEL NIVEL ------------------

def run_level(screen, clock):
    global skin_img, plane_skin_img, bg_image, SPIKE_IMG, SAW_IMG, saw_img, PORTAL_IMG
    skin_img = load_skin()
    plane_skin_img = load_plane_skin()
    bg_image = load_bg()


    font_title = pygame.font.SysFont("Arial Black", 60)
    font_ui = pygame.font.SysFont("Arial", 24)
    font_pct = pygame.font.SysFont("Arial Black", 28)

    bg_static = bg_image

    SPIKE_IMG = pygame.image.load(resource_path("assets/images/level1_spike.png")).convert_alpha()
    SPIKE_IMG = pygame.transform.scale(SPIKE_IMG, (70, 70))

    GROUND_IMG = pygame.image.load(resource_path("assets/images/suelo.png")).convert_alpha()
    GROUND_IMG = pygame.transform.scale(GROUND_IMG, (config.WIDTH, config.HEIGHT - config.GROUND_Y))

    SAW_IMG = pygame.image.load(resource_path("assets/images/level1_motioncirclespike.png")).convert_alpha()
    SAW_IMG = pygame.transform.scale(SAW_IMG, (70, 70))

    saw_img = pygame.image.load(resource_path("assets/images/level1_circlespike.gif")).convert_alpha()
    saw_img = pygame.transform.scale(saw_img, (70, 70))

    PORTAL_IMG = pygame.image.load(resource_path("assets/images/netherportal.gif")).convert_alpha()
    PORTAL_IMG = pygame.transform.scale(PORTAL_IMG, (90, 120))


    particles = []
    player = Player(start_x=150)
    objects, end_x, total_distance = generate_level()

    distance_traveled = 0
    progress = 0

    camera_shake = 0
    state = "PLAY"

    # Música
    music_path = resource_path(config.LEVEL_MUSIC)
    if os.path.exists(music_path):
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)
        except:
            pass


    running = True
    while running:
        dt = clock.tick(config.FPS) / 1000.0

        # ------------------ EVENTOS ------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            # INPUT SOLO EN PLAY
            if state == "PLAY":
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_SPACE, pygame.K_UP):
                        player.jump_held = True
                        if player.mode == "cube":
                            player.jump()

                if event.type == pygame.KEYUP:
                    if event.key in (pygame.K_SPACE, pygame.K_UP):
                        player.jump_held = False

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    player.jump_held = True
                    if player.mode == "cube":
                        player.jump()

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    player.jump_held = False

            # GAMEOVER
            if state == "GAMEOVER":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return run_level(screen, clock)
                    if event.key == pygame.K_ESCAPE:
                        running = False

        # ------------------ UPDATE ------------------
        # partículas siempre
        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)

        # SOLO HAY LÓGICA SI ESTÁ EN PLAY Y VIVO
        if state == "PLAY" and player.alive:

            # actualizar jugador
            player.update()

            # auto-salto (como GD)
            if player.mode == "cube" and player.jump_held and player.on_ground():
                player.jump()

            hitbox = player.rect.inflate(-4, -4)
            player.on_platform = False

            # actualizar objetos SOLO si estás vivo
            for obj in objects:
                obj.update(config.SPEED)

            # colisiones mortales
            for obj in objects:
                if obj.kind in ("spike", "saw", "movingsaw"):
                    if hitbox.colliderect(obj.rect):
                        player.alive = False
                        state = "GAMEOVER"
                        pygame.mixer.music.stop()  # parar música
                        camera_shake = 12
                        spawn_particles(
                            particles,
                            player.rect.centerx,
                            player.rect.centery,
                            (255, 50, 50),
                            40,
                            1.2
                        )
                        break  # NO MÁS COLISIONES

                if obj.kind == "portal" and hitbox.colliderect(obj.rect) and not obj.used:
                    obj.used = True
                    player.mode = "ship" if obj.portal_type == "in" else "cube"

                if obj.kind == "end" and hitbox.colliderect(obj.rect):
                    state = "WIN"

            # progreso solo avanza si estás vivo
            distance_traveled += config.SPEED
            progress = max(0, min(100, int((distance_traveled / total_distance) * 100)))

        # ------------------ DRAW ------------------
        # si estás muerto, NO hay shake
        if state == "PLAY":
            ox = random.randint(-camera_shake, camera_shake) if camera_shake > 0 else 0
            oy = random.randint(-camera_shake, camera_shake) if camera_shake > 0 else 0
        else:
            ox = 0
            oy = 0

        temp_surf = pygame.Surface((config.WIDTH, config.HEIGHT))

        if bg_static:
            temp_surf.blit(bg_static, (0, 0))
        else:
            temp_surf.fill(config.C_BG)

        temp_surf.blit(GROUND_IMG, (0, config.GROUND_Y))

        pygame.draw.line(temp_surf, (0, 0, 0), (0, config.GROUND_Y), (config.WIDTH, config.GROUND_Y), 3)

        for obj in objects:
            obj.draw(temp_surf)

        for p in particles:
            p.draw(temp_surf)

        player.draw(temp_surf)

        # barra de progreso
        bar_w = int(config.WIDTH * 0.72)
        bar_x = config.WIDTH // 2 - bar_w // 2
        bar_y = 18
        pygame.draw.rect(temp_surf, (30, 30, 30), (bar_x, bar_y, bar_w, 28), border_radius=8)
        pygame.draw.rect(temp_surf, (0, 200, 0), (bar_x, bar_y, int(bar_w * (progress / 100)), 28), border_radius=8)
        pygame.draw.rect(temp_surf, (0, 0, 0), (bar_x, bar_y, bar_w, 28), 3, border_radius=8)

        pct_text = font_pct.render(f"{progress}%", True, config.C_TEXT)
        temp_surf.blit(pct_text, (config.WIDTH // 2 - pct_text.get_width() // 2, bar_y + 34))

        # GAME OVER
        if state == "GAMEOVER":
            overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 230))
            temp_surf.blit(overlay, (0, 0))
            txt = font_title.render("HAS MUERTO", True, (255, 50, 50))
            temp_surf.blit(txt, (config.WIDTH//2 - txt.get_width()//2, config.HEIGHT//2 - 80))
            hint = font_ui.render("ENTER: reintentar  |  ESC: salir", True, config.C_TEXT)
            temp_surf.blit(hint, (config.WIDTH//2 - hint.get_width()//2, config.HEIGHT//2 + 10))

        screen.blit(temp_surf, (ox, oy))
        pygame.display.flip()



