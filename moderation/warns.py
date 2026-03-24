import discord
from discord.ext import commands

class WarnActionView(discord.ui.View):
    """Класс для кнопок выбора наказания"""
    def __init__(self, member, moderator):
        super().__init__(timeout=60)
        self.member = member
        self.moderator = moderator

    @discord.ui.button(label="Кикнуть", style=discord.ButtonStyle.secondary, emoji="👢")
    async def kick_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.moderator.id:
            return await interaction.response.send_message("❌ Только модератор может выбрать действие.", ephemeral=True)
        
        try:
            await self.member.kick(reason="Лимит варнов достигнут")
            await interaction.response.edit_message(content=f"👢 **{self.member}** был исключен с сервера.", view=None)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Недостаточно прав для кика.", ephemeral=True)

    @discord.ui.button(label="Забанить", style=discord.ButtonStyle.danger, emoji="🔨")
    async def ban_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.moderator.id:
            return await interaction.response.send_message("❌ Только модератор может выбрать действие.", ephemeral=True)
        
        try:
            await self.member.ban(reason="Лимит варнов достигнут", delete_message_days=1)
            await interaction.response.edit_message(content=f"🔨 **{self.member}** был забанен навсегда.", view=None)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Недостаточно прав для бана.", ephemeral=True)

class Warns(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_limit(self, guild_id):
        res = self.bot.supabase.table("guild_settings").select("warn_limit").eq("guild_id", str(guild_id)).execute()
        if not res.data:
            self.bot.supabase.table("guild_settings").insert({"guild_id": str(guild_id), "warn_limit": 3}).execute()
            return 3
        return res.data[0]['warn_limit']

    @commands.command(name='warn', aliases=['пред'])
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member = None, *, reason="Нарушение"):
        if not member and ctx.message.reference:
            msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            member = msg.author
        
        if not member:
            return await ctx.send("❓ Кого варним?")

        if member.bot or member.id == ctx.author.id:
            return await ctx.send("❌ Нельзя варнить ботов или себя.")

        limit = await self.get_limit(ctx.guild.id)
        uid, gid = str(member.id), str(ctx.guild.id)
        
        self.bot.supabase.table("warns").insert({
            "user_id": uid, "guild_id": gid, 
            "moderator_id": str(ctx.author.id), "reason": reason
        }).execute()
        
        res = self.bot.supabase.table("warns").select("*", count="exact").eq("user_id", uid).eq("guild_id", gid).execute()
        count = res.count if res.count else 1
        
        await ctx.send(f"⚠️ {member.mention} получил варн! **({count}/{limit})**\n**Причина:** {reason}")

        if count >= limit:
            view = WarnActionView(member, ctx.author)
            await ctx.send(f"🚨 **Лимит варнов ({limit}) достигнут для {member.mention}!**\nВыберите окончательное наказание:", view=view)

    @commands.command(name='setlimit')
    @commands.has_permissions(administrator=True)
    async def set_limit(self, ctx, new_limit: int):
        """Установить новый лимит варнов (от 3 до 10)"""
        if not (3 <= new_limit <= 10):
            return await ctx.send("❌ Установите лимит в диапазоне от **3 до 10**.")
        
        self.bot.supabase.table("guild_settings").update({"warn_limit": new_limit}).eq("guild_id", str(ctx.guild.id)).execute()
        await ctx.send(f"⚙️ Лимит варнов для этого сервера теперь: **{new_limit}**")

    @commands.command(name='warns', aliases=['варны'])
    async def warns_list(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        res = self.bot.supabase.table("warns").select("*").eq("user_id", str(member.id)).eq("guild_id", str(ctx.guild.id)).execute()
        if not res.data: return await ctx.send("✅ Нарушений нет.")
        
        limit = await self.get_limit(ctx.guild.id)
        txt = "\n".join([f"**#{i+1}** | {w['reason']} (от <@{w['moderator_id']}>)" for i, w in enumerate(res.data)])
        
        embed = discord.Embed(title=f"📋 Нарушения — {member.display_name}", description=txt, color=0x2b2d31)
        embed.set_footer(text=f"Текущий лимит сервера: {limit}")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Warns(bot))