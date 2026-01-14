## errmail 是什么

`errmail` 是一个**不侵入业务代码**的命令行工具：你用它来启动后端服务（或任何命令），它会在**不影响程序正常输出**的前提下监听 `stderr`，一旦检测到疑似报错（例如 Python Traceback / Exception / ERROR），就给你配置的邮箱发提醒。

## 适用场景

- **后端服务**：例如 `uvicorn` / `gunicorn` / `python app.py` / 任意二进制
- **你只关心“命令行报错”**：不想改业务代码、不想引入 SDK

## 安装

推荐在虚拟环境里安装（最不影响系统 Python）：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

如果你的环境较老、`pip install -e .` 提示 PEP660 editable 不支持，可以用兼容模式：

```bash
python -m pip install -e . --no-use-pep517
```

你也可以**不安装**，直接运行：

```bash
python -m errmail run -- python -c "raise RuntimeError('boom')"
```

## 快速开始

### 1) 平台默认使用“你的 SMTP”，用户只填邮箱（推荐）

你（工具提供方/平台方）在机器上预置一个文件：`/etc/errmail.env`（或用 `ERRMAIL_CONFIG_FILE` 指定路径）。

`/etc/errmail.env` 示例：

```bash
ERRMAIL_SMTP_HOST=smtp.your-company.com
ERRMAIL_SMTP_PORT=587
ERRMAIL_SMTP_USER=alert-bot@your-company.com
ERRMAIL_SMTP_PASS=YOUR_SMTP_PASSWORD
ERRMAIL_MAIL_FROM=alert-bot@your-company.com
```

然后用户运行时只需要提供自己的收件邮箱即可（二选一）：

```bash
export ERRMAIL_MAIL_TO="user@example.com"
```

或：

```bash
errmail run --to user@example.com -- python -m uvicorn yourapp:app --port 8000
```

### 2) 直接用环境变量配置 SMTP（不预置文件时使用）

最小配置：

```bash
export ERRMAIL_SMTP_HOST="smtp.gmail.com"
export ERRMAIL_SMTP_PORT="587"
export ERRMAIL_SMTP_USER="your_account@gmail.com"
export ERRMAIL_SMTP_PASS="your_app_password"
export ERRMAIL_MAIL_FROM="your_account@gmail.com"
export ERRMAIL_MAIL_TO="your_account@gmail.com"
```

可选：

```bash
export ERRMAIL_SMTP_TLS="1"          # 默认 1，使用 STARTTLS
export ERRMAIL_COOLDOWN_SECONDS="300" # 同一类错误 5 分钟最多发一次
export ERRMAIL_TAIL_LINES="200"       # 邮件里附带的 stderr 末尾行数
```

### 2) 用 errmail 启动你的服务

```bash
errmail run -- python -m uvicorn yourapp:app --port 8000
```

或任意命令：

```bash
errmail run -- bash -lc "python -c 'raise RuntimeError(\"boom\")'"
```

## 行为说明（保证“不影响正常运行”）

- **输出不变**：`stdout/stderr` 仍会原样打印到你的终端/日志系统
- **后台发送**：发邮件在后台线程执行；即使 SMTP 挂了，也不会阻塞命令退出
- **防刷屏**：同一类错误（按指纹 fingerprint 去重）在冷却窗口内只发一次

## 常见问题

- **为什么不用解析 exit code？**  
  会用，但不够：有些程序会把错误打印到 `stderr` 后继续跑，所以我们是“stderr 触发 + exit code 兜底”的组合。

