import discord
from discord.ext import commands
import asyncio
import os

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} is now an empty shell. Ready for commands.')

# --- MANUAL CHANNEL WIZARD ---
@bot.command()
@commands.has_permissions(administrator=True)
async def create(ctx):
    """Starts the Channel Setup Wizard"""
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        await ctx.send("🛠️ **Step 1:** What should the channel be named?")
        msg_name = await bot.wait_for('message', check=check, timeout=30.0)
        channel_name = msg_name.content.lower().replace(" ", "-")

        await ctx.send(f"📂 **Step 2:** Should **{channel_name}** be a `text` or `voice` channel?")
        msg_type = await bot.wait_for('message', check=check, timeout=30.0)
        c_type = msg_type.content.lower()

        await ctx.send("🔒 **Step 3:** Should this be a `private` channel? (yes/no)")
        msg_priv = await bot.wait_for('message', check=check, timeout=30.0)
        is_private = msg_priv.content.lower() == "yes"

        guild = ctx.guild
        overwrites = {}
        if is_private:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True)
            }

        if "voice" in c_type:
            await guild.create_voice_channel(channel_name, overwrites=overwrites)
            await ctx.send(f"🔊 Voice channel **{channel_name}** created.")
        else:
            await guild.create_text_channel(channel_name, overwrites=overwrites)
            await ctx.send(f"📝 Text channel **{channel_name}** created.")

    except asyncio.TimeoutError:
        await ctx.send("⌛ Setup timed out.")

# --- MANUAL REMOVE ---
@bot.command()
@commands.has_permissions(administrator=True)
async def remove(ctx, *, name: str):
    channel = discord.utils.get(ctx.guild.channels, name=name.lower().replace(" ", "-"))
    if channel:
        await channel.delete()
        await ctx.send(f"🗑️ Deleted **{name}**.")
    else:
        await ctx.send("❌ Channel not found.")

bot.run(TOKEN)
