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
RESISTANCE = 10
TIR = 11
AGILITE = 12
MAGIE = 13
CHARISME = 14
INTELLIGENCE = 15
REMAIN = 16

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
    
def getstat(id):
    for line in wb.get_all_values():
        if line[ID_DISCORD] == str(id):
            return line
    return None
            
async def stats(message=None, member=None, args=None, force=False):
    if not args : args = ["show"]
    if args[0] == "show":
        stat = getstat(message.guild.get_member(args[1]) if len(args) >= 2 else member.id)
        em = discord.Embed(title="Fiche de personnage",
              description="Niveau {} ({})\nClasse : **{}**/{}".format(
                  stat[LEVEL],stat[XP],stat[MAIN_CLASSE],stat[SECOND_CLASSE]) +
"""```
Force       : {}
Résistance  : {}
Tir         : {}
Agilité     : {}
Magie       : {}
Charisme    : {}
Intelligence: {}
```""".format(stat[FORCE],stat[RESISTANCE],stat[TIR],stat[AGILITE],
           stat[MAGIE],stat[CHARISME],stat[INTELLIGENCE]))
        em.set_image(url=stat[IMAGE_URL])
        em.set_author(name=member.name, url=member.avatar_url)
        await message.channel.send(embed=em)


with open("private/token") as fd: client.run(fd.read())
