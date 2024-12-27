import openai
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_analysis(match_details):
    """Generate match analysis using OpenAI with Markdown format."""
    system_content = """
    你是一位专业的 Dota 2 分析师，擅长用生动的语言和细致的洞察分析比赛。你的分析应包含以下特点：
    1. **语言生动**：使用引人入胜的描述，比如“这位玩家的精准技能释放在团战中成为致胜关键”。
    2. **挖掘细节**：提到比赛关键点，如某次精彩的团战、地图控制或出装选择的亮点与失误。
    3. **全面分析**：不仅关注玩家的击杀和助攻，还要结合经济、团队协作、技能使用等多方面评价。
    4. **分析胜利失败** 分析胜利队伍中，哪个玩家起到关键性的作用，以及失败队伍中，哪些环节导致了失利，以及哪些玩家表现不佳以及不佳的行为，提出改进建议。
    """
    prompt = f"""
    你是一个专业的Dota 2分析师，根据以下比赛数据完成分析：
    {match_details}
    请按照 Markdown 格式输出内容，并包含以下部分：
    1. 比赛结果
    2. 玩家表现
    3. 团队表现
    4. 比赛走势
    5. 改进建议
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt},
        ],
        max_tokens=2000,
        temperature=0.9,
    )
    return response.choices[0].message['content'].strip()

