# boss0.py — Tutorial avanzado e interactivo
import os
import pygame
import config
from boss.boss_template import run_boss_generic

def run_boss(screen, clock):

    font_big = pygame.font.SysFont("Arial Black", 40)
    font_med = pygame.font.SysFont("Arial", 22)
    font_small = pygame.font.SysFont("Arial", 18)

    def wait_for_space_or_timeout(timeout_ms=None):
        start = pygame.time.get_ticks()
        while True:
            clock.tick(config.FPS)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); raise SystemExit
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                    return
            if timeout_ms and pygame.time.get_ticks() - start >= timeout_ms:
                return
            # simple background
            screen.fill((10,10,25))
            hint = font_small.render("Pulsa ESPACIO para continuar", True, (200,200,200))
            screen.blit(hint, (config.WIDTH//2 - hint.get_width()//2, config.HEIGHT - 120))
            pygame.display.flip()

    def show_message(text, duration=None):
        start = pygame.time.get_ticks()
        while True:
            clock.tick(config.FPS)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); raise SystemExit
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                    return
            screen.fill((10,10,25))
            txt = font_big.render(text, True, (255,255,255))
            screen.blit(txt, (config.WIDTH//2 - txt.get_width()//2, 160))
            if duration is None:
                hint = font_small.render("Pulsa ESPACIO para continuar", True, (200,200,200))
                screen.blit(hint, (config.WIDTH//2 - hint.get_width()//2, config.HEIGHT - 120))
            pygame.display.flip()
            if duration and pygame.time.get_ticks() - start >= duration:
                return

    # 1) Intro
    show_message("Bienvenido al Tutorial de Boss", duration=1400)
    show_message("Objetivo: aprende movimiento, disparo y armas", duration=1600)

    # 2) Movimiento práctico: pide al jugador ir a un área objetivo
    target_rect = pygame.Rect(220, config.HEIGHT//2 - 40, 120, 80)
    show_message("Practica el movimiento: ve al recuadro verde", duration=800)
    # loop hasta que el jugador entre en target_rect
    from player import Player
    p = Player()
    practicing = True
    while practicing:
        clock.tick(config.FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
        keys = pygame.key.get_pressed()
        p.update(keys)
        if p.rect.colliderect(target_rect):
            practicing = False
        screen.fill((10,10,25))
        pygame.draw.rect(screen, (30,80,30), target_rect)
        p.draw(screen)
        hint = font_small.render("Entra en el recuadro verde para continuar", True, (220,220,220))
        screen.blit(hint, (config.WIDTH//2 - hint.get_width()//2, config.HEIGHT - 120))
        pygame.display.flip()

    show_message("Bien. Ahora aprenderás a disparar.", duration=1000)

    # 3) Disparo práctico: aparece un dummy que debes acertar 3 veces
    dummy = pygame.Rect(520, config.HEIGHT//2 - 24, 48, 48)
    hits_needed = 3
    hits = 0
    p = Player()
    # permitir disparar solo pistola inicialmente
    p.allowed_weapons = {"pistol": True, "shotgun": False, "rocket": False}
    while hits < hits_needed:
        clock.tick(config.FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                p.shoot(target_rect=dummy)
        keys = pygame.key.get_pressed()
        p.update(keys)
        # check collisions of shots with dummy
        for s in list(p.shots):
            if dummy.colliderect(s["rect"]):
                hits += 1
                try:
                    p.shots.remove(s)
                except:
                    pass
        screen.fill((10,10,25))
        pygame.draw.rect(screen, (120,40,40), dummy)
        p.draw(screen)
        info = font_small.render(f"Acierta al dummy {hits}/{hits_needed}", True, (220,220,220))
        screen.blit(info, (config.WIDTH//2 - info.get_width()//2, config.HEIGHT - 120))
        pygame.display.flip()

    show_message("Perfecto. Has usado la PISTOLA.", duration=1200)

    # 4) Curativos: muestra un cubo y pide recogerlo
    show_message("Ahora practica curativos: recoge el cubo verde", duration=1000)
    heal_rect = pygame.Rect(420, config.HEIGHT//2 + 40, 28, 28)
    p = Player()
    collected = False
    while not collected:
        clock.tick(config.FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
        keys = pygame.key.get_pressed()
        p.update(keys)
        if p.rect.colliderect(heal_rect):
            collected = True
            p.hp = min(p.hp + 30, p.hp + 30)
        screen.fill((10,10,25))
        pygame.draw.rect(screen, (0,200,120), heal_rect)
        p.draw(screen)
        hint = font_small.render("Recoge el cubo para curarte", True, (220,220,220))
        screen.blit(hint, (config.WIDTH//2 - hint.get_width()//2, config.HEIGHT - 120))
        pygame.display.flip()

    show_message("Bien. Ahora desbloquearemos la Escopeta.", duration=1200)

    # 5) Desbloqueo Escopeta: explicación y práctica
    show_message("Escopeta: más daño a corta distancia. Pulsa 2 para seleccionarla.", duration=2000)
    # unlock shotgun in the upcoming boss via tutorial messages; we just ensure player knows
    show_message("Práctica: cambia a 2 y dispara al dummy (3 aciertos).", duration=1600)
    p = Player()
    p.allowed_weapons = {"pistol": True, "shotgun": True, "rocket": False}
    hits = 0
    while hits < 3:
        clock.tick(config.FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                p.shoot(target_rect=dummy)
        keys = pygame.key.get_pressed()
        p.update(keys)
        for s in list(p.shots):
            if dummy.colliderect(s["rect"]):
                hits += 1
                try:
                    p.shots.remove(s)
                except:
                    pass
        screen.fill((10,10,25))
        pygame.draw.rect(screen, (120,40,40), dummy)
        p.draw(screen)
        info = font_small.render(f"Acierta al dummy con escopeta {hits}/3", True, (220,220,220))
        screen.blit(info, (config.WIDTH//2 - info.get_width()//2, config.HEIGHT - 120))
        pygame.display.flip()

    show_message("Buen trabajo. Ahora el Lanzacohetes.", duration=1400)

    # 6) Lanzacohetes: explicación y práctica (1 disparo)
    show_message("Lanzacohetes: gran daño, cooldown 9s. Pulsa 3 para seleccionarlo.", duration=2200)
    p = Player()
    p.allowed_weapons = {"pistol": True, "shotgun": True, "rocket": True}
    # pedir 1 disparo con rocket
    fired = False
    while not fired:
        clock.tick(config.FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                p.shoot(target_rect=dummy)
                fired = True
        keys = pygame.key.get_pressed()
        p.update(keys)
        screen.fill((10,10,25))
        pygame.draw.rect(screen, (120,40,40), dummy)
        p.draw(screen)
        hint = font_small.render("Pulsa ESPACIO para disparar el lanzacohetes (1 vez)", True, (220,220,220))
        screen.blit(hint, (config.WIDTH//2 - hint.get_width()//2, config.HEIGHT - 120))
        pygame.display.flip()

    show_message("Tutorial completado. Prepárate para el combate.", duration=1400)

    # --- CONFIGURACIÓN DEL BOSS TUTORIAL ---
    params = {
        "image_path": os.path.join(config.ASSETS_IMG, "Ruth.jpg"),
        "proj_image_path": os.path.join(config.ASSETS_IMG, "ronlarecompensa.jpg"),
        "big_proj_image_path": os.path.join(config.ASSETS_IMG, "obunga700.png"),
        "music_path": os.path.join(config.ASSETS_AUDIO, "Estamos perdidas.mp3"),

        "boss_size": 140,
        "boss_hp": 300,
        "name": "La Ruth",

        "base_pattern": "fan",
        "shoot_interval": 90,
        "projectile_speed": 4.5,
        "ob_interval": 260,
        "obstacle_types": ["falling"],

        "player_damage_to_boss": 14,
        "boss_proj_damage": 6,
        "obstacle_damage": 10,

        "laser_interval": 0,
        "laser_duration": 0,

        # curativos y tutorial
        "heal_image_path": os.path.join(config.ASSETS_IMG, "heal_cube.png"),
        "heal_interval": 500,
        "heal_amount": 30,
        "heal_spawn_count": 2,

        "tutorial": True,
        "enable_puddles": False,
        "enable_lasers": False,
        "enable_enrage": False,
        # sonido de explosión específico para este boss 
        "explosion_sound": config.EXPLOSION_SOUND_BOSS0
    }

    # Bucle de ejecución y manejo de resultado (reintento/volver al menú)
    while True:
        result = run_boss_generic(screen, clock, params)
        if result == "exit":
            return
        if result == "lose":
            # pantalla de derrota: Enter para reintentar, Esc para volver al menú
            font = pygame.font.SysFont("Arial Black", 48)
            small = pygame.font.SysFont("Arial", 22)
            waiting = True
            while waiting:
                clock.tick(config.FPS)
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        pygame.quit(); raise SystemExit
                    if ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_RETURN:
                            waiting = False  # reintentar
                        if ev.key == pygame.K_ESCAPE:
                            return  # volver al menú
                screen.fill((20,10,10))
                msg = font.render("Has perdido", True, (255, 80, 80))
                hint = small.render("Pulsa ENTER para reintentar o ESC para volver al menú", True, (220,220,220))
                screen.blit(msg, (config.WIDTH//2 - msg.get_width()//2, config.HEIGHT//2 - 40))
                screen.blit(hint, (config.WIDTH//2 - hint.get_width()//2, config.HEIGHT//2 + 40))
                pygame.display.flip()
            # si sale del while, reintenta (loop)
            continue
        if result == "win":
            # ya se ejecutó la explosión dentro de run_boss_generic
            # mostrar pantalla de victoria y esperar ESC para volver al menú
            font = pygame.font.SysFont("Arial Black", 48)
            small = pygame.font.SysFont("Arial", 22)
            waiting = True
            while waiting:
                clock.tick(config.FPS)
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        pygame.quit(); raise SystemExit
                    if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                        return
                screen.fill((10,20,10))
                msg = font.render("¡Has ganado!", True, (120, 255, 120))
                hint = small.render("Pulsa ESC para volver al menú", True, (220,220,220))
                screen.blit(msg, (config.WIDTH//2 - msg.get_width()//2, config.HEIGHT//2 - 40))
                screen.blit(hint, (config.WIDTH//2 - hint.get_width()//2, config.HEIGHT//2 + 40))
                pygame.display.flip()
