import discord
from core import Cog
from core.utils import cleanup_webhooks

class GlobalCommandsCog(Cog):
    def __init__(self, bot):
        self.bot = bot
        
    global_cmd = discord.SlashCommandGroup("global", "Global bot commands and settings")
    parameters_group = global_cmd.create_subgroup("parameters", "Manage global parameters for all agents")
    
    @global_cmd.command(name="cleanup", description="Cleanup all bot webhooks")
    async def cleanup_webhooks_command(self, ctx):
        """Command to cleanup all bot webhooks"""
        await ctx.defer()
        await cleanup_webhooks(ctx.channel, self.bot.user)
        await ctx.respond("Cleaned up all webhooks!", ephemeral=True)
        
    @global_cmd.command(name="set_system_prompt", description="Set the global system prompt for all agents")
    @discord.option(name="prompt", description="The system prompt to set for all agents", type=str, required=False)
    async def set_system_prompt(self, ctx, prompt: str):
        """Command to set the global system prompt"""
        # Get the AgentCog instance
        agent_cog = self.bot.get_cog("AgentCog")
        if not agent_cog:
            await ctx.respond("Agent system is not loaded!", ephemeral=True)
            return
        
        if prompt is None:
            prompt = """You are participating in a multi-agent conversation. Keep your responses short and relevant.
            Always stay in character and respond from your specialized perspective while engaging meaningfully with other agents' messages."""
            
        agent_cog.global_system_prompt = prompt
        
        embed = discord.Embed(
            title="✅ Global System Prompt Updated",
            description="The global system prompt has been updated for all agents",
            color=discord.Color.green()
        )
        embed.add_field(name="New Prompt", value=prompt, inline=False)
        
        await ctx.respond(embed=embed)

    @parameters_group.command(name="set", description="Set the global parameters for all agents")
    @discord.option(name="temperature", description="The temperature of the model. (Default: 0.8)", type=float, required=False)
    @discord.option(name="num_ctx", description="Sets the size of the context window. (Default: 2048)", type=int, required=False)
    @discord.option(name="top_k", description="Reduces the probability of generating nonsense. (Default: 40)", type=int, required=False)
    @discord.option(name="top_p", description="Works together with top-k. (Default: 0.9)", type=float, required=False)
    @discord.option(name="repeat_penalty", description="Sets how strongly to penalize repetitions (Default: 1.1)", type=float, required=False)
    @discord.option(name="num_predict", description="Sets the number of tokens to predict. (Default: 150)", type=int, required=False)
    async def parameters_set(self, ctx, temperature: float = None, num_ctx: int = None, top_k: int = None, top_p: float = None, repeat_penalty: float = None, num_predict: int = None):


        """Command to set the global parameters for all agents"""
        # Get the AgentCog instance
        agent_cog = self.bot.get_cog("AgentCog")
        if not agent_cog:
            await ctx.respond("Agent system is not loaded!", ephemeral=True)
            return
        
        if temperature is not None:
            agent_cog.global_temperature = temperature
        if num_ctx is not None:
            agent_cog.global_num_ctx = num_ctx
        if top_k is not None:
            agent_cog.global_top_k = top_k
        if top_p is not None:
            agent_cog.global_top_p = top_p
        if repeat_penalty is not None:
            agent_cog.global_repeat_penalty = repeat_penalty
        if num_predict is not None:
            agent_cog.global_num_predict = num_predict


        embed = discord.Embed(
            title="✅ Global Parameters Updated",
            description=f"The global parameters have been updated.",
            color=discord.Color.green()
        )

        embed.add_field(name="Temperature", value=agent_cog.global_temperature, inline=True)
        embed.add_field(name="Num Context", value=agent_cog.global_num_ctx, inline=True)
        embed.add_field(name="Top K", value=agent_cog.global_top_k, inline=True)
        embed.add_field(name="Top P", value=agent_cog.global_top_p, inline=True)
        embed.add_field(name="Repeat Penalty", value=agent_cog.global_repeat_penalty, inline=True)
        embed.add_field(name="Num Predict", value=agent_cog.global_num_predict, inline=True)

        await ctx.respond(embed=embed)

    @parameters_group.command(name="list", description="Show current global parameters for all agents")
    async def parameters_list(self, ctx):
        """Command to show the current global parameters"""
        agent_cog = self.bot.get_cog("AgentCog")
        if not agent_cog:
            await ctx.respond("Agent system is not loaded!", ephemeral=True)
            return

        embed = discord.Embed(
            title="📊 Current Global Parameters",
            description="These are the current global parameters for all agents:",
            color=discord.Color.blue()
        )
        embed.add_field(name="Temperature", value=agent_cog.global_temperature, inline=True)
        embed.add_field(name="Num Context", value=agent_cog.global_num_ctx, inline=True)
        embed.add_field(name="Top K", value=agent_cog.global_top_k, inline=True)
        embed.add_field(name="Top P", value=agent_cog.global_top_p, inline=True)
        embed.add_field(name="Repeat Penalty", value=agent_cog.global_repeat_penalty, inline=True)
        embed.add_field(name="Num Predict", value=agent_cog.global_num_predict, inline=True)

        await ctx.respond(embed=embed)


    @parameters_group.command(name="model", description="Set the global model for all agents")
    @discord.option(
        name="model",
        description="The model to set for all agents",
        choices=[
            "llama3.2",
            "smollm:135m"
        ],
        required=True
    )
    async def parameters_model(self, ctx, model: str):
        """Command to set the global model for all agents"""
        agent_cog = self.bot.get_cog("AgentCog")
        if not agent_cog:
            await ctx.respond("Agent system is not loaded!", ephemeral=True)
            return

        agent_cog.global_model = model

        embed = discord.Embed(
            title="✅ Global Model Updated",
            description="The global model has been updated",
            color=discord.Color.green()
        )
        embed.add_field(name="New Model", value=model, inline=False)

        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(GlobalCommandsCog(bot)) 