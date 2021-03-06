#!/usr/bin/python3
import discord
import logging
import traceback
from typing import Optional

from exc import SITOException
from pnj_manager import pnj_say
from archiver import archive
from DynamicEmbed import on_reaction_change
from gdoc_manager import DataBase, PJ
from roll import cmd_test

logging.basicConfig(level=logging.INFO)
client = discord.Client()

GUILD_ID = 457673969017815063
db = None # wait for discord socket to be initialised

@client.event
async def on_ready():
    print("Connected")
    global db
    db = DataBase(guild=client.get_guild(GUILD_ID))

@client.event
async def on_raw_reaction_add(payload : discord.RawReactionActionEvent):
    if payload.user_id == client.user.id: return
    await on_reaction_change(payload)

@client.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    if payload.user_id == client.user.id: return
    await on_reaction_change(payload)


@client.event
async def on_message(m: discord.Message):
    if m.content.startswith(">>"):
        await pnj_say(m, db.get_all_pnj_info())
    if m.content.startswith('/'):
        member = m.author
        cmd = m.content.split(" ")[0][1:].lower()
        force = True if cmd == "force" and member.id == 384274248799223818 else False
        if force:
            cmd = m.content.split(" ")[1].lower()
            args = m.content.split(" ")[2:]
        else: args = m.content.split(" ")[1:]
        try:
            await command(m, member, cmd, args, force)
        except SITOException:
            error = traceback.format_exc().split('\n')[-1] or traceback.format_exc().split('\n')[-2]
            await m.channel.send(error[4:])
        except Exception:
            em = discord.Embed(title="Oh no !  😱",
                               description="Une erreur s'est produite lors de l'éxécution de la commande\n```diff\n- [FATAL ERROR]\n" + traceback.format_exc() + "```",
                               colour=0xFF0000)
            em.set_footer(text="command : " + m.content,icon_url=m.author.avatar_url)
            await m.channel.send(embed=em)

async def command(message : discord.Message, member, cmd : str, args : list, force : bool):
    if cmd == "stats" : await stats(message=message, member=member, args=args)
    elif cmd == "exp" : await parse_ressource(XP, message=message, args=args, member=member)
    elif cmd == "credit": await parse_ressource(GOLD, message=message, args=args, member=member)
    elif cmd == "archive": await archive(message, message.channel)
    elif cmd == "test":await cmd_test(message, member, args, database=db)
    elif cmd == "dbrefresh":
        db.refresh()
        await message.channel.send("done")

def getstat(id) -> Optional[list]:
    for line in db.get_all_pj_info():
        if line[0] == str(id):
            return line
    return None

def get_dbb_stats_line(id) -> Optional[int]:
    ll = db.get_all_pj_info()
    for line in range(len(ll)):
        if ll[line][0] == str(id):
            return line
    return None

def get_level(xp) -> tuple:
    xp = int(xp)
    xpNeeded = 100
    level = 0
    while xp >= xpNeeded:
        level += 1
        xpNeeded += 100 + 10 * level
    return (level, xpNeeded)

# COMMANDS

async def parse_ressource(ressource: int, message=None, member=None, args=None):
    if not args:
        stat = getstat(member.id)
        await message.channel.send("Vous avez {} {}".format(stat[ressource] ,STAT_NAME[ressource]))
    if len(args) == 1:
        member = message.guild.get_member_named(args[0])
        if not member:
            await message.channel.send("Membre non trouvé")
            return None
        stat = getstat(member.id)
        if not stat:
            await message.channel.send("Le membre ne possède aucun personnage joueur")
            return None
        await message.channel.send(member.name + " a {} {}".format(stat[ressource], STAT_NAME[ressource]))
    if len(args) == 2:
        await add_ressource(ressource, message=message, member=member, args=args)
        
async def add_ressource(ressource : int, message=None, member=None, args=None):
    sh = db.pj_sh
    nb = int(args[-1])
    member = message.guild.get_member_named(" ".join(args[:-1]))
    if not member:
        await message.channel.send("Membre non trouvé")
        return None
    stat = getstat(member.id)
    new_nb = int(stat[ressource]) + nb
    msg = "{} a {} {} {}, il en possède désormais {}".format(
                                member.mention,
                                "gagné" if nb > 0 else "perdu",
                                abs(nb),
                                STAT_NAME[ressource].replace(' ',''),
                                new_nb
    )
    await message.channel.send(msg)
    sh.update_cell(get_dbb_stats_line(member.id) + 1, ressource + 1, str(new_nb))
    if ressource == XP:
        level = get_level(new_nb)[0]
        if level > int(stat[LEVEL]):
            await message.channel.send(member.mention + " a level up au niveau " + str(level) +" !!")
        if level != int(stat[LEVEL]):
            sh.update_cell(get_dbb_stats_line(member.id) + 1, LEVEL + 1, str(level))
            sh.update_cell(get_dbb_stats_line(member.id) + 1, REMAIN + 1,
                           str(int(stat[REMAIN]) + level - int(stat[LEVEL])))
    db.refresh()
    
async def stats(message=None, member=None, args=None, force=False):
    await message.channel.trigger_typing()
    if args:
        member = message.guild.get_member_named(" ".join(args))
        if not member:
            await message.channel.send("Membre non trouvé")
            return None
    if len(args) >= 2:
        member = message.guild.get_member_named(args[1])
        if not member:
            await message.channel.send("Membre non trouvé")
            return False
    stat = getstat(member.id)
    if not stat:
        await message.channel.send("Le membre n'a pas de personnage joueur")
        return None
    pj = PJ(stat, guild=message.guild)
    await pj.create_interactive_sheet(message.channel)

        
with open("private/token") as fd: client.run(fd.read())
