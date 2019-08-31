import gspread
import discord
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Tuple, Union
from exc import NotFound, InvalidSheet, ALEDException
from DynamicEmbed import DynamicEmbed
from utils import get_member
import re

MAIN_GDOC_KEY = "1rqKgJRIqoOSa0LoWyp5Dh9PZZnUIYWqKAGB3XvOp5fk"

def verify_gs_token(function):
    def wrapper(*args, **kwargs):
        print("verifing token ...")
        DataBase.gc.login()
        function(*args, **kwargs)
    return wrapper

class DataBase:
    creds = ServiceAccountCredentials.from_json_keyfile_name("private/google", ["https://spreadsheets.google.com/feeds"])
    gc = gspread.authorize(creds)

    def __init__(self, guild=None):
        self.wb = self.gc.open_by_key(MAIN_GDOC_KEY)
        self.pj_sh = self.wb.get_worksheet(0)
        self.pnj_sh = self.wb.get_worksheet(1)
        self.pj_ll = None   # type: List[List[str]]
        self.pnj_ll = None  # type: List[List[str]]
        self.refresh()
        self.guild = guild
    def get_all_pj_info(self) -> [list]:
        return self.pj_ll
    def get_all_pnj_info(self) -> [list]:
        return self.pnj_ll

    def get_pj(self, name):
        """
        Args:
            name (Union[str, discord.Member]): can be a str or a discord.Member
        Returns:
            Optional[PJ]: a PJ object
        """
        if isinstance(name, str):
            member = get_member(self.guild, name)
            if member:
                return self.get_pj_by_member(member)
            return self.get_pj_by_name(name)

        elif isinstance(name, discord.Member) or isinstance(name, discord.User):
            return self.get_pj_by_member(name)
        else:
            raise ALEDException("Database.get_pj argument must be a str or a discord member object !")

    def get_pj_by_name(self, name : str):
        for line in self.pj_ll:
            if line[1].lower() == name.lower():
                return PJ(line, guild=self.guild)
        return None

    def get_pj_by_member(self, member : discord.User):
        for line in self.pj_ll:
            if line[0] == str(member.id):
                return PJ(line, guild=self.guild)
        return None

    def refresh(self):
        self.pj_ll = self.pj_sh.get_all_values()
        self.pnj_ll = self.pnj_sh.get_all_values()

class Skill:
    def __init__(self, name, base, exp, total):
        """
        Args:
            base (str): base xp for this skill
            exp (str): xp given by player in this skill
            total (str): total xp
        """
        if not base.isnumeric():
            raise InvalidSheet(f"L'xp de base pour les compétence doit être un nombre, et non pas \"{base}\"")
        if not exp:
            exp = 0
        elif not exp.isnumeric():
            raise InvalidSheet(f"L'xp investi pour les compétence doit être un nombre ou vide, et non pas \"{exp}\"")
        if not total.isnumeric():
            raise InvalidSheet(f"L'xp total pour les compétence doit être un nombre, et non pas \"{total}\"")
        self.name = name                # type: str
        self.base_value = int(base)     # type: int
        self.exp_value = int(exp)       # type: int
        self.total_value = int(total)   # type: int
    def __repr__(self):
        return f"Skill({self.name, self.base_value, self.exp_value, self.total_value})"

