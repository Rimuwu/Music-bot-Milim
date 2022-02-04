import nextcord as discord
from nextcord.utils import utcnow
import math
import time
from datetime import datetime, timedelta
import pprint
import asyncio
import config

class functions:

    @staticmethod
    def time_end(seconds:int, mini = False):

        mm = int(seconds//2592000)
        seconds -= mm*2592000
        w = int(seconds//604800)
        seconds -= w*604800
        d = int(seconds//86400)
        seconds -= d*86400
        h = int(seconds//3600)
        seconds -= h*3600
        m = int(seconds//60)
        seconds -= m*60
        s = int(seconds%60)

        if mm < 10: mm = f"0{mm}"
        if w < 10: w = f"0{w}"
        if d < 10: d = f"0{d}"
        if h < 10: h = f"0{h}"
        if m < 10: m = f"0{m}"
        if s < 10: s = f"0{s}"

        if m == '00' and h == '00' and d == '00' and w == '00' and mm == '00':
            return f"{s}c"
        elif h == '00' and d == '00' and w == '00' and mm == '00':
            return f"{m}:{s}c"
        elif d == '00' and w == '00' and mm == '00':
            return f"{h}:{m}:{s}c"
        elif w == '00' and mm == '00':
            return f"{d}:{h}:{m}:{s}c"
        elif mm == '00':
            return f"{w}:{h}:{m}:{s}c"
        else:
            return f"{M}:{w}:{h}:{m}:{s}c"


    @staticmethod
    def roles_check(user:discord.Member, guild_id:int, author):
        roles = user.roles
        list_roles = []

        if user.id == author.id:
            return True
        else:
            if user.guild_permissions.administrator == True:
                return True
            else:
                for role in roles: list_roles.append(role.id)
                result = list(set(config.dj_roles) & set(list_roles))
                if result != []:
                    return True
                else:
                    return False
