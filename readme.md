# Ollama Client in Discord with Custom Agents


## Setup
> **_NOTE:_**  Recommended to create a virtual environment for this project.


`python -m venv venv`

`source venv/bin/activate` (Linux)

`venv\Scripts\activate` (Windows)

`pip install -r requirements.txt`


## .env config

```
TOKEN=XXX (Main token)

ERRORS_WEBHOOK=YYY (Webhook for sending errors)

TESTTOKEN= ZZZ (Optional, for testing)
```

## Run

`python main.py -s`


## Command Line Arguments

| Argument | Description |
|----------|-------------|
| `-d` `--debug` | Enables debug mode with additional logging |
| `-s` `--sync` | Syncs slash commands with Discord |
| `-t` `--test` | Uses test token instead of main token |

## Commands

### Agent Commands

| Command | Arguments | Description |
|---------|-----------|-------------|
| `/agent ask` | `agent_name` `question` | Ask a specific agent a question |
| `/agent create` | `agent_name` `personality` | Create a new agent with given personality |
| `/agent default` | None | Reset to default agent settings |
| `/agent delete` | `agent_name` | Delete a specific agent |
| `/agent delete_all` | None | Delete all agents |
| `/agent list` | None | List all available agents |
| `/agent simulation` | `num_agents` `topic` `turns` `random_order` `channel` | Start a simulation with multiple agents discussing a topic |
| `/agent toggle` | `agent_name` | Enable/disable a specific agent |

### Global Commands

| Command | Arguments | Description |
|---------|-----------|-------------|
| `/global cleanup` | None | Clean up bot resources |
| `/global parameters list` | None | Show current model parameters |
| `/global parameters model` | `model` | Set the AI model to use |
| `/global parameters set` | `temperature` `top_k` `top_p` `repeat_penalty` `num_predict` `num_ctx` | Configure model generation parameters |
| `/global set_system_prompt` | `prompt` | Set the system prompt for the AI |

