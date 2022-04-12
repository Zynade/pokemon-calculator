import main
import requests
import streamlit as st
import json

with open("valid_pokemons.json") as f:
    valid_pokemons = json.load(f)
with open("nature.json") as f:
    nature=json.load(f)
api_url = "https://pokeapi.co/api/v2"

def move_list(pkm):
    moves = []
    info_on_pokemon = json.loads(
        (requests.get(api_url + "/pokemon/" + str(pkm)).text))
    for i in info_on_pokemon['moves']:
        moves.append(i['move']['name'])
    return sorted(moves)

def nature_view(nat):
    l = []
    for i in nat:
        l.append(i['name'])
    return l


pokemon_ally = {}
pokemon_enemy = {}
st.title("Pokemon Calculator")
col0_1, col0_2, col0_3 = st.columns(3)

with col0_1:
    pokemon_ally['name'] = st.selectbox("Choose Ally Pokemon", valid_pokemons)
    pokemon_ally['lvl'] = st.slider("Level", 1, 100)
    pokemon_ally['iv'] = st.number_input("IV", 1, 31)
    pokemon_ally['ev'] = st.number_input("EV", 1, 31)
    pokemon_ally['nature'] = st.selectbox("Nature", nature_view(nature))
    pokemon_ally['move'] = st.selectbox("Choose Move", move_list(pokemon_ally['name']))

with col0_2:
    st.write('Result')

with col0_3:
    pokemon_enemy['name'] = st.selectbox("Choose Enemy Pokemon", valid_pokemons, key = "enemy")
    pokemon_enemy['lvl'] = st.slider("Level", 1, 100, key = "enemylvl")
    pokemon_enemy['iv'] = st.number_input("IV", 1, 31, key = "enemyiv")
    pokemon_enemy['ev'] = st.number_input("EV", 1, 31, key = "enemyev")
    pokemon_enemy['nature'] = st.selectbox("Nature", nature_view(nature), key = "enemynat")
    pokemon_enemy['move'] = st.selectbox("Choose Move", move_list(pokemon_enemy['name']), key = "enemymove")
    
col1_1, col1_2, col1_3,col1_4,col1_5 = st.columns(5)
with col1_1:
        pass
with col1_2:
    pass
with col1_3:
    calc = st.button("Calculate")
    
with col1_4:
    pass
with col1_5:
    pass
if calc:
    with col0_2:
        # st.write('Past stats')
        statistics = main.get_output(pokemon_ally,pokemon_enemy)
        print(statistics)
        st.write(f"{statistics['winner_cat']} wins!")
        st.write(f"Winning Pokemon: {statistics['winner_name']}")
        st.write(f"{statistics['winner_turns']} turns taken!")
        # Pokemon: {statistics['winner_name']}
        # Number of turns taken: {statistics['winner_turns']}""")