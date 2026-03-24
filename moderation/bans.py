import discord
from discord.ext import commands

class Bans(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ban', aliases=['бан'])
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member = None, *, reason="Нарушение правил"):
        if not member and ctx.message.reference:
            msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            member = msg.author

        if not member:
            return await ctx.send("❓ Кого баним? Упомяните юзера или ответьте на его сообщение.")

        if member.id == ctx.author.id:
            return await ctx.send("🗿 Самоуничтожение — это не выход.")

        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            return await ctx.send("❌ У вас недостаточно прав (ваша роль ниже или равна роли цели).")
        
        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.send("❌ Моя роль слишком низкая, чтобы забанить этого пользователя.")

        try:
            await member.ban(reason=f"{ctx.author}: {reason}", delete_message_days=1)
            await ctx.send(f"🔨 **{member}** забанен. Причина: {reason}")
        except discord.Forbidden:
            await ctx.send("❌ Ошибка прав. Проверьте настройки ролей.")

    @commands.command(name='softban')
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx, member: discord.Member, *, reason="Softban (очистка сообщений)"):
        """Банит и сразу разбанивает, чтобы удалить все сообщения юзера"""
        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.send("❌ Моя роль слишком низкая.")

        await member.ban(reason=reason, delete_message_days=7)
        await ctx.guild.unban(member)
        await ctx.send(f"🧼 **{member}** подвергся софтбану (сообщения за 7 дней удалены).")

    @commands.command(name='unban', aliases=['разбан'])
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, user_id: int):
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            await ctx.send(f"✅ Пользователь **{user}** (ID: {user_id}) разбанен.")
        except discord.NotFound:
            await ctx.send("❌ Пользователь с таким ID не найден в списке банов.")

    @commands.command(name='kick', aliases=['кик'])
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member = None, *, reason="Нарушение правил"):
        if not member and ctx.message.reference:
            msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            member = msg.author

        if not member:
            return await ctx.send("❓ Кого исключить?")

        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            return await ctx.send("❌ Ваша роль ниже роли цели.")
            
        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.send("❌ Моя роль ниже роли цели.")

        await member.kick(reason=f"{ctx.author}: {reason}")
        await ctx.send(f"👢 **{member}** исключен. Причина: {reason}")

async def setup(bot):
    await bot.add_cog(Bans(bot))