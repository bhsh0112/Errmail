## 目录

- [目录](#目录)
- [errmail 是什么](#errmail-是什么)
- [适用场景](#适用场景)
- [安装](#安装)
  - [方式一：通过 pip 从 Git 仓库安装（推荐）](#方式一通过-pip-从-git-仓库安装推荐)
  - [方式二：本地开发安装](#方式二本地开发安装)
  - [方式三：不安装直接运行](#方式三不安装直接运行)
- [快速开始](#快速开始)
  - [方式一：使用配置文件（推荐）](#方式一使用配置文件推荐)
    - [1. 生成配置模板](#1-生成配置模板)
    - [2. 编辑配置文件](#2-编辑配置文件)
    - [3. 获取授权码/应用密码](#3-获取授权码应用密码)
    - [4. 测试邮件发送](#4-测试邮件发送)
    - [5. 使用 errmail 运行你的指令](#5-使用-errmail-运行你的指令)
  - [方式二：使用环境变量](#方式二使用环境变量)
  - [方式三：系统级配置（可选）](#方式三系统级配置可选)
- [命令行参数](#命令行参数)
  - [errmail init](#errmail-init)
  - [errmail test](#errmail-test)
  - [errmail run](#errmail-run)
- [行为说明](#行为说明)
- [配置文件详细说明](#配置文件详细说明)
- [SMTP 配置指南](#smtp-配置指南)
  - [通用规则](#通用规则)
  - [快速开始](#快速开始-1)
- [常见问题](#常见问题)

---

## errmail 是什么

`errmail` 是一个**不侵入业务代码**的命令行工具：你用它来启动后端服务（或任何命令），它会在**不影响程序正常输出**的前提下监听 `stderr`，一旦检测到疑似报错（例如 Python Traceback / Exception / ERROR），就给你配置的邮箱发提醒。

## 适用场景

- **后端服务**：例如 `uvicorn` / `gunicorn` / `python app.py` / 任意二进制
- **你只关心"命令行报错"**：不想改业务代码、不想引入 SDK

## 安装

### 方式一：通过 pip 从 Git 仓库安装（推荐）

最简单的方式，无需 clone 源码：

```bash
pip install git+https://github.com/bhsh0112/Errmail.git
```

或者指定分支/标签：

```bash
pip install git+https://github.com/bhsh0112/Errmail.git@main
```

如果仓库是私有的，可以使用 SSH：

```bash
pip install git+ssh://git@github.com/your-username/Errmail.git
```

### 方式二：本地开发安装

如果你已经 clone 了源码，可以在开发模式下安装：

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -U pip
python -m pip install -e .
```

如果你的环境较老、`pip install -e .` 提示 PEP660 editable 不支持，可以用兼容模式：

```bash
python -m pip install -e . --no-use-pep517
```

### 方式三：不安装直接运行

你也可以**不安装**，直接运行：

```bash
python -m errmail run -- python -c "raise RuntimeError('boom')"
```

> **注意**：如果项目已发布到 PyPI，你也可以直接使用 `pip install errmail` 安装。

## 快速开始

### 方式一：使用配置文件（推荐）

配置文件是最简单、最安全的方式。配置文件是一个简单的文本文件，格式为 `KEY=VALUE`，每行一个配置项。

#### 1. 生成配置模板

首先，生成一个配置模板文件：

```bash
errmail init
```

这个命令会在你的用户目录下创建 `~/.errmail.env` 文件（Windows 下是 `C:\Users\你的用户名\.errmail.env`）。

**使用预设邮箱配置（推荐）**：

如果你使用的是常见邮箱服务，可以使用 `--provider` 参数自动填充大部分配置：

```bash
# Gmail / Google Workspace
errmail init --provider gmail

# Outlook / Office 365
errmail init --provider outlook

# QQ 邮箱
errmail init --provider qq

# 163 邮箱
errmail init --provider 163

# 126 邮箱
errmail init --provider 126

# 自定义邮箱（默认）
errmail init --provider custom
```

使用预设配置后，你只需要填写邮箱地址和授权码即可，其他参数已经自动配置好了。

**查看配置模板内容**：

如果你想先查看模板内容而不写入文件，可以使用：

```bash
errmail init --print
```

#### 2. 编辑配置文件

打开生成的配置文件（`~/.errmail.env`），你会看到类似这样的内容：

```bash
# errmail config template (KEY=VALUE)
# SMTP server settings
ERRMAIL_SMTP_HOST=smtp.gmail.com
ERRMAIL_SMTP_PORT=587
ERRMAIL_SMTP_TLS=1
ERRMAIL_SMTP_SSL=0
ERRMAIL_SMTP_USER=your_account@gmail.com
ERRMAIL_SMTP_PASS=YOUR_APP_PASSWORD_OR_AUTH_CODE

# Mail settings
ERRMAIL_MAIL_FROM=your_account@gmail.com
# ERRMAIL_MAIL_TO=user@example.com

# Optional
ERRMAIL_COOLDOWN_SECONDS=300
ERRMAIL_TAIL_LINES=200
ERRMAIL_SERVICE=unknown-service
```

**必须修改的配置项**：

1. **`ERRMAIL_SMTP_USER`**：你的邮箱地址
   - 例如：`ERRMAIL_SMTP_USER=your_email@gmail.com`

2. **`ERRMAIL_SMTP_PASS`**：SMTP 授权码或应用专用密码
   - ⚠️ **重要**：这不是你的邮箱登录密码！
   - 需要根据你的邮箱服务商生成授权码（详见下方"如何获取授权码"章节）
   - 例如：`ERRMAIL_SMTP_PASS=abcd efgh ijkl mnop`

3. **`ERRMAIL_MAIL_FROM`**：发件人邮箱（通常与 `ERRMAIL_SMTP_USER` 相同）
   - 例如：`ERRMAIL_MAIL_FROM=your_email@gmail.com`

**可选修改的配置项**：

- **`ERRMAIL_MAIL_TO`**：默认收件人邮箱（可以在运行时用 `--to` 参数覆盖）
- **`ERRMAIL_SERVICE`**：服务名称，会显示在邮件主题中
- **`ERRMAIL_COOLDOWN_SECONDS`**：相同错误的冷却时间（秒），防止重复发送
- **`ERRMAIL_TAIL_LINES`**：邮件中包含的错误日志行数

**配置文件位置说明**：

- **用户级配置**：`~/.errmail.env`（默认位置）
  - Linux/Mac: `/home/用户名/.errmail.env`
  - Windows: `C:\Users\用户名\.errmail.env`
- **系统级配置**：`/etc/errmail.env`（需要管理员权限）
- **自定义位置**：通过环境变量 `ERRMAIL_CONFIG_FILE` 指定

#### 3. 获取授权码/应用密码

**为什么需要授权码？**

现代邮箱服务商为了安全，不允许直接使用登录密码通过 SMTP 发送邮件。你需要生成一个专门的"授权码"或"应用专用密码"。

**各邮箱获取授权码的方法**：

详见下方"📧 如何获取各邮箱授权码"章节。

#### 4. 测试邮件发送

配置完成后，先测试一下邮件是否能正常发送：

```bash
errmail test --to your_email@example.com --verbose
```

- `--to`：指定测试邮件的收件人（可以是你自己的邮箱）
- `--verbose`：显示详细的调试信息，方便排查问题

如果看到类似 `✓ Email sent successfully` 的提示，说明配置成功！

**常见错误排查**：

- 如果提示 `SMTP authentication failed`：检查 `ERRMAIL_SMTP_USER` 和 `ERRMAIL_SMTP_PASS` 是否正确
- 如果提示 `Connection refused`：检查 `ERRMAIL_SMTP_HOST` 和 `ERRMAIL_SMTP_PORT` 是否正确
- 如果提示 `SSL/TLS error`：检查 `ERRMAIL_SMTP_TLS` 和 `ERRMAIL_SMTP_SSL` 的设置是否与端口匹配

#### 5. 使用 errmail 运行你的指令

配置测试成功后，就可以开始使用了：

```bash
# 运行你的服务，错误会自动发邮件
errmail run --to your_email@example.com -- python -m uvicorn app:app --port 8000

# 或者运行任意命令
errmail run --to your_email@example.com -- python your_script.py

# 如果配置文件中已经设置了 ERRMAIL_MAIL_TO，可以省略 --to
errmail run -- python your_script.py
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
errmail run --to user@example.com -- <command>
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

## 配置文件详细说明

配置文件是一个简单的文本文件，采用 `KEY=VALUE` 格式，每行一个配置项。以 `#` 开头的行为注释，会被忽略。

**快速参考**：

- **必须配置**：`ERRMAIL_SMTP_HOST`, `ERRMAIL_SMTP_PORT`, `ERRMAIL_SMTP_USER`, `ERRMAIL_SMTP_PASS`, `ERRMAIL_MAIL_FROM`
- **推荐配置**：`ERRMAIL_MAIL_TO`（或运行时使用 `--to` 参数）
- **可选配置**：`ERRMAIL_SERVICE`, `ERRMAIL_COOLDOWN_SECONDS`, `ERRMAIL_TAIL_LINES`

📖 **详细配置说明请查看**：[配置文件详细说明](docs/CONFIGURATION.md)

## SMTP 配置指南

### 通用规则

- **推荐使用 587 + STARTTLS**：`ERRMAIL_SMTP_PORT=587` 且 `ERRMAIL_SMTP_TLS=1`
- **如果使用 465 端口（SSL）**：设置 `ERRMAIL_SMTP_PORT=465`、`ERRMAIL_SMTP_SSL=1` 且 `ERRMAIL_SMTP_TLS=0`
- **使用授权码/应用专用密码**：不要使用网页登录密码
- **配置优先级**：命令行参数 > 环境变量 > 配置文件

### 快速开始

使用预设邮箱配置可以快速生成配置模板：

```bash
errmail init --provider gmail    # Gmail / Google Workspace
errmail init --provider outlook  # Outlook / Office 365
errmail init --provider qq       # QQ 邮箱
errmail init --provider 163     # 163 邮箱
errmail init --provider 126     # 126 邮箱
```

📖 **详细配置指南请查看**：[SMTP 配置指南](docs/SMTP_SETUP.md) - 包含各邮箱授权码获取的详细步骤

🔧 **遇到问题？**：[常见配置问题排查](docs/TROUBLESHOOTING.md)

## 常见问题

- **为什么不用解析 exit code？**  
  会用，但不够：有些程序会把错误打印到 `stderr` 后继续跑，所以我们是"stderr 触发 + exit code 兜底"的组合。
