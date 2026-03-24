import discord
from discord.ext import commands
import traceback

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        error = getattr(error, 'original', error)

        if isinstance(error, commands.MissingPermissions):
            perms = ", ".join(error.missing_permissions).replace('_', ' ').title()
            return await ctx.send(f"🚫 {ctx.author.mention}, нужны права: `{perms}`", delete_after=5)

        elif isinstance(error, commands.BotMissingPermissions):
            perms = ", ".join(error.missing_permissions).replace('_', ' ').title()
            return await ctx.send(f"❌ Мне не хватает прав: `{perms}`", delete_after=7)

        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(f"⏳ Подождите **{error.retry_after:.1f}с.** перед повтором.", delete_after=3)

        elif isinstance(error, commands.MissingRequiredArgument):
            usage = f"{ctx.prefix}{ctx.command} {ctx.command.signature}"
            return await ctx.send(f"❓ Не хватает аргумента: `{error.param.name}`\nИспользование: `{usage}`", delete_after=10)

        elif isinstance(error, (commands.MemberNotFound, commands.UserNotFound)):
            return await ctx.send("👤 Пользователь не найден. Убедитесь, что ID верен или юзер есть на сервере.", delete_after=5)
        
        elif isinstance(error, commands.ChannelNotFound):
            return await ctx.send("📺 Канал не найден.", delete_after=5)

        elif isinstance(error, commands.BadArgument):
            return await ctx.send("⚠️ Неверный формат данных. Проверьте ввод.", delete_after=5)

        elif isinstance(error, commands.CommandNotFound):
            return

        else:
            print(f"🔥 [Критическая ошибка]: {error}")
            traceback.print_exception(type(error), error, error.__traceback__)
            
            try:
                res = self.bot.supabase.table("guild_settings").select("log_channel_id").eq("guild_id", str(ctx.guild.id)).execute()
                
                if res.data and res.data[0].get('log_channel_id'):
                    log_channel = self.bot.get_channel(int(res.data[0]['log_channel_id']))
                    if log_channel:
                        emb = discord.Embed(title="🚨 Ошибка выполнения", color=discord.Color.red())
                        emb.add_field(name="Команда", value=f"`{ctx.message.content}`", inline=False)
                        emb.add_field(name="Автор", value=f"{ctx.author} (`{ctx.author.id}`)", inline=True)
                        error_text = str(error)[:1000]
                        emb.description = f"```py\n{error_text}\n```"
                        await log_channel.send(embed=emb)
            except Exception as e:
                print(f"⚠️ Не удалось отправить лог ошибки: {e}")

async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))