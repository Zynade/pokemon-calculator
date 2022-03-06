import requests
import json
from random import randint
from math import floor, ceil

with open("board.json") as f:
    typechart = json.load(f)
with open("valid_pokemons.json") as f:
    valid_pokemons = json.load(f)

api_url = "https://pokeapi.co/api/v2"


def hp_calculator(base_hp):
    """A simplified HP formula is used"""
    return (2 * base_hp) + 110


def other_stat_calculator(base_stat):
    """A simplified stat formula is used"""
    return (2 * base_stat) + 5


def stat_calculator(stat):
    '''Applies the Stat Growth formula of Gen3 onwards assuming level is 100 , EVs and IVs are 0'''
    cstat = {stat[i]["stat"]["name"]: other_stat_calculator(
        stat[i]["base_stat"]) for i in range(1, 6)}
    cstat["hp"] = hp_calculator(stat[0]["base_stat"])
    return cstat
  # Assumption


def damage_calculator(attack_pokemon, defend_pokemon):
    '''Applies the Damage formula of Gen3 onwards'''
    move_url = attack_pokemon["move"]["url"]
    move_info = json.loads((requests.get(move_url).text))
    attack = dict()
    attack["power"] = move_info["power"]
    if attack["power"] == None:
        return 0
    attack["combat"] = move_info["damage_class"]["name"]
    attack["type"] = move_info["type"]["name"]
    random = randint(85, 100)/100
    #type effictiveness refers to the damage multiplier based on the type chart
    type_effectiveness = 1
    for i in defend_pokemon["types"]:
        # i is {type:{name:val}......} 
        type_effectiveness *= typechart[attack["type"]][i["type"]["name"]]
    if attack["combat"] == "physical":
        damage = floor((0.84*attack["power"]*attack_pokemon["stats"]["attack"]/defend_pokemon["stats"]["defense"]+2)*type_effectiveness*random)
    else:
        damage = floor((0.84*attack["power"]*attack_pokemon["stats"]["special-attack"]/defend_pokemon["stats"]["special-defense"]+2)*type_effectiveness*random)
    return damage

def number_of_turns(health, damage):
    if damage!=0:
        return ceil(health/damage)
    # max integer possible as can never beat it
    return 9223372036854775807

def input_pokemon_moves(moves):
    move = dict()
    if len(moves) > 21:
        for i in range(20):
            print(str(i+1)+". " + moves[i]["move"]["name"])
    else:
        counter = 0
        for i in moves:
            print(str(counter+1)+". " + i["move"]["name"])
            counter += 1
    while True:
        move_selected = input("\nChoose your move from the above list.\n").lower()
        if not move_selected.isdigit():
            for i in range(len(moves)):
                if move_selected == moves[i]["move"]["name"]: 
                    move = moves[i]["move"]
                    return move
            print("Invalid Move. Please try again.\n")
        elif move_selected in [str(i+1) for i in range(len(moves))]:
            move = moves[int(move_selected)-1]["move"]
            return move
        else:
            print("Invalid Move.\n")
    return move


def input_pokemon_id(player):
    while True:
        pokemon_id = input(f"\nChoose {player} pokemon name from the below list, or enter a number between 1 to 898: ")
        try:
            pokemon_id = int(pokemon_id)
            if pokemon_id > 0 and pokemon_id < 899:
                break
            print("Invalid number, please try a number between 1 and 898.\n")
        except ValueError:
            if pokemon_id in valid_pokemons:
                break
            else:
                print("Invalid number, please try a number between 1 and 898.\n")
    info_on_pokemon1 = json.loads(
        (requests.get(api_url + "/pokemon/" + str(pokemon_id)).text))
    pokemon = dict()
    pokemon["name"] = info_on_pokemon1["name"]
    pokemon["stats"] = stat_calculator(info_on_pokemon1["stats"])
    pokemon["types"] = info_on_pokemon1["types"]
    pokemon["move"] = input_pokemon_moves(info_on_pokemon1["moves"])
    return pokemon


def main():
    pokemon_ally = input_pokemon_id("your")
    pokemon_enemy = input_pokemon_id("enemy")
    ally_dmg = damage_calculator(pokemon_ally,pokemon_enemy)
    enemy_dmg = damage_calculator(pokemon_enemy,pokemon_ally)
    no_ko_turns_ally = number_of_turns(pokemon_enemy['stats']['hp'], ally_dmg)
    no_ko_turns_enemy = number_of_turns(pokemon_ally['stats']['hp'],enemy_dmg )
    if no_ko_turns_ally < no_ko_turns_enemy:
        print(f"Ally {pokemon_ally['name']} wins in {no_ko_turns_ally} turns")
    elif no_ko_turns_ally == no_ko_turns_enemy:
        if no_ko_turns_ally != 9223372036854775807:
            if pokemon_ally['stats']['speed'] > pokemon_enemy['stats']['speed']:
                print(f"Ally {pokemon_ally['name']} wins in {no_ko_turns_ally} turns")
            elif  pokemon_ally['stats']['speed'] == pokemon_enemy['stats']['speed']:
                print("It is upto chance")
            else:
                print(f"Enemy {pokemon_enemy['name']} wins in {no_ko_turns_enemy} turns")
        else:
            print("They have become pacifists and never faint one another")
    else:
        print(f"Enemy {pokemon_enemy['name']} wins in {no_ko_turns_enemy} turns")


    ally_name = f"{pokemon_ally['name']} (Ally)"
    enemy_name = f"{pokemon_enemy['name']} (Enemy)"
    ally_dmg_done = f"Damage done per turn: {ally_dmg}"
    enemy_dmg_done = f"Damage done per turn: {enemy_dmg}"
    ally_total_hp = f"Total health: {pokemon_ally['stats']['hp']}"
    enemy_total_hp = f"Total health: {pokemon_enemy['stats']['hp']}"
    underline = f"{'-'*30}"
    print()
    print(f"{ally_name: <30}{enemy_name: >30}")
    print(f"{underline: <30}{underline: >30}")
          
    print(f"{ally_dmg_done: <30}{enemy_dmg_done: >30}")
    print(f"{ally_total_hp: <30}{enemy_total_hp: >30}")

    
main()