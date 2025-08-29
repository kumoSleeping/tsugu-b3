import re
import asyncio
import tsugu_api_async
from dataclasses import dataclass

from typing import Awaitable, List, Union, Dict, Optional, Callable, Any
from tsugu_api_core._typing import ServerId, _UserPlayerInList
from loguru import logger
from arclet.alconna import output_manager, command_manager

from .alc_cmd import *
from .config import load_config, apply_config_to_settings
from .const import DIFFICULTY_TEXT_TO_ID, CAR_CONFIG, SERVER_TO_INDEX, INDEX_TO_SERVER


# 加载配置并应用到 settings
# 优先级：tsugu_api_core 默认值 < 程序默认值 < 用户配置
config: Dict[str, Any] = load_config()
apply_config_to_settings(config)


output_manager.set_action(lambda *_: None)  # 禁用 alc 自带输出


async def cmd_generator(
    *,
    message: str,
    user_id: str,
    platform: str = "chronocat",
    send_func: Optional[Callable[..., Awaitable[Any]]] = None,
) -> None:
    """
    ## 命令生成器
    生成命令并返回结果

    Args:
        message (str): 用户信息
        user_id (str): 用户ID
        platform (str, optional): 平台, 当用户ID为真实QQ号时, 平台可以为 chronocat == red == onebot. Defaults to "chronocat".
        send_func (Optional[Callable[..., Awaitable[Any]]]): 发送消息的函数. Defaults to None (控制台打印).

    send_func 需处理的消息格式为 List[Dict[str, str]]
    内部统一使用 send 函数，支持 str 和 List[Dict[str, str]] 两种格式
    当发送 str 时会自动转换为 [{"type": "string", "string": message}] 格式

    """
    
    async def send(message: Union[str, List[Dict[str, str]]]) -> None:
        """
        统一的发送函数
        - 支持发送 str 和 List[Dict[str, str]] 两种格式
        - 当发送 str 时，会转换为 List[Dict[str, str]] 格式
        - 如果没有提供 send_func，则默认打印到控制台
        """
        # 统一转换为列表格式
        if isinstance(message, str):
            formatted_message = [{"type": "string", "string": message}]
        else:
            formatted_message = message
        
        # 如果没有提供 send_func，默认打印
        if send_func is None:
            for item in formatted_message:
                if item.get("type") == "string":
                    print(item.get("string", ""))
        else:
            await send_func(formatted_message)
    
    # 使用统一的 send 函数
    try:
        result = await _handler(
            message=message,
            user_id=user_id,
            platform=platform,
            send=send,
        )
        if result:
            # 使用统一的 send 函数
            await send(result)
    except Exception as e:
        await send("内部错误")
        raise e
    

