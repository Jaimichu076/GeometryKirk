import os
import config
from boss.boss_template import run_boss_generic

params = {
    "image_path": os.path.join(config.ASSETS_IMG, "boss_5.png"),
    "proj_image_path": os.path.join(config.ASSETS_IMG, "boss_5_proj.png"),
    "big_proj_image_path": os.path.join(config.ASSETS_IMG, "boss_5_big.png"),
    "music_path": os.path.join(config.ASSETS_AUDIO, "boss_5.mp3"),
    "boss_size": 190,
    "boss_hp": 1700,
    "name": "BOSS 5",
    "base_pattern": "mixed",
    "shoot_interval": 40,
    "projectile_speed": 8.5,
    "ob_interval": 150,
    "obstacle_types": ["moving", "mine"],
    "player_damage_to_boss": 8,
    "boss_proj_damage": 22,
    "obstacle_damage": 26,
    "laser_interval": 440,
    "laser_duration": 130,
    "phases": [
        {"threshold": 1300, "overrides": {"shoot_interval": 34, "projectile_speed": 9.5}}
    ]
}

def run_boss(screen, clock):
    run_boss_generic(screen, clock, params)
