import re

mention_regex = re.compile(r"(?<=^<@)\d+(?=>$)")

def get_member(guild, name):
    member = guild.get_member_named(name)
    if member:
        return member
    match = re.search(mention_regex, name)
    if match:
        return guild.get_member(int(match[0]))
    if name.isdigit():
        return guild.get_member(int(name))
    return None