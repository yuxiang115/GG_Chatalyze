import os
import json
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI

# 加载环境变量
load_dotenv()

# 初始化 OpenAI GPT 模型
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=1.0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# 步骤 1：加载 JSON 数据并分段
def load_match_details(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def segment_data(data, chunk_size=500):
    """
    将 JSON 数据分段为小块文本。
    """
    data_str = json.dumps(data, ensure_ascii=False)
    return [data_str[i:i + chunk_size] for i in range(0, len(data_str), chunk_size)]

# 假设你的比赛数据存储在 match_detail.json

segments = segment_data(match_data, chunk_size=500)

# 步骤 2：构建向量数据库
print("正在构建向量数据库...")
embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
vectorstore = FAISS.from_texts(segments, embeddings)
print("向量数据库构建完成！")

# 步骤 3：定义多段 PromptTemplates
overview_prompt = PromptTemplate(
    input_variables=["context"],
    template=(
        "根据以下比赛数据，撰写比赛概况，包括以下内容：\n"
        "- 比赛时长\n"
        "- 胜利方及其胜利原因（团队合作、关键决策、装备等）。\n\n"
        "比赛数据：{context}\n"
    ),
)

radiant_players_prompt = PromptTemplate(
    input_variables=["context"],
    template=(
        "根据以下比赛数据，分析胜方队伍中关键玩家的表现，具体包括：\n"
        "- 表现最好的玩家及其数据（击杀、金钱、英雄伤害等）。\n"
        "- 这些玩家对比赛胜利的贡献。\n\n"
        "比赛数据：{context}\n"
    ),
)

dire_players_prompt = PromptTemplate(
    input_variables=["context"],
    template=(
        "根据以下比赛数据，分析败方队伍中表现较亮眼或失误的玩家，具体包括：\n"
        "- 表现亮眼的玩家及其贡献。\n"
        "- 失误玩家的数据和问题。\n\n"
        "比赛数据：{context}\n"
    ),
)

team_highlights_prompt = PromptTemplate(
    input_variables=["context"],
    template=(
        "根据以下比赛数据，分析胜方队伍的亮点，具体包括：\n"
        "- 经济领先、地图控制等。\n"
        "- 关键装备的选择和使用。\n\n"
        "比赛数据：{context}\n"
    ),
)

failure_analysis_prompt = PromptTemplate(
    input_variables=["context"],
    template=(
        "根据以下比赛数据，分析败方队伍的失败原因，包括但不限于：\n"
        "- 资源争夺、团战配合的不足。\n"
        "- 决策或装备选择的问题。\n"
        "- 改进建议。\n\n"
        "比赛数据：{context}\n"
    ),
)

# 步骤 4：为每个任务创建 LLMChains
overview_chain = LLMChain(llm=llm, prompt=overview_prompt)
radiant_players_chain = LLMChain(llm=llm, prompt=radiant_players_prompt)
dire_players_chain = LLMChain(llm=llm, prompt=dire_players_prompt)
team_highlights_chain = LLMChain(llm=llm, prompt=team_highlights_prompt)
failure_analysis_chain = LLMChain(llm=llm, prompt=failure_analysis_prompt)

# 步骤 5：合并向量数据库所有数据并生成内容
def generate_analysis():
    """
    使用向量数据库中所有片段作为上下文，生成完整比赛分析。
    """
    print("合并向量数据库数据...")
    retriever = vectorstore.as_retriever()
    all_docs = retriever.get_relevant_documents("")  # 获取所有片段
    context = "\n".join([doc.page_content for doc in all_docs])  # 合并所有片段

    print("生成比赛概况...")
    overview = overview_chain.run({"context": context})
    print("生成胜方队伍表现...")
    radiant_players = radiant_players_chain.run({"context": context})
    print("生成败方队伍表现...")
    dire_players = dire_players_chain.run({"context": context})
    print("生成团队亮点...")
    team_highlights = team_highlights_chain.run({"context": context})
    print("生成失败原因分析...")
    failure_analysis = failure_analysis_chain.run({"context": context})

    # 合并内容
    return f"""
    **比赛概况：**\n{overview}\n
    **胜方队伍表现：**\n{radiant_players}\n
    **败方队伍表现：**\n{dire_players}\n
    **团队亮点：**\n{team_highlights}\n
    **失败原因分析：**\n{failure_analysis}
    """

# 示例提问
if __name__ == "__main__":
    print("RAG 系统已准备好！")

    analysis_report = generate_analysis()

    print("\n完整比赛分析报告：")
    print(analysis_report)
