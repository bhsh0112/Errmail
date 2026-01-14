#!/usr/bin/env python3
"""/**
 * @file test_error.py
 * @description 用于测试 errmail 的错误脚本
 * 
 * 用法:
 *   python -m errmail run --to your@email.com --verbose -- python test_error.py
 * 
 * 或直接运行（会触发错误）:
 *   python test_error.py
 */"""

import sys
import time


def test_runtime_error():
    """/**
     * @description 测试 RuntimeError
     */"""
    print("正在执行一些操作...", file=sys.stdout)
    print("即将触发错误...", file=sys.stdout)
    raise RuntimeError("这是一个测试用的运行时错误！")


def test_value_error():
    """/**
     * @description 测试 ValueError
     */"""
    print("尝试转换无效值...", file=sys.stdout)
    value = "not_a_number"
    result = int(value)  # 这会触发 ValueError


def test_file_not_found():
    """/**
     * @description 测试 FileNotFoundError
     */"""
    print("尝试打开不存在的文件...", file=sys.stdout)
    with open("non_existent_file.txt", "r") as f:
        content = f.read()


def test_zero_division():
    """/**
     * @description 测试 ZeroDivisionError
     */"""
    print("执行除法运算...", file=sys.stdout)
    result = 10 / 0  # 这会触发 ZeroDivisionError


def main():
    """/**
     * @description 主函数 - 根据命令行参数选择要触发的错误类型
     */"""
    error_type = sys.argv[1] if len(sys.argv) > 1 else "runtime"
    
    print("=" * 60, file=sys.stdout)
    print("Errmail 错误测试脚本", file=sys.stdout)
    print("=" * 60, file=sys.stdout)
    print(f"错误类型: {error_type}", file=sys.stdout)
    print(file=sys.stdout)
    
    try:
        if error_type == "runtime":
            test_runtime_error()
        elif error_type == "value":
            test_value_error()
        elif error_type == "file":
            test_file_not_found()
        elif error_type == "zero":
            test_zero_division()
        elif error_type == "all":
            # 依次触发多个错误（只执行第一个）
            print("测试多个错误类型...", file=sys.stdout)
            test_runtime_error()
        else:
            print(f"未知的错误类型: {error_type}", file=sys.stderr)
            print("可用类型: runtime, value, file, zero, all", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        # 错误会自动输出到 stderr
        raise


if __name__ == "__main__":
    main()

