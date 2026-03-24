import discord
from discord.ext import commands
import datetime

class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='clear', aliases=['purge', 'очистить'])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int, member: discord.Member = None):
        """Очистка сообщений. Можно указать юзера: !clear 10 @User"""
        await ctx.message.delete() 
        if member:
            def check(m):
                return m.author == member
            deleted = await ctx.channel.purge(limit=amount, check=check)
            msg = f"🧹 Удалено сообщений от **{member.display_name}**: **{len(deleted)}**"
        else:
            deleted = await ctx.channel.purge(limit=amount)
            msg = f"🧹 Удалено сообщений: **{len(deleted)}**"

        await ctx.send(msg, delete_after=3)

    @commands.command(name='slowmode', aliases=['медленный'])
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int = 0):
        """Установка медленного режима. !slowmode 0 — выключить"""
        await ctx.channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            await ctx.send("⏲ Медленный режим **выключен**.")
        else:
            await ctx.send(f"⏲ Медленный режим установлен на **{seconds}с**.")

    @commands.command(name='userinfo', aliases=['ui', 'инфо'])
    async def user_info(self, ctx, member: discord.Member = None):
        """Подробная техническая информация о пользователе"""
        member = member or ctx.author
        
        roles = [role.mention for role in member.roles[1:]] 
        roles.reverse() 

        embed = discord.Embed(title=f"Информация о пользователе — {member}", color=member.color)
        embed.set_thumbnail(url=member.display_avatar.url)
        
        embed.add_field(name="🆔 ID", value=member.id, inline=True)
        embed.add_field(name="👤 Никнейм", value=member.display_name, inline=True)
        
        created = member.created_at.strftime("%d.%m.%Y")
        joined = member.joined_at.strftime("%d.%m.%Y")
        
        embed.add_field(name="🗓 Регистрация", value=created, inline=True)
        embed.add_field(name="📥 Зашел на сервер", value=joined, inline=True)
        
        if roles:
            embed.add_field(name=f"🎭 Роли ({len(roles)})", value=" ".join(roles[:10]) + ("..." if len(roles) > 10 else ""), inline=False)
        
        embed.set_footer(text=f"Запрос от {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name='serverinfo', aliases=['si'])
    async def server_info(self, ctx):
        """Информация о текущем сервере"""
        guild = ctx.guild
        embed = discord.Embed(title=f"О сервере {guild.name}", color=0x2b2d31)
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="👑 Владелец", value=f"<@{guild.owner_id}>", inline=True)
        embed.add_field(name="👥 Участники", value=guild.member_count, inline=True)
        embed.add_field(name="📅 Создан", value=guild.created_at.strftime("%d.%m.%Y"), inline=True)
        embed.add_field(name="💬 Каналы", value=f"Текст: {len(guild.text_channels)} | Голос: {len(guild.voice_channels)}", inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utils(bot))