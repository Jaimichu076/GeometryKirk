import os
import config
from boss.boss_template import run_boss_generic

params = {
    "image_path": os.path.join(config.ASSETS_IMG, "boss_6.png"),
    "proj_image_path": os.path.join(config.ASSETS_IMG, "boss_6_proj.png"),
    "big_proj_image_path": os.path.join(config.ASSETS_IMG, "boss_6_big.png"),
    "music_path": os.path.join(config.ASSETS_AUDIO, "boss_6.mp3"),
    "boss_size": 200,
    "boss_hp": 1900,
    "name": "BOSS 6",
    "base_pattern": "mixed",
    "shoot_interval": 36,
    "projectile_speed": 9.0,
    "ob_interval": 140,
    "obstacle_types": ["falling", "moving", "mine"],
    "player_damage_to_boss": 7,
    "boss_proj_damage": 24,
    "obstacle_damage": 28,
    "laser_interval": 420,
    "laser_duration": 130,
    "phases": [
        {"threshold": 1500, "overrides": {"shoot_interval": 30, "projectile_speed": 10.0}}
    ]
}

def run_boss(screen, clock):
    run_boss_generic(screen, clock, params)
