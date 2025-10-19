#BhaluBotV2.0 – Discord Photo-Only Moderation Bot
---
🎯 Why I Made This Bot

I created BhaluBotV2.0 to enforce order in Discord servers where people were spamming text in photo-only channels. It ensures that channels meant for images remain focused, while still letting users share limited text messages per day.
---

#✨Features

Photo-Only Channels – Unlimited images, limited text.

Daily Text Limit – Users can only send 3 text messages/day in restricted channels.

Silent Moderation – Deletes messages silently without spamming warnings.

Slash Commands – /restrict, /unrestrict, /logs.

Automatic Log Cleanup – Logs older than 24 hours are automatically deleted.

Persistent Storage – Uses SQLite to save restrictions and logs.
---

#⚙️ Setup & Installation

Clone the repository:

git clone <repo_url>
cd <repo_folder>


Install dependencies:

pip install -U discord.py python-dotenv aiosqlite


Create a .env file:

DISCORD_TOKEN=your_bot_token_here
GUILD_ID=123456789012345678   # optional


Run the bot:

python bhalubot.py

#🛡Permissions Required

Manage Messages – Delete excess messages.

Read Message History – Inspect messages.

Send Messages – Reply to commands.

Use Slash Commands – Execute /restrict, /unrestrict, /logs.
---

#🚀Slash Commands

Command	Description

/restrict	Mark a channel as photo-only

/unrestrict	Remove photo-only restriction

/logs [limit]	Show recent deletions (default 50, max 200)

#🛠 Tech Stack

Python 3.11

discord.py v2

aiosqlite

SQLite for persistent storage
