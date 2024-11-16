import os
from loguru import logger
from arclet.alconna import (
    Args,
    Alconna,
    AllParam,
    MultiVar,
    CommandMeta,
)

from .const import ServerNameFull


TSUGU_COMPACT = os.environ.get("TSUGU_COMPACT", "true") == "true"

if not TSUGU_COMPACT:
    logger.warning("TSUGU_COMPACT is off")


alc_help = Alconna(
    ["help"],
    Args["cmd;?", str],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="",
    ),
)


alc_event_stage = Alconna(
    ["查试炼", "查stage", "查舞台", "查festival", "查5v5"],
    Args["eventId;?", [int]]["meta;?", ["-m"]],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="查询活动的试炼信息",
        example="""查试炼 157 -m :返回157号活动的试炼信息，包含歌曲meta
查试炼 -m :返回当前活动的试炼信息，包含歌曲meta
查试炼 :返回当前活动的试炼信息""",
    ),
)


alc_gacha_simulate = Alconna(
    ["抽卡模拟", "卡池模拟"],
    Args["times", int, 10]["gacha_id;?", int],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="就像真的抽卡一样",
        example="抽卡模拟 300 922 :模拟抽卡300次，卡池为922号卡池",
    ),
)

alc_get_card_illustration = Alconna(
    ["查卡面", "查插画"],
    Args["cardId?", int],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="根据卡面ID查询卡面插画",
        example="查卡面 1399 :返回1399号卡牌的插画",
    ),
)

alc_cutoff_list_of_recent_event = Alconna(
    ["lsycx", "历史预测线"],
    Args["tier", int]["eventId;?", int][
        "serverName;?",
        ServerNameFull,
    ],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="查询指定档位的预测线与最近的4期活动类型相同的活动的档线数据",
        example="lsycx 1000\nlsycx 1000 177 jp",
    ),
)

alc_search_gacha = Alconna(
    ["查卡池"],
    Args["gachaId", int],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="根据卡池ID查询卡池信息",
        example="查卡池 947 :返回947号卡池的信息",
    ),
)

alc_search_character = Alconna(
    ["查角色"],
    Args["word", AllParam],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="根据角色名、乐队、昵称等查询角色信息",
        example="查角色 10 :返回10号角色的信息\n查角色 吉他 :返回所有角色模糊搜索标签中包含吉他的角色列表",
    ),
)

alc_search_event = Alconna(
    ["查活动"],
    Args["word", AllParam],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="根据活动名、乐队、活动ID等查询活动信息",
        example="查活动 绿 tsugu :返回所有属性加成为pure，且活动加成角色中包括羽泽鸫的活动列表\n查活动 177 :返回177号活动的信息",
    ),
)

alc_search_card = Alconna(
    ["查卡"],
    Args["word", AllParam],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="根据卡面ID、角色名、乐队、昵称等查询卡面信息",
        example="查卡 1399 :返回1399号卡牌的信息\n查卡 红 ars 5x :返回角色 ars 的 5x 卡片的信息",
    ),
)

alc_search_player = Alconna(
    ["查玩家", "查询玩家"],
    Args["playerId", int][
        "serverName;?",
        ServerNameFull,
    ],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="根据玩家ID、服务器查询玩家信息",
        example="""查玩家 1003282233 : 查询默认服务器中玩家ID为1003282233的玩家信息
查玩家 40474621 jp : 查询日服玩家ID为40474621的玩家信息
""",
    ),
)

alc_song_random = Alconna(
    ["随机曲"],
    Args["word;?", AllParam],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="根据关键词或曲目ID随机曲目信息",
        example="""随机曲 lv27 :在所有包含27等级难度的曲中, 随机返回其中一个
随机曲 ag :返回随机的 Afterglow 曲目""",
    ),
)

alc_search_song = Alconna(
    ["查曲"],
    Args["word", AllParam],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="根据关键词或曲目ID查询曲目信息",
        example="""查曲 1 :返回1号曲的信息
查曲 ag lv27 :返回所有难度为27的ag曲列表""",
    ),
)

