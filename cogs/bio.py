import discord
from discord.ext import commands

class Bio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def update_user(self, user_id, data: dict):
        self.bot.supabase.table("users").update(data).eq("user_id", str(user_id)).execute()

    @commands.command(name='setbio')
    async def set_bio(self, ctx, *, text: str):
        """Установить описание (макс. 200 симв.)"""
        if len(text) > 200: return await ctx.send("❌ Слишком длинно!")
        await self.update_user(ctx.author.id, {"bio": text})
        await ctx.send("✅ Описание обновлено!")

    @commands.command(name='setage')
    async def set_age(self, ctx, age: int):
        """Установить возраст (1-99)"""
        if not (1 <= age <= 99): return await ctx.send("❌ Некорректный возраст.")
        await self.update_user(ctx.author.id, {"age": age})
        await ctx.send(f"✅ Возраст установлен: **{age}**")

    @commands.command(name='setgender', aliases=['пол'])
    async def set_gender(self, ctx, gender: str):
        """Установить пол (М/Ж/Другое)"""
        await self.update_user(ctx.author.id, {"gender": gender[:20]})
        await ctx.send(f"✅ Пол изменен на: **{gender}**")

    @commands.command(name='setcity', aliases=['город'])
    async def set_city(self, ctx, *, city: str):
        """Установить город проживания"""
        await self.update_user(ctx.author.id, {"location": city[:30]})
        await ctx.send(f"✅ Город установлен: **{city}**")

    @commands.command(name='sethobby', aliases=['хобби'])
    async def set_hobby(self, ctx, *, hobby: str):
        """Расскажите о своих увлечениях"""
        await self.update_user(ctx.author.id, {"hobby": hobby[:50]})
        await ctx.send("✅ Хобби сохранено!")

    @commands.command(name='setcolor')
    async def set_color(self, ctx, hex_code: str):
        """Установить цвет полоски в профиле (Hex: #ff0000)"""
        if not hex_code.startswith("#") or len(hex_code) != 7:
            return await ctx.send("❌ Формат: `#FFFFFF`")
        await self.update_user(ctx.author.id, {"custom_color": hex_code})
        await ctx.send(f"✅ Цвет профиля изменен на **{hex_code}**")

async def setup(bot):
    await bot.add_cog(Bio(bot))