async def _handler(message: str, user_id: str, platform: str, send: Callable[[Union[str, List[Dict[str, str]]]], Awaitable[None]]) -> Any:
    
    logger.debug(f"UserId: {user_id} Platform: {platform} Message: {message}")
    
    @dataclass
    class User:
        user_id: str
        platform: str
        main_server: ServerId
        displayed_server_list: List[ServerId]
        share_room_number: bool
        user_player_index: int
        user_player_list: List[_UserPlayerInList]
        
    async def get_user(user_id: str, platform: str) -> User:
        """
        多次尝试获取用户数据，如果失败则抛出异常

        :param user_id:
        :param platform:
        :return:
        :raises ValueError: 当无法获取用户数据时抛出
        """
        for i in range(3):
            try:
                user_data_raw = await tsugu_api_async.get_user_data(platform, user_id)
                user_data = user_data_raw.get("data")
                user = User(
                    user_id=user_id,
                    platform=platform,
                    main_server=user_data.get("mainServer"),
                    displayed_server_list=user_data.get("displayedServerList"),
                    share_room_number=user_data.get("shareRoomNumber"),
                    user_player_index=user_data.get("userPlayerIndex"),
                    user_player_list=user_data.get("userPlayerList"),
                )
                logger.debug(f"User: {user}")
                return user
            except TimeoutError:
                await asyncio.sleep(0.2)
                logger.warning(f"TimeoutError: {i} ,will retry in 0.2s")
                continue
            except Exception as e:
                logger.error(f"Error: {e}")
                raise e
        
        # 如果所有重试都失败，抛出异常
        raise ValueError("无法获取用户数据，请稍后重试")
            
    class HandlerUtils:
        @staticmethod
        def server_names_2_server_ids(server_name: List[str]) -> List[ServerId]:
            """
            服务器名(多)转服务器ID(多)
            """
            return [SERVER_TO_INDEX[code] for code in server_name] #type: ignore

        @staticmethod
        def server_name_2_server_id(server_name: str) -> ServerId:
            """
            服务器名(1)转服务器ID(1)
            """
            return SERVER_TO_INDEX[server_name] if server_name in SERVER_TO_INDEX else None #type: ignore


        # def server_ids_2_server_names(index: List[ServerId]) -> List[str]:
        #     """
        #     服务器ID(多)转服务器名(多)
        #     """
        #     return [INDEX_TO_SERVER[code] for code in index]

        @staticmethod
        def server_id_2_server_name(index: ServerId) -> str:
            """
            服务器ID(1)转服务器名(1)
            """
            return INDEX_TO_SERVER[index] if index in INDEX_TO_SERVER else None #type: ignore

        @staticmethod
        def get_user_account_list_msg(user: User) -> str:
            """
            用于获取绑定的账号的列表信息文字
            """

            def mask_data(game_id: str) -> str:
                game_id = str(game_id)
                if len(game_id) < 6:
                    return game_id[:3] + "*" * (len(game_id) - 3)
                elif len(game_id) < 3:
                    return "*" * len(game_id)
                else:
                    game_id = game_id[:3] + "*" * (len(game_id) - 6) + game_id[-3:]
                return game_id

            bind_record = "\n".join(
                [
                    f'{i + 1}. {mask_data(str(x.get("playerId")))} {HandlerUtils.server_id_2_server_name(x.get("server"))}'
                    for i, x in enumerate(user.user_player_list)
                ]
            )
            if bind_record.strip() == "":
                return "error: 暂无记录，请先绑定"
            logger.debug(f"bind_record: \n{bind_record}")
            return bind_record

    if (res := alc_5v5.parse(message)).matched:
        user = await get_user(user_id, platform)
        meta = True if res.meta else False
        # 使用 return 直接返回同样可以发送消息, 次写法等同于 return await _send( await tsugu_api_async... )
        return await tsugu_api_async.event_stage(
            main_server=user.main_server, event_id=res.eventId, meta=meta
        )

    if (res := alc_pull.parse(message)).matched:
        user = await get_user(user_id, platform)
        gacha_id = res.gacha_id if res.gacha_id else None
        return await tsugu_api_async.gacha_simulate(
            main_server=user.main_server, times=res.times, gacha_id=gacha_id
        )

    if (res := alc_card_art.parse(message)).matched:
        if res.cardId is None:
            return "卡片ID不能为空"
        return await tsugu_api_async.get_card_illustration(card_id=res.cardId)

    if (res := alc_cutoff_history.parse(message)).matched:
        user = await get_user(user_id, platform)
        server = (
            HandlerUtils.server_name_2_server_id(res.serverName)
            if res.serverName
            else user.main_server
        )
        return await tsugu_api_async.cutoff_list_of_recent_event(
            main_server=server, tier=res.tier, event_id=res.eventId  # type: ignore
        )

    if (res := alc_gacha.parse(message)).matched:
        user = await get_user(user_id, platform)
        return await tsugu_api_async.search_gacha(
            displayed_server_list=user.displayed_server_list, gacha_id=res.gachaId  # type: ignore
        )

    if (res := alc_char.parse(message)).matched:
        user = await get_user(user_id, platform)
        return await tsugu_api_async.search_character(
            displayed_server_list=user.displayed_server_list, text=" ".join(str(word) for word in res.word)  # type: ignore
        )

    if (res := alc_event.parse(message)).matched:
        user = await get_user(user_id, platform)
        return await tsugu_api_async.search_event(
            displayed_server_list=user.displayed_server_list, text=" ".join(str(word) for word in res.word)  # type: ignore
        )

    if (res := alc_card.parse(message)).matched and message != "查卡面":
        user = await get_user(user_id, platform)
        return await tsugu_api_async.search_card(
            displayed_server_list=user.displayed_server_list, text=" ".join(str(word) for word in res.word)  # type: ignore
        )

    if (res := alc_player.parse(message)).matched:
        user = await get_user(user_id, platform)
        server = (
            HandlerUtils.server_name_2_server_id(res.serverName)
            if res.serverName
            else user.main_server
        )
        if str(res.playerId).startswith("4") and server == 3:
            return "Bestdori 暂不支持渠道服相关功能"
        return await tsugu_api_async.search_player(
            player_id=res.playerId, main_server=server  # type: ignore
        )

    if (res := alc_song_random.parse(message)).matched:
        user = await get_user(user_id, platform)
        text = " ".join(str(word) for word in res.word) if res.word else None  # type: ignore
        return await tsugu_api_async.song_random(
            main_server=user.main_server, text=str(text)
        )

    if (res := alc_song.parse(message)).matched:
        user = await get_user(user_id, platform)
        return await tsugu_api_async.search_song(
            displayed_server_list=user.displayed_server_list, text=" ".join(str(word) for word in res.word)  # type: ignore
        )

    if (res := alc_chart.parse(message)).matched:
        user = await get_user(user_id, platform)
        return await tsugu_api_async.song_chart(
            displayed_server_list=user.displayed_server_list,
            song_id=res.songId,  # type: ignore
            difficulty_id=DIFFICULTY_TEXT_TO_ID[res.difficultyText],  # type: ignore
        )

    if (res := alc_scores.parse(message)).matched:
        user = await get_user(user_id, platform)
        server = (
            HandlerUtils.server_name_2_server_id(res.serverName)
            if res.serverName
            else user.main_server
        )
        return await tsugu_api_async.song_meta(
            displayed_server_list=user.displayed_server_list, main_server=server
        )

    if (res := alc_cutoff_all.parse(message)).matched:
        user = await get_user(user_id, platform)
        server = (
            HandlerUtils.server_name_2_server_id(res.serverName)
            if res.serverName
            else user.main_server
        )
        return await tsugu_api_async.cutoff_all(
            main_server=server, event_id=res.eventId
        )

    if (res := alc_cutoff.parse(message)).matched:
        user = await get_user(user_id, platform)
        server = (
            HandlerUtils.server_name_2_server_id(res.serverName)
            if res.serverName
            else user.main_server
        )
        return await tsugu_api_async.cutoff_detail(
            main_server=server, tier=res.tier, event_id=res.eventId  # type: ignore
        )

    if (res := alc_bind.parse(message)).matched:
        if res.playerId == 0:
            r = await tsugu_api_async.bind_player_request(
                user_id=user_id, platform=platform
            )
            return f"绑定玩家 0 用于刷新验证码\n刷新成功, 验证码为 {r.get('data')['verifyCode']} "

        user = await get_user(user_id, platform)
        server = (
            HandlerUtils.server_name_2_server_id(res.serverName)
            if res.serverName
            else user.main_server
        )

        if str(res.playerId).startswith("4") and server == 3:
            return "Bestdori 暂不支持渠道服相关功能"

        if res.playerId in [player["playerId"] for player in user.user_player_list]:
            return "你已经绑定过这个玩家了"

        r = await tsugu_api_async.bind_player_request(
            user_id=user_id, platform=platform
        )
        await send(f"""请将在2min内将游戏账号的"评论(签名)"或"当前编队的名称"改为\n{r.get('data')['verifyCode']}\nbot验证成功后会发送消息通知""")

        
        for i in range(7):
            logger.debug(f"开始等待绑定验证, 第{i}次")
            await asyncio.sleep(20)
            logger.debug(f"时间到, 开始验证绑定")
            try:
                await tsugu_api_async.bind_player_verification(
                    user_id=user_id,
                    platform=platform,
                    server=server,
                    player_id=res.playerId,  # type: ignore
                    binding_action="bind",
                )
                user_new = await get_user(user_id, platform)
                bind_record = HandlerUtils.get_user_account_list_msg(user=user_new)
                logger.debug(f"绑定成功, 绑定列表: {bind_record}")
                return f"""绑定成功, 现在可以使用 "玩家状态" 命令查看绑定的玩家状态\n绑定列表: {bind_record}"""
            except Exception as e:
                # 如果最后一次
                if i == 6:
                    logger.debug(f"绑定超时, {e}")
                    return f"解除绑定超时, {e}\n用户未及时修改游戏信息或Bestdori服务器暂时失效"
                if "都与验证码不匹配" in str(e):
                    logger.debug(f"验证码不匹配, 重试")
                    continue
                # 其他错误
                logger.debug(f'出现意外错误, {e}')
                return f"出现意外错误, {e}"

    if (res := alc_server_default.parse(message)).matched:
        user = await get_user(user_id, platform)
        server_list = HandlerUtils.server_names_2_server_ids(res.serverList)  # type: ignore
        update = {"displayedServerList": server_list}
        await tsugu_api_async.change_user_data(
            platform=platform, user_id=user.user_id, update=update  # type: ignore
        )
        return f"默认服务器已设置为 {', '.join(res.serverList)}"  # type: ignore

    if (res := alc_server_main.parse(message)).matched:
        user = await get_user(user_id, platform)
        server = HandlerUtils.server_name_2_server_id(res.serverName)  # type: ignore
        r = await tsugu_api_async.change_user_data(
            platform=platform, user_id=user.user_id, update={"mainServer": server}  # type: ignore
        )
        return f"主服务器已设置为 {res.serverName}"  # type: ignore

    if (res := alc_share_room_off.parse(message)).matched:
        user = await get_user(user_id, platform)
        update = {"shareRoomNumber": False}
        await tsugu_api_async.change_user_data(
            platform=platform, user_id=user.user_id, update=update  # type: ignore
        )
        return "关闭车牌转发成功"

    if (res := alc_share_room_on.parse(message)).matched:
        user = await get_user(user_id, platform)
        update = {"shareRoomNumber": True}
        await tsugu_api_async.change_user_data(
            platform=platform, user_id=user.user_id, update=update  # type: ignore
        )
        return "开启车牌转发成功"

    if (res := alc_player_status.parse(message)).matched:

        async def _player_status_case_default():
            """
            默认情况下, 返回主账号的玩家状态
            """
            user_player_index = user.user_player_index
            if len(user.user_player_list) == 0:
                return "未找到记录, 请先绑定"

            if user.user_player_index + 1 > len(user.user_player_list):
                update = {"userPlayerIndex": 0}
                await tsugu_api_async.change_user_data(
                    platform=platform, user_id=user.user_id, update=update  # type: ignore
                )
                await send(f"""主账号异常, 自动修正成功, 将生成玩家状态（1）""")
            game_id_msg = user.user_player_list[user_player_index]
            return await tsugu_api_async.search_player(
                player_id=int(game_id_msg.get("playerId")),
                main_server=game_id_msg.get("server"),
            )

        async def _player_status_case_server():
            """
            指定服务器名, 返回该服务器的玩家状态(如果存在)（只返回第一个）
            """
            server_id = HandlerUtils.server_name_2_server_id(res.serverName)  # type: ignore
            if server_id is None:
                return "未找到服务器 " + res.serverName  # type: ignore

            for i, x in enumerate(user.user_player_list):
                if x.get("server") == server_id:
                    game_id_msg = user.user_player_list[i]
                    return await tsugu_api_async.search_player(
                        player_id=int(game_id_msg.get("playerId")),
                        main_server=game_id_msg.get("server"),
                    )
            return f"未找到服务器 {res.serverName} 的记录"

        async def _player_status_case_index():
            """
            指定账号序号, 返回该账号的玩家状态
            """
            if res.accountIndex > len(user.user_player_list) or res.accountIndex < 1:  # type: ignore
                return f"未找到记录 {res.accountIndex}, 请先绑定"

            game_id_msg = user.user_player_list[res.accountIndex - 1]  # type: ignore
            return await tsugu_api_async.search_player(
                int(game_id_msg.get("playerId")), game_id_msg.get("server")
            )

        user = await get_user(user_id, platform)
        if res.accountIndex and not res.serverName:
            return await _player_status_case_index()
        elif res.serverName and not res.accountIndex:
            return await _player_status_case_server()
        elif res.serverName and res.accountIndex:
            return "只能同时指定一个账号或服务器"
        else:
            return await _player_status_case_default()

    if (res := alc_account_main.parse(message)).matched:
        user = await get_user(user_id, platform)

        # 如果没有账号或者账号序号不在范围内
        if (
            not res.accountIndex
            or (len(user.user_player_list) < res.accountIndex)
            or res.accountIndex < 1
        ):
            bind_record = HandlerUtils.get_user_account_list_msg(user)
            if bind_record == "":
                return "未找到记录, 请先绑定账号"
            return f"请选择你要设置为主账号的账号数字: \n{bind_record}\n例如: 主账号 1"

        update = {"userPlayerIndex": res.accountIndex - 1}  # type: ignore
        await tsugu_api_async.change_user_data(platform, user.user_id, update)  # type: ignore
        return f"主账号已设置为账号 {res.accountIndex}"  # type: ignore

    if (res := alc_unbind.parse(message)).matched:

        if res.index == 0:
            r = await tsugu_api_async.bind_player_request(
                user_id=user_id, platform=platform
            )
            return (
                f"解除绑定 0 用于刷新验证码\n刷新成功, 验证码为 {r.get('data')['verifyCode']} "
                ""
            )

        user = await get_user(user_id, platform)

        if (
            not res.index
            or len(user.user_player_list) < res.index
            or res.index < 1
        ):
            bind_record = HandlerUtils.get_user_account_list_msg(user)
            if bind_record == "":
                return "未找到记录, 请先绑定账号"
            return f"选择你要解除的账号数字: \n{bind_record}\n例如: 解除绑定 1"

        r = await tsugu_api_async.bind_player_request(
            user_id=user_id, platform=platform
        )

        # 私有数据库API的解绑流程
        if r.get("extra") == "safe_mode":
            logger.debug(f"启用 tsugu-3b safe_mode 解绑流程")
            await tsugu_api_async.bind_player_verification(
                user_id=user_id,
                platform=platform,
                server=user.user_player_list[res.index - 1].get("server"),
                player_id=user.user_player_list[res.index - 1].get("playerId"),
                binding_action="unbind",
            )
            return f"解除绑定成功"

        # 常规解绑流程
        await send(
            f"""请将在2min内将游戏账号的"评论(签名)"或"当前编队的名称"改为\n{r.get('data')['verifyCode']}\nbot验证成功后会发送消息通知"""
        )
        for i in range(7):
            logger.debug(f"开始等待解绑验证, 第{i}次")
            await asyncio.sleep(20)
            logger.debug(f"时间到, 开始验证解绑")
            try:
                await tsugu_api_async.bind_player_verification(
                    user_id=user_id,
                    platform=platform,
                    server=user.user_player_list[res.index - 1].get("server"),
                    player_id=user.user_player_list[res.index - 1].get("playerId"),
                    binding_action="unbind",
                )
                logger.debug(f"解除绑定成功")
                return f"解除绑定成功"
            except Exception as e:
                if i == 6:
                    logger.debug(f"解除绑定超时, {e}")
                    return f"解除绑定超时, 用户未及时修改游戏信息或Bestdori服务器暂时失效"
                if "都与验证码不匹配" in str(e):
                    logger.debug(f"验证码不匹配, 重试")
                    continue
                logger.debug(f'出现意外错误, {e}')
                return f"出现意外错误, {e}"

    if (res := alc_room.parse(message)).matched:

        data = await tsugu_api_async.query_room_number()
        if not data:
            return "myc"

        user = await get_user(user_id, platform)
        new_data_list = []
        seen_numbers = set()

        # 一开始就逆序 data 列表
        data.reverse()

        for i in data:
            number = int(i["number"])

            # 跳过已经处理过的 number
            if number in seen_numbers:
                continue

            new_data = {}
            # 添加 number 到 seen_numbers, 以便后续检查
            seen_numbers.add(number)

            # 检查是否有足够的玩家信息
            if len(user.user_player_list) > user.user_player_index:
                # 添加玩家信息
                new_data.update(
                    {
                        "playerId": user.user_player_list[user.user_player_index][
                            "playerId"
                        ],
                        "server": user.user_player_list[user.user_player_index][
                            "server"
                        ],
                    }
                )
            # 更新其他数据
            new_data.update(
                {
                    "number": number,
                    "source": i["source_info"]["name"],
                    "userId": i["user_info"]["user_id"],
                    "time": i["time"],
                    "userName": i["user_info"]["username"],
                    "rawMessage": i["raw_message"],
                }
            )
            if i["user_info"]["avatar"]:
                new_data.update(
                    {
                        "avatarUrl": "https://asset.bandoristation.com/images/user-avatar/"
                        + i["user_info"]["avatar"]
                    }
                )
            elif i["user_info"]["type"] == "qq":
                new_data.update(
                    {
                        "avatarUrl": f'https://q2.qlogo.cn/headimg_dl?dst_uin={i["user_info"]["user_id"]}&spec=100'
                    }
                )

            new_data_list.append(new_data)

        return await tsugu_api_async.room_list(new_data_list)

    # 最后检查车牌
    message_for_car = message[4:].strip() if message.startswith("上传车牌") else message
    # 检查car_config['car']中的关键字
    if any(str(keyword) in message_for_car for keyword in CAR_CONFIG["car"]):
        # 检查car_config['fake']中的关键字
        if any(str(keyword) in message_for_car for keyword in CAR_CONFIG["fake"]):
            pass
        else:
            if re.match(r"^\d{5}(\D|$)|^\d{6}(\D|$)", message_for_car):

                user = await get_user(user_id, platform)
                if not user.share_room_number:
                    # 关闭车牌转发
                    return

                # 先假设 car_id 为 6 位数字, 如果不是则取前 5 位
                car_id = (
                    car_id[:5]
                    if not (car_id := message_for_car[:6]).isdigit()
                    and car_id[:5].isdigit()
                    else car_id
                )
                # 如果 user_id 不是数字, 则设置为默认值（TSUGU 官方 QQ 号）
                car_user_id = user.user_id if user.user_id.isdigit() else "3889000770"
                await tsugu_api_async.submit_room_number(
                    number=int(car_id),
                    user_id=car_user_id,
                    raw_message=message_for_car,
                    source=config["bandori_station_name"],
                    token=config["bandori_station_token"],
                )
                logger.debug(f"上传车牌成功: {message_for_car}")
                return "上传车牌成功"

    if (res := alc_help.parse(message)).matched:
        if not res.cmd:
            return '\n'.join(command_manager.all_command_help().split("\n")[:-1]) + """\n使用 "help 命令名" 查看命令帮助"""
        else:
            # 对应下方的最后处理没有匹配的命令给出帮助信息
            message = f"{res.cmd[0]} -h" # 模拟用户输入help命令
            logger.debug(f"已更改用户输入: {message}")


    # 最后处理没有匹配的命令给出帮助信息
    for command in command_manager.get_commands():
        if (res := command.parse(message)).head_matched and not command.parse(message).matched:
            # if message.endswith(" -h"):
            #     cmd_full: str = command_manager.command_help(res.source.name)
            #     foo = "● "+cmd_full.split("\n", 2)[1] +'\n'+ cmd_full.split("\n", 3)[3].strip()
            #     return foo
            # 如果命令头匹配了, 但是命令没有匹配, 返回 help 信息
            cmd_full: Optional[str] = command_manager.command_help(res.source.name)
            if cmd_full:
                # foo: str = command_manager.command_help(res.source.name).split("\n", 2)[1] +'\n'+ command_manager.command_help(res.source.name).split("\n", 3)[3].strip()
                foo = cmd_full.split("\n", 2)[1] +'\n'+ cmd_full.split("\n", 3)[3].strip()
                return foo


__all__ = ["cmd_generator"]