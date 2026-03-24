import discord
from discord.ext import commands
import datetime
import re

class Mutes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='mute', aliases=['timeout', 'm'])
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member = None, time: str = "1h", *, reason="Тихо!"):
        if not member and ctx.message.reference:
            msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            member = msg.author
            if isinstance(ctx.args[2], str) and not ctx.message.mentions:
                time = ctx.args[2]
        
        if not member:
            return await ctx.send("❓ Кого мутим? Упомяните юзера или ответьте на его сообщение.")

        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.send(f"❌ Не могу замутить **{member.display_name}**, его роль выше или равна моей!")

        if member.id == ctx.author.id:
            return await ctx.send("🗿 Самоуничтожение запрещено.")

        try:
            match = re.match(r"(\d+)([smhd])", time.lower())
            if match:
                amount, unit = int(match.group(1)), match.group(2)
                if unit == "s": d = datetime.timedelta(seconds=amount)
                elif unit == "m": d = datetime.timedelta(minutes=amount)
                elif unit == "h": d = datetime.timedelta(hours=amount)
                elif unit == "d": d = datetime.timedelta(days=amount)
            else:
                d = datetime.timedelta(hours=1)
                time = "1h (default)"
        except Exception:
            d = datetime.timedelta(hours=1)
            time = "1h (default)"

        if d > datetime.timedelta(days=28):
            return await ctx.send("❌ Максимальный мут — 28 дней.")

        try:
            await member.timeout(d, reason=reason)
            embed = discord.Embed(description=f"🔇 **{member.mention}** отправлен в тайм-аут на **{time}**\n**Причина:** {reason}", color=0x2b2d31)
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ Ошибка прав. Проверьте иерархию ролей!")

    @commands.command(name='unmute')
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member = None):
        if not member and ctx.message.reference:
            msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            member = msg.author
            
        if not member:
            return await ctx.send("❓ Кого размутить?")

        await member.timeout(None)
        await ctx.send(f"🔊 Тайм-аут с **{member.mention}** снят.")

async def setup(bot):
    await bot.add_cog(Mutes(bot))