<!-- =============================== -->
<!--      BhaluBOTV2.0 README    -->
<!-- =============================== -->

<h1 align="center">🤖 BhaluBotV2.0 – Discord Photo-Only Moderation Bot</h1>

<p align="center">
  <img src="https://i.pinimg.com/736x/d8/f6/64/d8f6643cca5701436567316cbe78e438.jpg" width="250px" alt="Bot Logo"/>
</p>

<p align="center">
  <b>Keep your Discord channels clean. No chatting in photo-only zones. Period.</b><br>
  Built with ❤️ using <code>Python</code>, <code>discord.py</code> & <code>aiosqlite</code>
</p>

---

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/discord.py-v2.0-blue?logo=discord&logoColor=white">
  <img src="https://img.shields.io/badge/SQLite-Database-orange?logo=sqlite&logoColor=white">
</p>

---

## 💡 Why I Built This

> People kept chatting in **photo-only** and **flex** channels like it was general chat.  
> So I built a bot that says: **“Shut up and post your pics.”**  

BhaluBotV2.0 ensures users can only:
- Send unlimited photos 📸  
- Send up to **3 text messages per day** 💬  
After that — their messages get silently deleted 🚫  

No warnings. No spam. Just **discipline**.

---

## ⚙️ Features

✅ **Photo-only enforcement** – Restrict chatting in certain channels  
✅ **Daily text limit** – 3 messages per user per day  
✅ **Silent deletion** – Deletes messages without any reply clutter  
✅ **Automatic log cleanup** – Removes logs older than 24 hours  
✅ **Slash commands** – Configure channels easily  
✅ **SQLite storage** – Fast and lightweight data saving  

---

## 🛠️ Slash Commands

| Command | Description |
|----------|-------------|
| `/restrict` | Mark current channel as photo-only |
| `/unrestrict` | Remove restriction from channel |
| `/logs [limit]` | View recent deleted messages (default: 50) |

---

## 🧠 Setup Instructions

### 1️⃣ Clone the repo <br>
git clone https://github.com/sakshyamkharel/DumbAssPiss.git <br>
cd BhaluBotV2.0 <br>
2️⃣ Install dependencies <br>
bash <br>
Copy code <br>
pip install -U discord.py python-dotenv aiosqlite<br>
3️⃣ Create a .env file<br>
env<br>
Copy code<br>
DISCORD_TOKEN=your_bot_token_here<br>
GUILD_ID=123456789012345678<br>
4️⃣ Run the bot<br>
bash<br>
Copy code<br>
python bhalubot.py<br>
🔒 Required Permissions
🧹 Manage Messages

📖 Read Message History

💬 Send Messages

⚡ Use Slash Commands

Make sure the bot can see all restricted channels or it won’t moderate them.

🧩 Tech Stack
Component	Description
Python	Core Language
discord.py	Discord API Wrapper
aiosqlite	Async database management
SQLite	Local lightweight data store

🧼 Automatic Maintenance
The bot automatically:

Deletes old logs every hour ⏳

Keeps only 24-hour-old logs 🧾

Reduces memory & DB load 🚀

🌐 Connect With Me
<p align="center"> <a href="https://github.com/sakshyamkharel"> <img src="https://img.shields.io/badge/GitHub-sakshyamkharel-181717?style=for-the-badge&logo=github&logoColor=white"/> </a> <a href="https://linkedin.com"> <img src="https://img.shields.io/badge/LinkedIn-Sakshyam-blue?style=for-the-badge&logo=linkedin&logoColor=white"/> </a> </p>
<p align="center"> <b>“No spam. No chaos. Just photos.”</b><br> 🧠 Made by <a href="https://github.com/sakshyamkharel">Sakshyam Kharel</a> </p>
