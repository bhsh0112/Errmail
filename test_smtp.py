#!/usr/bin/env python3
"""/**
 * @file test_smtp.py
 * @description SMTP 连接测试脚本，用于诊断 163 邮箱连接问题
 * 
 * 用法:
 *   python test_smtp.py
 * 
 * 该脚本会：
 * 1. 读取 ~/.errmail.env 配置文件
 * 2. 测试不同的端口和加密方式组合
 * 3. 显示详细的连接信息和错误
 */"""

from __future__ import annotations

import os
import socket
import smtplib
import ssl
import sys
import time
from pathlib import Path
from typing import Optional


def _read_config() -> dict[str, str]:
    """/**
     * @description 读取配置文件
     * @returns {Object<string, string>}
     */"""
    config_path = Path.home() / ".errmail.env"
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        print("💡 提示: 请先运行 'errmail init --provider 163' 生成配置文件")
        return {}
    
    config: dict[str, str] = {}
    try:
        for line in config_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            key = k.strip()
            val = v.strip().strip("'").strip('"')
            if key:
                config[key] = val
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return {}
    
    return config


def _get_config_value(config: dict[str, str], key: str, env_key: Optional[str] = None) -> Optional[str]:
    """/**
     * @param {Object<string, string>} config
     * @param {string} key
     * @param {?string} env_key
     * @returns {?string}
     */"""
    # 优先使用环境变量
    if env_key:
        value = os.getenv(env_key)
        if value:
            return value
    # 然后使用配置文件
    return config.get(key)


def test_port_connectivity(host: str, port: int, timeout: int = 5) -> tuple[bool, Optional[str]]:
    """/**
     * @description 测试端口连接性
     * @param {string} host
     * @param {number} port
     * @param {number} timeout
     * @returns {[boolean, ?string]}
     */"""
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        return True, None
    except socket.timeout:
        return False, "连接超时"
    except socket.gaierror as e:
        return False, f"DNS 解析失败: {e}"
    except ConnectionRefusedError:
        return False, "连接被拒绝（端口可能未开放）"
    except OSError as e:
        return False, f"网络错误: {e}"


def test_smtp_connection(
    host: str,
    port: int,
    use_ssl: bool,
    use_tls: bool,
    user: Optional[str],
    password: Optional[str],
    timeout: int = 15,
) -> tuple[bool, str]:
    """/**
     * @description 测试 SMTP 连接
     * @param {string} host
     * @param {number} port
     * @param {boolean} use_ssl
     * @param {boolean} use_tls
     * @param {?string} user
     * @param {?string} password
     * @param {number} timeout
     * @returns {[boolean, string]}
     */"""
    try:
        context = ssl.create_default_context()
        
        if use_ssl:
            # 使用 SSL (端口 465)
            print(f"    📡 尝试 SSL 连接 (端口 {port})...")
            server = smtplib.SMTP_SSL(host, port, timeout=timeout, context=context)
            print(f"    ✅ SSL 连接成功")
        elif use_tls:
            # 使用 STARTTLS (端口 587)
            print(f"    📡 尝试 STARTTLS 连接 (端口 {port})...")
            server = smtplib.SMTP(host, port, timeout=timeout)
            print(f"    ✅ TCP 连接成功")
            server.ehlo()
            print(f"    ✅ EHLO 成功")
            server.starttls(context=context)
            print(f"    ✅ STARTTLS 成功")
            server.ehlo()
            print(f"    ✅ EHLO (TLS) 成功")
        else:
            # 纯文本连接（不推荐）
            print(f"    📡 尝试纯文本连接 (端口 {port})...")
            server = smtplib.SMTP(host, port, timeout=timeout)
            print(f"    ✅ TCP 连接成功")
        
        # 尝试登录
        if user and password:
            print(f"    🔐 尝试登录...")
            server.login(user, password)
            print(f"    ✅ 登录成功")
        else:
            print(f"    ⚠️  跳过登录（未提供用户名或密码）")
        
        server.quit()
        return True, "连接成功"
        
    except smtplib.SMTPServerDisconnected as e:
        error_msg = str(e)
        if "timed out" in error_msg.lower() or "timeout" in error_msg.lower():
            return False, f"连接超时: {error_msg}"
        return False, f"服务器断开连接: {error_msg}"
    except smtplib.SMTPAuthenticationError as e:
        return False, f"认证失败: {e}"
    except smtplib.SMTPException as e:
        return False, f"SMTP 错误: {type(e).__name__}: {e}"
    except socket.timeout:
        return False, f"连接超时（{timeout} 秒）"
    except Exception as e:
        return False, f"未知错误: {type(e).__name__}: {e}"


