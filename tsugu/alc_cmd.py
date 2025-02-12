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


TSUGU_COMPACT: bool = os.environ.get("TSUGU_COMPACT", "true") == "true"

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
    ["查试炼"],
    Args["eventId;?", [int]]["meta;?", ["-m"]],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="查询5v5信息",
        example='''
可选参数:
  "-m" : 用于指定包含歌曲meta
  活动ID(数字) : 用于指定活动ID, 否则为当前活动
使用例:
  查试炼
  查试炼 -m
  查试炼 157 -m
''',
    ),
)


alc_gacha_simulate = Alconna(
    ["抽卡模拟", "卡池模拟"],
    Args["times", int, 10]["gacha_id;?", int],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="像真的抽卡一样",
        example='''
可选参数:
    "1~10000"(有限数字) : 用于指定抽卡的次数, 默认为10
    卡池ID(数字) : 用于指定卡池ID, 默认为当前卡池
使用例:
    抽卡模拟
    抽卡模拟 10
    抽卡模拟 10 947 : 10是次数, 947是卡池ID
特别提醒:
    注意顺序, 如果你想指定卡池ID, 请先输入次数, 再输入卡池ID
    本功能仅供娱乐, 请适当使用
''',
    ),
)

alc_get_card_illustration = Alconna(
    ["查卡面", "查插画"],
    Args["cardId?", int],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="查询卡面插画",
        example='''
必选参数:
    卡面ID(数字) : 用于指定卡面ID
使用例:
    查卡面 1399
关联指令:
    查卡 : 使用"查卡"命令获取卡面ID
'''
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
        description="历史同类活动档线数据",
        # example="lsycx 1000\nlsycx 1000 177 jp",
        example='''
功能介绍:
    查询 指定档位的预测线 与 [(最近的4期)(活动类型相同的)活动的]档线数据
必选参数:
    "20“ / "30" / "50" ...(档位数字) : 用于指定档位
可选参数:
    活动ID(数字) : 用于指定活动ID, 默认为当前活动
    "cn" / "jp" / "en" / "tw" : 用于指定服务器, 默认为你的默认服务器
使用例:
    lsycx 1000
    lsycx 1000 177 : 1000是档位, 177是活动ID
    lsycx 1000 jp
    lsycx 1000 177 jp
特别提醒:
    由于 bestdori 限制, 本功能暂不支持 10 档位的历史数据
'''
    ),
)

alc_search_gacha = Alconna(
    ["查卡池"],
    Args["gachaId", int],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="查询卡池信息",
        example='''
必选参数:
    "1~∞"(数字) : 用于指定卡池ID
使用例:
    查卡池 947
关联指令:
    查卡 : 使用"查卡"命令获取卡池ID
    查活动 : 使用"查活动"命令获取卡池ID
'''
    ),
)

alc_search_character = Alconna(
    ["查角色"],
    Args["word", AllParam],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="根据角色名、乐队、昵称等查询角色信息",
        # example="查角色 10 :返回10号角色的信息\n查角色 吉他 :返回所有角色模糊搜索标签中包含吉他的角色列表",
        example='''
使用ID查询时:
    必选参数:
        角色ID(数字) : 用于指定角色ID
使用模糊搜索时:
    可多选参数:
        角色姓/名/昵称 : 用于模糊搜索角色, 例如"香澄", "tmr", "土笔", "巧克力螺", "宇田川"
        乐队 : 用于模糊搜索乐队, 例如"popipa", "ras", "其他"
        职位 : 用于模糊搜索职位, 例如"gt", "vo", "吉他"
使用例:
    查角色 10
    查角色 popipa gt
    查角色 冰川
    查角色 鼓手
'''
    ),
)

alc_search_event = Alconna(
    ["查活动"],
    Args["word", AllParam],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="根据活动名、乐队、活动ID等查询活动信息",
        example='''
使用ID查询时:
    必选参数:
        活动ID(数字) : 用于指定活动ID
使用模糊搜索时:
    可多选参数:
        活动名 : 用于模糊搜索活动, 例如"绿", "tsugu"
        乐队 : 用于模糊搜索乐队, 例如"popipa", "ras", "其他"
        角色 : 用于指定活动加成角色, 例如"羽泽鸫", "ksm"
        属性 : 用于指定属性, 例如"pure", "蓝"
使用例:
    查活动 177
    查活动 绿 tsugu
    查活动 绿
'''
    ),
)

