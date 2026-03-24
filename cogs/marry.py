import discord
from discord.ext import commands
import asyncio
import datetime

class Marry(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='marry')
    async def marry(self, ctx, member: discord.Member):
        if member == ctx.author:
            return await ctx.send("💑 Вы не можете жениться на самом себе!")
        if member.bot:
            return await ctx.send("🤖 Боты не вступают в браки.")

        for user_id in [ctx.author.id, member.id]:
            check = self.bot.supabase.table("marriages") \
                .select("*") \
                .or_(f"user_one.eq.{user_id},user_two.eq.{user_id}") \
                .maybe_single().execute()
            
            if check.data:
                who = "Вы уже состоите" if user_id == ctx.author.id else f"{member.display_name} уже состоит"
                return await ctx.send(f"💍 {who} в браке!")

        embed = discord.Embed(
            title="❤️ Предложение руки и сердца",
            description=f"{member.mention}, пользователь {ctx.author.mention} предлагает вам вступить в брак!\n\n"
                        f"Напишите **`да`** или **`нет`** в чат.",
            color=0xff69b4
        )
        await ctx.send(embed=embed)

        def check_response(m):
            return m.author == member and m.channel == ctx.channel and m.content.lower() in ["да", "нет"]

        try:
            msg = await self.bot.wait_for('message', check=check_response, timeout=60.0)
            
            if msg.content.lower() == "да":
                now = datetime.datetime.utcnow().isoformat()
                self.bot.supabase.table("marriages").insert({
                    "user_one": ctx.author.id,
                    "user_two": member.id,
                    "married_at": now
                }).execute()

                await ctx.send(f"🎊 Поздравляем! {ctx.author.mention} и {member.mention} теперь официально женаты! ❤️")
            else:
                await ctx.send(f"💔 {ctx.author.mention}, к сожалению, вам отказали.")

        except asyncio.TimeoutError:
            await ctx.send(f"⌛ {member.mention} не ответил вовремя. Предложение аннулировано.")

    @commands.command(name='divorce')
    async def divorce(self, ctx):
        """Развод с текущим партнером"""
        res = self.bot.supabase.table("marriages") \
            .delete() \
            .or_(f"user_one.eq.{ctx.author.id},user_two.eq.{ctx.author.id}") \
            .execute()

        if res.data:
            await ctx.send(f"📉 {ctx.author.mention}, вы теперь официально разведены.")
        else:
            await ctx.send("❌ Вы и так не состоите в браке.")

async def setup(bot):
    await bot.add_cog(Marry(bot))