
from __future__ import annotations

import os
import asyncio
import aiosqlite
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from typing import Dict, Tuple, Optional, Set

import discord
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv

# ----------------------- Env & Intents -----------------------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID") or 0) or None
if not TOKEN:
    raise SystemExit("Missing DISCORD_TOKEN in .env")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)
DB_PATH = "./dap_modbot.db"

# ----------------------- In-memory state -----------------------
@dataclass(frozen=True)
class Key:
    guild_id: int
    channel_id: int
    user_id: int
    date: str  # YYYY-MM-DD

counts: Dict[Key, int] = {}
restricted_cache: Dict[int, Set[int]] = {}

# ----------------------- DB helpers -----------------------
CREATE_SQL = (
    """
    CREATE TABLE IF NOT EXISTS restricted_channels (
        guild_id INTEGER,
        channel_id INTEGER,
        PRIMARY KEY (guild_id, channel_id)
    );
    """
    """
    CREATE TABLE IF NOT EXISTS deletion_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts INTEGER,
        guild_id INTEGER,
        channel_id INTEGER,
        user_id INTEGER,
        excerpt TEXT
    );
    """
)

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        for stmt in CREATE_SQL.split(";\n"):
            s = stmt.strip()
            if s:
                await db.execute(s)
        await db.commit()

async def cleanup_old_logs():
    cutoff = int((datetime.now(tz=timezone.utc) - timedelta(hours=24)).timestamp())
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM deletion_logs WHERE ts < ?", (cutoff,))
        await db.commit()

@tasks.loop(hours=1)
async def periodic_cleanup():
    await cleanup_old_logs()

async def load_restricted_cache():
    restricted_cache.clear()
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT guild_id, channel_id FROM restricted_channels") as cur:
            async for row in cur:
                guild_id, channel_id = row
                restricted_cache.setdefault(guild_id, set()).add(channel_id)

async def add_restricted(guild_id: int, channel_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO restricted_channels (guild_id, channel_id) VALUES (?, ?)",
            (guild_id, channel_id),
        )
        await db.commit()
    restricted_cache.setdefault(guild_id, set()).add(channel_id)

async def remove_restricted(guild_id: int, channel_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM restricted_channels WHERE guild_id=? AND channel_id=?",
            (guild_id, channel_id),
        )
        await db.commit()
    restricted_cache.setdefault(guild_id, set()).discard(channel_id)

async def log_deletion(ts: int, guild_id: int, channel_id: int, user_id: int, excerpt: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO deletion_logs (ts, guild_id, channel_id, user_id, excerpt) VALUES (?, ?, ?, ?, ?)",
            (ts, guild_id, channel_id, user_id, excerpt[:200]),
        )
        await db.commit()

async def fetch_logs(guild_id: int, limit: int = 50):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT ts, channel_id, user_id, excerpt FROM deletion_logs WHERE guild_id=? ORDER BY id DESC LIMIT ?",
            (guild_id, limit),
        ) as cur:
            return await cur.fetchall()

# ----------------------- Utils -----------------------
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff"}

def has_image_attachment(msg: discord.Message) -> bool:
    for att in msg.attachments:
        try:
            if att.content_type and att.content_type.startswith("image/"):
                return True
        except Exception:
            pass
        if any((att.filename or "").lower().endswith(ext) for ext in IMAGE_EXTS):
            return True
    if msg.stickers:
        return True
    return False

def current_date_str() -> str:
    return datetime.now().date().isoformat()

# ----------------------- Events -----------------------
@bot.event
async def on_ready():
    await init_db()
    await load_restricted_cache()
    periodic_cleanup.start()
    try:
        if GUILD_ID:
            synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
            print(f"Synced {len(synced)} commands to guild {GUILD_ID}")
        else:
            synced = await bot.tree.sync()
            print(f"Globally synced {len(synced)} commands")
    except Exception as e:
        print("Slash sync failed:", e)
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

@bot.event
async def on_message(message: discord.Message):
    if message.guild is None or message.author.bot:
        return

    guild_id = message.guild.id
    chan_id = message.channel.id

    if chan_id not in restricted_cache.get(guild_id, set()):
        return

    if has_image_attachment(message):
        return

    key = Key(guild_id, chan_id, message.author.id, current_date_str())
    current = counts.get(key, 0)

    if current < 3:
        counts[key] = current + 1
        return

    try:
        await message.delete()
    except discord.Forbidden:
        return
    except discord.HTTPException:
        return

    excerpt = (message.content or "").strip().replace("\n", " ")
    ts = int(datetime.now(tz=timezone.utc).timestamp())
    await log_deletion(ts, guild_id, chan_id, message.author.id, excerpt)

# ----------------------- Slash Commands -----------------------
class RestrictCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="restrict", description="Mark a channel as photo-only with 3 text msgs/day limit")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def restrict(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await add_restricted(interaction.guild_id, channel.id)  
        await interaction.response.send_message(f"Restricted {channel.mention} (photo-only, 3 text/day).", ephemeral=True)

    @app_commands.command(name="unrestrict", description="Remove photo-only restriction from a channel")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unrestrict(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await remove_restricted(interaction.guild_id, channel.id)  
        await interaction.response.send_message(f"Unrestricted {channel.mention}.", ephemeral=True)

    @app_commands.command(name="logs", description="Show recent deletions in this server")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def logs(self, interaction: discord.Interaction, limit: Optional[int] = 50):
        limit = max(1, min(int(limit or 50), 200))
        rows = await fetch_logs(interaction.guild_id, limit)  
        if not rows:
            await interaction.response.send_message("No deletions logged yet.", ephemeral=True)
            return

        lines = []
        for ts, channel_id, user_id, excerpt in rows:
            dt = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone()
            when = dt.strftime("%Y-%m-%d %H:%M")
            lines.append(f"{when} — <#{channel_id}> — <@{user_id}> — {excerpt or '(no text)'}")

        text = "\n".join(lines)
        chunks = []
        while text:
            chunks.append(text[:1800])
            text = text[1800:]
        if not interaction.response.is_done():
            await interaction.response.send_message(chunks[0], ephemeral=True)
            for c in chunks[1:]:
                await interaction.followup.send(c, ephemeral=True)
        else:
            for c in chunks:
                await interaction.followup.send(c, ephemeral=True)

    async def cog_app_command_error(self, interaction: discord.Interaction, error: Exception):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("You lack permissions for this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Error: {error}", ephemeral=True)

async def setup_bot():
    await bot.add_cog(RestrictCog(bot))

@bot.event
async def setup_hook():
    await setup_bot()

bot.run(TOKEN)