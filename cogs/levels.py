import discord
from discord.ext import commands
import random
import io
from PIL import Image, ImageDraw, ImageFont

MAIN_COLOR = (255, 215, 0)
ACCENT_COLOR = (255, 255, 255)
BG_COLOR = (10, 10, 10)
BAR_BG = (40, 40, 40)
FONT_FILE = "IosevkaCharonMono-Bold.ttf"

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.xp_cooldown = commands.CooldownMapping.from_cooldown(1, 60, commands.BucketType.user)

    def get_xp_for_level(self, level):
        return 100 * (level ** 1.7)

    async def get_user_data(self, user_id):
        try:
            uid = str(user_id)
            res = self.bot.supabase.table("user_levels").select("*").eq("user_id", uid).maybe_single().execute()
            if res and res.data:
                return res.data
            
            data = {"user_id": uid, "xp": 0, "level": 1, "msg_count": 0}
            self.bot.supabase.table("user_levels").insert(data).execute()
            return data
        except Exception as e:
            print(f"DEBUG: Ошибка получения данных: {e}")
            return {"user_id": str(user_id), "xp": 0, "level": 1, "msg_count": 0}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        bucket = self.xp_cooldown.get_bucket(message)
        retry_after = bucket.update_rate_limit()
        
        if retry_after:
            return

        user_data = await self.get_user_data(message.author.id)
        
        new_msg_count = user_data.get('msg_count', 0) + 1
        
        gain = random.randint(20, 35)
        new_xp = user_data['xp'] + gain
        xp_needed = self.get_xp_for_level(user_data['level'])

        if new_xp >= xp_needed:
            new_lvl = user_data['level'] + 1
            self.bot.supabase.table("user_levels").update({
                "xp": new_xp, 
                "level": new_lvl, 
                "msg_count": new_msg_count
            }).eq("user_id", str(message.author.id)).execute()
            
            try:
                econ = self.bot.supabase.table("users").select("balance").eq("user_id", str(message.author.id)).maybe_single().execute()
                if econ.data:
                    self.bot.supabase.table("users").update({"balance": econ.data['balance'] + 2000}).eq("user_id", str(message.author.id)).execute()
            except: pass

            file = await self.generate_levelup_card(message.author, new_lvl)
            await message.channel.send(f"🚀 {message.author.mention}, уровень повышен! +2000 💸", file=file)
        else:
            self.bot.supabase.table("user_levels").update({
                "xp": new_xp,
                "msg_count": new_msg_count
            }).eq("user_id", str(message.author.id)).execute()

    async def generate_rank_card(self, member, user_data):
        lvl, xp = user_data['level'], user_data['xp']
        next_xp = self.get_xp_for_level(lvl)
        curr_xp = self.get_xp_for_level(lvl - 1) if lvl > 1 else 0
        progress = max(0, min((xp - curr_xp) / (next_xp - curr_xp), 1))

        base = Image.new("RGBA", (1200, 500), BG_COLOR)
        draw = ImageDraw.Draw(base)

        try:
            bg = Image.open("rank_bg.png").convert("RGBA").resize((1200, 500), Image.Resampling.LANCZOS)
            base.paste(bg, (0, 0))
            overlay = Image.new("RGBA", (1200, 500), (0, 0, 0, 200))
            base = Image.alpha_composite(base, overlay)
            draw = ImageDraw.Draw(base)
        except: pass

        try:
            f_name = ImageFont.truetype(FONT_FILE, 85)    
            f_lvl_val = ImageFont.truetype(FONT_FILE, 55) 
            f_lvl_txt = ImageFont.truetype(FONT_FILE, 22) 
            f_xp = ImageFont.truetype(FONT_FILE, 45)
        except:
            f_name = f_lvl_val = f_lvl_txt = f_xp = ImageFont.load_default()

        ava_b = await member.display_avatar.read()
        ava = Image.open(io.BytesIO(ava_b)).convert("RGBA").resize((260, 260), Image.Resampling.LANCZOS)
        mask = Image.new("L", (260, 260), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 260, 260), fill=255)
        ava.putalpha(mask)
        base.paste(ava, (80, 80), ava)
        draw.ellipse((75, 75, 345, 345), outline=MAIN_COLOR, width=6)

        draw.text((420, 90), member.name, font=f_name, fill=MAIN_COLOR)
        xp_text = f"{int(xp - curr_xp):,} / {int(next_xp - curr_xp):,} XP"
        draw.text((420, 230), xp_text, font=f_xp, fill=ACCENT_COLOR)

        cx, cy = 1000, 130 
        r = 70 
        draw.ellipse((cx-r, cy-r, cx+r, cy+r), outline=MAIN_COLOR, width=4)
        
        lvl_s = str(lvl)
        tw = draw.textlength(lvl_s, font=f_lvl_val)
        draw.text((cx - tw/2, cy - 45), lvl_s, font=f_lvl_val, fill=MAIN_COLOR)
        
        tw_lbl = draw.textlength("LEVEL", font=f_lvl_txt)
        draw.text((cx - tw_lbl/2, cy + 10), "LEVEL", font=f_lvl_txt, fill=ACCENT_COLOR)

        bx, by, bw, bh = 420, 310, 680, 40
        draw.rounded_rectangle((bx, by, bx + bw, by + bh), radius=20, fill=BAR_BG)
        if progress > 0:
            draw.rounded_rectangle((bx, by, bx + int(bw * progress), by + bh), radius=20, fill=MAIN_COLOR)

        buf = io.BytesIO()
        base.save(buf, "PNG")
        buf.seek(0)
        return discord.File(buf, "rank.png")

    async def generate_levelup_card(self, member, lvl):
        base = Image.new("RGBA", (550, 180), (15, 15, 15))
        draw = ImageDraw.Draw(base)
        try:
            f_up = ImageFont.truetype(FONT_FILE, 40)
            f_val = ImageFont.truetype(FONT_FILE, 70)
        except: f_up = f_val = ImageFont.load_default()
        
        draw.text((30, 30), "LEVEL UP TO", font=f_up, fill=ACCENT_COLOR)
        draw.text((30, 85), str(lvl), font=f_val, fill=MAIN_COLOR)
        
        buf = io.BytesIO()
        base.save(buf, "PNG")
        buf.seek(0)
        return discord.File(buf, "levelup.png")

    @commands.command(name='rank', aliases=['r'])
    async def rank(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        if member.bot: return
        user_data = await self.get_user_data(member.id)
        async with ctx.typing():
            file = await self.generate_rank_card(member, user_data)
            await ctx.send(file=file)

async def setup(bot):
    await bot.add_cog(Levels(bot))