import json
import nextcord as discord
from nextcord.ext import commands, tasks
import lavaplayer
import config
from functions import functions
import pprint
import time
import random


PREFIX = "+"
TOKEN = config.bot_token

bot = commands.Bot(PREFIX, enable_debug_events=True)
lavalink = lavaplayer.LavalinkClient(
    host="lavalink.eu",
    port=2333,
    password="Raccoon",
    user_id=927893555366731836
)

message = None
vol = 50
last_q = []
rep = False
pas = '▶'
author = None

async def embed(end = True):
    global volume, last_q, rep, pas
    if last_q == []:
        end = False

    if end == True:
        track = last_q[0]

        embed = discord.Embed(
            description= f'🎶 | **[{track.title}]({track.uri})**',
            color=0x96516a)
        embed.add_field(name = 'Информация о треке', value =
            f"**Трек:** {track.title}\n"
            f"**Автор:** {track.author}\n"
            f"**Громкость:** {vol}%\n"
            f'**Продолжительность:** {functions.time_end(track.length / 1000)}\n'
            f'**Повтор:** {rep}\n'
            f'**Статус:** {pas}\n'.replace("True", 'Включён').replace("False", 'Отключён')
            )

        tracks = [f"**{i + 1}.** `{t.title}`" for (i, t) in enumerate(last_q)]

        embed.add_field(name = 'Очередь', value = "\n".join(tracks))
        return embed

    if end == False or last_q == []:

        embed = discord.Embed(
            description= f'Воспроизведение прервано / закончено',
            color=0x96516a)
        return embed



@bot.event
async def on_ready():
    print(f"Bot {bot.user.name} is online.")
    await bot.change_presence( status = discord.Status.online, activity = discord.Game('Starting...'))
    task.start()
    change_stats.start()

@tasks.loop(seconds = 15)
async def change_stats():
    await bot.change_presence( status = discord.Status.online, activity = discord.Game(name = f"🎵 | Музыка? +play {random.choice(['Shape of you', 'Me Too', 'Bella Cio', 'Bella Poarch'])}"))

@tasks.loop(seconds = 0.5)
async def task():
    global last_q, message, vol, rep, pas
    # print(time.time())

    if message != None:
        # print(message.id)
        if last_q != None and last_q != []:
            try:
                qu = await lavalink.queue(601124004224434357)
            except:
                qu = []

            # print(qu, last_q, qu == last_q)
            if last_q != qu:
                if len(qu) < len(last_q):
                    last_q.pop(0)
                    if last_q == []:
                        last_q = None
                    else:
                        await message.edit(embed = await embed())

        if last_q == None:
            await message.edit(embed = await embed(False))

            message = None
            vol = 50
            last_q = []
            rep = False
            pas = '▶'
            author = None

            guild = bot.get_guild(601124004224434357)
            await guild.change_voice_state(channel=None)
            await lavalink.wait_for_remove_connection(601124004224434357)


@bot.command()
async def leave(ctx):
    global author
    if ctx.author.voice == None:
        await ctx.send("Зайдите в войс!")
        return
    if author != None:
        if functions.roles_check(ctx.author, ctx.author.guild.id, author) == False:
            await ctx.send("Вы не являетесь диджеем или заказчиком музыки!")
            return
    else:
        return

    await ctx.guild.change_voice_state(channel=None)
    await lavalink.wait_for_remove_connection(ctx.guild.id)
    await ctx.message.add_reaction('✅')

