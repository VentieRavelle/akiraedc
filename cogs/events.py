import discord
from discord.ext import commands

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_id = 1416034311693402134

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        
        if any(word in message.content.lower() for word in self.bot.swear_words):
            await message.delete()
            await message.channel.send(f"⚠️ {message.author.mention}, фильтруй базу!", delete_after=3)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        log_channel = self.bot.get_channel(self.log_id)
        if log_channel:
            embed = discord.Embed(title="Member Joined", description=f"{member.mention} welcome to the server!", color=0x2ecc71)
            await log_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Events(bot))