alc_search_card = Alconna(
    ["查卡"],
    Args["word", AllParam],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="根据卡面ID、角色名、乐队、昵称等查询卡面信息",
        # example="查卡 1399 :返回1399号卡牌的信息\n查卡 红 ars 5x :返回角色 ars 的 5x 卡片的信息",
        example='''
使用ID查询时:
    必选参数:
        卡面ID(数字) : 用于指定卡面ID
使用模糊搜索时:
    可多选参数:
        特殊类型:
            "dfes" | "kfes" | "fes"
            "活动" | "联动" | "生日"
            "常驻" | "限定" | "初始"
        技能类型:
            "分" / "大分"
            "判" / "判定"
            "奶" / "奶卡"
            "盾" / "无敌"
        卡名 : 用于模糊搜索卡面, 例如"爱之花飞舞的瞬间"
        角色姓/名/昵称 : 用于模糊搜索角色, 例如"香澄", "tmr", "土笔"
        乐队 : 用于模糊搜索乐队, 例如"popipa", "ras", "其他"
        星级 : 用于指定卡牌编号, 例如"5x", "四星", "3*"
使用例:
    查卡 1399
    查卡 生日 ars
    查卡 dfes ksm 分 5x
    查卡 mygo 大分
'''
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
        example="""
必选参数:
    玩家ID(数字) : 用于指定玩家ID
可选参数:
    "cn" / "jp" / "en" / "tw" : 用于指定服务器, 不指定时为你的默认服务器
使用例:
    查玩家 1003282233 : 从你的默认服务器查玩家 1003282233
    查玩家 40474621 jp 
""",
    ),
)

alc_song_random = Alconna(
    ["随机曲"],
    Args["word;?", AllParam],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="根据关键词或曲目ID随机曲目信息",
        example="""
可多选参数:
    乐队: 例如"popipa", "ras", "其他"
    难度等级: 例如"27", "28"
    类型:
        "翻唱" / "cover"
        "原创"
        "动画"
使用例:
    随机曲
    随机曲 mygo 26
吐槽:
    虽然是随机曲, 但是可以有 "随机曲 lzn" 是什么鬼啊()
""",

    ),
)

alc_search_song = Alconna(
    ["查曲"],
    Args["word", AllParam],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="根据关键词或曲目ID查询曲目信息",
#         example="""查曲 1 :返回1号曲的信息
# 查曲 ag lv27 :返回所有难度为27的ag曲列表""",
        example='''
使用ID查询时:
    必选参数:
        曲目ID(数字) : 用于指定曲目ID
使用模糊搜索时:
    可多选参数:
        乐队: 例如"popipa", "ras", "其他"
        难度等级: 例如"lv27", "lv28" *一定要加"lv"
        类型:
            "翻唱" / "cover"
            "原创"
            "动画"
        曲名: 使用完整或一部分曲名进行搜索
        歌曲别称: 歌曲的一些民间称呼, 例如"修车", "lzn", "ssfkk
使用例:
    查曲 1
    查曲 ag lv27
    查曲 lzn
    查曲 超高难易度
'''
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
        example="""
必选参数:
    曲目ID(数字) : 用于指定曲目ID
可选参数:
    "ez" / "easy" / "nm" ... : 用于指定难度, 默认为ex
使用例:
    查谱面 1 
    查谱面 128 special 
关联指令:
    查曲 : 使用"查曲"命令获取曲目ID
""",
    ),
)

alc_song_meta = Alconna(
    ["查询分数表", "查分数表", "查询分数榜", "查分数榜"],
    Args["serverName;?", ServerNameFull],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="",
        # example="查询分数表 cn :返回国服的歌曲分数表",
        example="""
可选参数:
    "cn" / "jp" / "en" / "tw" : 用于指定服务器, 默认为你的默认服务器
使用例:
    查询分数表 
    查询分数表 jp
""",
    ),
)

alc_cutoff_all = Alconna(
    ["ycxall", "ycx all"],
    Args["eventId;?", int]["serverName;?", ServerNameFull],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="输出全部档位的预测线",
        example='''
必选参数:
    活动ID(数字) : 用于指定活动ID, 默认为当前活动
可选参数:
    "cn" / "jp" / "en" / "tw" : 用于指定服务器, 默认为你的默认服务器
使用例:
    ycxall 
    ycxall 177 
    ycxall 177 jp 
'''
    ),
)

alc_cutoff_detail = Alconna(
    ["ycx", "预测线"],
    Args["tier", int]["eventId;?", int]["serverName;?", ServerNameFull],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="指定档位的预测线",
#         example="""ycx 1000
# ycx 1000 177 jp""",
        example='''
必选参数:
    "20“ / "30" / "50" ...(档位数字) : 用于指定档位
可选参数:
    活动ID(数字) : 用于指定活动ID, 默认为当前活动
    "cn" / "jp" / "en" / "tw" : 用于指定服务器, 默认为你的默认服务器
使用例:
    ycx 1000
    ycx 1000 177 : 1000是档位, 177是活动ID
    ycx 1000 jp 
    ycx 1000 177 jp
特别提醒:
    由于 bestdori 限制, 本功能暂不支持 10 档位的数据
'''
    ),
)

