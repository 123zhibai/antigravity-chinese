from .common import CommonAdapter
from .fallback import FallbackAdapter
from .versions.v2_24 import V2_24_Adapter

def get_adapter(version, archive, runtime_script, menu_map):
    """
    根据 Antigravity 版本号及 archive 内容选择最匹配的适配器。
    匹配顺序：
    1. 特定版本适配器 (如 v2.24)
    2. 通用特征适配器 (Common)
    3. 兜底容灾适配器 (Fallback)
    """
    if version and version.startswith("2.24"):
        adapter = V2_24_Adapter(archive, runtime_script, menu_map)
        if adapter.can_apply():
            return adapter

    common = CommonAdapter(archive, runtime_script, menu_map)
    if common.can_apply():
        return common

    return FallbackAdapter(archive, runtime_script, menu_map)
