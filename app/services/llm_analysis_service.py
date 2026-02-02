import json

from langchain.chains import LLMChain, SequentialChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

from app.constant import env_constant

# 加载环境变量
load_dotenv()

# 初始化 GPT-4 模型
llm = ChatOpenAI(model=env_constant.LLM_MODEL, temperature=0.7, openai_api_key=env_constant.LLM_API_KEY, base_url=env_constant.LLM_HOST)



# 定义各部分任务的 Prompt
highlight_prompt = PromptTemplate(

    input_variables=["match_details"],
    template=(
        "你是一位资深Dota2战术分析师兼中文解说员，请阅读以下比赛 JSON 数据，并输出一份『亮眼玩家分析报告』，该报告将用于赛后复盘并展示在公开社群中。\n\n"
        "【比赛数据】：\n{match_details}\n\n"

        "【任务目标】：\n"
        "请你基于该场比赛的数据，输出胜方队伍（Dire）中**表现突出的选手分析**，并挑选败方（Radiant）中**少数依然发挥出色的选手**进行表扬。\n"
        "请根据实际数据，分析每位选手的表现价值，并给出战术定位和对比赛胜负的贡献判断。\n\n"

        "【写作要求】：\n"
        "- 请使用生动、专业、通俗的中文写作风格，像一个知乎高赞贴或B站UP主的视频稿。\n"
        "- 每位选手请以“标题 + 项目符号”输出，突出他们的英雄（中英文）与 personaname。\n"
        "- 如果 personaname 为空，请使用“匿名玩家”代称。\n"
        "- 用 Bullet List 列出：\n"
        "  1. 📊 关键数据（Kills/Deaths/Assists, GPM, XPM, 英雄伤害, 推塔伤害）\n"
        "  2. 🎮 角色定位（例如核心输出、控制型辅助、前排坦克等）\n"
        "  3. 🧠 战术影响力分析：关键团战、带节奏能力、控图能力等\n"
        "  4. ⚙️ 出装与打法评价：装备是否契合，是否突出技能机制优势\n"
        "- **重点在于给出“评价”与“判断”，而不是仅罗列数据。**\n"
        "- 每个段落都应体现“数据支撑 + 评价 + 战术解读”三者结合。\n"

        "【结构格式】：请严格使用以下格式输出（多个玩家逐个输出）：\n\n"
        "### 🔥 玩家：personaname (hero_en / hero_cn) - Rank：rank_tier\n"
        "- 📊 **关键数据**：Kills: X / Deaths: X / Assists: X | GPM: XXX | XPM: XXX | Hero Damage: XXXX | Tower Damage: XXXX\n"
        "- 🎮 **角色定位**：XXXX（例如“远程后排输出核心”、“视野型功能辅助”）\n"
        "- 🧠 **战术表现与影响力**：请分析该玩家在比赛中对节奏、团战、关键时刻的贡献。例如是否多次先手开团、是否成功打出关键控制、是否打出爆发翻盘等。\n"
        "- ⚙️ **出装与打法评价**：是否契合英雄定位？有无亮点或明显不足？出装是否合理支撑其团战定位？\n\n"
        "请输出胜方关键选手 2~4 位，若败方中有选手输出或节奏极其出色，也请加以分析。\n"
        "请勿出现“以下是XXX”、“数据如下”等系统化描述，直接进入内容输出。\n"
    )
)

