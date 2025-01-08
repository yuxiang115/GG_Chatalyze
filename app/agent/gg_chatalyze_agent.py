import logging
import re

from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool

from app.constant import env_constant
from app.repository import player_repository
from app.services import match_analyze_service
import json

from app.controller import player_controller

# 加载环境变量
discord_bot_token = env_constant.DISCORD_BOT_TOKEN

llm = ChatOpenAI(model="deepseek-chat", temperature=0.7, openai_api_key=env_constant.DEEPSEEK_API_KEY, base_url='https://api.deepseek.com')

def load_args(input_str):
    try:
        cleaned_input = re.sub(r'```(?:json)?|```', '', input_str).strip()
        # 使用正则表达式提取 JSON 部分
        json_match = re.search(r'\{[\s\S]*\}', cleaned_input)
        if not json_match:
            error = f"input: {input_str}, No JSON object found in the input, please provide a valid JSON string"
            logging.error(error)
            raise ValueError(error)

        # 获取匹配的 JSON 字符串部分
        json_str = json_match.group(0)

        # 尝试将其解析为 JSON 对象
        json_obj = json.loads(json_str)

        return json_obj
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON Decode Error: {e}, input: {input_str}")
    except Exception as e:
        raise ValueError(f"Unexpected Error: {e}, input: {input_str}")




def analyze_match(args: str):
    try:
        args = load_args(args)
    except Exception as e:
        return {"message": str(e)}
    res = match_analyze_service.analyze_match(args['match_id'])
    return res['match_detail']

def analyze_most_recently_match_for_player(args: str):
    try:
        args = load_args(args)
    except Exception as e:
        return {"message": str(e)}
    res = match_analyze_service.refresh_matches_by_player_ids([args["player_id"]])
    if len(res) == 0:
        return {"message": "No match found for this player： " + args["player_id"]}
    match = res[0]
    return match['match_detail']

def analyze_most_recently_match_for_player_by_discord_name(args: str):
    try:
        args = load_args(args)
    except Exception as e:
        return {"message": str(e)}
    player_db = player_repository.fetch_player_by_discord_name(args["discord_name"])
    if not player_db:
        return {"message": "Player not found!"}
    res = match_analyze_service.refresh_matches_by_player_ids([player_db["player_id"]])
    if len(res) == 0:
        return {"message": "No match found for this player： " + player_db["player_id"]}
    match = res[0]
    return match['match_detail']

def analyze_most_recently_match_for_player_by_discord_id(args: str):
    try:
        args = load_args(args)
    except Exception as e:
        return {"message": str(e)}
    player_db = player_repository.fetch_player_by_discord_id(args["discord_id"])
    if not player_db:
        return {"message": "Player not found!"}
    res = match_analyze_service.refresh_matches_by_player_ids([player_db["player_id"]])
    if len(res) == 0:
        return {"message": "No match found for this player： " + player_db["player_id"]}
    match = res[0]
    return match['match_detail']

def enable_auto_analyze(args: str):
    args = load_args(args)
    player_db = player_repository.get_player(args["player_id"])
    if not player_db:
        return {"message": "Please contact the admin to add your player info!"}
    return player_controller.enable_auto_analyze(player_id=args["player_id"], hours=args["hours"], discord_id=args.get("discord_id", None))


# 初始化 GPT-4 模型

tools = [
    Tool(name="Analyze Match", func=analyze_match, description="Analyze a specific match by match_id. input is a JSON string with: required parameters: match_id"),
    Tool(name="Enable Auto Analyze", func=enable_auto_analyze,
         description="Enable automatic match analysis for a player with most recently matches. "
                     "input is a JSON string with: "
                     "required parameters: player_id, hours (hours > 0), "
                     "optional: discord_id"),
    Tool(name="Analyze Most Recently Match By Player ID", func=analyze_most_recently_match_for_player,
         description="Analyze the most recently match for a player. input is a JSON string with: required parameters: player_id"),
    Tool(name="Analyze Most Recently Match By Discord Name", func=analyze_most_recently_match_for_player_by_discord_name,
         description="Analyze the most recently match for a player by their discord_name. input is a JSON string with: required parameters: discord_name"),
    Tool(name="Analyze Most Recently Match By Discord ID",
         func=analyze_most_recently_match_for_player_by_discord_id,
         description="Analyze the most recently match for a player by their discord_id. input is a JSON string with: required parameters: discord_id")

]



agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)

tools_descriptions = "\n".join([f"{tool.name}: {tool.description}" for tool in tools])
