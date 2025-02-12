


<div align="center">


<h1 align="center"> Tsugu B3 </h1>


<div align="center">

</div>

✨<img src="./logo.jpg" width="30" width="30" height="30" alt="tsugu"/>✨



_✨ User (Natural language) -> ^^^^^  -> [Tsugu BanG Dream Bot](https://github.com/Yamamoto-2/tsugu-bangdream-bot?tab=readme-ov-file)  ✨_
</div>

<p align="center">
<a href="https://github.com/Yamamoto-2/tsugu-bangdream-bot">
    <img src="https://img.shields.io/badge/tsugubangdream bot - api-yellow" alt="license">
  </a>

<a href="https://github.com/kumoSleeping/tsugu-python-frontend?tab=MIT-1-ov-file">
    <img src="https://img.shields.io/github/license/kumoSleeping/tsugu-python-frontend" alt="license">
  </a>
<a href="https://pypi.org/project/tsugu/">
    <img src="https://img.shields.io/pypi/v/tsugu.svg" alt="license">
  </a>
</p>

---

## 📦 Install

```shell
pip install tsugu
```

> API powered by  <a href="https://github.com/WindowsSov8forUs/tsugu-api-python?tab=readme-ov-file">tsugu-api-python</a>

> Command matching provided by <a href="https://github.com/ArcletProject/Alconna">Alconna</a>

***

## 🚗 App
| 项目 | 说明 |
| --- | --- |
| [Tsugu QQ 官方机器人](https://github.com/kumoSleeping/tsugu-qq-open-platform-bot) | 主力项目 |
| [TBBP](https://github.com/zhaomaoniu/tsugu-bangdream-bot-py) | 无人维护 NoneBot 用户请使用 [NPTBB](https://github.com/WindowsSov8forUs/nonebot-plugin-tsugu-bangdream-bot) |
|[LTP](https://github.com/kumoSleeping/lgr-tsugu-py) | 无人维护 无法使用 |


## 📜 Feat

- 为改善用户体验，本包与 `koishi 插件` 在部分行为上略有不同。
  - 更加详细的帮助信息。
  - 默认不需要命令头后跟上完整的空格（可关闭）。
  - `绑定玩家` `解除绑定` `刷新验证吗` 等自验证策略。
  - 基于 `Alconna` 的真 “可选参数” 。
  - 车站相关功能不主动支持绑定账号的配队信息，但被动渲染车站给出的配队信息。
  - 参数错误时输出完整的命令帮助信息。
  - 略有不同的车站屏蔽词策略。
  - 增加 `上传车牌` 命令，但仍然支持自动从文本开头提取车牌。
  - `主账号` 和 `解除绑定` 的不同行为。
- 争议功能
  - 暂时支持 玩家状态 \<serverName\> 策略
  - 暂不支持 shortcut类指令
    - 暂不支持 `国服模式` `国服玩家状态` 等指令
    - 而应该使用 `主服务器 国服` `玩家状态 国服` 等指令式响应。
  - 暂不支持 Tsugu 内部车站互通，只通 `bangdori station` 。
- 为了适应官方 BOT 的特性，本包提供了隐式一些非通用方法。
  - 当解除绑定用户数据库返回特定值时会被认定为安全模式，触发直接解除绑定操作。



## 📚 Async & Higher-Order Function
`cmd_generator` 是一个异步方法，用于直接处理用户输入的自然语言并处理，调用传入的 `send_func` 发送结果
- `message` (str)：用户输入的自然语言
- `user_id` (str)：用户的 `channel_id` 或 `user_id`，当 `platform` 为 `red` 、 `chronocat` 、 `onebot` 时，该值一般为用户 QQ 号
- `platform` (str)：用户的平台（默认值：`red`）
- `send_func`（Awaitable）：期望一个接受 `result` 参数的异步方法，用于发送结果，具体需要实现的方法请参考下方示例


```python
import asyncio
from tsugu import cmd_generator
from loguru import logger

async def _test_send_eg(result):
    if isinstance(result, list): [logger.success(item['string']) for item in result if item["type"] == "string"]
    if isinstance(result, str): logger.success("\n" + result)

asyncio.run(cmd_generator(message='查卡 -h', user_id='114514', platform='satori',send_func=_test_send_eg))


```

## ✏️ Config

>配置方式

- 通过环境变量
  linux & macos
  ```zsh
  export TSUGU_COMPACT=false
  ...
  ```
  windows
  ```bat
  set TSUGU_COMPACT=false
  ...
  ```

- 通过 `.env` 文件
  ```shell
  TSUGU_COMPACT=false
  ...
  ```

> 可配置项

```zsh
# 命令头后是否必须跟上完整的空格才能匹配，例如 `查卡947` 与 `查卡 947` 。（默认值：false）
TSUGU_COMPACT=false 

# 设置请求超时时间（默认值：120秒）
TSUGU_TIMEOUT=120

# 设置代理地址（默认值：空字符串）
TSUGU_PROXY=''

# 设置后端地址（默认值：http://tsugubot.com:8080）
TSUGU_BACKEND_URL=http://tsugubot.com:8080

# 设置是否使用后端代理（默认值：true）
TSUGU_BACKEND_PROXY=true

# 设置用户数据后端地址（默认值：http://tsugubot.com:8080）
TSUGU_USERDATA_BACKEND_URL=http://tsugubot.com:8080

# 设置是否使用用户数据后端代理（默认值：true）
TSUGU_USERDATA_BACKEND_PROXY=true

# 设置是否使用简易背景（默认值：true）
TSUGU_USE_EASY_BG=true

# 设置是否压缩返回数据（默认值：true）
TSUGU_COMPRESS=true
```



## 🔧 开发相关

> 安装依赖
> 
```shell
pip install -r req
```

---