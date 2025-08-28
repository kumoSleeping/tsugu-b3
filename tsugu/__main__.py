import argparse
import asyncio
from .__init__ import cmd_generator
import base64
import sys
from loguru import logger


def init_log(log_level):
    # 设置日志格式
    log_format = "<green>{time:HH:mm:ss.S}</green> <level>[{level}]</level> {message}" 
    # 移除默认的控制台输出
    logger.remove()
    # 控制台日志
    logger.add(
        sink=sys.stderr,
        format=log_format,
        level=log_level,
    )

# 检查PIL可用性
try:
    import importlib
    Image = importlib.import_module("PIL.Image")
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

async def cli_send_func(result):
    img_count = 0
    if isinstance(result, list):
        for item in result:
            if item["type"] == "string":
                logger.info(item["string"])
            elif item["type"] == "base64":
                img_bytes = base64.b64decode(item["string"])
                img_count += 1
                logger.info(f"[图片: 图像大小: {len(img_bytes) / 1024:.2f}KB]")
                if PIL_AVAILABLE:
                    try:
                        import io
                        img = Image.open(io.BytesIO(img_bytes))
                        img.show()
                    except Exception as e:
                        logger.error(f"图片显示失败: {e}")
                else:
                    logger.warning("未检测到PIL库，无法直接展示图片。您可以通过如下命令安装：\n  pip install pillow")
    elif isinstance(result, str):
        logger.info(result)
    else:
        logger.warning(f"未知返回类型: {result}")

def main():
    try:
        parser = argparse.ArgumentParser(description="Tsugu 命令行工具")
        parser.add_argument("message", nargs='*', help="要发送的消息内容")
        parser.add_argument("-u", "--user_id", type=str, default="114514", help="用户ID，默认114514")
        parser.add_argument("-p", "--platform", type=str, default="chronocat", help="平台，默认chronocat")
        parser.add_argument("-d", "--debug", action="store_true", help="启用调试模式")
        parser.add_argument("-e", "--env", action="store_true", help="输出可选的环境变量配置")
        args = parser.parse_args()
        
        # 根据参数设置日志等级
        log_level = "DEBUG" if args.debug else "INFO"
        init_log(log_level)
        
        # 如果请求输出环境变量配置
        if args.env:
            logger.info("""可选的环境变量:

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
""")
            return
        
        # 将所有位置参数合并为一个字符串
        message = ' '.join(args.message) if args.message else ""
        
        # 如果没有消息内容，显示帮助
        if not message:
            parser.print_help()
            return
            
        asyncio.run(cmd_generator(
            message=message,
            user_id=args.user_id,
            platform=args.platform,
            send_func=cli_send_func
        ))
    except KeyboardInterrupt:
        logger.info("程序已终止")
        sys.exit(0)
    except Exception as e:
        logger.error(f"内部错误: {e}")

if __name__ == "__main__":
    main() 