alc_song_chart = Alconna(
    ["查谱面", "查铺面"],
    Args["songId", int][
        "difficultyText",
        ("easy", "ez", "normal", "nm", "hard", "hd", "expert", "ex", "special", "sp"),
        "ex",
    ],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="根据曲目ID与难度查询铺面信息",
        example="查谱面 1 :返回1号曲的ex难度谱面\n查谱面 128 special :返回128号曲的special难度谱面",
    ),
)

alc_song_meta = Alconna(
    ["查询分数表", "查分数表", "查询分数榜", "查分数榜"],
    Args["serverName;?", ServerNameFull],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="",
        example="查询分数表 cn :返回国服的歌曲分数表",
    ),
)

alc_cutoff_all = Alconna(
    ["ycxall", "ycx all"],
    Args["eventId;?", int]["serverName;?", ServerNameFull],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="输出全部档位的预测线",
        example="""ycxall 177 :返回177号活动的全部档位预测线
ycxall 177 jp :返回日服177号活动的全部档位预测线""",
    ),
)

alc_cutoff_detail = Alconna(
    ["ycx", "预测线"],
    Args["tier", int]["eventId;?", int]["serverName;?", ServerNameFull],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="指定档位的预测线",
        example="""ycx 1000
ycx 1000 177 jp""",
    ),
)

alc_bind_player = Alconna(
    ["绑定玩家"],
    Args["playerId", int]["serverName;?", ServerNameFull],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="绑定游戏账号",
        example="""绑定玩家 114514 : 绑定默认服务器中玩家ID为114514的玩家
绑定玩家 1919810 jp : 绑定日服玩家ID为1919810的玩家
绑定玩家 0 : 刷新你的验证码""",
    ),
)


alc_change_displayed_server_list = Alconna(
    ["设置默认服务器", "默认服务器"],
    Args["serverList", MultiVar(ServerNameFull)],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="设定信息显示中的默认服务器排序",
        example="""设置默认服务器 cn jp : 将国服设置为第一服务器，日服设置为第二服务器""",
    ),
)

alc_change_main_server = Alconna(
    ["主服务器", "设置主服务器"],
    Args["serverName", ServerNameFull],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="将指定的服务器设置为你的主服务器",
        example="""主服务器 cn : 将国服设置为主服务器""",
    ),
)

alc_toggle_share_room_number_off = Alconna(
    ["关闭车牌转发", "关闭个人车牌转发"],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="",
    ),
)

alc_toggle_share_room_number_on = Alconna(
    ["开启车牌转发", "开启个人车牌转发"],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="",
    ),
)

alc_player_status = Alconna(
    ["玩家状态"],
    Args["accountIndex;?", int]["serverName;?", ServerNameFull],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="查询自己的玩家状态",
        example="""
玩家状态 :返回指定默认账号的玩家状态
玩家状态 2 :返回账号2的玩家状态
主账号 2 :设置账号2为默认查询账号
绑定玩家 / 解除绑定 :管理存储的账号
""",
    ),
)

alc_set_main_account = Alconna(
    ["主账号"],
    Args["accountIndex;?", int],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="设定默认玩家状态、车牌展示中的主账号使用第几个账号",
        example="""主账号 : 返回所有账号列表
主账号 2 : 将第二个账号设置为主账号""",
    ),
)

alc_unbind_player = Alconna(
    ["解除绑定"],
    Args["index;?", int],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="解除绑定游戏账号",
        example="解除绑定 1 : 解绑第一个记录",
    ),
)

alc_query_room_number = Alconna(
    ["ycm", "车来", "有车吗"],
    Args["_;?", AllParam],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="获取车站信息",
    ),
)

alc_26 = Alconna(
    ["上传车牌"],
    Args["roomNumber", str],
    meta=CommandMeta(
        description="自动检测车牌并上传",
    ),
)
