import discord
from discord.ext import commands

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_full_user_data(self, user_id: int):
        uid = str(user_id)
        user_info = self.bot.supabase.table("users").select("*").eq("user_id", uid).maybe_single().execute()
        lvl_info = self.bot.supabase.table("user_levels").select("*").eq("user_id", uid).maybe_single().execute()
        
        return {
            "profile": user_info.data if user_info.data else {},
            "levels": lvl_info.data if lvl_info.data else {"level": 1, "xp": 0, "msg_count": 0}
        }

    @commands.command(name='profile', aliases=['p', 'профиль'])
    async def profile(self, ctx, member: discord.Member = None):
        """Показать расширенную карточку профиля"""
        member = member or ctx.author
        if member.bot: return

        async with ctx.typing():
            data = await self.get_full_user_data(member.id)
            prof = data["profile"]
            lvls = data["levels"]

            embed_color = prof.get("custom_color", "#ffdd00")
            try:
                color = discord.Color(int(embed_color.replace("#", ""), 16))
            except:
                color = discord.Color.from_rgb(255, 221, 0)

            embed = discord.Embed(title=f"📋 Личное дело — {member.display_name}", color=color)
            
            bio_info = (
                f"**🎂 Возраст:** `{prof.get('age') or '—'}`\n"
                f"**⚧️ Пол:** `{prof.get('gender') or 'Не указан'}`\n"
                f"**📍 Город:** `{prof.get('location') or 'Скрыт'}`\n"
                f"**🎨 Хобби:** `{prof.get('hobby') or 'Отсутствует'}`"
            )
            embed.add_field(name="👤 Личность", value=bio_info, inline=True)

            game_info = (
                f"**🆙 Уровень:** `{lvls.get('level', 1)}`\n"
                f"**💰 Баланс:** `{prof.get('balance', 0):,} 💸`\n"
                f"**⭐ Репутация:** `{prof.get('rep', 0)}`\n"
                f"**💬 Сообщений:** `{lvls.get('msg_count', 0)}`"
            )
            embed.add_field(name="📊 Прогресс", value=game_info, inline=True)

            about_me = prof.get('bio', 'Пользователь еще не заполнил биографию.')
            embed.add_field(name="📝 О себе", value=f"```text\n{about_me}```", inline=False)

            embed.set_thumbnail(url=member.display_avatar.url)
            
            if prof.get('partner_id'):
                embed.add_field(name="❤️ Партнер", value=f"<@{prof['partner_id']}>", inline=False)

            created_at = member.created_at.strftime("%d.%m.%Y")
            embed.set_footer(text=f"В Discord с {created_at} • ID: {member.id}")

            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Profile(bot))