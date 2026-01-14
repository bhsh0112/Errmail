#!/usr/bin/env python3
"""/**
 * @file test_service.py
 * @description 模拟一个会报错的服务，用于测试 errmail
 * 
 * 用法:
 *   python -m errmail run --to your@email.com --verbose -- python test_service.py
 */"""

import sys
import time


def main():
    """/**
     * @description 模拟一个服务，运行一段时间后出错
     */"""
    print("=" * 60, file=sys.stdout)
    print("模拟服务启动中...", file=sys.stdout)
    print("=" * 60, file=sys.stdout)
    
    # 模拟正常运行的日志
    for i in range(3):
        print(f"[INFO] 服务正常运行中... ({i+1}/3)", file=sys.stdout)
        time.sleep(0.5)
    
    print(file=sys.stdout)
    print("=" * 60, file=sys.stdout)
    print("❌ 服务遇到错误！", file=sys.stdout)
    print("=" * 60, file=sys.stdout)
    
    # 触发一个错误，这个错误会被 errmail 捕获并发送邮件
    raise RuntimeError(
        "服务异常: 数据库连接失败\n"
        "详细信息: 无法连接到 MySQL 服务器 127.0.0.1:3306\n"
        "请检查数据库服务是否正常运行"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # 重新抛出异常，让 errmail 捕获
        raise

