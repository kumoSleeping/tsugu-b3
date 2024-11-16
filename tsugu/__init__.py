import re
import asyncio
import tsugu_api_async

from typing import Awaitable, List, Union, Dict, Optional
from arclet.alconna import output_manager, command_manager

from .utils import *
from .alc_cmd import *
from .config import load_config, apply_config
from .const import DIFFICULTY_TEXT_TO_ID, CAR_CONFIG


config = load_config()
apply_config(config)

output_manager.set_action(lambda *_: None)  # 禁用 alc 自带输出


async def async_print(*args, **kwargs):  # 默认 send 输出函数
    print(*args, **kwargs)


async def cmd_generator(
    message: str,
    user_id: str,
    platform: str = "red",
    send_func: Optional[Awaitable] = async_print,
):
    """
    ## 命令生成器
    生成命令并返回结果

    Args:
        message (str): 用户信息
        user_id (str): 用户ID
        platform (str, optional): 平台，当用户ID为真实QQ号时，平台可以为red. Defaults to "red".
        send_func (Optional[Awaitable], optional): 发送消息的函数. Defaults to None.

    send_func 需处理的消息格式为 str 或者 List[Dict[str, str]]

    """
    try:
        result = await _handler(
            message=message,
            user_id=user_id,
            platform=platform,
            send_func=send_func,
        )
        if result:
            # 使得 _handler 函数直接 return 与 send 都可以发送消息
            await send_func(result)
    except Exception as e:
        await send_func("出现错误，请联系管理员")
        raise e


