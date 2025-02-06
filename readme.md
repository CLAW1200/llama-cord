# 🤖 Ollama Client in Discord with Custom Agents

A Discord bot that lets you create and interact with multiple AI agents powered by Ollama, featuring agent simulations and customizable personalities.

## ✨ Features

- 🎭 Support for multiple agents with distinct personalities
- 🎬 Simulate conversations between multiple agents in a channel
- 👤 Realistic agent interactions using Discord webhooks with custom avatars
- 💡 Create custom agents with custom personalities
- 📝 Benchmarking of agent performance
- ⚙️ Global commands for managing agents and model parameters

## Screenshots

### Agent List & Management
<img src="https://i.imgur.com/fcyEbjs.png" alt="Agent Management" height="300"/>

### Multi-Agent Simulation
<img src="https://i.imgur.com/deiWjob.png" alt="Agent Simulation" height="300"/>

### Custom Agent Creation
<img src="https://i.imgur.com/Oh7E2IC.png" alt="Custom Agents" height="200"/>

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Discord Bot Token
- Ollama installed and running

### Installation

1. **Create a Virtual Environment (Recommended)**

   ```bash
   # Create venv
   python -m venv venv

   # Activate venv
   # For Linux/macOS:
   source venv/bin/activate
   # For Windows:
   venv\Scripts\activate
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**

   Create a `.env` file in the root directory:

   ```env
   # Required
   TOKEN=your_discord_bot_token
   ERRORS_WEBHOOK=your_error_webhook_url

   # Optional
   TESTTOKEN=your_test_bot_token
   ```

### 🏃‍♂️ Running the Bot

```bash
python main.py -s
```

## 🛠️ Command Line Arguments

| Argument | Description |
|:---------|:------------|
| `-d, --debug` | Enable debug mode with additional logging |
| `-s, --sync` | Sync slash commands with Discord |
| `-t, --test` | Use test token instead of main token |

## 📚 Available Commands

### Agent Management

| Command | Description |
|:--------|:------------|
| `/agent ask <agent_name> <question>` | Ask a specific agent a question |
| `/agent create <agent_name> <personality>` | Create a new agent with given personality |
| `/agent default` | Reset to default agent settings |
| `/agent delete <agent_name>` | Delete a specific agent |
| `/agent delete_all` | Delete all agents |
| `/agent list` | List all available agents |
| `/agent simulation` | Start an agent discussion simulation |
| `/agent toggle <agent_name>` | Enable/disable a specific agent |

### Global Settings

| Command | Description |
|:--------|:------------|
| `/global cleanup` | Clean up bot resources |
| `/global parameters list` | Show current model parameters |
| `/global parameters model <model>` | Set the AI model to use |
| `/global parameters set` | Configure model generation parameters |
| `/global set_system_prompt <prompt>` | Set the system prompt for the AI |

## 🔧 Simulation Parameters

When using `/agent simulation`, you can configure:
- Number of participating agents
- Discussion topic
- Number of conversation turns
- Random order toggle
- Target channel

## 📝 License

See [LICENSE](LICENSE)

## 🤝 Contributing

Please make a pull request or open an issue.

