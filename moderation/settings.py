import discord
from discord.ext import commands

class SettingsView(discord.ui.View):
    def __init__(self, bot, guild, author):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild = guild
        self.author = author
        self.page = "main"
        self.add_main_buttons() 

    def add_main_buttons(self):
        self.clear_items()
        btn_mod = discord.ui.Button(label="Модерация", style=discord.ButtonStyle.blurple, emoji="🛡️")
        btn_mod.callback = self.go_mod
        self.add_item(btn_mod)
        
        btn_log = discord.ui.Button(label="Логи", style=discord.ButtonStyle.gray, emoji="📜")
        btn_log.callback = self.go_logs
        self.add_item(btn_log)

    async def get_config(self):
        res = self.bot.supabase.table("guild_settings").select("*").eq("guild_id", str(self.guild.id)).execute()
        if not res.data:
            data = {"guild_id": str(self.guild.id), "warn_limit": 3}
            self.bot.supabase.table("guild_settings").insert(data).execute()
            return data
        return res.data[0]

    def create_embed(self, conf):
        warn_limit = conf.get('warn_limit', 3)
        log_channel = conf.get('log_channel_id')
        mute_role = conf.get('muted_role_id')
        
        emb = discord.Embed(color=0x2b2d31)
        if self.page == "main":
            emb.title = f"🛠 Akirae Dashboard — {self.guild.name}"
            status = (f"**Варн-лимит:** `{warn_limit}`\n"
                      f"**Логи:** <#{log_channel}>\n" if log_channel else "**Логи:** `Выключены` ❌\n")
            status += f"**Роль мута:** <@&{mute_role}>" if mute_role else "**Роль мута:** `Не выбрана` ❌"
            emb.add_field(name="📊 Текущий статус", value=status)
        elif self.page == "mod":
            emb.title = "🛡 Модерация"
            emb.description = f"Настройте лимиты. Текущий: **{warn_limit}**"
        elif self.page == "logs":
            emb.title = "📜 Логирование"
            emb.description = "Выберите канал для отчетов."
        return emb

    async def update_message(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("❌ Не ваше меню.", ephemeral=True)
            
        conf = await self.get_config()
        self.clear_items()
        
        if self.page == "main":
            self.add_main_buttons()
        elif self.page == "mod":
            s_warn = discord.ui.Select(placeholder="Лимит варнов", options=[
                discord.SelectOption(label="1 Варна", value="1"),
                discord.SelectOption(label="2 Варна", value="2"),
                discord.SelectOption(label="3 Варна", value="3"),
                discord.SelectOption(label="4 Варна", value="4"),
                discord.SelectOption(label="5 Варна", value="5"),
                discord.SelectOption(label="6 Варна", value="6"),
                discord.SelectOption(label="7 Варна", value="7"),
                discord.SelectOption(label="8 Варна", value="8"),
                discord.SelectOption(label="9 Варна", value="9"),
                discord.SelectOption(label="10 Варна", value="10"),
                discord.SelectOption(label="15 Варнов", value="15"),
                discord.SelectOption(label="20 Варнов", value="20"),
                discord.SelectOption(label="25 Варнов", value="25"),
                discord.SelectOption(label="30 Варнов", value="30"),
            ])
            s_warn.callback = self.set_warn_limit
            self.add_item(s_warn)
            
            s_role = discord.ui.RoleSelect(placeholder="Роль мута", max_values=1)
            s_role.callback = self.set_mute_role
            self.add_item(s_role)
        elif self.page == "logs":
            s_ch = discord.ui.ChannelSelect(placeholder="Канал логов", channel_types=[discord.ChannelType.text])
            s_ch.callback = self.set_log_channel
            self.add_item(s_ch)

        if self.page != "main":
            back = discord.ui.Button(label="Назад", style=discord.ButtonStyle.red)
            back.callback = self.go_main
            self.add_item(back)

        await interaction.response.edit_message(embed=self.create_embed(conf), view=self)

    async def go_mod(self, interaction): self.page = "mod"; await self.update_message(interaction)
    async def go_logs(self, interaction): self.page = "logs"; await self.update_message(interaction)
    async def go_main(self, interaction): self.page = "main"; await self.update_message(interaction)

    async def set_warn_limit(self, interaction):
        val = int(interaction.data['values'][0])
        self.bot.supabase.table("guild_settings").update({"warn_limit": val}).eq("guild_id", str(self.guild.id)).execute()
        await interaction.response.send_message(f"✅ Лимит: {val}", ephemeral=True)
        await self.update_message(interaction)

    async def set_log_channel(self, interaction):
        ch_id = interaction.data['values'][0]
        self.bot.supabase.table("guild_settings").update({"log_channel_id": str(ch_id)}).eq("guild_id", str(self.guild.id)).execute()
        await interaction.response.send_message("✅ Логи настроены", ephemeral=True)
        await self.update_message(interaction)

    async def set_mute_role(self, interaction):
        r_id = interaction.data['values'][0]
        self.bot.supabase.table("guild_settings").update({"muted_role_id": str(r_id)}).eq("guild_id", str(self.guild.id)).execute()
        await interaction.response.send_message("✅ Роль мута сохранена", ephemeral=True)
        await self.update_message(interaction)

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='st')
    @commands.has_permissions(administrator=True)
    async def st(self, ctx):
        res = self.bot.supabase.table("guild_settings").select("*").eq("guild_id", str(ctx.guild.id)).execute()
        conf = res.data[0] if res.data else {"warn_limit": 3}
        view = SettingsView(self.bot, ctx.guild, ctx.author)
        await ctx.send(embed=view.create_embed(conf), view=view)

async def setup(bot):
    await bot.add_cog(Settings(bot))