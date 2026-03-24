import discord
from discord.ext import commands
import os
import sys         
import importlib   
from dotenv import load_dotenv 
from keep_alive import keep_alive
from db import Database 

load_dotenv() 

TOKEN = os.getenv('TOKEN')

class Akirae(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents, help_command=None)
        
        self.db = Database()
        self.supabase = self.db.client 
        self.swear_words = self.load_words()

    def load_words(self):
        try:
            if os.path.exists('swear_words.txt'):
                with open('swear_words.txt', 'r', encoding='utf-8') as f:
                    return [w.strip().lower() for w in f.readlines() if w.strip()]
            return []
        except Exception as e:
            print(f"⚠️ Ошибка при загрузке swear_words.txt: {e}")
            return []

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    async def setup_hook(self):
        print("--- Загрузка модулей ---")
        folders = ['./cogs', './moderation']
        
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)
            
            for filename in os.listdir(folder):
                if filename.endswith('.py') and not filename.startswith('__'):
                    folder_name = folder.replace('./', '').replace('/', '')
                    cog_path = f'{folder_name}.{filename[:-3]}'
                    try:
                        if cog_path in sys.modules:
                            importlib.reload(sys.modules[cog_path])
                        await self.load_extension(cog_path)
                        print(f"✅ Модуль {cog_path} загружен")
                    except Exception as e:
                        print(f"❌ Ошибка в {cog_path}: {e}")
        print("------------------------")

bot = Akirae()

@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Game(name="!help | Akirae Bot")
    )
    print(f'🚀 {bot.user.name} успешно запущен!')

@bot.event
async def on_guild_join(guild):
    role_name = "Akirae"
    role = discord.utils.get(guild.roles, name=role_name)

    if not role:
        try:
            role = await guild.create_role(
                name=role_name, 
                colour=discord.Colour.from_rgb(255, 221, 0), 
                hoist=True, 
                reason="Автоматическая настройка оформления бота"
            )
            print(f"🛠 Создана роль {role_name} на сервере {guild.name}")
        except discord.Forbidden:
            print(f"❌ Нет прав на управление ролями на сервере {guild.name}")
            return

    try:
        if role not in guild.me.roles:
            await guild.me.add_roles(role)
    except Exception as e:
        print(f"❌ Ошибка при выдаче роли: {e}")

if __name__ == "__main__":
    if TOKEN:
        keep_alive()
        try:
            bot.run(TOKEN)
        except Exception as e:
            print(f"🔥 Критическая ошибка: {e}")
    else:
        print("❌ Ошибка: TOKEN не найден")