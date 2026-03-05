import pygame
import os
import random
import sys

def resource_path(relative_path):
    # MISMA LÓGICA QUE EN main.py
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class AudioManager:
    def __init__(self):
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except:
            print("⚠ No se pudo inicializar el audio.")

        self.menu_tracks = []
        self.current_track = None
        self.music_paused = False
        self.is_menu_music = False

        folder = resource_path("assets/audio/menu_soundtracks")
        if os.path.exists(folder):
            for f in os.listdir(folder):
                if f.lower().endswith((".mp3", ".ogg", ".wav")):
                    self.menu_tracks.append(os.path.join(folder, f))

    def play_random_menu_music(self):
        if not self.menu_tracks:
            return

        self.is_menu_music = True
        track = random.choice(self.menu_tracks)
        self.current_track = track

        try:
            pygame.mixer.music.load(track)
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print("⚠ Error cargando música del menú:", track, e)

    def play_music(self, relative_path):
        path = resource_path(relative_path)
        if not os.path.exists(path):
            print("⚠ Música no encontrada:", path)
            return

        self.is_menu_music = False
        self.current_track = path

        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print("⚠ Error cargando música:", path, e)

    def update(self):
        if self.is_menu_music and not pygame.mixer.music.get_busy() and not self.music_paused:
            self.play_random_menu_music()

    def stop(self):
        pygame.mixer.music.stop()

    def pause(self):
        pygame.mixer.music.pause()
        self.music_paused = True

    def resume(self):
        pygame.mixer.music.unpause()
        self.music_paused = False

    def play_sfx(self, relative_path):
        path = resource_path(relative_path)
        if not os.path.exists(path):
            return
        try:
            sfx = pygame.mixer.Sound(path)
            sfx.set_volume(0.7)
            sfx.play()
        except Exception as e:
            print("⚠ Error reproduciendo SFX:", path, e)


audio = AudioManager()