async def _handler(message: str, user_id: str, platform: str, send_func: Awaitable):

    async def _send(message: Union[str, List[Dict[str, str]]]):
        await send_func(message)

    if (res := alc_song_meta.parse(message)).matched:
        user = await get_user(user_id, platform)
        meta = True if res.meta else False
        # 使用 return 直接返回同样可以发送消息，次写法等同于 return await _send( await tsugu_api_async... )
        return await tsugu_api_async.event_stage(
            main_server=user.main_server, event_id=res.eventId, meta=meta
        )

    if (res := alc_gacha_simulate.parse(message)).matched:
        user = await get_user(user_id, platform)
        gacha_id = res.gacha_id if res.gacha_id else None
        return await tsugu_api_async.gacha_simulate(
            main_server=user.main_server, times=res.times, gacha_id=gacha_id
        )

    if (res := alc_get_card_illustration.parse(message)).matched:
        # 如果没有卡面ID，则返回帮助信息，因为可能会出现“查卡面”触发后面的查卡的问题
        if res.cardId is None:
            return command_manager.command_help(res.source.name)
        return await tsugu_api_async.get_card_illustration(card_id=res.cardId)

    if (res := alc_cutoff_list_of_recent_event.parse(message)).matched:
        user = await get_user(user_id, platform)
        server = (
            server_name_2_server_id(res.serverName)
            if res.serverName
            else user.main_server
        )
        return await tsugu_api_async.cutoff_list_of_recent_event(
            main_server=server, tier=res.tier, event_id=res.eventId
        )

    if (res := alc_search_gacha.parse(message)).matched:
        user = await get_user(user_id, platform)
        return await tsugu_api_async.search_gacha(
            displayed_server_list=user.displayed_server_list, gacha_id=res.gachaId
        )

    if (res := alc_search_character.parse(message)).matched:
        user = await get_user(user_id, platform)
        return await tsugu_api_async.search_character(
            displayed_server_list=user.displayed_server_list, text=" ".join(res.word)
        )

    if (res := alc_search_event.parse(message)).matched:
        user = await get_user(user_id, platform)
        return await tsugu_api_async.search_event(
            displayed_server_list=user.displayed_server_list, text=" ".join(res.word)
        )

    if (res := alc_search_card.parse(message)).matched:
        user = await get_user(user_id, platform)
        return await tsugu_api_async.search_card(
            displayed_server_list=user.displayed_server_list, text=" ".join(res.word)
        )

    if (res := alc_search_player.parse(message)).matched:
        user = await get_user(user_id, platform)
        server = (
            server_name_2_server_id(res.serverName)
            if res.serverName
            else user.main_server
        )
        if str(res.playerId).startswith("4") and server == 3:
            return "Bestdori 暂不支持渠道服相关功能"
        return await tsugu_api_async.search_player(
            player_id=res.playerId, main_server=server
        )

    if (res := alc_song_random.parse(message)).matched:
        user = await get_user(user_id, platform)
        text = " ".join(res.word) if res.word else None
        return await tsugu_api_async.song_random(
            main_server=user.main_server, text=text
        )

    if (res := alc_search_song.parse(message)).matched:
        user = await get_user(user_id, platform)
        return await tsugu_api_async.search_song(
            displayed_server_list=user.displayed_server_list, text=" ".join(res.word)
        )

    if (res := alc_song_chart.parse(message)).matched:
        user = await get_user(user_id, platform)
        return await tsugu_api_async.song_chart(
            displayed_server_list=user.displayed_server_list,
            song_id=res.songId,
            difficulty_id=DIFFICULTY_TEXT_TO_ID[res.difficultyText],
        )

    if (res := alc_song_meta.parse(message)).matched:
        user = await get_user(user_id, platform)
        server = (
            server_name_2_server_id(res.serverName)
            if res.serverName
            else user.main_server
        )
        return await tsugu_api_async.song_meta(
            displayed_server_list=user.displayed_server_list, main_server=server
        )

    if (res := alc_cutoff_all.parse(message)).matched:
        user = await get_user(user_id, platform)
        server = (
            server_name_2_server_id(res.serverName)
            if res.serverName
            else user.main_server
        )
        return await tsugu_api_async.cutoff_all(
            main_server=server, event_id=res.eventId
        )

    if (res := alc_cutoff_detail.parse(message)).matched:
        user = await get_user(user_id, platform)
        server = (
            server_name_2_server_id(res.serverName)
            if res.serverName
            else user.main_server
        )
        return await tsugu_api_async.cutoff_detail(
            main_server=server, tier=res.tier, event_id=res.eventId
        )

    if (res := alc_bind_player.parse(message)).matched:
        if res.playerId == 0:
            r = await tsugu_api_async.bind_player_request(
                user_id=user_id, platform=platform
            )
            return f"绑定玩家 0 用于刷新验证码\n刷新成功，验证码为 {r.get('data')['verifyCode']} "

        user = await get_user(user_id, platform)
        server = (
            server_name_2_server_id(res.serverName)
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
        await _send(
            f"""已进入绑定流程，请将在2min内将游戏账号的 评论(个性签名) 或者 当前使用的 乐队编队名称改为\n{r.get('data')['verifyCode']}\nbot将自动验证，绑定成功后会发送消息通知\n若验证码不可用，使用「绑定玩家 0」刷新验证码"""
        )

        for i in range(7):
            await asyncio.sleep(20)
            try:
                await tsugu_api_async.bind_player_verification(
                    user_id=user_id,
                    platform=platform,
                    server=server,
                    player_id=res.playerId,
                    binding_action="bind",
                )
                return f"绑定成功，现在可以使用 玩家状态 命令查看绑定的玩家状态"
            except Exception as e:
                # 如果最后一次
                if i == 6:
                    return f"解除绑定超时，{e}\n用户未及时修改游戏信息或Bestdori服务器暂时失效"
                if "都与验证码不匹配" in str(e):
                    continue
                # 其他错误
                return f"绑定失败，{e}"

    if (res := alc_change_displayed_server_list.parse(message)).matched:
        user = await get_user(user_id, platform)
        server_list = server_names_2_server_ids(res.serverList)
        update = {"displayedServerList": server_list}
        await tsugu_api_async.change_user_data(
            platform=platform, user_id=user.user_id, update=update
        )
        return f"默认服务器已设置为 {', '.join(res.serverList)}"

    if (res := alc_change_main_server.parse(message)).matched:
        user = await get_user(user_id, platform)
        server = server_name_2_server_id(res.serverName)
        r = await tsugu_api_async.change_user_data(
            platform=platform, user_id=user.user_id, update={"mainServer": server}
        )
        return f"主服务器已设置为 {res.serverName}"

    if (res := alc_toggle_share_room_number_off.parse(message)).matched:
        user = await get_user(user_id, platform)
        update = {"shareRoomNumber": False}
        await tsugu_api_async.change_user_data(
            platform=platform, user_id=user.user_id, update=update
        )
        return "关闭车牌转发成功"

    if (res := alc_toggle_share_room_number_on.parse(message)).matched:
        user = await get_user(user_id, platform)
        update = {"shareRoomNumber": True}
        await tsugu_api_async.change_user_data(
            platform=platform, user_id=user.user_id, update=update
        )
        return "开启车牌转发成功"

    if (res := alc_player_status.parse(message)).matched:

        async def _player_status_case_default():
            """
            默认情况下，返回主账号的玩家状态
            """
            user_player_index = user.user_player_index
            if len(user.user_player_list) == 0:
                return "未找到记录，请先绑定"

            if user.user_player_index + 1 > len(user.user_player_list):
                update = {"userPlayerIndex": 0}
                await tsugu_api_async.change_user_data(
                    platform=platform, user_id=user.user_id, update=update
                )
                await _send(f"""主账号异常，自动修正成功，将生成玩家状态（1）""")
            game_id_msg = user.user_player_list[user_player_index]
            return await tsugu_api_async.search_player(
                player_id=int(game_id_msg.get("playerId")),
                main_server=game_id_msg.get("server"),
            )

        async def _player_status_case_server():
            """
            指定服务器名，返回该服务器的玩家状态(如果存在)（只返回第一个）
            """
            server_id = server_name_2_server_id(res.serverName)
            if not server_exists(server_id):
                return "未找到服务器 " + res.serverName

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
            指定账号序号，返回该账号的玩家状态
            """
            if res.accountIndex > len(user.user_player_list) or res.accountIndex < 1:
                return f"未找到记录 {res.accountIndex}，请先绑定"

            game_id_msg = user.user_player_list[res.accountIndex - 1]
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

    if (res := alc_set_main_account.parse(message)).matched:
        user = await get_user(user_id, platform)

        # 如果没有账号或者账号序号不在范围内
        if (
            not res.accountIndex
            or (len(user.user_player_list) < res.accountIndex)
            or res.accountIndex < 1
        ):
            bind_record = get_user_account_list_msg(user=user)
            if bind_record == "":
                return "未找到记录，请先绑定账号"
            return f"请选择你要设置为主账号的账号数字：\n{bind_record}\n例如：主账号 1"

        update = {"userPlayerIndex": res.accountIndex - 1}
        await tsugu_api_async.change_user_data(platform, user.user_id, update)
        return f"主账号已设置为账号 {res.accountIndex}"

    if (res := alc_unbind_player.parse(message)).matched:

        if res.index == 0:
            r = await tsugu_api_async.bind_player_request(
                user_id=user_id, platform=platform
            )
            return (
                f"解除绑定 0 用于刷新验证码\n刷新成功，验证码为 {r.get('data')['verifyCode']} "
                ""
            )

        user = await get_user(user_id, platform)

        if (not res.index) or len(user.user_player_list) < res.index or res.index < 1:
            bind_record = get_user_account_list_msg(user=user)
            if bind_record == "":
                return "未找到记录，请先绑定账号"
            return f"选择你要解除的账号数字：\n{bind_record}\n例如：解除绑定 1"

        r = await tsugu_api_async.bind_player_request(
            user_id=user_id, platform=platform
        )

        # 私有数据库API的解绑流程
        if r.get("extra") == "safe_mode":
            await tsugu_api_async.bind_player_verification(
                user_id=user_id,
                platform=platform,
                server=user.user_player_list[res.index - 1].get("server"),
                player_id=user.user_player_list[res.index - 1].get("playerId"),
                binding_action="unbind",
            )
            return f"解除绑定成功"

        # 常规解绑流程
        await _send(
            f"""已进入解除绑定流程，请将在2min内将游戏账号的 评论(个性签名) 或者 当前使用的 乐队编队名称改为\n{r.get('data')['verifyCode']}\nbot将自动验证，解除成功后会发送消息通知\n若验证码不可用，使用「解除绑定 0」刷新验证码"""
        )
        for i in range(7):
            await asyncio.sleep(20)
            try:
                await tsugu_api_async.bind_player_verification(
                    user_id=user_id,
                    platform=platform,
                    server=user.user_player_list[res.index - 1].get("server"),
                    player_id=user.user_player_list[res.index - 1].get("playerId"),
                    binding_action="unbind",
                )
                return f"解除绑定成功"
            except Exception as e:
                if i == 6:
                    return f"解除绑定超时，{e}\n用户未及时修改游戏信息或Bestdori服务器暂时失效"
                if "都与验证码不匹配" in str(e):
                    continue
                return f"解除绑定失败，{e}"

    if (res := alc_query_room_number.parse(message)).matched:

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
            # 添加 number 到 seen_numbers，以便后续检查
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

                # 先假设 car_id 为 6 位数字，如果不是则取前 5 位
                car_id = (
                    car_id[:5]
                    if not (car_id := message_for_car[:6]).isdigit()
                    and car_id[:5].isdigit()
                    else car_id
                )
                # 如果 user_id 不是数字，则设置为默认值（TSUGU 官方 QQ 号）
                car_user_id = user.user_id if user.user_id.isdigit() else "3889000770"
                await tsugu_api_async.submit_room_number(
                    number=int(car_id),
                    user_id=car_user_id,
                    raw_message=message_for_car,
                    source=config["bandori_station_name"],
                    token=config["bandori_station_token"],
                )
                return

    if (res := alc_help.parse(message)).matched:
        if not res.cmd:
            return command_manager.all_command_help()
        message = res.cmd + " -h"

    # 最后再次全匹配一次所有命令的 help 信息
    for command in command_manager.get_commands():
        if (res := command.parse(message)).head_matched and not command.parse(
            message
        ).matched:
            await send_func(command_manager.command_help(res.source.name))
