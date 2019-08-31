import random
import discord
import re
from typing import List, Tuple, Dict
from exc import InvalidArgs, NotFound
from gdoc_manager import PJ

def parse_expr(expr : str, *, pj : PJ):
    goal = 0 # type: int
    stats_recap = []  # type: List[Tuple[str, int]]
    bonus_recap = 0

    expr.replace(' ', '').lower()
    ex_list = re.split(r"([\+-])", expr)
    if ex_list[0] == '':
        del ex_list[0]
    else:
        ex_list.insert(0, '+')
    ex_list = [(ex_list[i * 2] + ex_list[i * 2 + 1]) for i in range(len(ex_list)//2)]
    for ex in ex_list:
        b = re.findall(r"^([\+-])?(\d+)$", ex)
        s = re.findall(r"^([\+-])?(\S+)$", ex)
        if b:
            b = b[0]
            v = int(b[0] + b[1])
            goal += v
            bonus_recap += v
        elif s:
            s = s[0]
            stats = pj.get_stats_by_name(s[1])
            if len(stats) == 0:
                raise InvalidArgs(f"Aucune stats du nom de \"{s[1]}\" a été trouvé dans la fiche.")
            if len(stats) > 1:
                raise InvalidArgs(f"La stat \"{s[1]}\" n'est pas assez spécifique, {'/'.join([i.name for i in stats])} ont été matchés.")
            stats_recap.append((stats[0].name, stats[0].total_value))
            if s[0] == '-':
                goal -= stats[0].total_value
            else:
                goal += stats[0].total_value
        else:
            raise InvalidArgs(f"L'expression \"{ex}\" ne correspond pas à une formule connu")
    return goal, stats_recap, bonus_recap



async def cmd_test(message, member, args, *, database):
    """
    Args:
        message (discord.Message):
        member (discord.User):
        args (List[str]):
    """
    pj = database.get_pj(member)
    if not pj:
        raise NotFound("Impossible de récupérer le PJ pour obtenir les stats.")
    expr = ''.join(args)
    goal, stats, bonus = parse_expr(expr, pj=pj)
    dice = random.randint(1, 100)
    em = discord.Embed(title="Test de compétence", color=member.color)
    recap = ""
    if stats:
        recap += "\n".join([f"{pj.name} a **{stat[1]}** en {stat[0]}" for stat in stats])
    if bonus:
        recap += f"\navec un {'malus' if bonus < 0 else 'bonus'} total de {abs(bonus)}"
    recap += f"\n\nIl faudra moins de **{goal}** pour réussir le test"
    em.add_field(name="Récap", value=recap)

    if dice <= goal:
        result = "+ Réussite Critique" if dice * 10 <= goal else "+ Réussite"
    else:
        result = "- Échec Critique" if dice == 100 or dice >= 100 - ((100 - goal)// 10) else "- Échec"
    em.add_field(name="Résultat", value=f"{member.mention} a lancé 1d100 et a obtenu :\n\n**{dice}**\n\n```diff\n{result}```")
    await message.channel.send(embed=em)
