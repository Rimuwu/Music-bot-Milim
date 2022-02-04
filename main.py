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
bot.remove_command( "help" )

message = None
vol = 50
last_q = []
rep = False
pas = '▶'
author = None
rec = False

async def embed(end = True):
    global volume, last_q, rep, pas, author, rec, PREFIX, message
    if last_q == []:
        end = False

    if end == True:
        track = last_q[0]

        embed = discord.Embed(
            description= f'**[`{track.title}`]({track.uri})**',
            color=0x96516a)
        embed.add_field(name = '🎶 | Информация о треке', value =
            f"**Трек:** {track.title}\n"
            f"**Автор:** {track.author}\n"
            f"**Громкость:** {vol}%\n"
            f'**Продолжительность:** {functions.time_end(track.length / 1000)}\n'
            f'**Повтор:** {rep}\n'
            f'**Статус:** {pas}\n'
            f'**Заказал**: {author.mention}'.replace("True", 'Включён').replace("False", 'Отключён')
            )

        tracks = [f"**{i + 1}.** `{t.title}`" for (i, t) in enumerate(last_q)]
        embed.add_field(name = '🎞 | Очередь', value = "\n".join(tracks))

        embed.add_field(name = '🎨 | Команды', value = f"Пропишите **{PREFIX}mhelp** для получения команд!" , inline = False)

    if end == False or last_q == []:
        embed = discord.Embed(
            description= f'Воспроизведение прервано / закончено',
            color=0x96516a)
        try:
            await message.clear_reactions()
        except:
            pass

    await message.edit(view = None, embed = embed)

    if rec == False:
        rec = True
        for i in ['▶', '⏸', '🔄', '🔀', '🔉', '🔊', '⏩', '⏹️']:
            await message.add_reaction(i)

@bot.event
async def on_ready():
    print(f"Bot {bot.user.name} is online.")
    await bot.change_presence( status = discord.Status.online, activity = discord.Game('Starting...'))
    task.start()
    change_stats.start()

@tasks.loop(seconds = 15)
async def change_stats():
    await bot.change_presence( status = discord.Status.online, activity = discord.Game(name = f"🎵 | Музыка? +play {random.choice(['Shape of you', 'Me Too', 'Bella Cio', 'Bella Poarch', 'Go Kitty Go'])}"))

@tasks.loop(seconds = 0.5)
async def task():
    global last_q, message, vol, rep, pas, author, rec
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
                        await embed()

        if last_q == None:
            await embed(False)

            message = None
            vol = 50
            last_q = []
            rep = False
            pas = '▶'
            author = None
            rec = False

            guild = bot.get_guild(601124004224434357)
            await guild.change_voice_state(channel=None)
            await lavalink.wait_for_remove_connection(601124004224434357)


@bot.command()
async def mhelp(ctx):
    global author
    embed = discord.Embed(
        description= f'🎶 | **Помощь**',
        color=0x96516a)
    embed.add_field(name = '👁‍🗨 | Команды', value =
                f'**{ctx.prefix}mhelp** - команда помощи\n'
                f'**{ctx.prefix}play (url / music_name)** - включить трек / добавить в очередь\n'
                f'**{ctx.prefix}leave - отключить бота от войса**\n'
                f'**{ctx.prefix}pause** - поставить на паузы\n'
                f'**{ctx.prefix}resume** - снять с паузы\n'
                f'**{ctx.prefix}stop** - остановить воспроизведение\n'
                f'**{ctx.prefix}skip** - пропустить играющий трек\n'
                f'**{ctx.prefix}queue** - показать очередь треков\n'
                f'**{ctx.prefix}volume (1 - 200)** - установить громкость\n'
                f'**{ctx.prefix}seek (sec)** - установка позиции трека\n'
                f'**{ctx.prefix}shuffle** - перемешать очередь\n'
                f'**{ctx.prefix}repeat** - включить повтор трека / очереди\n'
    )
    if author != None:
        embed.add_field(name = '👁 | Статус', inline = False, value = f'Могу я в данный момент управлять треками?\nСтатус: {functions.roles_check(ctx.author, ctx.author.guild.id, author)}'.replace('True', '**Да**').replace('False', '**Нет**')
    )
    await ctx.send(embed = embed)

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

            await embed()


        class Dropdown(discord.ui.Select):
            def __init__(self, ctx, msg, options, placeholder, min_values, max_values:int, rem_args):
                global mes

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


            async def on_error(self, error, item, interaction):
                pass

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
    await embed()
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
    await embed()
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
    if rep == True:
        pass
    else:
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
    if volume > 200 or volume < 1:
        await ctx.send("Нельзя установить громкость больше 200% или меньше 1%!")
    else:
        await lavalink.volume(ctx.guild.id, volume)
        vol = volume
        await embed()
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

@bot.command()
async def shuffle(ctx):
    global last_q, rep, author
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
        await ctx.send("Отключите повтор!")
    else:
        i = await lavalink.shuffle(ctx.guild.id)
        last_q = i.queue.copy()
        await embed()
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
    await embed()
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
    global last_q, message, vol, rep, pas, author, rec
    aut = author
    if aut != None:
        if aut.id == member.id:
            guild = aut.guild

            if guild.me.voice == None:
                try:
                    await guild.change_voice_state(channel=None)

                    message = None
                    vol = 50
                    last_q = []
                    rep = False
                    pas = '▶'
                    author = None
                    rec = False
                except:
                    pass

            else:
                if len(guild.me.voice.channel.members) <= 1:
                    await guild.change_voice_state(channel=None)

                    message = None
                    vol = 50
                    last_q = []
                    rep = False
                    pas = '▶'
                    author = None
                    rec = False

@bot.event
async def on_raw_reaction_add(payload):
    global last_q, message, vol, rep, pas, author, rec
    if message != None:
        if payload.member.bot == False:
            if message.id == payload.message_id:
                await message.remove_reaction(payload.emoji, payload.member)
                if functions.roles_check(payload.member, payload.member.guild.id, author) == True:
                    if payload.emoji.name in ['▶', '⏸', '🔄', '🔀', '🔉', '🔊', '⏩', '⏹️']:
                        rec = payload.emoji.name
                        if rec == '▶':

                            await lavalink.pause(payload.member.guild.id, False)
                            pas = '▶'

                        elif rec == '⏸':

                            await lavalink.pause(payload.member.guild.id, True)
                            pas = '⏸'

                        elif rec == '🔄':

                            if rep == True:
                                await lavalink.repeat(payload.member.guild.id, False)
                                rep = False
                            else:
                                await lavalink.repeat(payload.member.guild.id, True)
                                rep = True

                        elif rec == '🔀':

                            if rep == True:
                                pass
                            else:
                                i = await lavalink.shuffle(payload.member.guild.id)
                                last_q = i.queue.copy()

                        elif rec == '🔉':
                            if vol - 10 < 1:
                                vol = 1
                            else:
                                vol -= 10

                            await lavalink.volume(payload.member.guild.id, vol)

                        elif rec == '🔊':

                            if vol + 10 > 200:
                                vol = 200
                            else:
                                vol += 10

                            await lavalink.volume(payload.member.guild.id, vol)

                        elif rec == '⏩':

                            await lavalink.skip(payload.member.guild.id)

                        elif rec == '⏹️':

                            await lavalink.stop(payload.member.guild.id)

                        await embed()

lavalink.connect()
bot.run(TOKEN)
