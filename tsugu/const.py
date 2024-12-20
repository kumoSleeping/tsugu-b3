from typing import Literal, TypeAlias

ServerNameFull: TypeAlias = Literal[
    "jp", "en", "tw", "cn", "kr", "日服", "国际服", "台服", "国服", "韩服"
]
INDEX_TO_SERVER = {0: "jp", 1: "en", 2: "tw", 3: "cn", 4: "kr"}
SERVER_TO_INDEX = {
    "jp": 0,
    "en": 1,
    "tw": 2,
    "cn": 3,
    "kr": 4,
    "日服": 0,
    "国际服": 1,
    "台服": 2,
    "国服": 3,
    "韩服": 4,
}
DIFFICULTY_TEXT_TO_ID = {
    "easy": 0,
    "ez": 0,
    "normal": 1,
    "nm": 1,
    "hard": 2,
    "hd": 2,
    "expert": 3,
    "ex": 3,
    "special": 4,
    "sp": 4,
}

CAR_CONFIG = {
    "car": [
        "q1",
        "q2",
        "q3",
        "q4",
        "Q1",
        "Q2",
        "Q3",
        "Q4",
        "缺1",
        "缺2",
        "缺3",
        "缺4",
        "差1",
        "差2",
        "差3",
        "差4",
        "3火",
        "三火",
        "3把",
        "三把",
        "打满",
        "清火",
        "奇迹",
        "中途",
        "大e",
        "大分e",
        "exi",
        "大分跳",
        "大跳",
        "大a",
        "大s",
        "大分a",
        "大分s",
        "长途",
        "生日车",
        "军训",
        "禁fc",
    ],
    "fake": [
        "11451",
        "1919",
        "810",
        "雀魂",
        "麻将",
        "打牌",
        "maj",
        "麻",
        "[",
        "]",
        "断幺",
        "qq.com",
        "腾讯会议",
        "master",
    ],
}
