from ...config import config
from ...utils import text_response, UserLocal
from ...command_matcher import MC
import tsugu_api
from ...utils import server_exists, n_2_i, i_2_n, ns_2_is, is_2_ns
from tsugu_api._typing import _ServerId, _Update
import typing
from ..db import db_manager, get_user_data
import json


def handler(user: UserLocal, res: MC, platform: str, channel_id: str):
    server_mode: typing.Optional[_ServerId] = n_2_i(res.args[0]) if res.args else None
    if not server_mode:
        return text_response('未找到服务器，请输入正确的服务器名')
    cursor = db_manager.conn.cursor()
    cursor.execute("UPDATE users SET server_mode = ? WHERE user_id = ? AND platform = ?",
                   (server_mode, user.user_id, platform))
    db_manager.conn.commit()
    return text_response(f'服务器模式设置为 {i_2_n(server_mode)}')