def main() -> int:
    """/**
     * @returns {number}
     */"""
    print("=" * 60)
    print("🔍 SMTP 连接诊断工具 (163 邮箱)")
    print("=" * 60)
    print()
    
    # 读取配置
    config = _read_config()
    if not config:
        return 1
    
    # 获取配置值
    host = _get_config_value(config, "ERRMAIL_SMTP_HOST", "ERRMAIL_SMTP_HOST") or "smtp.163.com"
    user = _get_config_value(config, "ERRMAIL_SMTP_USER", "ERRMAIL_SMTP_USER")
    password = _get_config_value(config, "ERRMAIL_SMTP_PASS", "ERRMAIL_SMTP_PASS")
    mail_from = _get_config_value(config, "ERRMAIL_MAIL_FROM", "ERRMAIL_MAIL_FROM")
    
    print("📋 当前配置:")
    print(f"   SMTP 主机: {host}")
    print(f"   用户名: {user or '(未设置)'}")
    print(f"   密码: {'*' * (len(password) if password else 0) if password else '(未设置)'}")
    print(f"   发件人: {mail_from or '(未设置)'}")
    print()
    
    # 检查必要配置
    if not user:
        print("❌ 错误: 未设置 ERRMAIL_SMTP_USER")
        print("💡 请在配置文件中设置 ERRMAIL_SMTP_USER")
        return 1
    
    if not password:
        print("❌ 错误: 未设置 ERRMAIL_SMTP_PASS")
        print("💡 提示: 163 邮箱需要使用授权码（不是登录密码）")
        print("   请登录 163 邮箱网页版 -> 设置 -> POP3/SMTP/IMAP -> 开启服务并生成授权码")
        return 1
    
    # 测试端口连接性
    print("=" * 60)
    print("🔌 步骤 1: 测试端口连接性")
    print("=" * 60)
    
    ports_to_test = [465, 587, 25]
    port_status = {}
    
    for port in ports_to_test:
        print(f"\n📌 测试端口 {port}...")
        success, error = test_port_connectivity(host, port, timeout=5)
        port_status[port] = success
        if success:
            print(f"   ✅ 端口 {port} 可以连接")
        else:
            print(f"   ❌ 端口 {port} 无法连接: {error}")
    
    print()
    
    # 测试 SMTP 连接
    print("=" * 60)
    print("📧 步骤 2: 测试 SMTP 连接")
    print("=" * 60)
    
    test_configs = [
        {"port": 465, "ssl": True, "tls": False, "name": "465 端口 + SSL (推荐用于 163)"},
        {"port": 587, "ssl": False, "tls": True, "name": "587 端口 + STARTTLS (备选方案)"},
        {"port": 25, "ssl": False, "tls": False, "name": "25 端口 + 纯文本 (不推荐)"},
    ]
    
    success_count = 0
    for cfg in test_configs:
        port = cfg["port"]
        print(f"\n📌 测试配置: {cfg['name']}")
        print(f"   主机: {host}:{port}")
        
        # 如果端口连接性测试失败，跳过
        if not port_status.get(port, False):
            print(f"   ⏭️  跳过（端口连接性测试失败）")
            continue
        
        success, message = test_smtp_connection(
            host=host,
            port=port,
            use_ssl=cfg["ssl"],
            use_tls=cfg["tls"],
            user=user,
            password=password,
            timeout=15,
        )
        
        if success:
            print(f"   🎉 {message}")
            success_count += 1
        else:
            print(f"   ❌ {message}")
    
    print()
    print("=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    
    if success_count > 0:
        print(f"✅ 成功: {success_count} 个配置可以正常连接")
        print()
        print("💡 建议:")
        print("   1. 使用可以正常连接的配置更新 ~/.errmail.env")
        print("   2. 如果 465 端口可用，推荐使用:")
        print("      ERRMAIL_SMTP_PORT=465")
        print("      ERRMAIL_SMTP_SSL=1")
        print("      ERRMAIL_SMTP_TLS=0")
        print("   3. 如果 587 端口可用，可以使用:")
        print("      ERRMAIL_SMTP_PORT=587")
        print("      ERRMAIL_SMTP_TLS=1")
        print("      ERRMAIL_SMTP_SSL=0")
        return 0
    else:
        print("❌ 所有配置都无法连接")
        print()
        print("💡 可能的原因:")
        print("   1. 网络问题（防火墙、代理等）")
        print("   2. 163 邮箱 SMTP 服务未开启")
        print("   3. 授权码错误（请确认使用的是授权码，不是登录密码）")
        print("   4. 账户被限制（可能需要登录网页版检查）")
        print()
        print("🔧 建议检查:")
        print("   1. 登录 163 邮箱网页版")
        print("   2. 设置 -> POP3/SMTP/IMAP")
        print("   3. 确认已开启 SMTP 服务")
        print("   4. 重新生成授权码并更新配置文件")
        return 1


if __name__ == "__main__":
    sys.exit(main())

