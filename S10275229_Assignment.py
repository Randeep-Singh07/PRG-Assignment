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

# ---------- Game Init ----------
def initialize_game():
    try:
        load_map("level1.txt", game_map)
    except Exception as e:
        print(f"Error initializing game: {e}")
        return
    initialize_fog()
    player.clear()
    while True:
        try:
            name = input("Greetings, miner! What is your name? ").strip()
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt detected. Returning to main menu.")
            return
        if name:
            break
        print("Name cannot be empty.")

    print(f"Pleased to meet you, {name}. Welcome to Sundrop Town!")
    player.update({
        'name': name, 'x': 0, 'y': 0, 'copper': 0, 'silver': 0, 'gold': 0,
        'GP': 0, 'day': 1, 'steps': 0, 'turns': TURNS_PER_DAY,
        'max_load': 10, 'pickaxe': 1, 'portal': (0, 0),
        'magic_torch': False,
        'warehouse': {'copper': 0, 'silver': 0, 'gold': 0},
    })
    clear_fog(fog, player)

# ---------- Map Drawing ----------
def draw_map():
    print("+" + "-" * MAP_WIDTH + "+")
    for y in range(MAP_HEIGHT):
        line = "|"
        for x in range(MAP_WIDTH):
            if y < len(fog) and x < len(fog[y]):
                if player['x'] == x and player['y'] == y:
                    line += "M"
                elif (x, y) == player.get('portal', (-1, -1)):
                    line += "P"
                else:
                    line += fog[y][x]
            else:
                line += " "
        print(line + "|")
    print("+" + "-" * MAP_WIDTH + "+")

def draw_view():
    size = 2 if not player.get('magic_torch', False) else 4
    print("+" + "-" * (size * 2 + 1) + "+")
    for dy in range(-size, size + 1):
        line = "|"
        for dx in range(-size, size + 1):
            x, y = player['x'] + dx, player['y'] + dy
            if 0 <= y < len(game_map) and 0 <= x < len(game_map[y]):
                if x == player['x'] and y == player['y']:
                    line += "M"
                else:
                    line += fog[y][x]
            else:
                line += "#"
        print(line + "|")
    print("+" + "-" * (size * 2 + 1) + "+")

def show_information():
    print("\n----- Player Information -----")
    print(f"Name: {player.get('name', '???')}")
    print(f"Current position: ({player.get('x', '?')}, {player.get('y', '?')})")
    pickaxe = player.get('pickaxe', 1)
    pickaxe_level = minerals[pickaxe - 1] if 0 < pickaxe <= 3 else 'unknown'
    print(f"Pickaxe level: {pickaxe} ({pickaxe_level})")
    print(f"Gold: {player.get('gold', 0)} | Silver: {player.get('silver', 0)} | Copper: {player.get('copper', 0)}")
    total_load = get_total_load(player)
    print(f"Load: {total_load} / {player.get('max_load', '?')}")
    print(f"GP: {player.get('GP', '?')}")
    print(f"Steps taken: {player.get('steps', '?')}")
    print(f"Day: {player.get('day', '?')}")
    print("------------------------------")