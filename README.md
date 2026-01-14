## errmail 是什么

`errmail` 是一个**不侵入业务代码**的命令行工具：你用它来启动后端服务（或任何命令），它会在**不影响程序正常输出**的前提下监听 `stderr`，一旦检测到疑似报错（例如 Python Traceback / Exception / ERROR），就给你配置的邮箱发提醒。

## 适用场景

- **后端服务**：例如 `uvicorn` / `gunicorn` / `python app.py` / 任意二进制
- **你只关心"命令行报错"**：不想改业务代码、不想引入 SDK

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

### 方式一：使用配置文件（推荐）

#### 1. 生成配置模板

```bash
errmail init
```

它会生成 `~/.errmail.env`，你打开把以下几项填成真实值：

- `ERRMAIL_SMTP_HOST`
- `ERRMAIL_SMTP_PORT`（推荐 587）
- `ERRMAIL_SMTP_TLS`（推荐 1）或 `ERRMAIL_SMTP_SSL`（如果是 465 端口）
- `ERRMAIL_SMTP_USER`
- `ERRMAIL_SMTP_PASS`（通常是"授权码/应用专用密码"）
- `ERRMAIL_MAIL_FROM`（通常等于 SMTP_USER）

你也可以让模板自动带上常见邮箱的默认参数（仍然需要你自己填写授权码/应用专用密码）：

```bash
errmail init --provider gmail
errmail init --provider qq
errmail init --provider 163
errmail init --provider outlook
errmail init --provider 126
```

#### 2. 测试邮件发送

```bash
errmail test --to user@example.com --verbose
```

#### 3. 使用 errmail 运行你的指令

```bash
errmail run --to user@example.com -- <command>
```

或任意命令：

```bash
errmail run --to user@example.com -- python -c "raise RuntimeError('boom')"
```

### 方式二：使用环境变量

如果不想使用配置文件，可以直接设置环境变量：

```bash
export ERRMAIL_SMTP_HOST="smtp.gmail.com"
export ERRMAIL_SMTP_PORT="587"
export ERRMAIL_SMTP_USER="your_account@gmail.com"
export ERRMAIL_SMTP_PASS="your_app_password"
export ERRMAIL_MAIL_FROM="your_account@gmail.com"
export ERRMAIL_MAIL_TO="your_account@gmail.com"
export ERRMAIL_SMTP_TLS="1"
```

然后运行：

```bash
errmail run -- <command>
```

### 方式三：系统级配置（可选）

如果你有系统管理权限，可以在 `/etc/errmail.env` 配置系统默认的 SMTP 设置，用户只需要设置自己的收件邮箱。

生成系统级配置模板：

```bash
errmail init --path /etc/errmail.env
```

用户运行时只需要提供自己的收件邮箱：

```bash
errmail run --to user@example.com -- python -m uvicorn yourapp:app --port 8000
```

## 命令行参数

### errmail init

生成配置文件模板。

- `--path`: 指定配置文件路径（默认：`~/.errmail.env`）
- `--provider`: 预设邮箱服务商配置（`custom`, `gmail`, `outlook`, `qq`, `163`, `126`）
- `--force`: 覆盖已存在的配置文件
- `--print`: 输出模板到标准输出（不写入文件）

### errmail test

发送测试邮件。

- `--to`: 指定收件人邮箱（覆盖配置文件中的 `ERRMAIL_MAIL_TO`）
- `--service`: 覆盖服务名称
- `--verbose`: 显示详细日志

### errmail run

运行命令并监控错误。

- `--to`: 指定收件人邮箱（覆盖配置文件中的 `ERRMAIL_MAIL_TO`）
- `--service`: 覆盖服务名称
- `--cwd`: 指定工作目录
- `--cooldown-seconds`: 设置错误冷却时间（秒）
- `--tail-lines`: 设置邮件中包含的 stderr 末尾行数
- `--verbose`: 显示详细日志

## 行为说明

- **输出不变**：`stdout/stderr` 仍会原样打印到你的终端/日志系统
- **后台发送**：发邮件在后台线程执行；即使 SMTP 挂了，也不会阻塞命令退出
- **防刷屏**：同一类错误（按指纹 fingerprint 去重）在冷却窗口内只发一次（默认 300 秒）

## 配置文件说明

配置文件支持以下环境变量：

### SMTP 服务器设置

- `ERRMAIL_SMTP_HOST`: SMTP 服务器地址
- `ERRMAIL_SMTP_PORT`: SMTP 端口（默认：587）
- `ERRMAIL_SMTP_USER`: SMTP 用户名
- `ERRMAIL_SMTP_PASS`: SMTP 密码（授权码/应用专用密码）
- `ERRMAIL_SMTP_TLS`: 是否使用 STARTTLS（默认：1）
- `ERRMAIL_SMTP_SSL`: 是否使用 SSL（默认：0）

### 邮件设置

- `ERRMAIL_MAIL_FROM`: 发件人邮箱
- `ERRMAIL_MAIL_TO`: 收件人邮箱（可通过 `--to` 参数覆盖）

### 可选设置

- `ERRMAIL_SERVICE`: 服务名称（默认：`unknown-service`）
- `ERRMAIL_COOLDOWN_SECONDS`: 错误冷却时间（秒，默认：300）
- `ERRMAIL_TAIL_LINES`: 邮件中包含的 stderr 末尾行数（默认：200）

## SMTP 配置指南

### 通用规则

- **推荐使用 587 + STARTTLS**：`ERRMAIL_SMTP_PORT=587` 且 `ERRMAIL_SMTP_TLS=1`
- **如果使用 465 端口（SSL）**：设置 `ERRMAIL_SMTP_PORT=465`、`ERRMAIL_SMTP_SSL=1` 且 `ERRMAIL_SMTP_TLS=0`
- **使用授权码/应用专用密码**：不要使用网页登录密码

### 常见邮箱服务配置

#### Gmail / Google Workspace

- 开启两步验证后生成 App Password
- `ERRMAIL_SMTP_HOST=smtp.gmail.com`
- `ERRMAIL_SMTP_PORT=587`
- `ERRMAIL_SMTP_TLS=1`
- `ERRMAIL_SMTP_USER=你的邮箱`
- `ERRMAIL_SMTP_PASS=App Password`

#### 163 / 126 / QQ 邮箱

- 在邮箱"客户端/SMTP"设置里开启 SMTP/IMAP，并生成授权码
- `ERRMAIL_SMTP_HOST=smtp.163.com`（或 `smtp.126.com`、`smtp.qq.com`）
- `ERRMAIL_SMTP_PORT=465`
- `ERRMAIL_SMTP_SSL=1`
- `ERRMAIL_SMTP_TLS=0`
- `ERRMAIL_SMTP_USER=你的邮箱`
- `ERRMAIL_SMTP_PASS=授权码`

#### Outlook / Office 365

- 开启两步验证后生成应用密码
- `ERRMAIL_SMTP_HOST=smtp.office365.com`
- `ERRMAIL_SMTP_PORT=587`
- `ERRMAIL_SMTP_TLS=1`

### 安全提醒

- **不要把你的 SMTP 密码给别人**
- `~/.errmail.env` 里包含敏感信息，建议：
  - 给文件设权限（例如 `chmod 600 ~/.errmail.env`）
  - 不要提交到 git

## 常见问题

- **为什么不用解析 exit code？**  
  会用，但不够：有些程序会把错误打印到 `stderr` 后继续跑，所以我们是"stderr 触发 + exit code 兜底"的组合。
