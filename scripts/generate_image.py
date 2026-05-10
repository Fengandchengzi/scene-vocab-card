#!/usr/bin/env python3
"""
scene-vocab-card 图片生成脚本

调用老张 API (laozhang.ai) 的 Gemini 模型，将 scene_image_prompt 生成为场景词汇卡图片。

用法:
    python generate_image.py --prompt "A young boy sitting on bed..." --type 场景词汇卡
    python generate_image.py --file prompt.txt --type 场景词汇卡竖版 --output my_card.png
    echo "prompt text" | python generate_image.py --type 场景词汇卡
"""

import argparse
import base64
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from config import (
    API_KEY,
    API_URL,
    CARD_TYPE_MAP,
    DEFAULT_CARD_TYPE,
    MAX_RETRIES,
    OUTPUT_DIR,
    REQUEST_TIMEOUT,
)


def build_request_body(prompt: str, aspect_ratio: str, image_size: str) -> dict:
    """构造 Gemini generateContent 请求体"""
    return {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "responseModalities": ["image", "text"],
            "aspectRatio": aspect_ratio,
            "imageSize": image_size,
        },
    }


def call_api(prompt: str, aspect_ratio: str, image_size: str) -> bytes:
    """调用 API 并返回图片的 bytes 数据"""
    if not API_KEY:
        print("错误: 未设置 LAOZHANG_API_KEY 环境变量", file=sys.stderr)
        print("请运行: export LAOZHANG_API_KEY='你的API密钥'", file=sys.stderr)
        sys.exit(1)

    body = build_request_body(prompt, aspect_ratio, image_size)
    data = json.dumps(body).encode("utf-8")

    req = Request(
        API_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
        method="POST",
    )

    last_error = None
    for attempt in range(1 + MAX_RETRIES):
        if attempt > 0:
            print(f"重试第 {attempt} 次...", file=sys.stderr)
            time.sleep(3)

        try:
            with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
            return extract_image(resp_data)

        except HTTPError as e:
            last_error = e
            error_body = e.read().decode("utf-8", errors="replace")
            if e.code == 401:
                print("错误: API Key 无效或已过期", file=sys.stderr)
                sys.exit(1)
            elif e.code == 402 or "insufficient" in error_body.lower():
                print("错误: API 余额不足，请充值后重试", file=sys.stderr)
                sys.exit(1)
            elif e.code == 429:
                print("警告: 请求频率过高，等待后重试...", file=sys.stderr)
                time.sleep(5)
                continue
            else:
                print(f"API 错误 (HTTP {e.code}): {error_body}", file=sys.stderr)

        except (URLError, TimeoutError) as e:
            last_error = e
            print(f"网络错误: {e}", file=sys.stderr)

    print(f"请求失败，已重试 {MAX_RETRIES} 次: {last_error}", file=sys.stderr)
    sys.exit(1)


def extract_image(resp_data: dict) -> bytes:
    """从 API 响应中提取 base64 图片数据并解码"""
    try:
        candidates = resp_data.get("candidates", [])
        for candidate in candidates:
            parts = candidate.get("content", {}).get("parts", [])
            for part in parts:
                inline_data = part.get("inlineData")
                if inline_data and inline_data.get("data"):
                    return base64.b64decode(inline_data["data"])
    except (KeyError, IndexError, TypeError):
        pass

    print("错误: 未能从 API 响应中提取图片数据", file=sys.stderr)
    print(f"响应内容: {json.dumps(resp_data, ensure_ascii=False, indent=2)[:1000]}", file=sys.stderr)
    sys.exit(1)


def get_prompt(args: argparse.Namespace) -> str:
    """从命令行参数、文件或 stdin 获取 prompt"""
    if args.prompt:
        return args.prompt

    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"错误: 文件不存在: {args.file}", file=sys.stderr)
            sys.exit(1)
        return path.read_text(encoding="utf-8").strip()

    # 尝试从 stdin 读取
    if not sys.stdin.isatty():
        text = sys.stdin.read().strip()
        if text:
            return text

    print("错误: 请通过 --prompt、--file 或 stdin 提供 prompt", file=sys.stderr)
    sys.exit(1)


def resolve_output_path(args: argparse.Namespace, card_type: str) -> Path:
    """确定输出文件路径"""
    if args.output:
        path = Path(args.output)
        if not path.suffix:
            path = path.with_suffix(".png")
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{card_type}_{timestamp}.png"
    return OUTPUT_DIR / filename


def main():
    parser = argparse.ArgumentParser(
        description="scene-vocab-card 图片生成：scene_image_prompt → API → PNG"
    )
    parser.add_argument("--prompt", "-p", help="直接传入 prompt 文本")
    parser.add_argument("--file", "-f", help="从文件读取 prompt")
    parser.add_argument(
        "--type", "-t",
        dest="card_type",
        default=DEFAULT_CARD_TYPE,
        choices=list(CARD_TYPE_MAP.keys()),
        help=f"卡片类型 (默认: {DEFAULT_CARD_TYPE})",
    )
    parser.add_argument("--output", "-o", help="输出文件路径 (默认: ~/scene-vocab-card/output/<类型>_<时间>.png)")

    args = parser.parse_args()

    # 获取 prompt
    prompt = get_prompt(args)

    print(f"卡片类型: {args.card_type}", file=sys.stderr)
    print(f"Prompt 长度: {len(prompt)} 字符", file=sys.stderr)

    # 获取卡片参数
    aspect_ratio, image_size = CARD_TYPE_MAP[args.card_type]
    print(f"比例: {aspect_ratio}, 分辨率: {image_size}", file=sys.stderr)

    # 调用 API
    print("正在生成图片...", file=sys.stderr)
    image_bytes = call_api(prompt, aspect_ratio, image_size)

    # 保存图片
    output_path = resolve_output_path(args, args.card_type)
    output_path.write_bytes(image_bytes)

    print(f"图片已保存: {output_path}", file=sys.stderr)
    # stdout 输出路径，便于管道调用
    print(output_path)


if __name__ == "__main__":
    main()
