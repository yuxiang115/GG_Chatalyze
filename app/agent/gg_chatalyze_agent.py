import re
from datetime import datetime, timedelta

from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from app.repository import player_repository
from app.services import open_dota_api_service
from app.services import match_analyze_service
import json

from app.controller import match_controller, player_controller
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
discord_bot_token = os.getenv("DISCORD_BOT_TOKEN")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, openai_api_key=os.getenv("OPENAI_API_KEY"))


def load_args(input_str):
    try:
        # 使用正则表达式提取 JSON 部分
        json_match = re.search(r'\{.*?\}', input_str)
        if not json_match:
            raise ValueError("No JSON object found in the input, please provide a valid JSON string")

        # 获取匹配的 JSON 字符串部分
        json_str = json_match.group(0)

        # 尝试将其解析为 JSON 对象
        json_obj = json.loads(json_str)

        return json_obj
    except json.JSONDecodeError:
        raise ValueError("Please provide a valid JSON string as input")
    except Exception as e:
        raise ValueError(f"未知错误：{str(e)}")




def analyze_match(args: str):
    args = load_args(args)
    res = match_analyze_service.analyze_match(args['match_id'])
    return res

def analyze_most_recently_match_for_player(args: str):
    args = load_args(args)

    res = match_analyze_service.refresh_matches_by_player_ids([args["player_id"]])
    if len(res) == 0:
        return {"message": "No match found for this player： " + args["player_id"]}
    match = res[0]
    return match



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
    Tool(name="Analyze Most Recently Match", func=analyze_most_recently_match_for_player,
         description="Analyze the most recently match for a player. input is a JSON string with: required parameters: player_id")
]



agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)

tools_descriptions = "\n".join([f"{tool.name}: {tool.description}" for tool in tools])
