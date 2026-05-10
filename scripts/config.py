"""scene-vocab-card 配置文件"""

import os
from pathlib import Path

# API 配置
API_KEY = os.environ.get("LAOZHANG_API_KEY", "")
API_URL = "https://api.laozhang.ai/v1beta/models/gemini-3-pro-image-preview:generateContent"

# 输出目录
OUTPUT_DIR = Path.home() / "scene-vocab-card" / "output"

# 请求超时（秒）
REQUEST_TIMEOUT = 120

# 最大重试次数
MAX_RETRIES = 1

# 卡片类型 → (aspectRatio, imageSize) 映射
CARD_TYPE_MAP = {
    "场景词汇卡": ("4:3", "2K"),
    "场景词汇卡竖版": ("3:4", "2K"),
}

# 默认卡片类型
DEFAULT_CARD_TYPE = "场景词汇卡"