@bot.command()
async def play(ctx, *, query: str):
    global message
    global last_q, author

    if ctx.author.voice == None:
        await ctx.send("Зайдите в войс!")
        return
    if author != None:
        if functions.roles_check(ctx.author, ctx.author.guild.id, author) == False:
            await ctx.send("Вы не являетесь диджеем или заказчиком музыки!")
            return

    if ctx.author.voice != None:
        tracks = await lavalink.auto_search_tracks(query)
        if not tracks:
            return await ctx.send("По вашему запросу не было найдено ни одного трека!")

        async def mus(tr):
            nonlocal tracks
            nonlocal ctx
            global last_q, author

            ntl = []
            for tt in tracks:
                ntl.append(str(tt))

            ind = int(ntl.index(tr))
            track = tracks[ind]

            await ctx.guild.change_voice_state(channel=ctx.author.voice.channel, self_deaf=True)
            await lavalink.wait_for_connection(ctx.guild.id)
            await lavalink.volume(ctx.guild.id, vol)
            await lavalink.play(ctx.guild.id, track, ctx.author.id)
            qu = await lavalink.queue(message.guild.id)
            last_q = qu.copy()
            if author == None:
                author = ctx.author

            await message.edit(view = None, embed = await embed())


        class Dropdown(discord.ui.Select):
            def __init__(self, ctx, msg, options, placeholder, min_values, max_values:int, rem_args):
                global mes
                #options.append(discord.SelectOption(label=f''))

                super().__init__(placeholder=placeholder, min_values=min_values, max_values=max_values, options=options)

                message = rem_args[0]

            async def callback(self, interaction: discord.Interaction):
                if ctx.author.id == interaction.user.id:
                    self.view.stop()

                    if message != msg:
                        await msg.delete()

                    await ctx.message.delete()
                    await mus(self.values[0])

                else:
                    await interaction.response.send_message(f'Только автор сообщения может выбрать трек!', ephemeral = True)

        class DropdownView(discord.ui.View):
            def __init__(self, ctx, msg, options:list, placeholder:str, min_values:int = 1, max_values:int = 1, timeout: float = 20.0, rem_args:list = []):
                super().__init__(timeout=timeout)
                self.add_item(Dropdown(ctx, msg, options, placeholder, min_values, max_values, rem_args))

            async def on_timeout(self):
                await msg.edit(view = None)

        ntl = []
        for tt in tracks:
            if str(tt) not in ntl:
                ntl.append(str(tt))

        if len(ntl) == 1:
            emb = discord.Embed(description = f'🎶 | Совпадение!', color= 0x96516a)
            msg = await ctx.send(embed = emb)
            if message == None:
                message = msg
            else:
                await msg.delete()

            await ctx.message.delete()
            await mus(ntl[0])

        else:
            options = []
            a = 0
            for t in ntl:
                a += 1
                if a > 25:
                    break
                options.append(discord.SelectOption(label=str(t), emoji = '🎶'))

            emb = discord.Embed(title = '🎶 | Совпадения', description = f'Найдено несколько совпадений, выберите из выпадающего списка!', color= 0x96516a)
            msg = await ctx.send(embed = emb)
            if message == None:
                message = msg

            await msg.edit(view=DropdownView(ctx, msg, options = options, placeholder = 'Сделайте выбор...', min_values = 1, max_values=1, timeout = 200.0, rem_args = [message]))



@bot.command()
async def pause(ctx):
    global pas
    global author
    if ctx.author.voice == None:
        await ctx.send("Зайдите в войс!")
        return
    if author != None:
        if functions.roles_check(ctx.author, ctx.author.guild.id, author) == False:
            await ctx.send("Вы не являетесь диджеем или заказчиком музыки!")
            return
    else:
        return
    await lavalink.pause(ctx.guild.id, True)
    pas = '⏸'
    await message.edit(embed = await embed())
    await ctx.message.add_reaction('✅')


@bot.command()
async def resume(ctx):
    global pas
    global author
    if ctx.author.voice == None:
        await ctx.send("Зайдите в войс!")
        return
    if author != None:
        if functions.roles_check(ctx.author, ctx.author.guild.id, author) == False:
            await ctx.send("Вы не являетесь диджеем или заказчиком музыки!")
            return
    else:
        return
    await lavalink.pause(ctx.guild.id, False)
    pas = '▶'
    await message.edit(embed = await embed())
    await ctx.message.add_reaction('✅')

@bot.command()
async def stop(ctx):
    global author
    if ctx.author.voice == None:
        await ctx.send("Зайдите в войс!")
        return
    if author != None:
        if functions.roles_check(ctx.author, ctx.author.guild.id, author) == False:
            await ctx.send("Вы не являетесь диджеем или заказчиком музыки!")
            return
    else:
        return
    await lavalink.stop(ctx.guild.id)
    await ctx.message.add_reaction('✅')

@bot.command()
async def skip(ctx):
    global message, last_q, rep
    global author
    if ctx.author.voice == None:
        await ctx.send("Зайдите в войс!")
        return
    if author != None:
        if functions.roles_check(ctx.author, ctx.author.guild.id, author) == False:
            await ctx.send("Вы не являетесь диджеем или заказчиком музыки!")
            return
    else:
        return
    await lavalink.skip(ctx.guild.id)
    qu = await lavalink.queue(ctx.guild.id)
    if rep != True:
        last_q.pop(0)
    if rep == True:
        last_q = qu.copy()
    if last_q == []:
        last_q = None
        await message.edit(embed = await embed(False))
    else:
        await message.edit(embed = await embed())
    await ctx.message.add_reaction('✅')

