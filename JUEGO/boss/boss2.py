import os
import config
from boss.boss_template import run_boss_generic

params = {
    "image_path": os.path.join(config.ASSETS_IMG, "falete.jpg"),
    "proj_image_path": os.path.join(config.ASSETS_IMG, "boss_2_proj.png"),
    "big_proj_image_path": os.path.join(config.ASSETS_IMG, "boss_2_big.png"),
    "music_path": os.path.join(config.ASSETS_AUDIO, "faletesong.mp3"),
    "boss_size": 160,
    "boss_hp": 1100,
    "name": "BOSS 2",
    "base_pattern": "mixed",
    "shoot_interval": 52,
    "projectile_speed": 7.0,
    "ob_interval": 200,
    "obstacle_types": ["mine", "falling"],
    "player_damage_to_boss": 11,
    "boss_proj_damage": 14,
    "obstacle_damage": 20,
    "laser_interval": 0,
    "laser_duration": 0,
    "phases": [
        {"threshold": 800, "overrides": {"shoot_interval": 44, "projectile_speed": 8.0}}
    ]
}

def run_boss(screen, clock):
    run_boss_generic(screen, clock, params)

