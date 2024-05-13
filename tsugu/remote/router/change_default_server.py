from ...config import config
from ...utils import text_response, User
from ...command_matcher import MC
import tsugu_api
from ...utils import server_exists, ns_2_is
from tsugu_api._typing import _Update


def handler(user: User, res: MC, platform: str, channel_id: str):
    default_server = ns_2_is(res.args)
    if not default_server:
        return text_response('未找到服务器，请输入正确的服务器名')
    change_data: _Update = {'default_server': default_server}
    r = tsugu_api.change_user_data(platform, user.user_id, change_data)
    if r.get('status') == 'success':
        return text_response(f'默认服务器已设置为 {", ".join(res.args)}')
    return text_response(r.get('data'))