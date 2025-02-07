# 🤖 Ollama Client for Discord

A powerful Discord bot that enables multi-agent AI interactions powered by Ollama, featuring dynamic conversations and customizable AI personalities.

## 🌟 Overview

This Discord bot creates an interactive multi-agent AI environment where multiple AI personalities can engage in natural conversations, respond to queries, and participate in simulated discussions. Built on Ollama's language models, it offers advanced features for managing AI agents and their interactions.

## ✨ Key Features

- **Multi-Agent Support**: Create and manage multiple AI agents with distinct personalities
- **Interactive Simulations**: Generate dynamic conversations between AI agents
- **Custom Webhooks**: Realistic agent interactions with personalized Discord avatars
- **Flexible Configuration**: Customize agent personalities and behaviors
- **Performance Monitoring**: Built-in benchmarking for agent performance
- **Advanced Controls**: Comprehensive commands for agent and model management

## 📸 Interface

<details>
<summary><b>View Screenshots</b></summary>

### Agent Management Interface
<img src="https://i.imgur.com/fcyEbjs.png" alt="Agent Management Interface" width="600"/>

### Multi-Agent Simulation
<img src="https://i.imgur.com/oXJK6Yf.png" alt="Multi-Agent Simulation" width="600"/>

### Agent Creation
<img src="https://i.imgur.com/Oh7E2IC.png" alt="Agent Creation Interface" width="400"/>

</details>

## 🚀 Getting Started

### System Requirements

- Python 3.8+
- Discord Bot Token
- Ollama (installed and running)

### Installation Guide

1. **Set Up Virtual Environment**
   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   # Linux/macOS:
   source venv/bin/activate
   # Windows:
   venv\Scripts\activate
   ```

2. **Install Required Packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   
   Create a `.env` file in the project root:
   ```env
   # Required Configuration
   TOKEN=your_discord_bot_token
   ERRORS_WEBHOOK=your_error_webhook_url

   # Optional Configuration
   TESTTOKEN=your_test_bot_token
   ```

### Launch Application

```bash
python main.py -s
```

## ⚙️ Command Line Options

| Option | Description |
|:-------|:------------|
| `-d, --debug` | Enable debug logging |
| `-s, --sync` | Synchronize slash commands |
| `-t, --test` | Use test environment token |

## 📚 Command Reference

### Agent Commands

| Command | Function |
|:--------|:---------|
| `/agent ask <agent_name> <question>` | Direct a question to a specific agent |
| `/agent create <agent_name> <personality>` | Create a new agent with defined personality |
| `/agent default` | Restore default agent configuration |
| `/agent delete <agent_name>` | Remove a specific agent |
| `/agent delete_all` | Remove all agents |
| `/agent list` | Display available agents |
| `/agent simulation` | Initialize agent discussion simulation |
| `/agent toggle <agent_name>` | Toggle agent participation in simulations |

### Global Commands

| Command | Function |
|:--------|:---------|
| `/global cleanup` | Remove server webhooks |
| `/global parameters list` | Display current model settings |
| `/global parameters model <model>` | Configure AI model selection |
| `/global parameters set` | Adjust model parameters |
| `/global set_system_prompt <prompt>` | Define system prompt |

## 🎮 Simulation Configuration

The `/agent simulation` command supports configuration of:
- Agent participant count
- Conversation subject
- Interaction rounds
- Random sequence option
- Target channel selection

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to:
- Submit pull requests
- Open issues for bugs or feature requests
- Suggest improvements to documentation

---

<div align="center">
<i>Powered by Ollama • Built for Discord</i>
</div
