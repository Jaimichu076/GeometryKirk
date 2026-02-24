import os
import config
from boss.boss_template import run_boss_generic

params = {
    "image_path": os.path.join(config.ASSETS_IMG, "boss_1.png"),
    "proj_image_path": os.path.join(config.ASSETS_IMG, "boss_1_proj.png"),
    "big_proj_image_path": os.path.join(config.ASSETS_IMG, "boss_1_big.png"),
    "music_path": os.path.join(config.ASSETS_AUDIO, "boss_1.mp3"),
    "boss_size": 150,
    "boss_hp": 900,
    "name": "BOSS 1",
    "base_pattern": "fan",
    "shoot_interval": 60,
    "projectile_speed": 6.0,
    "ob_interval": 220,
    "obstacle_types": ["falling", "moving"],
    "player_damage_to_boss": 12,
    "boss_proj_damage": 12,
    "obstacle_damage": 16,
    "laser_interval": 0,
    "laser_duration": 0,
    "phases": [
        {"threshold": 600, "overrides": {"shoot_interval": 52, "projectile_speed": 6.5}}
    ]
}

def run_boss(screen, clock):
    run_boss_generic(screen, clock, params)
