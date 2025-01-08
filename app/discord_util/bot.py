import asyncio
from concurrent.futures import ThreadPoolExecutor
import functools

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from datetime import datetime
import os
from dotenv import load_dotenv
from app.agent import gg_chatalyze_agent
from app.repository import player_repository
import discord

# 加载环境变量
load_dotenv()
discord_bot_token = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

agent = gg_chatalyze_agent.agent
llm = gg_chatalyze_agent.llm
channel_context = {}

executor = ThreadPoolExecutor()

def update_context(channel_id, user_discord_id, user_name, content, is_bot=False):
    global channel_context
    if channel_id not in channel_context:
        channel_context[channel_id] = []
    # 添加消息到上下文
    role = "bot" if is_bot else "user"
    channel_context[channel_id].append({
        "timestamp": datetime.now(),
        "content": content,
        "user_name": user_name,
        "discord_id": user_discord_id,
        "role": role
    })
    # 只保留最近 20 条消息
    if len(channel_context[channel_id]) > 20:
        channel_context[channel_id] = channel_context[channel_id][-20:]


intent_classification_prompt = PromptTemplate(
    input_variables=["context", "query"],
    template=f"""
    You are a helpful assistant in a Discord channel. Your job is to decide if a user query is a task (command) or a casual chat based on the context of the conversation.
    Based on the context, user query and Supported task commands below, decide if the query is a task or casual chat, and also decide which language in the response.
    Supported task commands:
    {gg_chatalyze_agent.tools_descriptions}
    """
    +
    """
    Context:
    {context}

    User query:
    {query}
    
    Respond with JSON string only that contains
    intent: "Task" or "Chat", language: "zh" for Chinese, "en" for English etc.
    Don't response any other content, only response with JSON string.
    """
)


def classify_intent(context, query):
    chain = LLMChain(llm=llm, prompt=intent_classification_prompt)
    result = chain.run(context=context, query=query)
    result.strip()
    return gg_chatalyze_agent.load_args(result)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    print(f"Received message: {message.content}")
    global channel_context

    if message.author == client.user:
        return

    channel_id = message.channel.id
    user_name = message.author.name
    user_query = message.content.replace(f"<@{client.user.id}>", "").strip()

    player = player_repository.fetch_player_by_discord_id(message.author.id)
    user_info_prompt = ""
    if player:
        user_info_prompt = f"""
        This is user info that send query:
        discord_id: {message.author.id}, Steam ID/player_id: {player['player_id']}, Steam Name/personal_name: {player['personal_name']}
        """

    # 更新上下文
    update_context(channel_id, message.author.id, user_name, user_query)

    if client.user.mentioned_in(message):
        async with message.channel.typing():
            try:
                # 构建上下文
                context = "\n".join([
                    f"{'bot' if ctx['role'] == 'bot' else ctx['discord_id']}#{ctx['user_name']}: {ctx['content']}"
                    for ctx in channel_context[channel_id]
                ])

                # 判断意图
                intent_result = classify_intent(context, user_query)

                if intent_result['intent'] == "Task":
                    user_query = f"""
                    action input should be dict, json string value
                    {user_info_prompt}
                    
                    user query info: if @xxx it is mention by discord_name, if <@numbers> ex <@123456789> it is mention by discord_id
                    user_query:
                    {user_query}
                    response in Language: {intent_result['language']} for example "zh" for Chinese, "en" for English
                    """
                    # 任务执行模式
                    response = await run_in_executor(agent.run, user_query)
                else:
                    # 聊天模式
                    chat_prompt = f"""
                    You are a conversational assistant. Engage in a natural and friendly conversation based on the context.
                    context is the conversation history in the channel, format: discor_id#user_name: content
                    bot#{client.user.name}: content  represent it is your chat history
                    Context:
                    {context}
    
                    {user_info_prompt}
    
                    User query:
                    {user_query}
                    
                    Only response with your content, dont include bot#GG_Chatalyze, 
                    Response in Language: {intent_result['language']} for example "zh" for Chinese, "en" for English
                    Note: Do not add language identifiers (e.g., zh:) in the response
                    
                    Respond:
                    """
                    response = llm(chat_prompt).content

                # 回复用户
                update_context(channel_id, client.user.id, client.user.name, response, is_bot=True)

                await message.channel.send(response)

            except Exception as e:
                await message.channel.send(f"出错了: {e.with_traceback()}")

async def run_in_executor(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    partial_func = functools.partial(func, *args, **kwargs)
    return await loop.run_in_executor(executor, partial_func)

def start():
    client.run(discord_bot_token)
