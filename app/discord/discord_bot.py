import discord
import os
from dotenv import load_dotenv

load_dotenv()


class DiscordBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.guilds = True  # 需要启用以访问 guild（服务器）信息
        super().__init__(intents=intents)
        self.server_id = int(os.getenv("DISCORD_SERVER_ID"))  # 替换为你的服务器 ID
        self.channel_id = int(os.getenv("DISCORD_CHANNEL_ID"))  # 替换为你的频道 ID

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        # 检查频道是否存在
        guild = self.get_guild(self.server_id)
        if not guild:
            print(f"Guild with ID {self.server_id} not found.")
            return

        channel = guild.get_channel(self.channel_id)
        if not channel:
            print(f"Channel with ID {self.channel_id} not found.")
        else:
            print(f"Bot is connected to channel: {channel.name} ({channel.id})")

    async def send_analysis_to_channel(self, analysis: str):
        try:
            channel = await self.fetch_channel(self.channel_id)  # 异步从 API 获取频道
            if not channel:
                print(f"Channel with ID {self.channel_id} not found.")
                return

            # 异步发送消息
            await channel.send(analysis)
            print("Message sent successfully.")
        except discord.NotFound:
            print(f"Channel with ID {self.channel_id} does not exist.")
        except discord.Forbidden:
            print(f"Bot does not have permission to access channel {self.channel_id}.")
        except Exception as e:
            print(f"Failed to send message: {e}")

