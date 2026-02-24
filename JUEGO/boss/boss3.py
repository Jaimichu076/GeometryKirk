import os
import config
from boss.boss_template import run_boss_generic

params = {
    "image_path": os.path.join(config.ASSETS_IMG, "boss_3.png"),
    "proj_image_path": os.path.join(config.ASSETS_IMG, "boss_3_proj.png"),
    "big_proj_image_path": os.path.join(config.ASSETS_IMG, "boss_3_big.png"),
    "music_path": os.path.join(config.ASSETS_AUDIO, "boss_3.mp3"),
    "boss_size": 170,
    "boss_hp": 1300,
    "name": "BOSS 3",
    "base_pattern": "aimed",
    "shoot_interval": 48,
    "projectile_speed": 7.5,
    "ob_interval": 190,
    "obstacle_types": ["falling", "moving"],
    "player_damage_to_boss": 10,
    "boss_proj_damage": 18,
    "obstacle_damage": 22,
    "laser_interval": 520,
    "laser_duration": 110,
    "phases": [
        {"threshold": 900, "overrides": {"shoot_interval": 40, "projectile_speed": 8.5}}
    ]
}

def run_boss(screen, clock):
    run_boss_generic(screen, clock, params)
