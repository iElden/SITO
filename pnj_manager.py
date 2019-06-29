import discord
import logging
from constant import *

logger = logging.getLogger("PNJ Manager")


async def get_webhook(channel : discord.TextChannel) -> discord.Webhook:
    webhooks = await channel.webhooks()
    for webhook in webhooks:
        if webhook.name == WEBHOOK_NAME:
            return webhook
    logger.info("PNJ Manager not found, creating webhook ...")
    webhook = await channel.create_webhook(name=WEBHOOK_NAME)
    return webhook

async def get_pnj(ll : [list], pnj_name : str) -> list:
    for line in ll:
        if line[CHAR_NAME].lower() == pnj_name.lower():
            return line
    return None

async def pnj_say(message: discord.Message, ll : [list]):
    webhook = await get_webhook(message.channel)
    pnj, content = message.content.split('\n', 1)
    pnj = pnj[2:]
    line = await get_pnj(ll, pnj)
    if not line:
        await message.channel.send("Le PNJ {} n'a pas été trouvé".format(pnj))
    await webhook.send(content,
                       username="{}{}".format(line[CHAR_NAME], f" ({line[PNJ_GROUP]})" if line[PNJ_GROUP] else ""),
                       avatar_url=line[IMAGE_URL])
    await message.delete()