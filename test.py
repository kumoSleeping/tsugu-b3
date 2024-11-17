import io
import base64
import asyncio
from PIL import Image
from loguru import logger
from tsugu import cmd_generator


tsugu_test_all = [
    'help',
    '查试炼',
    '查试炼 -m',
    '抽卡模拟',
    '抽卡模拟 10',
    '抽卡模拟 10 947',
    '查卡面',
    '查卡面 1399',
    'lsycx 1000',
    'lsycx 1000 177 jp',
    '查卡池 947',
    '查角色 ksm',
    '查角色 吉他',
    '查活动 绿 tsugu',
    '查活动 177',
    '查卡 1399',
    '查卡 红 ars 5x',
    '查玩家 1003282233',
    '查玩家 40474621 jp',
    '随机曲 lv27',
    '随机曲 ag',
    '查曲 1',
    '查曲 ag lv27',
    '查谱面 1',
    '查谱面 128 special',
    '查询分数表 cn',
    'ycxall 177',
    'ycxall 177 jp',
    'ycx 1000',
    'ycx 1000 177 jp',
    '绑定玩家',
    '绑定玩家 0',
    '设置默认服务器 cn jp',
    '主服务器',
    '主服务器日服',
    '主账号',
    '主账号 0',
    '主账号 1',
    '主账号 3',
    '主账号 -1',
    '主服务器 cn',
    '国服模式',
    '关闭车牌转发',
    '开启车牌转发',
    '绑定玩家',
    '玩家状态',
    '主账号',
    '主账号 2',
    '解除绑定 1',
    'ycm',
    '上传车牌 12345q4',
]


async def test_tsugu():

    async def _test_send(result):
        if isinstance(result, list):
            if not result:
                logger.error("没有返回数据")
                return
            for item in result:
                if item["type"] == "string":
                    logger.success("\n" + item['string'])
                elif item["type"] == "base64":
                    i = base64.b64decode(item["string"])
                    logger.warning(
                        "\n" + f"[图片: 图像大小: {len(i) / 1024:.2f}KB]"
                    )
                    img = Image.open(io.BytesIO(i))
                    img.show()
        if isinstance(result, str):
            logger.success("\n" + result)

    test_count = 0
    user_id = "114514"

    for i in tsugu_test_all:
        msg = await cmd_generator(message=i, user_id=user_id, send_func=_test_send)


# 启动测试
if __name__ == "__main__":
    asyncio.run(test_tsugu())