@bot.command()
async def queue(ctx):
    qu = await lavalink.queue(ctx.guild.id)
    if not qu:
        return await ctx.send("No tracks in queue.")
    tracks = [f"**{i + 1}.** {t.title}" for (i, t) in enumerate(qu)]
    await ctx.send("\n".join(tracks))

@bot.command()
async def volume(ctx, volume: int):
    global message, vol
    global author
    if ctx.author.voice == None:
        await ctx.send("Зайдите в войс!")
        return
    if author != None:
        if functions.roles_check(ctx.author, ctx.author.guild.id, author) == False:
            await ctx.send("Вы не являетесь диджеем или заказчиком музыки!")
            return
    else:
        return
    if volume > 200:
        await ctx.send("Нельзя установить громкость больше 200%!")
    else:
        await lavalink.volume(ctx.guild.id, volume)
        vol = volume
        await message.edit(embed = await embed())
        await ctx.message.add_reaction('✅')

@bot.command()
async def seek(ctx, seconds: int):
    global author
    if ctx.author.voice == None:
        await ctx.send("Зайдите в войс!")
        return
    if author != None:
        if functions.roles_check(ctx.author, ctx.author.guild.id, author) == False:
            await ctx.send("Вы не являетесь диджеем или заказчиком музыки!")
            return
    else:
        return
    await lavalink.seek(ctx.guild.id, seconds*1000)
    await ctx.message.add_reaction('✅')

# @bot.command()
# async def shuffle(ctx):
#     await lavalink.shuffle(ctx.guild.id)
#     await message.edit(embed = await embed())
#     await ctx.message.add_reaction('✅')

@bot.command()
async def clear(ctx):
    global author
    if ctx.author.voice == None:
        await ctx.send("Зайдите в войс!")
        return
    if author != None:
        if functions.roles_check(ctx.author, ctx.author.guild.id, author) == False:
            await ctx.send("Вы не являетесь диджеем или заказчиком музыки!")
            return
    else:
        return
    await lavalink.clear(ctx.guild.id)
    await message.edit(embed = await embed())
    await ctx.message.add_reaction('✅')

@bot.command()
async def repeat(ctx):
    global message, rep
    global author
    if ctx.author.voice == None:
        await ctx.send("Зайдите в войс!")
        return
    if author != None:
        if functions.roles_check(ctx.author, ctx.author.guild.id, author) == False:
            await ctx.send("Вы не являетесь диджеем или заказчиком музыки!")
            return
    else:
        return

    if rep == True:
        await lavalink.repeat(ctx.guild.id, False)
        rep = False
    else:
        await lavalink.repeat(ctx.guild.id, True)
        rep = True
    await message.edit(embed = await embed())
    await ctx.message.add_reaction('✅')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass

@bot.event
async def on_socket_raw_receive(data):
    data = json.loads(data)

    if not data or not data["t"]:
        return

    if data["t"] == "VOICE_SERVER_UPDATE":
        guild_id = int(data["d"]["guild_id"])
        endpoint = data["d"]["endpoint"]
        token = data["d"]["token"]

        await lavalink.raw_voice_server_update(guild_id, endpoint, token)

    elif data["t"] == "VOICE_STATE_UPDATE":
        if not data["d"]["channel_id"]:
            channel_id = None
        else:
            channel_id = int(data["d"]["channel_id"])

        guild_id = int(data["d"]["guild_id"])
        user_id = int(data["d"]["user_id"])
        session_id = data["d"]["session_id"]

        await lavalink.raw_voice_state_update(
            guild_id,
            user_id,
            session_id,
            channel_id,
        )

@bot.event
async def on_voice_state_update(member, before, after):
    global author, message, vol, last_q, rep, pas
    aut = author
    if aut != None:
        guild = aut.guild
        if len(aut.voice.channel.members) <= 1:
            await guild.change_voice_state(channel=None)

            message = None
            vol = 50
            last_q = []
            rep = False
            pas = '▶'
            author = None


lavalink.connect()
bot.run(TOKEN)