alc_bind_player = Alconna(
    ["绑定玩家"],
    Args["playerId", int]["serverName;?", ServerNameFull],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="绑定游戏账号",
        example="""
必选参数:
    玩家ID(数字) : 用于指定玩家ID
可选参数:
    "cn" / "jp" / "en" / "tw" : 用于指定服务器, 默认为你的默认服务器
使用例:
    绑定玩家 114514 
    绑定玩家 1919810 jp 
关联指令:
    玩家状态 : 查询绑定的游戏账号信息
    解除绑定 : 解绑游戏账号
    主账号 : 设定默认账号
特别提醒:
    请发送指令后按照提示登录游戏并验证, 完成绑定
""",
    ),
)


alc_change_displayed_server_list = Alconna(
    ["设置默认服务器", "默认服务器"],
    Args["serverList", MultiVar(ServerNameFull)],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="设定信息显示中的默认服务器排序",
        # example="""设置默认服务器 cn jp : 将国服设置为第一服务器，日服设置为第二服务器""",
        example="""
可多选参数:
    "cn" / "jp" / "en" / "tw" : 用于指定服务器
使用例:
    设置默认服务器 cn jp : 将国服设置为第一服务器，日服设置为第二服务器
特别提醒:
    本指令与 "主服务器" 指令完全不同, 本指令主要涉及改变顺序后的部分指令的优先查询匹配与显示效果
""",
    ),
)

alc_change_main_server = Alconna(
    ["主服务器", "设置主服务器"],
    Args["serverName", ServerNameFull],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="将指定的服务器设置为你的主服务器",
        # example="""主服务器 cn : 将国服设置为主服务器""",
        example="""
必选参数:
    "cn" / "jp" / "en" / "tw" : 用于指定服务器
使用例:
    主服务器 cn
特别提示:
    本指令用于绝大部分指令的默认查询服务器
    "玩家状态" 指令不受 "主服务器" 影响, 由 "主账号" 决定
""",
    ),
)

alc_toggle_share_room_number_off = Alconna(
    ["关闭车牌转发", "关闭个人车牌转发"],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="",
        example="""
特别提醒:
    车牌转发默认开启
"""
    ),
)

alc_toggle_share_room_number_on = Alconna(
    ["开启车牌转发", "开启个人车牌转发"],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="",
        example="""
特别提醒:
    车牌转发默认开启
"""
    ),
)

alc_player_status = Alconna(
    ["玩家状态"],
    Args["accountIndex;?", int]["serverName;?", ServerNameFull],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="查询自己的玩家状态",
        example="""
可选参数:
    主账号顺序(数字) : 用于指定账号
使用例:
    玩家状态 : 返回默认账号的玩家状态(默认账号由 "主账号" 指令设定)
    玩家状态 2 : 返回账号2的玩家状态
关联指令:
    主账号 : 设定默认账号
    绑定玩家 : 绑定游戏账号
    解除绑定 : 解绑游戏账号
特别提醒:
    本指令默认返回 "主账号" 设定的账号的玩家状态, 与 "主服务器" 无关
    本指令至少需要绑定一个账号才能使用, 请先使用 "绑定玩家" 指令
""",
    ),
)

alc_set_main_account = Alconna(
    ["主账号", "主账户"],
    Args["accountIndex;?", int],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="设定默认玩家状态、车牌展示中的主账号使用第几个账号",
#         example="""主账号 : 返回所有账号列表
# 主账号 2 : 将第二个账号设置为主账号""",
        example="""
可选参数:
    主账号顺序(数字) : 用于指定账号
使用例:
    主账号 : 返回所有账号列表
    主账号 2 : 将第二个账号设置为主账号
关联指令:
    玩家状态 : 查询绑定的游戏账号信息
特别提醒:
    本指令用于设定默认账号, 用于 "玩家状态" 指令的默认查询
    本指令至少需要绑定一个账号才能使用, 请先使用 "绑定玩家" 指令
    本指令还会影响 "车牌转发" 时您默认携带车队号的账号信息
""",
    ),
)

alc_unbind_player = Alconna(
    ["解除绑定"],
    Args["index;?", int],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="解除绑定游戏账号",
        example="""
可选参数:
    绑定记录序号(数字) : 用于指定解绑的记录
使用例:
    解除绑定 : 解绑默认账号
关联指令:
    绑定玩家 : 绑定游戏账号
""",
    ),
)

alc_query_room_number = Alconna(
    ["ycm", "车来", "有车吗"],
    Args["_;?", AllParam],
    meta=CommandMeta(
        compact=TSUGU_COMPACT,
        description="获取车站信息",
        example="""
车牌来源:
    bandoristation
"""
    ),
)

alc_26 = Alconna(
    ["上传车牌"],
    Args["roomNumber", str],
    meta=CommandMeta(
        description="自动检测车牌并上传",
        example="""
必选参数:
    车牌号+描述(字符串) 
使用例:
    上传车牌 123456 大e3q1
    123456 大e3q1
特别提醒:
    可以直接发送 车牌号+描述 无需使用指令
    本指令仅用于上传车牌到 bandoristation, bot不会有任何回应
    本指令受到 "关闭车牌转发" 指令影响
""",
    ),
)
