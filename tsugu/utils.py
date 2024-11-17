import asyncio
import tsugu_api_async
from typing import List
from loguru import logger
from dataclasses import dataclass
from tsugu_api_core._typing import _ServerId, _UserPlayerInList

from .alc_cmd import *
from .const import SERVER_TO_INDEX, INDEX_TO_SERVER


@dataclass
class User:
    user_id: str
    platform: str
    main_server: _ServerId
    displayed_server_list: List[_ServerId]
    share_room_number: bool
    user_player_index: int
    user_player_list: List[_UserPlayerInList]


def server_names_2_server_ids(server_name: List[str]) -> List[_ServerId]:
    """
    服务器名(多)转服务器ID(多)
    """
    return [SERVER_TO_INDEX[code] for code in server_name]


def server_name_2_server_id(server_name: str) -> _ServerId:
    """
    服务器名(1)转服务器ID(1)
    """
    return SERVER_TO_INDEX[server_name] if server_name in SERVER_TO_INDEX else None


def server_ids_2_server_names(index: List[_ServerId]) -> List[str]:
    """
    服务器ID(多)转服务器名(多)
    """
    return [INDEX_TO_SERVER[code] for code in index]


def server_id_2_server_name(index: _ServerId) -> str:
    """
    服务器ID(1)转服务器名(1)
    """
    return INDEX_TO_SERVER[index] if index in INDEX_TO_SERVER else None


def get_user_account_list_msg(user) -> str:
    """
    用于获取绑定的账号的列表信息文字
    """

    def mask_data(game_id: str):
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
            f'{i + 1}. {mask_data(str(x.get("playerId")))} {server_id_2_server_name(x.get("server"))}'
            for i, x in enumerate(user.user_player_list)
        ]
    )

    if bind_record.strip() == "":
        return "error: 暂无记录，请先绑定"

    return bind_record


async def get_user(user_id: str, platform: str) -> User:
    """
    多次尝试获取用户数据

    :param user_id:
    :param platform:
    :return:
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
            return user
        except TimeoutError:
            await asyncio.sleep(0.2)
            continue
        except Exception as e:
            logger.error(f"Error: {e}")
            
