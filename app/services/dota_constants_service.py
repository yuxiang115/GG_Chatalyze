import requests
import os
from dotenv import load_dotenv
load_dotenv()

heroes = []
items_by_name = []
items_by_id = []
abilities = []
dotaconstants_host = os.getenv("DOTA_CONSTANTS_HOST", "localhost:3000")
data_fetch_url = "http://" + dotaconstants_host + "/api/data?type={}"

def convert_rank_tier(rank_tier):
    if not isinstance(rank_tier, int):
        return "Unknown"
    """Convert rank_tier number to corresponding rank and stars."""
    rank_mapping = {
        1: "Herald/先锋",
        2: "Guardian/卫士",
        3: "Crusader/中军",
        4: "Archon/统帅",
        5: "Legend/传奇",
        6: "Ancient/万古流芳",
        7: "Divine/超凡入圣",
        8: "Immortal/冠绝一世"
    }

    # Extract rank and stars
    rank_group = rank_tier // 10  # Get the tens place (1-8)
    stars = rank_tier % 10  # Get the ones place (0-5)

    # Handle Immortal (no stars)
    if rank_group == 8:
        return "Immortal"

    # Map to rank and stars
    rank = rank_mapping.get(rank_group, "Unknown")
    if 1 <= stars <= 5:
        return f"{rank} {stars} *"
    return f"{rank}"

#call api to get heroes, items, abilities url: localhost:3000/api/data?type=heroes
def load_heroes():
    global heroes
    response = requests.get(data_fetch_url.format("heroes"))
    heroes = response.json()
    heroes = {int(hero_id) : hero for hero_id, hero in heroes.items()}

def load_items():
    global items_by_name, items_by_id
    response = requests.get(data_fetch_url.format("items"))
    items_by_name = response.json()
    for item_name, item in items_by_name.items():
        item['name'] = item_name
    items_by_id = {item['id']: item for item_name, item in items_by_name.items()}


def load_abilities():
    global abilities
    response = requests.get(data_fetch_url.format("ability_ids"))
    abilities_details = requests.get(data_fetch_url.format("abilities")).json()
    abilities = response.json()

    for id, ability in abilities.items():
        if ability in abilities_details:
            abilities_details[ability]['name'] = abilities[id]

    abilities_details_by_id = {}
    for id, ability in abilities.items():
        if ability in abilities_details:
            abilities_details_by_id[int(id)] = abilities_details[ability]
        else:
            abilities_details_by_id[int(id)] = {'name': ability, 'dname': ''}

    abilities = abilities_details_by_id


def load_all_data():
    load_heroes()
    load_items()
    load_abilities()

def fill_match_details(match_details):
    items = {}
    abilities_details_by_name = {}
    for player in match_details["players"]:
        player["hero"] = heroes[player["hero_id"]]['localized_name']
        for i in range(6):
            item_id = player["item_" + str(i)]
            if item_id not in items_by_id:
                player["item_" + str(i)] = None
            else:
                player["item_" + str(i)] = items_by_id[item_id]["dname"]
                if "abilities" in items_by_id[item_id]:
                    items[player["item_" + str(i)]] = {'abilities': items_by_id[item_id]['abilities'], 'cost': items_by_id[item_id]['cost']}

        for i in range(3):
            item_id = player["backpack_" + str(i)]
            if item_id not in items_by_id:
                player["backpack_" + str(i)] = None
            else:
                player["backpack_" + str(i)] = items_by_id[item_id]["dname"]
                if "abilities" in items_by_id[item_id]:
                    items[player["backpack_" + str(i)]] = {'abilities': items_by_id[item_id]['abilities'], 'cost': items_by_id[item_id]['cost']}
        if player['item_neutral'] in items_by_id:
            item_id = player['item_neutral']
            player['item_neutral'] = items_by_id[player['item_neutral']]['dname']
            if 'abilities' in items_by_id[item_id]:
                items[player['item_neutral']] = {'abilities': items_by_id[item_id]['abilities'], 'cost': items_by_id[item_id]['cost']}

        player_ability_upgrades = []
        for ability_id in player['ability_upgrades_arr']:
            if 'dname' in abilities[ability_id]:
                player_ability_upgrades.append(abilities[ability_id]['dname'])
                if 'desc' in abilities[ability_id]:
                    abilities_details_by_name[abilities[ability_id]['dname']] = abilities[ability_id]['desc']
        player['ability_upgrades_arr'] = player_ability_upgrades

        match_details['info'] = {}
        match_details['info']['item_abilities'] = items
        match_details['info']['abilities_details'] = abilities_details_by_name

        rank_tier = player['rank_tier'] if 'rank_tier' in player else None
        player['rank_tier'] = convert_rank_tier(rank_tier)

    for picks_bans in match_details['picks_bans']:
        picks_bans['hero'] = heroes[picks_bans['hero_id']]['localized_name']
        if 'hero_id' in picks_bans:
            picks_bans['hero'] = heroes[picks_bans['hero_id']]['localized_name']
    if '_id' in match_details:
        del match_details['_id']
    return match_details





load_all_data()


