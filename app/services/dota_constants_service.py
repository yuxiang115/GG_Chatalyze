import json

import requests
import os
from dotenv import load_dotenv
load_dotenv()

heroes = []
items_by_name = []
items_by_id = []
abilities = []
game_mode = {}
team_by_id = {0: "Radiant", 1: "Dire"}

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

def load_game_mode():
    global game_mode
    response = requests.get(data_fetch_url.format("game_mode"))
    result = response.json()
    game_mode = {int(game_mode_id): game_mode['name'] for game_mode_id, game_mode in result.items()}
    for game_mode_id, game_mode_name in game_mode.items():
        game_mode[game_mode_id] = game_mode_name.replace("game_mode_", "").replace("_", " ").title()

def load_all_data():
    load_heroes()
    load_items()
    load_abilities()
    load_game_mode()


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

    return simplify_match_detail(match_details)

def format_float(value):
    if isinstance(value, float):
        return round(value, 2)  # 保留两位小数
    return value

def simplify_match_players(match_details):
    simplified_players = []
    for player in match_details["players"]:
        if_win = (
            player["radiant_win"] and player["team_number"] == 0
            or not player["radiant_win"] and player["team_number"] == 1
        )

        # 处理 benchmarks，确保字段存在并格式化浮点数
        benchmarks = {
            key: {
                "value": format_float(player.get("benchmarks", {}).get(key, {}).get("raw", "Unknown")),
                "percentile": format_float(player.get("benchmarks", {}).get(key, {}).get("pct", 0) * 100)
            }
            for key in [
                "gold_per_min",
                "xp_per_min",
                "kills_per_min",
                "last_hits_per_min",
                "hero_damage_per_min",
                "hero_healing_per_min",
                "tower_damage"
            ]
        }

        # 构建简化后的玩家数据，仅插入存在的键值
        simplified_player = {}
        keys_to_include = [
            "account_id", "personaname", "player_slot", "team_number", "hero", "level",
            "leaver_status", "item_neutral", "rank_tier", "kills", "deaths", "assists",
            "last_hits", "denies", "gold_per_min", "xp_per_min", "total_xp", "net_worth",
            "aghanims_scepter", "aghanims_shard", "moonshard", "hero_damage",
            "tower_damage", "hero_healing", "gold", "gold_spent", "ability_upgrades_arr",
            "kills_per_min", "kda", "abandons"
        ]

        for key in keys_to_include:
            if key in player:
                simplified_player[key] = player[key]

        # 处理布尔值和其他逻辑字段
        simplified_player["win"] = if_win
        simplified_player["benchmarks"] = benchmarks

        # 处理 Inventory，排除为 None 或 "None" 的物品
        simplified_player["Inventory"] = [
            item for item in [
                player.get("item_0"), player.get("item_1"), player.get("item_2"),
                player.get("item_3"), player.get("item_4"), player.get("item_5")
            ] if item and item != "None"
        ]

        simplified_players.append(simplified_player)

    return simplified_players

def simplify_match_detail(match_detail):
    simplified_match = {
        "match_id": match_detail.get("match_id", None),
        "team_won": "Radiant" if match_detail.get("radiant_win", False) else "Dire",
        "duration": (
            f"{format_float(match_detail.get('duration', 0) / 60)} minutes"
            if "duration" in match_detail
            else "Unknown"
        ),
        "game_mode": game_mode.get(match_detail.get("game_mode", -1), None),
        "radiant_score": match_detail.get("radiant_score", None),
        "dire_score": match_detail.get("dire_score", None),
        "start_time": match_detail.get("start_time", None),
        "item_and_ability_logs": match_detail.get("info", []),
        "players": simplify_match_players(match_detail)
    }
    return simplified_match





load_all_data()

#open json file load data
# def load_match_details(file_path):
#     with open(file_path, "r", encoding="utf-8") as file:
#         return json.load(file)
#
# match_detail = load_match_details("../match_detail.json")
# res = simplify_match_detail(match_detail)
# # import llm_analysis_service as llm_analysis
# # res = llm_analysis.analyze(res)
# # from app.discord_util import discordWebhook as discordWebhook
# # content = [f'### Match ID: {match_detail["match_id"]}'] + [message for message in res.values()]
# # discordWebhook.send(content)
# print(res)

