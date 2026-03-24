import discord
from discord.ext import commands
import random
import asyncio

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def ensure_user(self, user_id: int):
        """Проверяет наличие юзера в базе. Если нет — создает."""
        uid = str(user_id)
        try:
            query = self.bot.supabase.table("users").select("*").eq("user_id", uid).maybe_single()
            response = query.execute()
            
            if not response or response.data is None:
                data = {"user_id": uid, "balance": 1000}
                self.bot.supabase.table("users").insert(data).execute()
                return data
            
            return response.data
        except Exception as e:
            print(f"🔴 Economy Error (ensure_user): {e}")
            return {"user_id": uid, "balance": 1000}

    @commands.command(name='balance', aliases=['bal', 'деньги'])
    async def balance(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        if member.bot: return
        
        async with ctx.typing():
            user_data = await self.ensure_user(member.id)
            bal = user_data.get('balance', 0)
            
            embed = discord.Embed(
                title=f"💰 Казна — {member.display_name}",
                description=f"На счету: **{bal:,} 💸**",
                color=0x2ecc71
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await ctx.send(embed=embed)

    @commands.command(name='work', aliases=['работать'])
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def work(self, ctx):
        async with ctx.typing():
            user_data = await self.ensure_user(ctx.author.id)
            current_bal = user_data.get('balance', 0)
            
            income = random.randint(150, 600)
            new_bal = current_bal + income
            
            try:
                self.bot.supabase.table("users").update({"balance": new_bal}).eq("user_id", str(ctx.author.id)).execute()
                
                jobs = [
                    "разработчиком в Google", "охотником на демонов", 
                    "бариста в Старбаксе", "личным водителем", 
                    "стримером на Twitch", "дизайнером логотипов"
                ]
                
                await ctx.send(f"🏢 **{ctx.author.display_name}**, ты поработал **{random.choice(jobs)}** и получил: `+{income} 💸`")
            except Exception as e:
                print(f"🔴 Work Error: {e}")
                await ctx.send("❌ Произошла ошибка при сохранении данных в базу.")

    @commands.command(name='pay', aliases=['передать'])
    async def pay(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            return await ctx.send("❌ Сумма должна быть больше нуля.")
        if member.bot or member.id == ctx.author.id:
            return await ctx.send("🤔 Нельзя передать деньги боту или самому себе.")

        author_data = await self.ensure_user(ctx.author.id)
        target_data = await self.ensure_user(member.id)
        
        if author_data['balance'] < amount:
            return await ctx.send("❌ У тебя недостаточно средств!")

        try:
            self.bot.supabase.table("users").update({"balance": author_data['balance'] - amount}).eq("user_id", str(ctx.author.id)).execute()
            self.bot.supabase.table("users").update({"balance": target_data['balance'] + amount}).eq("user_id", str(member.id)).execute()
            await ctx.send(f"✅ {ctx.author.mention} передал **{amount} 💸** пользователю {member.mention}!")
        except:
            await ctx.send("❌ Ошибка транзакции.")

    @commands.command(name='slots', aliases=['казино'])
    async def slots(self, ctx, bet: int):
        user_data = await self.ensure_user(ctx.author.id)
        bal = user_data.get('balance', 0)

        if bet < 50:
            return await ctx.send("❌ Минимальная ставка: `50 💸`")
        if bal < bet:
            return await ctx.send("❌ Недостаточно средств!")

        emojis = ["🍎", "🍊", "🍋", "💎", "🔔"]
        res = [random.choice(emojis) for _ in range(3)]
        
        display_slots = " | ".join(res)
        embed = discord.Embed(title="🎰 Akirae Casino", color=0xf1c40f)
        
        if res[0] == res[1] == res[2]:
            win = bet * 7
            new_bal = bal + win
            embed.description = f"**[ {display_slots} ]**\n\n🏆 **ДЖЕКПОТ!** Выигрыш: `{win} 💸`"
        elif res[0] == res[1] or res[1] == res[2] or res[0] == res[2]:
            win = int(bet * 1.5)
            new_bal = bal + win
            embed.description = f"**[ {display_slots} ]**\n\n✨ Почти! Выигрыш: `{win} 💸`"
        else:
            new_bal = bal - bet
            embed.description = f"**[ {display_slots} ]**\n\n💀 Проигрыш. Ты потерял `{bet} 💸`"

        self.bot.supabase.table("users").update({"balance": new_bal}).eq("user_id", str(ctx.author.id)).execute()
        await ctx.send(embed=embed)

    @work.error
    async def work_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            minutes = round(error.retry_after / 60)
            if minutes < 1:
                await ctx.send(f"⏳ Ты уже устал! Вернись через **{round(error.retry_after)} сек.**")
            else:
                await ctx.send(f"⏳ Ты уже устал! Вернись через **{minutes} мин.**")

async def setup(bot):
    await bot.add_cog(Economy(bot))