#!/usr/bin/python3
import sys
import os
import discord
import asyncio
import logging
import gspread
import traceback
from oauth2client.service_account import ServiceAccountCredentials

ID_DISCORD = 0
CHAR_NAME = 1
AGE = 2
IMAGE_URL = 3
LEVEL = 4
XP = 5
GOLD = 6
MAIN_CLASSE = 7
SECOND_CLASSE = 8
FORCE = 9
RESIS = 10
TIR = 11
AGILITE = 12
MAGIE = 13
CHARISME = 14
INTEL = 15
REMAIN = 16
NOTE = 17
ALL_STATS = [FORCE, RESIS, TIR, AGILITE, MAGIE, CHARISME, INTEL]
STAT_NAME = {
     5:"Expérience",
     6:"Crédit",
     9:"Force     ",
    10:"Résistance",
    11:"Tir       ",
    12:"Agilité   ",
    13:"Magie     ",
    14:"Charisme  ",
    15:"Intellig. "
}

logging.basicConfig(level=logging.INFO)
client = discord.Client()

gc = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_name("private/google",["https://spreadsheets.google.com/feeds"]))
wb = gc.open_by_key('1rqKgJRIqoOSa0LoWyp5Dh9PZZnUIYWqKAGB3XvOp5fk')
wb = wb.get_worksheet(0)

@client.event
async def on_message(m):
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
        except KeyError:
            await m.channel.send("Commande non reconnu")
        except Exception:
            em = discord.Embed(title="Oh no !  😱",
                               description="Une erreur s'est produite lors de l'éxécution de la commande\n```diff\n- [FATAL ERROR]\n" + traceback.format_exc() + "```",
                               colour=0xFF0000).set_footer(
                                   text="command : " + m.content,icon_url=m.author.avatar_url)
            await m.channel.send(embed=em)

async def command(message, member, cmd, args, force):
    if cmd == "stats" : await stats(message=message, member=member, args=args)
    elif cmd == "exp" : await parse_ressource(XP, message=message, args=args, member=member)
    elif cmd == "credit": await parse_ressource(GOLD, message=message, args=args, member=member)

def getstat(id):
    for line in wb.get_all_values():
        if line[ID_DISCORD] == str(id):
            return line
    return None

def get_dbb_stats_line(id):
    sh = wb.get_all_values()
    for line in range(len(sh)):
        if sh[line][ID_DISCORD] == str(id):
            return line
    return None

async def parse_ressource(ressource, message=None, member=None, args=None):
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
        
async def add_ressource(ressource, message=None, member=None, args=None):
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
    wb.update_cell(get_dbb_stats_line(member.id) + 1, ressource + 1, str(new_nb))
    if ressource == XP:
        level = get_level(new_nb)[0]
        if level > int(stat[LEVEL]):
            await message.channel.send(member.mention + " a level up au niveau " + str(level) +" !!")
        if level != int(stat[LEVEL]):
            wb.update_cell(get_dbb_stats_line(member.id) + 1, LEVEL + 1, str(level))
            wb.update_cell(get_dbb_stats_line(member.id) + 1, REMAIN + 1,
                           str(int(stat[REMAIN]) + level - int(stat[LEVEL])))
    
async def stats(message=None, member=None, args=None, force=False):
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
    em = discord.Embed(title="Fiche de personnage", colour=member.colour)
    em.add_field(
        name="Personnage",
        value="Niveau **{}**\nExpérience : {}/{}\nCrédit : {}\nClasse : **{}**\n{}{}".format(
            stat[LEVEL], stat[XP], get_level(stat[XP])[1], stat[GOLD],
            stat[MAIN_CLASSE], ' '*15, stat[SECOND_CLASSE])
        )
    em.add_field(
        name="Description",
        value=stat[NOTE]
    )
    em.add_field(
        inline=False,
        name="Statistiques",
        value="""```diff\n{}```""".format(
            "\n".join([
            ("+" if int(stat[x]) >= 60 else ("-" if int(stat[x]) < 25 else ">")) +
            STAT_NAME[x] + " :" + 
            stat[x] +
            " " * (3 - len(stat[x])) +
            "▬" * (int(stat[x]) // 5)
            for x in ALL_STATS
            ])) +
            ("Points restant : {}".format(stat[REMAIN]) if int(stat[REMAIN]) else "")
        )
    em.set_image(url=stat[IMAGE_URL])
    em.set_author(name=member.name, url=member.avatar_url)
    await message.channel.send(embed=em)


def get_level(xp):
    xp = int(xp)
    xpNeeded = 100
    level = 0
    while xp >= xpNeeded:
        level += 1
        xpNeeded += 100 + 10 * level
    return (level, xpNeeded)
        
with open("private/token") as fd: client.run(fd.read())
