from ..common import CommonAdapter

class V2_24_Adapter(CommonAdapter):
    """
    Antigravity v2.24.x 专有版本适配器
    针对 2.24.0 官方 release 的 dist/utils.js 和 dist/menu.js 进行了特征对齐
    """
    name = "v2.24"

    def can_apply(self):
        # 必须同时存在 dist/utils.js 与 dist/menu.js
        return self.archive.has_file('/dist/utils.js') and self.archive.has_file('/dist/menu.js')
