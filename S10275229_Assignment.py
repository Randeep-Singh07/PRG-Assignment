from random import randint
import os
import pickle

# Global structures
player = {}
game_map = []
fog = []
mined_nodes = []  # Track mined nodes for possible replenishment

MAP_WIDTH = 0
MAP_HEIGHT = 0

# Constants 
TURNS_PER_DAY = 20
WIN_GP = 1500
current_level = 1

minerals = ['copper', 'silver', 'gold']
mineral_names = {'C': 'copper', 'S': 'silver', 'G': 'gold'}
pickaxe_price = [50, 150]
prices = {'copper': (1, 3), 'silver': (5, 8), 'gold': (10, 18)}
high_scores = []

# ---------- Helper Functions ----------
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def clamp(val, minval, maxval):
    return max(minval, min(val, maxval))

def get_total_load(player):
    return player.get('copper', 0) + player.get('silver', 0) + player.get('gold', 0)

def load_map(filename, map_struct):
    global MAP_WIDTH, MAP_HEIGHT
    try:
        with open(filename, 'r') as f:
            lines = [line.rstrip('\n') for line in f if line.strip()]
            map_struct.clear()
            for line in lines:
                map_struct.append(list(line))
            MAP_HEIGHT = len(map_struct)
            MAP_WIDTH = max(len(row) for row in map_struct) if map_struct else 0
    except Exception as e:
        print(f"Fatal error loading map: {e}")
        exit(1)

def initialize_fog():
    fog.clear()
    for row in range(MAP_HEIGHT):
        fog.append(['?' for _ in range(MAP_WIDTH)])

def clear_fog(fog, player):
    px, py = player['x'], player['y']
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            ny = py + dy
            nx = px + dx
            if 0 <= ny < len(game_map) and 0 <= nx < len(game_map[ny]):
                fog[ny][nx] = game_map[ny][nx]