class Atribute:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class PJ:

    def __init__(self, gdoc_line : List[str], *, guild : discord.Guild):
        self.advenced_info_fetched = False
        try:
            self.discord_id = int(gdoc_line[0])
        except:
            raise InvalidSheet(f"discord_id must be a int but it was \"{gdoc_line[0]}\"")
        self.name = gdoc_line[1]
        self.image_url = gdoc_line[2]
        self.age = gdoc_line[3]
        try:
            self.level= int(gdoc_line[4])
        except:
            raise InvalidSheet(f"level must be a int but it was \"{gdoc_line[4]}\"")
        try:
            self.xp = int(gdoc_line[5])
        except:
            raise InvalidSheet(f"xp must be a int but it was \"{gdoc_line[5]}\"")
        try:
            self.gold = int(gdoc_line[6])
        except:
            raise InvalidSheet(f"credits must be a int but it was \"{gdoc_line[6]}\"")
        self.origin = gdoc_line[7]
        self.job = gdoc_line[8]
        try:
            self.force = int(gdoc_line[9])
            self.resis = int(gdoc_line[10])
            self.dexteriry = int(gdoc_line[11])
            self.agility = int(gdoc_line[12])
            self.social = int(gdoc_line[13])
            self.knowledge = int(gdoc_line[14])
            self.magic = int(gdoc_line[15])
        except:
            raise InvalidSheet(f"Stats must be a int")
        self.desc = gdoc_line[16]
        self.note = gdoc_line[17]
        self.gdoc_url = gdoc_line[18]

        self.member = guild.get_member(self.discord_id) # type: discord.Member
        if not self.member:
            raise NotFound(f"member with id {self.discord_id} was not found in the server")

    @verify_gs_token
    def get_full_char_sheet_info(self):
        try:
            shs = DataBase.gc.open_by_url(self.gdoc_url)
            sh = shs.sheet1
            if not sh: raise NotFound
        except:
            raise NotFound(f"Impossible d'ouvrir le gdoc correspondant à l'URL {self.gdoc_url}")

        try:
            self.discord_id = int(sh.acell('C2').value)
        except:
            raise InvalidSheet(f"discord_id must be a int but it was \"{sh.acell('C2').value}\"")
        self.image_url = sh.acell('C3').value
        self.name = sh.acell('C4').value
        self.title = sh.acell('C5').value
        self.age = sh.acell('C6').value
        self.origin = sh.acell('C7').value
        self.job = sh.acell('C8').value
        try:
            self.level = int(sh.acell('C10').value)
        except:
            raise InvalidSheet(f"level must be a int but it was \"{sh.acell('C10').value}\"")
        try:
            self.xp = int(sh.acell('C11').value)
        except:
            raise InvalidSheet(f"xp must be a int but it was \"{sh.acell('C11').value}\"")
        try:
            self.gold = int(sh.acell('C12').value)
        except:
            raise InvalidSheet(f"credits must be a int but it was \"{sh.acell('C12').value}\"")
        self.desc = sh.acell('E3').value
        try:
            self.force = int(sh.acell('M4').value)
            self.resis = int(sh.acell('M5').value)
            self.dexteriry = int(sh.acell('M6').value)
            self.agility = int(sh.acell('M7').value)
            self.social = int(sh.acell('M8').value)
            self.knowledge = int(sh.acell('M9').value)
            self.magic = int(sh.acell('M10').value)
        except:
            raise InvalidSheet(f"Stats must be a int")
        self.main_skill = {'Force': self.force, 'Corpulence': self.resis, 'Dextérité': self.dexteriry,
                           'Agilité': self.agility, 'Social': self.social, 'Savoir': self.knowledge, 'Magie': self.magic}
        self.main_skill = [Skill(k, '0', '0', str(v)) for k, v in self.main_skill.items()]

        self.inventory = [i.value for i in sh.range("B15:B100") if i.value]
        atributes = [i.value for i in sh.range("E15:F100")]
        self.attributes = [Atribute(atributes[i*2], atributes[i*2 + 1]) for i in range(len(atributes) // 2) if atributes[i * 2]]
        states = [i.value for i in sh.range("O15:P100")]
        self.states = [Atribute(states[i * 2], states[i * 2 + 1]) for i in range(len(states) // 2) if states[i * 2]]
        skills =  [i.value for i in sh.range("J15:M100")]
        self.skills = [Skill(*skills[i*4:i*4+4]) for i in range(len(skills) // 4) if skills[i * 4]]

        self.advenced_info_fetched = True

    def __repr__(self):
        return f"<PJ: {self.name} ({self.discord_id})>"

    def get_full_name(self):
        if not self.advenced_info_fetched:
            self.get_full_char_sheet_info()
        if self.title:
            return f"{self.name}, {self.title}"
        return self.name

    def __str__(self):
        return self.name

    def get_stats_by_name(self, name):
        if not self.advenced_info_fetched:
            self.get_full_char_sheet_info()
        result = self.main_skill + self.skills  # type: List[Skill]
        print(result)
        return [i for i in result if i.name.lower().startswith(name.lower())]

    def main_sheet(self):
        """
        Returns:
            List[Tuple[str, str]]: embed that represent the first page of character sheet
        """
        fields = []
        fields.append((
            "Personnage",
            f"originaire de **{self.origin}**\n"
            f"{self.job} de {self.age} ans\n"
            f"Niveau **{self.level}** ({self.xp} XP)\n"
            f"{self.gold} crédit(s)"))
        fields.append((
            "Description / Histoire",
            self.desc[:1024]
        ))
        fields.append((
            "Statistiques",
            """```diff\n{}```""".format(
                "\n".join([
                    ("+" if stat_value >= 60 else ("-" if stat_value < 25 else ">")) +
                    f"{stat_name} : {stat_value}" +
                    " " * (3 - len(str(stat_value))) +
                    "▬" * (stat_value // 5)
                    for stat_name, stat_value in [("Force     ", self.force), ("Corpulence", self.resis), ("Dextérité ", self.dexteriry), ("Agilité   ", self.agility),
                          ("Social    ", self.social), ("Savoir    ", self.knowledge), ("Magie     ", self.magic)]
                ])
            )
        ))
        return fields

    def comp_sheet(self):
        pages = [] # type: List[List[Tuple[str, str]]]

        txt = "```diff\n"
        for skill in self.skills:
            v = skill.total_value
            new_txt = (("+" if v >= 60 else ("-" if v < 25 else ">")) +
            f"{skill.name} : {v}" +
            " " * (3 - len(str(v))) +
            "▬" * (v // 5) +
            '\n')
            if len(txt) + len(new_txt) >= (1024 - 8):
                pages.append([('Compétences', txt + "```")])
                txt = "```diff\n" + new_txt
            else:
                txt += new_txt
        pages.append([("Compétences", txt + "```")])
        return pages

    def attribute_sheets(self):
        pages = []  # type: List[List[Tuple[str, str]]]

        txt = ""
        for attribute in self.attributes:
            new_txt = f"**__{attribute.name}__**:\n{attribute.value}\n\n"
            if len(txt) + len(new_txt) >= 1024:
                pages.append([('Attributs', txt)])
                txt = ""
            else:
                txt += new_txt
        pages.append([('Attributs', txt)])
        return pages

    def state_sheets(self):
        pages = []  # type: List[List[Tuple[str, str]]]

        txt = ""
        for state in self.states:
            new_txt = f"**__{state.name}__**:\n{state.value}\n\n"
            if len(txt) + len(new_txt) >= 1024:
                pages.append([('Etat / Blessure / Sequelle', txt)])
                txt = ""
            else:
                txt += new_txt
        pages.append([('Etat / Blessure / Sequelle', txt)])
        return pages

    def inventory_sheet(self):
        pages = []  # type: List[List[Tuple[str, str]]]

        txt = ""
        for state in self.inventory:
            new_txt = f"- {state}\n"
            if len(txt) + len(new_txt) >= 1024:
                pages.append([('Inventaire', txt)])
                txt = ""
            else:
                txt += new_txt
        pages.append([('Inventaire', txt)])
        return pages


    async def create_interactive_sheet(self, channel):
        em = discord.Embed(title="Fiche de personnage", url=self.gdoc_url, colour=self.member.colour)
        em.set_author(name=self.get_full_name(), icon_url=self.member.avatar_url)
        em.set_image(url=self.image_url)
        de = DynamicEmbed([self.main_sheet()] + self.comp_sheet() + self.attribute_sheets() + self.state_sheets() + self.inventory_sheet(),
                          base_embed=em)
        return await de.send_embed(channel)