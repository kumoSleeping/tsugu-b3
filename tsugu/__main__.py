import argparse
import asyncio
from . import cmd_generator
import base64
import sys
from loguru import logger

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
                print(item["string"])
            elif item["type"] == "base64":
                img_bytes = base64.b64decode(item["string"])
                img_count += 1
                print(f"[图片: 图像大小: {len(img_bytes) / 1024:.2f}KB]")
                if PIL_AVAILABLE:
                    try:
                        import io
                        img = Image.open(io.BytesIO(img_bytes))
                        img.show()
                    except Exception as e:
                        print(f"图片显示失败: {e}")
                else:
                    print("未检测到PIL库，无法直接展示图片。您可以通过如下命令安装：\n  pip install pillow")
    elif isinstance(result, str):
        print(result)
    else:
        print(f"未知返回类型: {result}")

def main():
    try:
        parser = argparse.ArgumentParser(description="Tsugu 命令行调用工具 (python -m tsugu)")
        parser.add_argument("message", type=str, help="要发送的消息内容")
        parser.add_argument("--user_id", type=str, default="114514", help="用户ID，默认114514")
        parser.add_argument("--platform", type=str, default="chronocat", help="平台，默认chronocat")
        # 新增：无参数时显示帮助
        if len(sys.argv) == 1:
            parser.print_help()
            sys.exit(0)
        args = parser.parse_args()
        asyncio.run(cmd_generator(
            message=args.message,
            user_id=args.user_id,
            platform=args.platform,
            send_func=cli_send_func
        ))
    except KeyboardInterrupt:
        logger.info("程序已终止")
        sys.exit(0)
    except Exception as e:
        logger.error(f"发生错误: {e}")

if __name__ == "__main__":
    main() 