import os
import json
from dotenv import dotenv_values
from tsugu_api_core._settings import settings
from typing import Dict, Optional, Any
from loguru import logger


def get_program_defaults() -> Dict[str, Any]:
    """
    获取程序的默认配置值
    这些是对 tsugu_api_core.settings 默认值的覆盖
    """
    return {
        # 覆盖 tsugu_api_core 的默认值
        "timeout": 120,  # 从默认的 10 改为 120
        # 程序特有的配置项
        "compact": False,  # TSUGU_COMPACT
        "debug": False,    # TSUGU_DEBUG
        "bandori_station_token": "ZtV4EX2K9Onb",
        "bandori_station_name": "Tsugu",
    }


def check_config() -> Dict[str, Any]:
    """
    检查 .env 文件和环境变量中的 TSUGU_ 配置项
    优先使用 .env 文件，返回配置键值对
    """
    config = {}
    
    # 先读取环境变量
    for k, v in os.environ.items():
        if k.startswith("TSUGU_"):
            try:
                # 尝试解析 JSON 格式的值
                parsed_value = json.loads(v.lower())
                config[k] = parsed_value
            except json.JSONDecodeError:
                config[k] = v
    
    # .env 文件优先级更高，会覆盖环境变量中的同名配置
    kv = dotenv_values(".env")
    for k, v in kv.items():
        if k.upper().startswith("TSUGU_") and v is not None:
            k_upper = k.upper()
            try:
                # 尝试解析 JSON 格式的值
                parsed_value = json.loads(v.lower())
                config[k_upper] = parsed_value
            except json.JSONDecodeError:
                config[k_upper] = v
    
    return config


def load_config() -> Dict[str, Any]:
    """
    加载完整配置
    优先级：tsugu_api_core 默认值 < 程序默认值 < 用户配置
    """
    # 第一层：从 tsugu_api_core.settings 获取基础默认值
    result = {}
    for attr in ['client', 'timeout', 'max_retries', 'proxy', 'backend_url', 
                 'backend_proxy', 'userdata_backend_url', 'userdata_backend_proxy',
                 'use_easy_bg', 'compress']:
        if hasattr(settings, attr):
            result[attr] = getattr(settings, attr)
    
    # 第二层：应用程序默认值覆盖
    result.update(get_program_defaults())
    
    # 第三层：应用用户配置覆盖
    user_config = check_config()
    for k, v in user_config.items():
        # 移除 TSUGU_ 前缀并转为小写
        key = k.lower().removeprefix("tsugu_")
        result[key] = v
    
    return result


def apply_config_to_settings(config: Optional[Dict[str, Any]] = None):
    """
    应用配置到 tsugu_api_core.settings
    如果没有提供 config 参数，则自动调用 load_config() 获取配置
    """
    if config is None:
        config = load_config()
    
    if not config:
        return
    
    for k, v in config.items():
        if hasattr(settings, k) and v is not None:
            # 获取原属性的类型，进行类型转换
            original_value = getattr(settings, k)
            if original_value is not None:
                try:
                    # 如果原值是 bool 类型，特殊处理
                    if isinstance(original_value, bool):
                        if isinstance(v, str):
                            converted_value = v.lower() in ('true', '1', 'yes', 'on')
                        else:
                            converted_value = bool(v)
                    # 如果原值是数字类型，进行转换
                    elif isinstance(original_value, (int, float)):
                        converted_value = type(original_value)(v)  # type: ignore
                    # 其他情况直接使用原值类型转换
                    else:
                        converted_value = type(original_value)(v) if v is not None else v  # type: ignore
                    
                    setattr(settings, k, converted_value)
                except (ValueError, TypeError) as e:
                    # 转换失败时记录错误并使用原值
                    logger.warning(f"配置转换失败 {k}={v}: {e}")
                    setattr(settings, k, v)
            else:
                # 原值为 None 时直接设置
                setattr(settings, k, v)