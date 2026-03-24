import discord
from discord.ext import commands
from discord.ui import View, Button

SHOP_ITEMS = {
    "Vip": {"price": 50000, "role_id": 123456789012345678, "desc": "Особый статус в чате"},
    "Legend": {"price": 150000, "role_id": 987654321098765432, "desc": "Золотой ник и респект"},
}

class ShopView(View):
    def __init__(self, bot, ctx):
        super().__init__(timeout=60)
        self.bot = bot
        self.ctx = ctx

    async def buy_item(self, interaction: discord.Interaction, item_name: str):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("Это не ваше меню!", ephemeral=True)

        item = SHOP_ITEMS[item_name]
        uid = str(self.ctx.author.id)

        res = self.bot.supabase.table("users").select("balance").eq("user_id", uid).maybe_single().execute()
        balance = res.data['balance'] if res.data else 0

        if balance < item['price']:
            return await interaction.response.send_message(f"❌ Недостаточно средств! Нужно `{item['price']:,} 💸`", ephemeral=True)

        new_bal = balance - item['price']
        self.bot.supabase.table("users").update({"balance": new_bal}).eq("user_id", uid).execute()

        role = self.ctx.guild.get_role(item['role_id'])
        if role:
            try:
                await self.ctx.author.add_roles(role)
            except:
                pass 

        self.bot.supabase.table("inventory").insert({"user_id": uid, "item_name": item_name}).execute()

        await interaction.response.send_message(f"✅ Вы успешно купили **{item_name}** за `{item['price']:,} 💸`!", ephemeral=False)
        self.stop()

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='shop', aliases=['магазин'])
    async def shop(self, ctx):
        """Открыть магазин сервера"""
        embed = discord.Embed(
            title="🛒 Городской рынок Akirae",
            description="Выберите товар, который хотите приобрести:",
            color=0xffdd00
        )

        view = ShopView(self.bot, ctx)

        for name, info in SHOP_ITEMS.items():
            embed.add_field(
                name=f"{name} — {info['price']:,} 💸",
                value=info['desc'],
                inline=False
            )
            btn = Button(label=f"Купить {name}", style=discord.ButtonStyle.success)
            
            async def callback(interaction, n=name):
                await view.buy_item(interaction, n)
            
            btn.callback = callback
            view.add_item(btn)

        await ctx.send(embed=embed, view=view)

    @commands.command(name='inv', aliases=['inventory', 'инвентарь'])
    async def inventory(self, ctx):
        """Посмотреть свои покупки"""
        uid = str(ctx.author.id)
        res = self.bot.supabase.table("inventory").select("item_name").eq("user_id", uid).execute()
        
        if not res.data:
            return await ctx.send("📭 Ваш инвентарь пуст.")

        items = [item['item_name'] for item in res.data]
        await ctx.send(f"🎒 **Инвентарь {ctx.author.display_name}:**\n" + ", ".join(set(items)))

async def setup(bot):
    await bot.add_cog(Shop(bot))