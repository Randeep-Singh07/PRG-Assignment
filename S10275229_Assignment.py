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

# ---------- Shop ----------
def buy_stuff():
    while True:
        print("\n----------------------- Shop Menu -------------------------")
        # Pickaxe upgrade option
        if player.get('pickaxe', 1) < 3:
            next_pick = player['pickaxe']
            cost = pickaxe_price[next_pick - 1]
            print(f"(P)ickaxe upgrade to Level {next_pick+1} to mine {minerals[next_pick]} ore for {cost} GP")
        else:
            print("Pickaxe fully upgraded.")

        # Backpack upgrade option
        next_capacity = player.get('max_load', 10) + 2
        backpack_cost = player.get('max_load', 10) * 2
        print(f"(B)ackpack upgrade to carry {next_capacity} items for {backpack_cost} GP")

        # Magic Torch option
        valid_inputs = ['p', 'b', 'l']
        if not player.get('magic_torch', False):
            print(f"(T) Magic Torch (see 5x5 area) for 50 GP")
            valid_inputs.append('t')
        else:
            print("Magic Torch already owned.")

        print("(L)eave shop")
        print("-----------------------------------------------------------")
        print(f"GP: {player.get('GP', 0)}")

        try:
            choice = input("What do you want to buy? ").strip().lower()
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt detected. Returning to town.")
            return

        if choice not in valid_inputs:
            print("Invalid choice, please try again.")
            continue

        if choice == 'p' and player.get('pickaxe', 1) < 3:
            cost = pickaxe_price[player['pickaxe'] - 1]
            if player.get('GP', 0) >= cost:
                player['GP'] -= cost
                player['pickaxe'] += 1
                print(f"Congratulations! You can now mine {minerals[player['pickaxe'] - 1]}!")
            else:
                print("Not enough GP.")

        elif choice == 'b':
            if player.get('GP', 0) >= backpack_cost:
                player['GP'] -= backpack_cost
                player['max_load'] = next_capacity
                print(f"Congratulations! You can now carry {next_capacity} items!")
            else:
                print("Not enough GP.")

        elif choice == 't' and not player.get('magic_torch', False):
            if player.get('GP', 0) >= 50:
                player['GP'] -= 50
                player['magic_torch'] = True
                print("You bought the Magic Torch! Your view in the mine is now much larger.")
            else:
                print("Not enough GP.")

        elif choice == 'l':
            break

# ---------- Sell Ore ----------
def sell_ore():
    print("\n--- Sell Ore from Warehouse ---")
    valid_inputs = ['c', 's', 'g', 'l']
    while True:
        print(f"Warehouse: Copper: {player['warehouse'].get('copper', 0)}, Silver: {player['warehouse'].get('silver', 0)}, Gold: {player['warehouse'].get('gold', 0)}")
        print(f"GP: {player.get('GP', 0)}")
        print("What would you like to sell?")
        print("(C)opper, (S)ilver, (G)old, (L)eave")

        try:
            choice = input("Choice: ").strip().lower()
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt detected. Returning to town.")
            return
        
        if choice not in valid_inputs:
            print("Invalid choice, please try again.")
            continue
        if choice == 'l':
            break

        ore = {'c': 'copper', 's': 'silver', 'g': 'gold'}[choice]
        amount = player['warehouse'].get(ore, 0)
        if amount == 0:
            print(f"You have no {ore} to sell.")
            continue

        price = randint(*prices[ore])
        print(f"The current price for {ore} is {price} GP each.")
        try:
            confirm = input(f"Sell all {amount} {ore} for {amount * price} GP? (y/n): ").strip().lower()
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt detected. Cancelling sale.")
            continue
        if confirm == 'y':
            player['GP'] += amount * price
            print(f"Sold {amount} {ore} for {amount * price} GP.")
            player['warehouse'][ore] = 0
        else:
            print("Sale cancelled.")

