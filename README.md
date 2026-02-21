# GG_Chatalyze

A Discord bot powered by AI that provides automated Dota 2 match analysis, player insights, and intelligent conversations.

## Features

- **AI-Powered Match Analysis** - Automatically analyzes Dota 2 matches using LLM technology to provide detailed breakdowns of gameplay, strategy, and performance
- **Discord Integration** - Seamlessly integrates with Discord through bot commands and webhook notifications
- **Player Management** - Track multiple players, enable/disable auto-analysis, and link Discord accounts with Steam profiles
- **Intelligent Conversations** - Context-aware chat with intent recognition to distinguish between commands and casual conversation
- **Multi-language Support** - Supports both Chinese and English
- **RAG Enhancement** - Uses Retrieval Augmented Generation for enhanced analysis quality

## Tech Stack

**Backend & AI**
- Python
- FastAPI
- LangChain
- OpenAI API / Custom LLM
- FAISS (Vector Database)

**Database**
- MongoDB
- MySQL

**Integration & Infrastructure**
- discord.py
- Docker & Docker Compose
- APScheduler
- Uvicorn

## Project Structure

```
/app
├── agent/               # LangChain agent configuration
├── controller/          # API endpoints
├── services/            # Core business logic
├── repository/          # Database access layer
├── discord_util/        # Discord bot utilities
├── llm/                 # LLM-related utilities
├── scheduler/           # Background task scheduling
├── constant/            # Configuration constants
└── utils/               # Utility functions
```

## Prerequisites

- Docker and Docker Compose
- Steam API Key
- Discord Bot Token
- OpenAI API Key (or custom LLM endpoint)

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Discord Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token

# LLM Configuration
OPENAI_API_KEY=your_openai_api_key
LLM_HOST=your_llm_host_url
LLM_API_KEY=your_llm_api_key

# Steam Configuration
STEAM_API_KEY=your_steam_api_key

# Database Configuration
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=gg_chatalyze

MONGO_HOST=mongodb
MONGO_PORT=27017
MONGO_DATABASE=gg_chatalyze
```

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/GG_Chatalyze.git
   cd GG_Chatalyze
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Invite the bot to your Discord server**
   - Use the Discord Developer Portal to generate an invite link
   - Select the required bot permissions

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/match/analyze/{match_id}` | Analyze a specific Dota 2 match |
| GET | `/player/list` | List all tracked players |
| POST | `/player/add` | Add a player to tracking |
| DELETE | `/player/remove/{player_id}` | Remove a player from tracking |

## Discord Commands

- `/analyze <match_id>` - Analyze a specific match
- `/player add <steam_id>` - Add a player to tracking
- `/player remove <steam_id>` - Remove a player from tracking
- `/player list` - List all tracked players
- `/enable <steam_id>` - Enable auto-analysis for a player
- `/disable <steam_id>` - Disable auto-analysis for a player

## How It Works

1. **Match Detection** - The bot monitors tracked players for new matches
2. **Data Collection** - Match data is fetched from the Steam/Dota 2 API
3. **AI Analysis** - LangChain agents analyze the match using LLM technology
4. **Result Delivery** - Analysis results are sent to Discord via webhooks or commands

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Discord Bot   │────▶│   FastAPI App   │────▶│   LLM Service   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     MySQL       │    │     MongoDB     │    │   Steam API     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [LangChain](https://github.com/langchain-ai/langchain) for AI agent orchestration
- [discord.py](https://github.com/Rapptz/discord.py) for Discord integration
- [OpenDota](https://www.opendota.com/) for Dota 2 data insights
