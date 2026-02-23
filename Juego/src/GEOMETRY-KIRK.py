import pygame
import sys
import random
import os

# ==========================
# PERSONAJE ELEGIDO
# ==========================
personaje_elegido = os.getenv("PERSONAJE", "diddy")
print(f"Personaje elegido: {personaje_elegido}")

personajes = {
    "diddy": "../assets/IMG/diddy.jpg",
    "charlie": "../assets/IMG/charlie.jpg",
    "george": "../assets/IMG/george.jpg",
    "jeffrey": "../assets/IMG/jeffrey.jpg"
}

pygame.init()

# ==========================
# VENTANA
# ==========================
ANCHO = 800
ALTO = 400
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("GEOMETRY KIRK")

# ==========================
# COLORES
# ==========================
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)

# ==========================
# JUGADOR
# ==========================
jug_x = 50
jug_y = 300
jug_ancho = 60
jug_alto = 60
vel_y = 0
saltando = False

# Cargar imagen del jugador elegido
jugador_img = pygame.image.load(personajes[personaje_elegido])
jugador_img = pygame.transform.scale(jugador_img, (jug_ancho, jug_alto))

# ==========================
# OBSTÁCULO
# ==========================
obs_x = 800
obs_y = 300
obs_ancho = 60
obs_alto = 60
vel_obs = 7

obs_img_original = pygame.image.load("../assets/IMG/diddy.jpg")
obs_img = pygame.transform.scale(obs_img_original, (obs_ancho, obs_alto))

# ==========================
# SUELO
# ==========================
suelo_img_original = pygame.image.load("../assets/IMG/suelo.png")
suelo_img = pygame.transform.scale(suelo_img_original, (ANCHO, 60))

# ==========================
# FONDO Y MÚSICA
# ==========================
clock = pygame.time.Clock()

pygame.mixer.music.load("../assets/AUDIO/musica.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.5)

fondo_original = pygame.image.load("../assets/IMG/epictetus.jpg")
fondo = pygame.transform.scale(fondo_original, (ANCHO, ALTO))

# ==========================
# BUCLE PRINCIPAL
# ==========================
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE and not saltando:
                vel_y = -20
                saltando = True

    # Gravedad
    vel_y += 1
    jug_y += vel_y

    # Suelo
    if jug_y >= 300:
        jug_y = 300
        vel_y = 0
        saltando = False

    # Movimiento del obstáculo
    obs_x -= vel_obs
    if obs_x < -obs_ancho:
        obs_x = 800

    # Colisión
    jugador_rect = pygame.Rect(jug_x, jug_y, jug_ancho, jug_alto)
    obstaculo_rect = pygame.Rect(obs_x, obs_y, obs_ancho, obs_alto)

    if jugador_rect.colliderect(obstaculo_rect):
        print("¡Has perdido!")
        pygame.quit()
        sys.exit()

    # Dibujar
    ventana.blit(fondo, (0, 0))
    ventana.blit(jugador_img, (jug_x, jug_y))
    ventana.blit(obs_img, (obs_x, obs_y))
    ventana.blit(suelo_img, (0, 340))

    pygame.display.update()
    clock.tick(60)
