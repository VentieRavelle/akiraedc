import discord
from discord.ext import commands
from discord.ui import View, Select
import time
import datetime
import platform
import psutil
import os

class HelpSelect(Select):
    def __init__(self, bot, author):
        self.bot = bot
        self.author = author
        options = [
            discord.SelectOption(label="Главная", description="Общая информация о боте", emoji="🏠"),
        ]
        
        for name, cog in bot.cogs.items():
            if cog.get_commands():
                options.append(discord.SelectOption(label=name, description=f"Команды модуля {name}", emoji="📁"))
        
        super().__init__(placeholder="Выберите категорию команд...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("Это меню не для вас!", ephemeral=True)

        if self.values[0] == "Главная":
            embed = self.view.main_embed()
            return await interaction.response.edit_message(embed=embed)

        cog = self.bot.get_cog(self.values[0])
        cmds = cog.get_commands()
        
        embed = discord.Embed(title=f"Модуль: {self.values[0]}", color=0xffdd00)
        for c in cmds:
            if not c.hidden:
                embed.add_field(name=f"!{c.name}", value=c.help or "Описание отсутствует", inline=True)
        
        await interaction.response.edit_message(embed=embed)

class HelpView(View):
    def __init__(self, bot, author, main_embed):
        super().__init__(timeout=60)
        self.main_embed = lambda: main_embed
        self.add_item(HelpSelect(bot, author))

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    @commands.command(name='help')
    async def help_command(self, ctx):
        """Интеллектуальное меню помощи с категориями"""
        embed = discord.Embed(
            title="✨ Центр управления Akirae",
            description=(
                f"Привет, **{ctx.author.name}**!\n\n"
                "Я — ваш персональный ассистент. Используйте меню ниже, "
                "чтобы изучить мои возможности по категориям.\n\n"
                f"**Всего команд:** `{len(self.bot.commands)}`"
            ),
            color=0x2b2d31
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        file = None
        if os.path.exists("banner.jpg"):
            file = discord.File("banner.jpg", filename="banner.jpg")
            embed.set_image(url="attachment://banner.jpg")

        view = HelpView(self.bot, ctx.author, embed)
        
        if file:
            await ctx.send(embed=embed, view=view, file=file)
        else:
            await ctx.send(embed=embed, view=view)

    @commands.command(name='stats', aliases=['status', 'info'])
    async def stats(self, ctx):
        """Детальный мониторинг ресурсов системы"""
        uptime = str(datetime.timedelta(seconds=int(round(time.time() - self.start_time))))
        
        ram = psutil.virtual_memory()
        cpu_usage = psutil.cpu_percent()
        
        embed = discord.Embed(title="📊 Состояние системы", color=0x2b2d31)
        
        embed.add_field(
            name="🤖 Akirae", 
            value=f"**Uptime:** `{uptime}`\n**Ping:** `{round(self.bot.latency * 1000)}ms`", 
            inline=True
        )
        embed.add_field(
            name="⚙️ Ресурсы", 
            value=f"**CPU:** `{cpu_usage}%`\n**RAM:** `{ram.percent}%` ({ram.used // (1024**2)}MB)", 
            inline=True
        )
        embed.add_field(
            name="🌍 Окружение", 
            value=f"**OS:** `{platform.system()}`\n**Py:** `v{platform.python_version()}`", 
            inline=True
        )
        
        embed.add_field(
            name="📈 Сообщество", 
            value=f"**Гильдии:** `{len(self.bot.guilds)}`\n**Юзеры:** `{sum(g.member_count for g in self.bot.guilds)}`", 
            inline=False
        )

        embed.set_footer(text=f"Разработчик: Ventie Ravelle • v2.1", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name='ping')
    async def ping(self, ctx):
        """Проверка скорости отклика"""
        embed = discord.Embed(description="🛰️ Измеряю сигнал...", color=0xffdd00)
        msg = await ctx.send(embed=embed)
        
        ping = round(self.bot.latency * 1000)
        status = "🟢" if ping < 100 else "🟡" if ping < 250 else "🔴"
        
        embed.description = f"{status} **Понг!**\nЗадержка API: `{ping}ms`"
        await msg.edit(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))