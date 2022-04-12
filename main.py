import requests
import json
from random import randint
from math import floor, ceil

with open("board.json") as f:
    typechart = json.load(f)
with open("valid_pokemons.json") as f:
    valid_pokemons = json.load(f)
with open("nature.json") as f:
    nature=json.load(f)
valid_natures=[dic["name"] for dic in nature]

api_url = "https://pokeapi.co/api/v2"


def hp_calculator(base_hp,level,iv,ev):
    """A simplified HP formula is used"""
    return floor((2 * base_hp+iv+floor(ev/4))*level*0.01) + level+10


def other_stat_calculator(base_stat,level,iv,ev,nat):
    """A simplified stat formula is used"""
    return floor((floor((2 *base_stat+iv+floor(ev/4)*level*0.01) + 5)*nat))

def stat_calculator(stat,level,ev,iv,nat):
    '''Applies the Stat Growth formula of Gen3 onwards assuming level is 100 , EVs and IVs are 0'''
    api_dict={"attack":"atk","defense":"def","special-attack":"spa","special-defense":"spd","speed":"spe"}
    cstat=dict()
    for i in range(1, 6):
        nam=stat[i]["stat"]["name"]
        natur=[diction for diction in nature if diction["name"]==nat]
        natur=natur[0][api_dict[nam]]
        cstat[nam] = other_stat_calculator(stat[i]["base_stat"],level,ev,iv, natur)
    cstat["hp"] = hp_calculator(stat[0]["base_stat"],level,iv,ev)
    return cstat
  # Assumption


def damage_calculator(attack_pokemon, defend_pokemon):
    '''Applies the Damage formula of Gen3 onwards'''
    attack_stats=stat_dict(attack_pokemon)
    defense_stats=stat_dict(defend_pokemon)
    temp=json.loads((requests.get(api_url+
                                "/pokemon/"+attack_pokemon["name"]).text))
    temp=[elem for elem in temp["moves"] if elem["move"]["name"]==attack_pokemon["move"]][0]
    move_url = temp["move"]["url"]
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
    for i in defense_stats["types"]:
        # i is {type:{name:val}......} 
        type_effectiveness *= typechart[attack["type"]][i["type"]["name"]]
    if attack["combat"] == "physical":
        damage = floor(((2*attack_pokemon['lvl']+10)*attack["power"]*attack_stats["stats"]["attack"]/defense_stats["stats"]["defense"]+100)*type_effectiveness*random)/50
    else:
        damage = floor(((2*attack_pokemon['lvl']+10)*attack["power"]*attack_stats["stats"]["special-attack"]/defense_stats["stats"]["special-defense"]+100)*type_effectiveness*random)/50
    return damage

def number_of_turns(health, damage):
    if damage!=0:
        return ceil(health/damage)
    # max integer possible as can never beat it
    return 9223372036854775807

# def input_pokemon_moves(moves):
#     move = dict()
#     if len(moves) > 21:
#         for i in range(20):
#             print(str(i+1)+". " + moves[i]["move"]["name"])
#     else:
#         counter = 0
#         for i in moves:
#             print(str(counter+1)+". " + i["move"]["name"])
#             counter += 1
#     while True:
#         move_selected = input("\nChoose your move from the above list.\n").lower()
#         if not move_selected.isdigit():
#             for i in range(len(moves)):
#                 if move_selected == moves[i]["move"]["name"]: 
#                     move = moves[i]["move"]
#                     return move
#             print("Invalid Move. Please try again.\n")
#         elif move_selected in [str(i+1) for i in range(len(moves))]:
#             move = moves[int(move_selected)-1]["move"]
#             return move
#         else:
#             print("Invalid Move.\n")
#     return move


def stat_dict(pkm):
    info_on_pokemon1 = json.loads(
        (requests.get(api_url + "/pokemon/" + str(pkm['name'])).text))
    pokemon = dict()
    pokemon["name"] = pkm["name"]
    pokemon["stats"] = stat_calculator(info_on_pokemon1["stats"],pkm['lvl'],pkm['ev'],pkm['iv'],pkm["nature"])
    pokemon["types"] = info_on_pokemon1["types"]
    pokemon["move"] = pkm["move"]
    return pokemon


def get_output(ally,enemy):
    statistics = {}
    ally_stats=stat_dict(ally)
    enemy_stats=stat_dict(enemy)
    ally_dmg = damage_calculator(ally,enemy)
    enemy_dmg = damage_calculator(enemy,ally)
    no_ko_turns_ally = number_of_turns(enemy_stats['stats']['hp'], ally_dmg)
    no_ko_turns_enemy = number_of_turns(ally_stats['stats']['hp'],enemy_dmg )
    if no_ko_turns_ally < no_ko_turns_enemy:
        # print(f"Ally {pokemon_ally['name']} wins in {no_ko_turns_ally} turns")
        statistics['winner_cat'] = "Ally"
        statistics['winner_name'] = ally['name']
        statistics['winner_turns'] = no_ko_turns_ally
        
    elif no_ko_turns_ally == no_ko_turns_enemy:
        if no_ko_turns_ally != 9223372036854775807:
            if ally['stats']['speed'] > enemy['stats']['speed']:
                # print(f"Ally {pokemon_ally['name']} wins in {no_ko_turns_ally} turns")
                statistics['winner_cat'] = "Ally"
                statistics['winner_name'] = ally['name']
                statistics['winner_turns'] = no_ko_turns_ally
            elif  ally['stats']['speed'] == enemy['stats']['speed']:
                print("It is upto chance")
            else:
                # print(f"Enemy {pokemon_enemy['name']} wins in {no_ko_turns_enemy} turns")
                statistics['winner_cat'] = "Enemy"
                statistics['winner_name'] = enemy['name']
                statistics['winner_turns'] = no_ko_turns_enemy
        else:
            print("They have become pacifists and never faint one another")
    else:
        # print(f"Enemy {pokemon_enemy['name']} wins in {no_ko_turns_enemy} turns")
        statistics['winner_cat'] = "Enemy"
        statistics['winner_name'] = ally['name']
        statistics['winner_turns'] = no_ko_turns_enemy

    return statistics
    # ally_name = f"{pokemon_ally['name']} (Ally)"
    # enemy_name = f"{pokemon_enemy['name']} (Enemy)"
    # ally_dmg_done = f"Damage done per turn: {ally_dmg}"
    # enemy_dmg_done = f"Damage done per turn: {enemy_dmg}"
    # ally_total_hp = f"Total health: {pokemon_ally['stats']['hp']}"
    # enemy_total_hp = f"Total health: {pokemon_enemy['stats']['hp']}"
    # underline = f"{'-'*30}"
    # print()
    # print(f"{ally_name: <30}{enemy_name: >30}")
    # print(f"{underline: <30}{underline: >30}")
          
    # print(f"{ally_dmg_done: <30}{enemy_dmg_done: >30}")
    # print(f"{ally_total_hp: <30}{enemy_total_hp: >30}")

    
# main()