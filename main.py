import requests, json
from random import randint

with open("board.json") as f:
    typechart = json.loads(f.read())
with open("valid_pokemons.json") as f:
    valid_pokemons = json.loads(f.read())
    
api_url = "https://pokeapi.co/api/v2"

def hp_calculator(base_hp):
    return (2 * base_hp) + 110

def other_stat_calculator(base_stat):
    return (2 * base_stat) + 5

def stat_calculator(stat):
    '''Applies the Stat Growth formula of Gen3 onwards assuming level is 100 , EVs and IVs are 0'''
    cstat={stat[i]["stat"]["name"] : other_stat_calculator(stat[i]["base_stat"]) for i in range(1,6)}
    cstat["hp"]=hp_calculator(stat[0]["base_stat"])
    return cstat
  # Assumption

def damage_calculator(info,move_num):
    '''Applies the Damage formula of Gen3 onwards'''
    move_url=info["moves"][move_num]["move"]["url"]
    move_info=json.loads((requests.get(move_url).text))
    power=move_info["power"]
    random=randint(85,100)/100
    # Remaining factors
    damage=(0.84*power*a_d+2)*random
    return damage

def input_pokemon_moves(moves):
    if len(moves) > 21:
        for i in range(20):
            print(moves[i]["move"]["name"])
    else:
        for i in moves:
            print(i["move"]["name"])
    while(True):
        move_selected = input("Enter the move from the list above \n").lower()
        if move_selected in [moves[i]["move"]["name"] for i in range(len(moves))]:
            break
        print("Invalid Move. Please try again")
    return move_selected

    
def input_pokemon_id():
    while True:    
        pokemon_id = input("Enter your pokemon name or enter a number between 1 to 898: ")
        try:
            pokemon_id = int(pokemon_id)
            if pokemon_id > 0 and pokemon_id < 899:
                break
            print("Invalid number, please try a number between 1 and 898.")
        except ValueError:
            if pokemon_id in valid_pokemons:
                return str(pokemon_id)
            else:
                print("Invalid number, please try a number between 1 and 898.")
    return str(pokemon_id)
    

def main():
    pokemon_ally_id = input_pokemon_id()
    info_on_pokemon1 = json.loads((requests.get(api_url + "/pokemon/" + pokemon_ally_id).text))
    pokemon_ally = dict()
    pokemon_ally["name"] = info_on_pokemon1["name"]
    pokemon_ally["stats"] = stat_calculator(info_on_pokemon1["stats"])
    pokemon_ally["move"] = input_pokemon_moves(info_on_pokemon1["moves"])
    print(pokemon_ally["move"])
        
    pokemon_enemy_id = input_pokemon_id()
    info_on_pokemon2 = json.loads((requests.get(api_url + "/pokemon/" + pokemon_enemy_id).text))
    
    pokemon_enemy = dict()
    pokemon_enemy["name"] = info_on_pokemon2["name"]
    pokemon_enemy["stats"] = stat_calculator(info_on_pokemon2["stats"])
    print(pokemon_enemy)


# test = json.loads((requests.get(api_url+"/move/tackle").text))

main()
# print(input_pokemon_id())