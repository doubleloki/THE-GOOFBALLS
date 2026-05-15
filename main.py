import discord
from discord.ext import commands
import asyncio
import os

# --- CONFIG ---
TOKEN = os.getenv('DISCORD_TOKEN')
MEMBER_ROLE_ID = 1504273897531510906
UNVERIFIED_ROLE_ID = 1504644965932863588

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} is online. Role Cleanup is active.')

# --- AUTOMATIC ROLE CLEANUP ---
@bot.event
async def on_member_update(before, after):
    """Automatically removes Unverified role when Member role is added"""
    # Check if a role was added
    if len(before.roles) < len(after.roles):
        # Check if they have BOTH roles now
        has_member = any(r.id == MEMBER_ROLE_ID for r in after.roles)
        has_unverified = any(r.id == UNVERIFIED_ROLE_ID for r in after.roles)

        if has_member and has_unverified:
            unverified_role = after.guild.get_role(UNVERIFIED_ROLE_ID)
            if unverified_role:
                try:
                    await after.remove_roles(unverified_role)
                    print(f"🧹 Cleaned up: Removed 'Unverified' from {after.name} because they are now a Member.")
                except discord.Forbidden:
                    print(f"⚠️ Failed to remove role from {after.name}. Is my role high enough in the list?")

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
