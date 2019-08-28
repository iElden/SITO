from enum import IntEnum

class Stats(IntEnum):
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
    PNJ_GROUP = 18

ALL_STATS = [Stats.FORCE, Stats.RESIS, Stats.TIR, Stats.AGILITE, Stats.MAGIE, Stats.CHARISME, Stats.INTEL]



WEBHOOK_NAME = "SitoPnjManager"