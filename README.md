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
  - [配置文件格式示例](#配置文件格式示例)
  - [配置项详细说明](#配置项详细说明)
    - [SMTP 服务器设置（必填）](#smtp-服务器设置必填)
    - [邮件设置](#邮件设置)
    - [可选设置](#可选设置)
- [SMTP 配置指南](#smtp-配置指南)
  - [通用规则](#通用规则)
  - [📧 如何获取各邮箱授权码](#-如何获取各邮箱授权码)
    - [Gmail / Google Workspace](#gmail--google-workspace)
    - [QQ 邮箱](#qq-邮箱)
    - [163 邮箱](#163-邮箱)
    - [126 邮箱](#126-邮箱)
    - [Outlook / Office 365](#outlook--office-365)
    - [其他邮箱服务商](#其他邮箱服务商)
  - [安全提醒](#安全提醒)
  - [🔧 常见配置问题排查](#-常见配置问题排查)
    - [问题 1：`SMTP authentication failed`（SMTP 认证失败）](#问题-1smtp-authentication-failedsmtp-认证失败)
    - [问题 2：`Connection refused` 或 `Connection timeout`（连接被拒绝/超时）](#问题-2connection-refused-或-connection-timeout连接被拒绝超时)
    - [问题 3：`SSL/TLS error`（SSL/TLS 错误）](#问题-3ssltls-errorssltls-错误)
    - [问题 4：`535 Error: authentication failed`（Gmail 特有）](#问题-4535-error-authentication-failedgmail-特有)
    - [问题 5：配置文件找不到](#问题-5配置文件找不到)
    - [问题 6：测试邮件发送成功，但运行时没有收到邮件](#问题-6测试邮件发送成功但运行时没有收到邮件)
    - [问题 7：授权码包含空格或特殊字符](#问题-7授权码包含空格或特殊字符)
    - [调试技巧](#调试技巧)
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

### 配置文件格式示例

```bash
# 这是一个完整的配置示例
# SMTP 服务器设置
ERRMAIL_SMTP_HOST=smtp.gmail.com
ERRMAIL_SMTP_PORT=587
ERRMAIL_SMTP_TLS=1
ERRMAIL_SMTP_SSL=0
ERRMAIL_SMTP_USER=your_email@gmail.com
ERRMAIL_SMTP_PASS=your_app_password_here

# 邮件设置
ERRMAIL_MAIL_FROM=your_email@gmail.com
ERRMAIL_MAIL_TO=recipient@example.com

# 可选设置
ERRMAIL_SERVICE=my-backend-service
ERRMAIL_COOLDOWN_SECONDS=300
ERRMAIL_TAIL_LINES=200
```

### 配置项详细说明

#### SMTP 服务器设置（必填）

这些配置项用于连接到你的邮箱 SMTP 服务器。

| 配置项 | 说明 | 示例 | 必填 |
|--------|------|------|------|
| `ERRMAIL_SMTP_HOST` | SMTP 服务器地址 | `smtp.gmail.com` | ✅ |
| `ERRMAIL_SMTP_PORT` | SMTP 端口号 | `587` 或 `465` | ✅ |
| `ERRMAIL_SMTP_USER` | SMTP 用户名（通常是你的邮箱地址） | `your_email@gmail.com` | ✅ |
| `ERRMAIL_SMTP_PASS` | SMTP 密码（授权码/应用专用密码） | `abcd efgh ijkl mnop` | ✅ |
| `ERRMAIL_SMTP_TLS` | 是否使用 STARTTLS（用于 587 端口） | `1` 或 `0` | ⚠️ |
| `ERRMAIL_SMTP_SSL` | 是否使用 SSL（用于 465 端口） | `1` 或 `0` | ⚠️ |

**端口和加密方式的选择**：

- **587 端口 + STARTTLS**（推荐）：
  ```bash
  ERRMAIL_SMTP_PORT=587
  ERRMAIL_SMTP_TLS=1
  ERRMAIL_SMTP_SSL=0
  ```
  这是最常用的配置，兼容性好，安全性高。

- **465 端口 + SSL**：
  ```bash
  ERRMAIL_SMTP_PORT=465
  ERRMAIL_SMTP_TLS=0
  ERRMAIL_SMTP_SSL=1
  ```
  某些邮箱服务商（如 QQ、163）推荐使用此配置。

**重要提示**：
- `ERRMAIL_SMTP_PASS` 不是你的邮箱登录密码！
- 必须使用邮箱服务商提供的"授权码"或"应用专用密码"
- 授权码通常是一串 16 位的字符（可能包含空格）

#### 邮件设置

| 配置项 | 说明 | 示例 | 必填 |
|--------|------|------|------|
| `ERRMAIL_MAIL_FROM` | 发件人邮箱地址 | `your_email@gmail.com` | ✅ |
| `ERRMAIL_MAIL_TO` | 默认收件人邮箱 | `recipient@example.com` | ⚠️ |

**说明**：
- `ERRMAIL_MAIL_FROM` 通常与 `ERRMAIL_SMTP_USER` 相同
- `ERRMAIL_MAIL_TO` 可以在运行时通过 `--to` 参数覆盖，所以不是必须的
- 如果配置文件中没有设置 `ERRMAIL_MAIL_TO`，运行时必须使用 `--to` 参数

#### 可选设置

这些配置项有默认值，通常不需要修改。

| 配置项 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `ERRMAIL_SERVICE` | 服务名称，会显示在邮件主题中 | `unknown-service` | `my-backend-api` |
| `ERRMAIL_COOLDOWN_SECONDS` | 相同错误的冷却时间（秒） | `300` | `600` |
| `ERRMAIL_TAIL_LINES` | 邮件中包含的错误日志行数 | `200` | `500` |

**详细说明**：

- **`ERRMAIL_SERVICE`**：
  - 用于标识不同的服务，会出现在邮件主题中
  - 例如：`[my-backend-api] Error detected`
  - 也可以在运行时通过 `--service` 参数覆盖

- **`ERRMAIL_COOLDOWN_SECONDS`**：
  - 防止相同错误重复发送邮件
  - 系统会根据错误内容生成一个"指纹"，相同指纹的错误在冷却时间内只会发送一次
  - 例如：设置为 `300` 表示 5 分钟内相同错误只发一次邮件

- **`ERRMAIL_TAIL_LINES`**：
  - 控制邮件中包含多少行错误日志
  - 从 stderr 的末尾开始截取
  - 如果错误日志很长，只会包含最后 N 行

## SMTP 配置指南

### 通用规则

- **推荐使用 587 + STARTTLS**：`ERRMAIL_SMTP_PORT=587` 且 `ERRMAIL_SMTP_TLS=1`
- **如果使用 465 端口（SSL）**：设置 `ERRMAIL_SMTP_PORT=465`、`ERRMAIL_SMTP_SSL=1` 且 `ERRMAIL_SMTP_TLS=0`
- **使用授权码/应用专用密码**：不要使用网页登录密码
- **配置优先级**：命令行参数 > 环境变量 > 配置文件

### 📧 如何获取各邮箱授权码

#### Gmail / Google Workspace

**步骤 1：开启两步验证**

1. 访问 [Google 账户安全设置](https://myaccount.google.com/security)
2. 在"登录 Google"部分，点击"两步验证"
3. 按照提示完成两步验证设置（需要手机验证）

**步骤 2：生成应用专用密码**

1. 在"两步验证"页面，找到"应用专用密码"选项
2. 点击"应用专用密码"
3. 选择"邮件"和设备类型（例如"其他"）
4. 输入应用名称（例如"errmail"）
5. 点击"生成"
6. **复制生成的 16 位密码**（格式类似：`abcd efgh ijkl mnop`）

**步骤 3：配置 errmail**

```bash
# 生成 Gmail 配置模板
errmail init --provider gmail
```

然后编辑 `~/.errmail.env`：

```bash
ERRMAIL_SMTP_HOST=smtp.gmail.com
ERRMAIL_SMTP_PORT=587
ERRMAIL_SMTP_TLS=1
ERRMAIL_SMTP_SSL=0
ERRMAIL_SMTP_USER=your_email@gmail.com
ERRMAIL_SMTP_PASS=abcd efgh ijkl mnop  # 这里填入刚才生成的应用专用密码
ERRMAIL_MAIL_FROM=your_email@gmail.com
```

**注意事项**：
- 如果使用 Google Workspace（企业邮箱），可能需要管理员开启"安全性较低的应用的访问权限"
- 应用专用密码可以包含空格，复制时注意保留

---

#### QQ 邮箱

**步骤 1：开启 SMTP 服务**

1. 登录 QQ 邮箱网页版
2. 点击右上角"设置" → "账户"
3. 找到"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
4. 开启"POP3/SMTP服务"或"IMAP/SMTP服务"
5. 按照提示发送短信验证
6. 验证成功后，会显示"授权码"（一串 16 位的字符）

**步骤 2：配置 errmail**

```bash
# 生成 QQ 邮箱配置模板
errmail init --provider qq
```

然后编辑 `~/.errmail.env`：

```bash
ERRMAIL_SMTP_HOST=smtp.qq.com
ERRMAIL_SMTP_PORT=465
ERRMAIL_SMTP_TLS=0
ERRMAIL_SMTP_SSL=1
ERRMAIL_SMTP_USER=your_qq@qq.com
ERRMAIL_SMTP_PASS=your_auth_code  # 这里填入刚才获取的授权码
ERRMAIL_MAIL_FROM=your_qq@qq.com
```

**注意事项**：
- QQ 邮箱推荐使用 465 端口 + SSL
- 授权码只显示一次，请妥善保存
- 如果忘记授权码，需要重新生成

---

#### 163 邮箱

**步骤 1：开启 SMTP 服务**

1. 登录 163 邮箱网页版
2. 点击右上角"设置" → "POP3/SMTP/IMAP"
3. 开启"POP3/SMTP服务"或"IMAP/SMTP服务"
4. 按照提示发送短信验证
5. 验证成功后，会显示"授权码"（一串 16 位的字符）

**步骤 2：配置 errmail**

```bash
# 生成 163 邮箱配置模板
errmail init --provider 163
```

然后编辑 `~/.errmail.env`：

```bash
ERRMAIL_SMTP_HOST=smtp.163.com
ERRMAIL_SMTP_PORT=465
ERRMAIL_SMTP_TLS=0
ERRMAIL_SMTP_SSL=1
ERRMAIL_SMTP_USER=your_email@163.com
ERRMAIL_SMTP_PASS=your_auth_code  # 这里填入刚才获取的授权码
ERRMAIL_MAIL_FROM=your_email@163.com
```

**注意事项**：
- 163 邮箱推荐使用 465 端口 + SSL
- 授权码只显示一次，请妥善保存

---

#### 126 邮箱

**步骤 1：开启 SMTP 服务**

1. 登录 126 邮箱网页版
2. 点击右上角"设置" → "POP3/SMTP/IMAP"
3. 开启"POP3/SMTP服务"或"IMAP/SMTP服务"
4. 按照提示发送短信验证
5. 验证成功后，会显示"授权码"（一串 16 位的字符）

**步骤 2：配置 errmail**

```bash
# 生成 126 邮箱配置模板
errmail init --provider 126
```

然后编辑 `~/.errmail.env`：

```bash
ERRMAIL_SMTP_HOST=smtp.126.com
ERRMAIL_SMTP_PORT=465
ERRMAIL_SMTP_TLS=0
ERRMAIL_SMTP_SSL=1
ERRMAIL_SMTP_USER=your_email@126.com
ERRMAIL_SMTP_PASS=your_auth_code  # 这里填入刚才获取的授权码
ERRMAIL_MAIL_FROM=your_email@126.com
```

---

#### Outlook / Office 365

**步骤 1：开启两步验证**

1. 访问 [Microsoft 账户安全设置](https://account.microsoft.com/security)
2. 点击"高级安全选项"
3. 开启"两步验证"

**步骤 2：生成应用密码**

1. 在"高级安全选项"页面，找到"应用密码"
2. 点击"创建新的应用密码"
3. 输入应用名称（例如"errmail"）
4. 点击"下一步"
5. **复制生成的密码**（格式类似：`abcd-efgh-ijkl-mnop`）

**步骤 3：配置 errmail**

```bash
# 生成 Outlook 配置模板
errmail init --provider outlook
```

然后编辑 `~/.errmail.env`：

```bash
ERRMAIL_SMTP_HOST=smtp.office365.com
ERRMAIL_SMTP_PORT=587
ERRMAIL_SMTP_TLS=1
ERRMAIL_SMTP_SSL=0
ERRMAIL_SMTP_USER=your_email@outlook.com
ERRMAIL_SMTP_PASS=abcd-efgh-ijkl-mnop  # 这里填入刚才生成的应用密码
ERRMAIL_MAIL_FROM=your_email@outlook.com
```

**注意事项**：
- Office 365 企业邮箱可能需要管理员开启 SMTP 访问权限
- 应用密码可能包含连字符，复制时注意保留

---

#### 其他邮箱服务商

如果你使用的是其他邮箱服务商（如企业邮箱、自建邮箱等），可以：

1. 使用 `errmail init --provider custom` 生成自定义模板
2. 查阅你的邮箱服务商的 SMTP 配置文档
3. 通常需要的信息：
   - SMTP 服务器地址（例如：`smtp.example.com`）
   - SMTP 端口（通常是 587 或 465）
   - 是否需要 TLS/SSL
   - 如何获取授权码

**通用配置模板**：

```bash
# 587 端口 + STARTTLS（推荐）
ERRMAIL_SMTP_HOST=smtp.example.com
ERRMAIL_SMTP_PORT=587
ERRMAIL_SMTP_TLS=1
ERRMAIL_SMTP_SSL=0

# 或 465 端口 + SSL
ERRMAIL_SMTP_HOST=smtp.example.com
ERRMAIL_SMTP_PORT=465
ERRMAIL_SMTP_TLS=0
ERRMAIL_SMTP_SSL=1
```

### 安全提醒

- **不要把你的 SMTP 密码给别人**
- `~/.errmail.env` 里包含敏感信息，建议：
  - 给文件设权限（例如 `chmod 600 ~/.errmail.env`）
  - 不要提交到 git
  - 不要通过聊天工具、邮件等方式分享配置文件

### 🔧 常见配置问题排查

#### 问题 1：`SMTP authentication failed`（SMTP 认证失败）

**可能原因**：
- 用户名或密码错误
- 使用了登录密码而不是授权码
- 授权码已过期或被撤销

**解决方法**：
1. 确认 `ERRMAIL_SMTP_USER` 填写的是完整的邮箱地址
2. 确认 `ERRMAIL_SMTP_PASS` 使用的是授权码/应用专用密码，而不是登录密码
3. 重新生成授权码并更新配置
4. 使用 `errmail test --verbose` 查看详细错误信息

#### 问题 2：`Connection refused` 或 `Connection timeout`（连接被拒绝/超时）

**可能原因**：
- SMTP 服务器地址错误
- 端口号错误
- 网络防火墙阻止连接
- 邮箱服务商限制了 IP 访问

**解决方法**：
1. 检查 `ERRMAIL_SMTP_HOST` 是否正确（注意不要有多余的空格）
2. 检查 `ERRMAIL_SMTP_PORT` 是否与邮箱服务商文档一致
3. 尝试使用 `--verbose` 参数查看详细连接信息
4. 检查网络连接和防火墙设置
5. 某些企业邮箱可能需要 VPN 或特定网络环境

#### 问题 3：`SSL/TLS error`（SSL/TLS 错误）

**可能原因**：
- TLS/SSL 配置与端口不匹配
- 邮箱服务商不支持当前加密方式

**解决方法**：
1. **对于 587 端口**：
   ```bash
   ERRMAIL_SMTP_PORT=587
   ERRMAIL_SMTP_TLS=1
   ERRMAIL_SMTP_SSL=0
   ```

2. **对于 465 端口**：
   ```bash
   ERRMAIL_SMTP_PORT=465
   ERRMAIL_SMTP_TLS=0
   ERRMAIL_SMTP_SSL=1
   ```

3. 确认配置与邮箱服务商的文档一致

#### 问题 4：`535 Error: authentication failed`（Gmail 特有）

**可能原因**：
- 未开启两步验证
- 未生成应用专用密码
- Google 账户安全设置限制了访问

**解决方法**：
1. 确认已开启两步验证
2. 确认使用的是应用专用密码，而不是账户密码
3. 检查 Google 账户的"安全性较低的应用的访问权限"设置
4. 如果是 Google Workspace，可能需要管理员开启相关权限

#### 问题 5：配置文件找不到

**可能原因**：
- 配置文件路径错误
- 配置文件权限问题

**解决方法**：
1. 检查配置文件路径：
   - Linux/Mac: `~/.errmail.env` 或 `/home/用户名/.errmail.env`
   - Windows: `C:\Users\用户名\.errmail.env`
2. 使用 `errmail init --print` 查看默认路径
3. 使用 `--path` 参数指定自定义路径
4. 使用环境变量 `ERRMAIL_CONFIG_FILE` 指定配置文件位置

#### 问题 6：测试邮件发送成功，但运行时没有收到邮件

**可能原因**：
- 命令没有产生错误
- 错误被过滤了
- 冷却时间内重复错误

**解决方法**：
1. 使用 `--verbose` 参数查看详细日志
2. 确认命令确实产生了错误（检查 stderr 输出）
3. 检查 `ERRMAIL_COOLDOWN_SECONDS` 设置，可能相同错误在冷却期内
4. 尝试手动触发错误：`errmail run --to your@email.com -- python -c "raise RuntimeError('test')"`

#### 问题 7：授权码包含空格或特殊字符

**解决方法**：
- 授权码中的空格可以保留，直接复制粘贴到配置文件中
- 如果遇到问题，可以尝试去掉空格
- 某些邮箱的授权码可能包含连字符（如 Outlook），需要保留

#### 调试技巧

1. **使用 `--verbose` 参数**：
   ```bash
   errmail test --to your@email.com --verbose
   errmail run --to your@email.com --verbose -- python your_script.py
   ```
   这会显示详细的连接和发送过程，帮助定位问题。

2. **检查配置文件格式**：
   - 确保每行格式为 `KEY=VALUE`
   - 不要在 `=` 前后有多余空格（除非值是字符串的一部分）
   - 注释行以 `#` 开头
   - 确保没有语法错误

3. **验证配置项**：
   ```bash
   # 查看配置模板
   errmail init --print
   
   # 对比你的配置文件，确保格式正确
   ```

## 常见问题

- **为什么不用解析 exit code？**  
  会用，但不够：有些程序会把错误打印到 `stderr` 后继续跑，所以我们是"stderr 触发 + exit code 兜底"的组合。
