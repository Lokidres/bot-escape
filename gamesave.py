import json
import os

SAVE_FILE = "player_progress.json"

def save_game_progress(stats):
    save_data = {
        'best_time': stats.best_time,
        'best_wave': stats.best_wave,
        'player_lvl': stats.player_lvl,
        'xp': stats.xp,
        'xp_target': stats.xp_target,
        'selected_skin': stats.selected_skin
    }
    
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(save_data, f)
    except:
        print("Couldn't save game progress")

def load_game_progress(stats):
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'r') as f:
                save_data = json.load(f)
                
            stats.best_time = save_data.get('best_time', 0)
            stats.best_wave = save_data.get('best_wave', 1)
            stats.player_lvl = save_data.get('player_lvl', 1)
            stats.xp = save_data.get('xp', 0)
            stats.xp_target = save_data.get('xp_target', 100)
            stats.selected_skin = save_data.get('selected_skin', 0)
    except:
        print("Couldn't load save file")
