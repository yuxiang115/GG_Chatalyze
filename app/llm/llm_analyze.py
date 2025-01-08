import json
from langchain.chains import LLMChain, SequentialChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
import os
from dotenv import load_dotenv
from app.constant import env_constant
# 加载环境变量
load_dotenv()

# 初始化 OpenAI 模型
llm = OpenAI(model="deepseek-chat", temperature=0.7, openai_api_key=env_constant.DEEPSEEK_API_KEY, base_url='https://api.deepseek.com')

# 定义亮眼玩家分析的 Prompt
highlight_prompt = PromptTemplate(
    input_variables=["match_details"],
    template=(
        "以下是比赛的详细数据：\n{match_details}\n"
        "请使用中文和英文描述英雄名称，并且在分析玩家的的时候，提及他们的personaname, 如果没有personaname 就用 ‘匿名玩家’"
        "请从以下角度分析本场比赛中玩家表现, 列出胜方亮眼玩家们的表现，如果败方也有亮眼玩家，分析他的表现，分析这玩家对队伍的影响：\n"
        "1. 关键数据：包括击杀（Kills）、死亡（Deaths）、助攻（Assists）、金钱获取（GPM）、经验获取（XPM）、净值、英雄伤害、推塔伤害, 承受伤害等。关键数据写在一行\n"
        "2. 角色定位：分析该玩家在团队中的角色，例如经济核心、爆发输出、辅助等。\n"
        "3. 出装与策略：说明其主要装备选择和对战局的影响。\n"
        "玩家段位为他们的 rank_tier, 将下面的rank_tier 替换成比赛玩家数据里面的value\n"
        "\n请严格按照以下分层次格式输出，并确保子项是 sublist（缩进一个 tab 的内容）：\n"
        "请按照以下格式输出：\n"
        "- 玩家名称（角色）：XXX  rank_tier\n"
        "\t- 关键数据：...\n"
        "\t- 角色定位：...\n"
        "\t- 出装与策略：...\n"
    )
)

# 定义表现不佳玩家分析的 Prompt
underperform_prompt = PromptTemplate(
    input_variables=["match_details"],
    template=(
        "以下是比赛详情和玩家分析：\n比赛详情：{match_details}\n玩家分析：{highlights}\n"
        "请使用中文和英文描述英雄名称，并且在分析玩家的的时候，提及他们的personaname, 如果没有personaname 就用 ‘匿名玩家’"
        "请分析本场比赛中失败队伍表现不佳的玩家，主要导致队伍失败的玩家，重点关注以下几点：\n"
        "1. 关键数据：包括击杀（Kills）、死亡（Deaths）、助攻（Assists）、金钱获取（GPM）、经验获取（XPM）、净值、英雄伤害、推塔伤害, 承受伤害等。关键数据写在一行\n"
        "2. 问题分析：分析其低表现的原因，例如死亡次数过高、经济落后、定位错误等。 还要分析这个玩家的出装有哪些方面的问题\n"
        "3. 改进建议：给出针对该玩家的改进建议。包括出装改进建议，以及原先出装的问题所在\n"
        "4. 点名批评：最后着重点名批评是哪位玩家在队伍中严重拖后腿，导致队伍失败，以及应该如何提升\n"

        "玩家段位为他们的 rank_tier, 将下面的rank_tier 替换成比赛玩家数据里面的value\n"
        "\n请严格按照以下分层次格式输出，并确保子项是 sublist（缩进一个 tab 的内容）：\n"
        "请按照以下格式输出：\n"
        "- 玩家名称（角色）：XXX  rank_tier\n"
        "\t- 关键数据：...\n"
        "\t- 问题分析：...\n"
        "\t- 改进建议：...\n"
    )
)

# 定义比赛总结的 Prompt
summary_prompt = PromptTemplate(
    input_variables=["match_details", "highlights", "underperform"],
    template=(
        "以下是比赛详情、亮眼玩家分析和表现不佳玩家分析：\n比赛详情：{match_details}\n"
        "请使用中文和英文描述英雄名称，并且在分析玩家的的时候，提及他们的personaname, 如果没有personaname 就用 ‘匿名玩家’"
        "亮眼玩家分析：{highlights}\n表现不佳玩家分析：{underperform}\n"
        "请总结本场比赛的整体表现，包括：\n"
        "1. 胜负结果：哪个队伍获胜，比分如何，主要原因是什么？\n"
        "2. 亮点选手与策略：分析获胜队伍中表现突出的选手及其关键策略。\n"
        "3. 问题与失误：分析失败队伍中存在的问题，如战术失误、资源分配不均等。\n"
        "4. 改进建议：给出针对失败队伍的整体改进建议。\n"
        "请按照以下格式输出：\n"
        "### 胜负结果\n"
        "...\n\n"
        "### 亮点选手与策略\n"
        "...\n\n"
        "### 问题与失误\n"
        "...\n\n"
        "### 改进建议\n"
        "...\n"
    )
)

# 创建 LangChain 的 LLMChain
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

# 分析函数
def analyze(match_details):
    print("Analyzing match details...")
    result = overall_chain.invoke({"match_details": match_details})
    return result

