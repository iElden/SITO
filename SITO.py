#!/usr/bin/python3
import discord
import logging
import gspread
import traceback
from oauth2client.service_account import ServiceAccountCredentials

from constant import *
from pnj_manager import pnj_say

logging.basicConfig(level=logging.INFO)
client = discord.Client()

class DataBase:
    def __init__(self):
        gc = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_name("private/google",["https://spreadsheets.google.com/feeds"]))
        self.wb = gc.open_by_key('1rqKgJRIqoOSa0LoWyp5Dh9PZZnUIYWqKAGB3XvOp5fk')
        self.pj_sh = self.wb.get_worksheet(0)
        self.pnj_sh = self.wb.get_worksheet(1)
        self.pj_ll = None
        self.pnj_ll = None
        self.refresh()
    def get_pj_info(self) -> [list]:
        return self.pj_ll
    def get_pnj_info(self) -> [list]:
        return self.pnj_ll
    def refresh(self):
        self.pj_ll = self.pj_sh.get_all_values()
        self.pnj_ll = self.pnj_sh.get_all_values()

db = DataBase()

@client.event
async def on_message(m: discord.Message):
    if m.content.startswith(">>"):
        await pnj_say(m, db.get_pnj_info())
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
                               colour=0xFF0000)
            em.set_footer(text="command : " + m.content,icon_url=m.author.avatar_url)
            await m.channel.send(embed=em)

async def command(message : discord.Message, member, cmd : str, args : list, force : bool):
    if cmd == "stats" : await stats(message=message, member=member, args=args)
    elif cmd == "exp" : await parse_ressource(XP, message=message, args=args, member=member)
    elif cmd == "credit": await parse_ressource(GOLD, message=message, args=args, member=member)
    elif cmd == "dbrefresh":
        db.refresh()
        await message.channel.send("done")

def getstat(id) -> list:
    for line in db.get_pj_info():
        if line[ID_DISCORD] == str(id):
            return line
    return None

def get_dbb_stats_line(id) -> int:
    ll = db.get_pj_info()
    for line in range(len(ll)):
        if ll[line][ID_DISCORD] == str(id):
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

        
with open("private/token") as fd: client.run(fd.read())
