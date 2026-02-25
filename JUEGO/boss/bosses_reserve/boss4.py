import os
import config
from boss.boss_template import run_boss_generic

params = {
    "image_path": os.path.join(config.ASSETS_IMG, "boss_4.png"),
    "proj_image_path": os.path.join(config.ASSETS_IMG, "boss_4_proj.png"),
    "big_proj_image_path": os.path.join(config.ASSETS_IMG, "boss_4_big.png"),
    "music_path": os.path.join(config.ASSETS_AUDIO, "boss_4.mp3"),
    "boss_size": 180,
    "boss_hp": 1500,
    "name": "BOSS 4",
    "base_pattern": "rotating",
    "shoot_interval": 44,
    "projectile_speed": 8.0,
    "ob_interval": 170,
    "obstacle_types": ["falling", "moving", "mine"],
    "player_damage_to_boss": 9,
    "boss_proj_damage": 20,
    "obstacle_damage": 24,
    "laser_interval": 480,
    "laser_duration": 120,
    "phases": [
        {"threshold": 1100, "overrides": {"shoot_interval": 36, "projectile_speed": 9.0}}
    ]
}

def run_boss(screen, clock):
    run_boss_generic(screen, clock, params)
