from discord import DiscordException
from discord.ext import commands
from typing import Any, Literal
from datetime import timedelta
import discord
from typing import Optional
import json
from pathlib import Path
from dataclasses import dataclass
import subprocess
import asyncio

__all__ = (
    "s",
    "list_items",
    "humanize_time",
    "Lowercase",
    "BotMissingPermissions",
)

# functions
def s(data) -> Literal["", "s"]:
    if isinstance(data, str):# if data is a string
        data = int(not data.endswith("s")) # if the string ends with s, return 0, else return 1
    elif hasattr(data, "__len__"): # if data has a length 
        data = len(data) # get the length of the data
    check = data != 1 # if data is not equal to 1
    return "s" if check else "" # return s if check is true, else return an empty string


def list_items(items) -> str:
    return (
        f"{', '.join(items[:-1])} and {items[-1]}"
        if len(items) > 1
        else items[0]
    )

def humanize_time(time: timedelta) -> str:
    if time.days > 365:
        years, days = divmod(time.days, 365)
        return f"{years} year{s(years)} and {days} day{s(days)}"
    if time.days > 1:
        return f"{time.days} day{s(time.days)}, {humanize_time(timedelta(seconds=time.seconds))}"
    hours, seconds = divmod(time.seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if hours > 0:
        return f"{hours} hour{s(hours)} and {minutes} minute{s(minutes)}"
    if minutes > 0:
        return f"{minutes} minute{s(minutes)} and {seconds} second{s(seconds)}"
    return f"{seconds} second{s(seconds)}"

# converters
class _Lowercase(commands.Converter):
    async def convert(self, ctx, text):
        return text.lower()

Lowercase: Any = _Lowercase()

# exceptions
class BotMissingPermissions(DiscordException):
    def __init__(self, permissions) -> None:
        missing = [
            f"**{perm.replace('_', ' ').replace('guild', 'server').title()}**"
            for perm in permissions
        ]
        sub = (
            f"{', '.join(missing[:-1])} and {missing[-1]}"
            if len(missing) > 1
            else missing[0]
        )
        super().__init__(f"I require {sub} permissions to run this command.")


async def cleanup_webhooks(channel: discord.TextChannel, bot_user: discord.User):
    """Clean up existing webhooks created by the bot"""
    webhooks = await channel.webhooks()
    for webhook in webhooks:
        if webhook.user == bot_user:
            await webhook.delete()

async def get_or_create_webhook(channel: discord.TextChannel, name: str, bot_user: discord.User, avatar_data: Optional[bytes] = None):
    """Get existing webhook or create a new one"""
    # First check all webhooks in the guild
    guild_webhooks = await channel.guild.webhooks()
    
    # Look for existing webhook with same name created by the bot
    existing_webhook = next(
        (w for w in guild_webhooks 
         if w.name.lower() == name.lower() 
         and w.user and w.user.id == bot_user.id),
        None
    )
    
    if existing_webhook:
        # If webhook exists but in wrong channel, modify it
        if existing_webhook.channel_id != channel.id:
            await existing_webhook.edit(channel=channel)
        return existing_webhook
        
    # Create new webhook if none exists
    return await channel.create_webhook(
        name=name,
        avatar=avatar_data
    )

def get_available_models():
    """Get list of available models from ollama"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        # Parse the output to extract model names
        lines = result.stdout.strip().split('\n')[1:]  # Skip header line
        models = []
        for line in lines:
            if line.strip():
                model_name = line.split()[0]  # First column is model name
                models.append(model_name)
        return models
    except Exception as e:
        print(f"Error getting models: {e}")
        return ["llama2"]  # Fallback default

def save_bot_config(agent_templates, bot_config, user_id: str = "default"):
    """Save agent templates and bot configuration to config file for a specific user"""
    config_path = Path("data/config.json")
    
    # Create data directory and config file if they don't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
    if not config_path.exists():
        config_path.touch()
    
    # Convert templates to dictionary format
    templates_dict = [
        {
            "agent_name": t.agent_name,
            "personality": t.personality,
            "avatar_url": t.avatar_url,
            "active": t.active
        }
        for t in agent_templates
    ]
    
    # Load existing config if it exists and has content
    config = {}
    if config_path.stat().st_size > 0:
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            config = {}
    
    # Initialize users dict if it doesn't exist
    if 'users' not in config:
        config['users'] = {}
    
    # Update available models in global config
    if 'bot' not in config:
        config['bot'] = {}
    config['bot']['available_models'] = get_available_models()
    
    # Update or create user-specific config
    config['users'][user_id] = {
        'agent_templates': templates_dict,
        'bot_config': bot_config
    }
    
    # Save updated config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

def load_bot_config(default_templates, default_bot_config, user_id: str = "default"):
    """Load agent templates and bot configuration from config file for a specific user"""
    config_path = Path("data/config.json")
    
    if not config_path.exists():
        # Create data directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        # Save defaults for this user
        save_bot_config(default_templates, default_bot_config, user_id)
        return default_templates, default_bot_config
        
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Initialize users dict if it doesn't exist
        if 'users' not in config:
            config['users'] = {}
        
        # If user doesn't exist, create with defaults
        if user_id not in config['users']:
            config['users'][user_id] = {
                'agent_templates': [
                    {
                        "agent_name": t.agent_name,
                        "personality": t.personality,
                        "avatar_url": t.avatar_url,
                        "active": t.active
                    }
                    for t in default_templates
                ],
                'bot_config': default_bot_config
            }
            save_bot_config(default_templates, default_bot_config, user_id)
            return default_templates, default_bot_config
            
        user_config = config['users'][user_id]
        needs_save = False
        
        # Handle missing or empty configurations
        if 'agent_templates' not in user_config or not user_config['agent_templates']:
            user_config['agent_templates'] = [
                {
                    "agent_name": t.agent_name,
                    "personality": t.personality,
                    "avatar_url": t.avatar_url,
                    "active": t.active
                }
                for t in default_templates
            ]
            needs_save = True
            
        if 'bot_config' not in user_config:
            user_config['bot_config'] = default_bot_config
            needs_save = True
        else:
            # Check and set missing parameters
            if 'parameters' not in user_config['bot_config']:
                user_config['bot_config']['parameters'] = default_bot_config['parameters']
                needs_save = True
            else:
                for key, value in default_bot_config['parameters'].items():
                    if key not in user_config['bot_config']['parameters']:
                        user_config['bot_config']['parameters'][key] = value
                        needs_save = True
            
            # Check other bot_config fields
            for key, value in default_bot_config.items():
                if key not in user_config['bot_config'] and key != 'parameters':
                    user_config['bot_config'][key] = value
                    needs_save = True
        
        # Save if any defaults were added
        if needs_save:
            save_bot_config(default_templates, user_config['bot_config'], user_id)
        
        # Convert templates back to objects
        templates = [
            AgentTemplate(
                agent_name=t['agent_name'],
                personality=t['personality'],
                avatar_url=t['avatar_url'],
                active=t.get('active', True)
            )
            for t in user_config['agent_templates']
        ]
        
        return templates, user_config['bot_config']
        
    except Exception as e:
        print(f"Error loading configuration: {e}")
        # On any error, return and save defaults
        save_bot_config(default_templates, default_bot_config, user_id)
        return default_templates, default_bot_config

def update_bot_parameters(agent_cog, user_id: str = "default", **parameters):
    """Update bot parameters and save configuration for a specific user"""
    # Update parameters that were provided
    if 'temperature' in parameters:
        agent_cog.global_temperature = parameters['temperature']
    if 'num_ctx' in parameters:
        agent_cog.global_num_ctx = parameters['num_ctx']
    if 'top_k' in parameters:
        agent_cog.global_top_k = parameters['top_k']
    if 'top_p' in parameters:
        agent_cog.global_top_p = parameters['top_p']
    if 'repeat_penalty' in parameters:
        agent_cog.global_repeat_penalty = parameters['repeat_penalty']
    if 'num_predict' in parameters:
        agent_cog.global_num_predict = parameters['num_predict']
    if 'model' in parameters:
        agent_cog.global_model = parameters['model']

    # Create updated bot config
    bot_config = {
        'model': agent_cog.global_model,
        'system_prompt': agent_cog.global_system_prompt,
        'parameters': {
            'temperature': agent_cog.global_temperature,
            'num_ctx': agent_cog.global_num_ctx,
            'top_k': agent_cog.global_top_k,
            'top_p': agent_cog.global_top_p,
            'repeat_penalty': agent_cog.global_repeat_penalty,
            'num_predict': agent_cog.global_num_predict
        }
    }

    # Save configuration
    save_bot_config(agent_cog.agent_templates, bot_config, user_id)
    return bot_config

@dataclass
class AgentTemplate:
    """Class to represent an agent template"""
    agent_name: str
    personality: str
    avatar_url: str
    active: bool = True

# Default configurations
default_agent_templates = [
            AgentTemplate(
                agent_name="politics",
                personality="You are a political agent. Focus on discussing political events and world affairs.",
                avatar_url="https://thispersondoesnotexist.com/",
                active=True
            ),
            AgentTemplate(
                agent_name="sports",
                personality="You are a sports agent. Focus on sports news and athletic achievements.",
                avatar_url="https://thispersondoesnotexist.com/",
                active=True
            ),
            AgentTemplate(
                agent_name="finance", 
                personality="You are a finance agent. Focus on financial markets and economic news.",
                avatar_url="https://thispersondoesnotexist.com/",
                active=True
            ),
            AgentTemplate(
                agent_name="tech",
                personality="You are a tech agent. Focus on technology trends and innovations.",
                avatar_url="https://thispersondoesnotexist.com/",
                active=True
            ),
            AgentTemplate(
                agent_name="entertainment",
                personality="You are a entertainment agent. Focus on movies, music, and pop culture.",
                avatar_url="https://thispersondoesnotexist.com/",
                active=True
            ),
            AgentTemplate(
                agent_name="science",
                personality="You are a science agent. Focus on scientific discoveries and research.",
                avatar_url="https://thispersondoesnotexist.com/",
                active=True
            )
        ]

default_bot_config = {
    'model': 'llama3.2',
    'system_prompt': """You are participating in a multi-agent conversation. Keep your responses short and relevant.
    Always stay in character and respond from your specialized perspective while engaging meaningfully with other agents' messages.""",
    'parameters': {
        'temperature': 0.8,
        'num_ctx': 2048,
        'top_k': 40,
        'top_p': 0.9,
        'repeat_penalty': 1.1,
        'num_predict': 150
    }
} 