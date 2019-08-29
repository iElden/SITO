import discord

ARCHIVE_CHAN_NAME = "archives"

async def archive(message, channel):
    """
    Args:
        message (discord.Message):
        channel (discord.TextChannel):
    Returns:

    """

    category = channel.category # type: discord.CategoryChannel
    channels = [i for i in category.channels if i.name == "archives"]
    if not channels:
        await channel.send(f"Impossible de localiser le channel \"{ARCHIVE_CHAN_NAME}\" dans la catégorie \"{category.name}\"")
        return

    ar = channels[0]  # type: discord.TextChannel

    await channel.send("ENREGISTREMENT DES DONNEES")
    await message.delete()

    await ar.send(f"**==== #{channel.name} ====**\n\n{channel.topic if channel.topic else ''}")
    async for msg in channel.history(limit=None, before=message.created_at, oldest_first=True):
        em = discord.Embed(description=msg.content, timestamp=msg.created_at, colour=msg.author.colour)
        em.set_author(name=msg.author.display_name, icon_url=msg.author.avatar_url)
        em.set_footer(text=channel.name)
        await ar.send(embed=em)
    await channel.send("Terminé (par sécurité, la supression du canal n'est pas activé, elle le sera quand tout sera au point)")
    # await channel.delete()