# ---------- Mining ----------
def mine_turn():
    try:
        player['x'], player['y'] = player.get('portal', (0, 0))
    except Exception:
        player['x'], player['y'] = 0, 0
    clear_fog(fog, player)

    while True:
        print(f"\nDAY {player.get('day', '?')}")
        draw_view()
        print(f"Turns left: {player.get('turns', 0)}    Load: {get_total_load(player)} / {player.get('max_load', 0)}    Steps: {player.get('steps', 0)}")
        print("(WASD) to move | (M)ap | (I)nformation | (P)ortal | (Q)uit to town")
        valid_inputs = ['w', 'a', 's', 'd', 'm', 'i', 'p', 'q']
        try:
            action = input("Action? ").strip().lower()
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt detected. Returning to town.")
            return
        if action not in valid_inputs:
            print("Invalid input.")
            continue

        if action in 'wasd':
            dx, dy = 0, 0
            if action == 'w': dy = -1
            elif action == 'a': dx = -1
            elif action == 's': dy = 1
            elif action == 'd': dx = 1

            nx = player.get('x', 0) + dx
            ny = player.get('y', 0) + dy

            if not (0 <= ny < len(game_map)) or not (0 <= nx < len(game_map[ny])):
                print("You can't move there.")
            else:
                target = game_map[ny][nx]
                current_load = get_total_load(player)

                if target == 'T':
                    return_to_town()
                    return
                elif target in mineral_names:
                    if current_load >= player.get('max_load', 0):
                        print("You can't carry any more.")
                    elif player.get('pickaxe', 1) < minerals.index(mineral_names[target]) + 1:
                        print(f"You need a better pickaxe to mine {mineral_names[target]}.")
                    else:
                        mined = 0
                        if target == 'C': mined = randint(1, 5)
                        elif target == 'S': mined = randint(1, 3)
                        elif target == 'G': mined = randint(1, 2)
                        can_carry = min(mined, player.get('max_load', 0) - current_load)
                        player[mineral_names[target]] += can_carry
                        print(f"You mined {mined} piece(s) of {mineral_names[target]}.")
                        if can_carry < mined:
                            print(f"...but you can only carry {can_carry} more piece(s)!")
                        game_map[ny][nx] = ' '
                        if (nx, ny, target) not in mined_nodes:
                            mined_nodes.append((nx, ny, target))
                        player['x'], player['y'] = nx, ny
                        clear_fog(fog, player)

                elif target == 'D':
                    global current_level
                    if current_level == 1:
                        print("You step through the door to the next mine level!")
                        current_level = 2
                        load_map("level2.txt", game_map)
                        initialize_fog()
                        player['x'], player['y'] = 0, 0
                        clear_fog(fog, player)
                        continue
                    elif current_level == 2:
                        print("You step through the door back to the first mine!")
                        current_level = 1
                        load_map("level1.txt", game_map)
                        initialize_fog()
                        player['x'], player['y'] = MAP_WIDTH - 1, MAP_HEIGHT - 1
                        clear_fog(fog, player)
                        continue
                else:
                    player['x'], player['y'] = nx, ny
                    clear_fog(fog, player)

            player['steps'] += 1
            player['turns'] -= 1
            if player['turns'] <= 0:
                print("You are exhausted.")
                return_to_town()
                return

        elif action == 'm':
            draw_map()
        elif action == 'i':
            show_information()
        elif action == 'p':
            return_to_town()
            return
        elif action == 'q':
            return
        
# ---------- Town Loop ----------
def show_town_menu():
    print(f"\nDAY {player['day']}")
    print("----- Sundrop Town -----")
    print("(B)uy stuff")
    print("See Player (I)nformation")
    print("See Mine (M)ap")
    print("(E)nter mine")
    print("(S)ell ore from warehouse")
    print("Sa(V)e game")
    print("(Q)uit to main menu")
    print("------------------------")

def town_loop():
    while True:
        show_town_menu()
        valid_inputs = ['b', 'i', 'm', 'e', 'v', 'q', 's']
        try:
            choice = input("Your choice? ").strip().lower()
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt detected. Returning to main menu.")
            return
        if choice not in valid_inputs:
            print("Invalid choice, please try again.")
            continue
        if choice == 'b':
            buy_stuff()
        elif choice == 'i':
            show_information()
        elif choice == 'm':
            draw_map()
        elif choice == 'e':
            mine_turn()
        elif choice == 's':
            sell_ore()
        elif choice == 'v':
            save_game()
        elif choice == 'q':
            break

# ---------- Return to Town ----------
def return_to_town():
    print("\nYou place your portal stone here and zap back to town.")
    player['portal'] = (player['x'], player['y'])

    for ore in ['copper', 'silver', 'gold']:
        count = player[ore]
        if count > 0:
            player['warehouse'][ore] += count
            print(f"You store {count} {ore} ore in the warehouse.")
            player[ore] = 0

    print(f"Your warehouse now has: Copper: {player['warehouse']['copper']}, Silver: {player['warehouse']['silver']}, Gold: {player['warehouse']['gold']}")
    player['x'], player['y'] = 0, 0
    player['day'] += 1
    player['turns'] = TURNS_PER_DAY

    # 20% chance to replenish each mined node
    global mined_nodes
    replenished = []
    for idx, (x, y, node_type) in enumerate(mined_nodes):
        if 0 <= y < len(game_map) and 0 <= x < len(game_map[y]):
            if randint(1, 100) <= 20 and game_map[y][x] == ' ':
                game_map[y][x] = node_type
                replenished.append(idx)

    for idx in reversed(replenished):
        mined_nodes.pop(idx)
    clear_fog(fog, player)
    win_check()

# ---------- Win Check ----------
def win_check():
    if player['GP'] >= WIN_GP:
        print("-" * 60)
        print(f"Woo-hoo! Well done, {player['name']}, you have {player['GP']} GP!")
        print(f"You now have enough to retire and play video games every day.")
        print(f"And it only took you {player['day']} days and {player['steps']} steps! You win!")
        print("-" * 60)
        record_high_score()
        main_loop()

# ---------- High Scores ----------
def record_high_score():
    high_scores.append({
        'name': player['name'],
        'days': player['day'],
        'steps': player['steps'],
        'GP': player['GP']
    })
    high_scores.sort(key=lambda s: (s['days'], s['steps'], -s['GP']))
    if len(high_scores) > 5:
        high_scores[:] = high_scores[:5]

def view_high_scores():
    print("\n--- Top 5 High Scores ---")
    if not high_scores:
        print("No scores recorded yet.")
        return
    for i, entry in enumerate(high_scores, 1):
        print(f"{i}. {entry['name']} - Days: {entry['days']}, Steps: {entry['steps']}, GP: {entry['GP']}")