underperform_prompt = PromptTemplate(
    input_variables=["match_details", "highlights"],
    template=(
        "你是一名Dota2职业战队的数据分析师兼战术教练，任务是分析以下比赛中**失败方队伍中表现最不理想的选手**，并给出专业点评与提升建议。\n\n"
        "【比赛数据】：\n{match_details}\n\n"
        "【亮眼选手参考】（用于对比）：\n{highlights}\n\n"
        "【任务说明】：\n"
        "- 请找出 Radiant（败方）中表现严重落后的1~2位玩家，并从战术角度分析其低效表现是否导致了团队节奏断裂。\n"
        "- 必须指出最严重拖后腿的选手，并提供“问题 + 证据 + 建议”三位一体的点评。\n\n"

        "【每位玩家分析请包含以下内容】：\n"
        "### 😞 玩家：personaname (hero_en / hero_cn) - Rank：rank_tier\n"
        "- 📉 **关键数据**：Kills: X / Deaths: X / Assists: X | GPM: XXX | XPM: XXX | Hero DMG: XXXX | Tower DMG: XXXX\n"
        "- ⚠️ **问题分析**：请结合数据判断问题出现在哪里，例如：频繁死亡是否因走位失误、经济落后是否因游走无果或抢线、出装是否偏离英雄定位、参战率是否不足、是否未能对敌方后排造成有效威胁等。\n"
        "- 🧩 **战术脱节表现**：指出其在关键团战或资源争夺中缺席或失误的时机，是否拖慢了团队推进节奏或导致失败的决策。\n"
        "- 🛠️ **改进建议**：请从出装优化、打法风格调整、技能使用习惯等方面提出专业提升建议，不要泛泛而谈。\n\n"

        "【最终结论】：\n"
        "在所有败方选手中，**请点名指出“最严重拖后腿”的玩家**，写一段简明但有冲击力的总结性点评。\n"
        "请注意保持专业和理性语气，不使用侮辱性词语，但语言应有力量。\n\n"

        "【额外说明】\n"
        "- 所有英雄请使用中英文并列方式写出（如 Riki / 力丸）\n"
        "- 如果没有 personaname，请使用“匿名玩家”代替\n"
        "- 请写得像一篇知乎复盘帖，专业、带感、有逻辑\n"
    )
)

summary_prompt = PromptTemplate(
    input_variables=["match_details", "highlights", "underperform"],
    template=(
        "你是一位Dota 2专业赛事解说员兼战队分析师，请根据以下比赛数据和分析内容撰写一份完整的比赛总结，风格应当专业清晰、富有逻辑，同时语言有感染力。\n\n"
        "【比赛基础信息】\n{match_details}\n\n"
        "【亮眼玩家表现分析】\n{highlights}\n\n"
        "【失败方低表现分析】\n{underperform}\n\n"
        "【写作要求】\n"
        "- 使用中文写作，尽量以**教练+战术分析+职业解说**风格呈现；\n"
        "- 引用关键玩家（personaname）和英雄名时，请使用“中英文并列”方式（如 Sniper / 狙击手）；\n"
        "- 使用 bullet 和 markdown 标题结构，确保逻辑清晰；\n"
        "- 分析内容中应体现：对局势走势的判断、选手发挥的战术意义、关键物品/团战的作用、失误的代价与纠正路径；\n"
        "- 内容应为：基于数据 → 提出观点 → 给出判断。\n\n"
        "【总结内容结构】请严格按照以下结构与标题输出：\n\n"
        "### 🏆 胜负结果\n"
        "- 哪个队伍获胜？比分如何？\n"
        "- 指出决定胜负的关键因素，例如经济领先、团战控制、推塔压制等。\n\n"
        "### ✨ 亮点选手与关键策略\n"
        "- 聚焦胜方 2~3 位关键选手：他们的发挥如何带动全队？使用了哪些装备/技能组合？\n"
        "- 分析战术执行层面的成功因素（如换线、带线节奏、野区压制、先手控制等）。\n\n"
        "### ⚠️ 失败方问题与失误点\n"
        "- 哪些选手未能完成战术目标？失误点主要集中在哪些方面？\n"
        "- 是否存在资源分配混乱、出装错误、打团决策失衡？\n"
        "- 对位差距是否造成致命后果？\n\n"
        "### 🛠️ 整体改进建议\n"
        "- 给出战术层面、出装选择、团战协作、资源利用等方面的具体改进建议\n"
        "- 提出可以在下次比赛中重点优化的策略（如：前中期入侵节奏、团队沟通、单核转双核等）\n\n"
        "请避免使用“如下”、“以下是…”等机械化词汇，直接进入内容。写得像一篇知乎复盘贴或高水平战队训练日志。"
    )
)

# 定义每一步的 LLMChain
highlight_chain = LLMChain(llm=llm, prompt=highlight_prompt, output_key="highlights")
underperform_chain = LLMChain(llm=llm, prompt=underperform_prompt, output_key="underperform")
summary_chain = LLMChain(llm=llm, prompt=summary_prompt, output_key="summary")

# 使用 SequentialChain 串联步骤
overall_chain = SequentialChain(
    chains=[highlight_chain, underperform_chain, summary_chain],
    input_variables=["match_details"],
    output_variables=["highlights", "underperform", "summary"],
    verbose=True,
)


def analyze(match_details):
    print(f"""Analyzing match details: \n{json.dumps(match_details)}""")
    result = overall_chain.invoke({"match_details": match_details})
    return {'highlights': result["highlights"], 'underperform': result["underperform"], 'summary': result["summary"]}

