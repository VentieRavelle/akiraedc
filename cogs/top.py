import discord
from discord.ext import commands
from discord.ui import View, Select, Button

class TopMenu(View):
    def __init__(self, bot, ctx):
        super().__init__(timeout=60)
        self.bot = bot
        self.ctx = ctx
        self.category = "balance"  
        self.scope = "server"     

    async def get_data(self):
        table = "users" if self.category == "balance" else "user_levels"
        order_col = self.category
        
        res = self.bot.supabase.table(table).select("*").order(order_col, desc=True).execute()
        data = res.data or []

        if self.scope == "server":
            member_ids = [m.id for m in self.ctx.guild.members]
            data = [u for u in data if int(u['user_id']) in member_ids]
        
        return data[:10]

    async def build_embed(self):
        data = await self.get_data()
        
        titles = {
            "balance": "💰 Богатейшие пользователи",
            "level": "🚀 Самые высокие уровни",
            "msg_count": "💬 Самые активные (сообщения)"
        }
        
        emoji = {"balance": "💸", "level": "⭐", "msg_count": "✉️"}
        
        desc = ""
        for i, user in enumerate(data, 1):
            uid = int(user['user_id'])
            val = user[self.category]
            
            member = self.ctx.guild.get_member(uid)
            name = member.display_name if member else f"ID: {uid}"
            
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"**{i}.**")
            desc += f"{medal} {name} — `{val:,}` {emoji[self.category]}\n"

        if not desc: desc = "_Данные не найдены_"

        embed = discord.Embed(
            title=f"{titles[self.category]} ({'Сервер' if self.scope == 'server' else 'Глобал'})",
            description=desc,
            color=0x2b2d31
        )
        return embed

    @discord.ui.select(
        placeholder="Выберите категорию топа...",
        options=[
            discord.SelectOption(label="По деньгам", value="balance", emoji="💰"),
            discord.SelectOption(label="По уровням", value="level", emoji="🚀"),
            discord.SelectOption(label="По сообщениям", value="msg_count", emoji="💬"),
        ]
    )
    async def select_category(self, interaction: discord.Interaction, select: Select):
        if interaction.user.id != self.ctx.author.id: return
        self.category = select.values[0]
        await interaction.response.edit_message(embed=await self.build_embed(), view=self)

    @discord.ui.button(label="Сервер / Глобал", style=discord.ButtonStyle.gray)
    async def switch_scope(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.ctx.author.id: return
        self.scope = "global" if self.scope == "server" else "server"
        await interaction.response.edit_message(embed=await self.build_embed(), view=self)

class Top(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='top')
    async def top(self, ctx):
        """Выводит настраиваемый топ игроков"""
        view = TopMenu(self.bot, ctx)
        embed = await view.build_embed()
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Top(bot))