# 配置文件详细说明

配置文件是一个简单的文本文件，采用 `KEY=VALUE` 格式，每行一个配置项。以 `#` 开头的行为注释，会被忽略。

## 配置文件格式示例

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

## 配置项详细说明

### SMTP 服务器设置（必填）

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

### 邮件设置

| 配置项 | 说明 | 示例 | 必填 |
|--------|------|------|------|
| `ERRMAIL_MAIL_FROM` | 发件人邮箱地址 | `your_email@gmail.com` | ✅ |
| `ERRMAIL_MAIL_TO` | 默认收件人邮箱 | `recipient@example.com` | ⚠️ |

**说明**：
- `ERRMAIL_MAIL_FROM` 通常与 `ERRMAIL_SMTP_USER` 相同
- `ERRMAIL_MAIL_TO` 可以在运行时通过 `--to` 参数覆盖，所以不是必须的
- 如果配置文件中没有设置 `ERRMAIL_MAIL_TO`，运行时必须使用 `--to` 参数

### 可选设置

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

## 配置文件位置

- **用户级配置**：`~/.errmail.env`（默认位置）
  - Linux/Mac: `/home/用户名/.errmail.env`
  - Windows: `C:\Users\用户名\.errmail.env`
- **系统级配置**：`/etc/errmail.env`（需要管理员权限）
- **自定义位置**：通过环境变量 `ERRMAIL_CONFIG_FILE` 指定

## 配置优先级

配置项的优先级从高到低：
1. 命令行参数（如 `--to`, `--service`）
2. 环境变量
3. 配置文件（`~/.errmail.env` 或 `/etc/errmail.env`）

## 相关文档

- [SMTP 配置指南](SMTP_SETUP.md) - 如何获取各邮箱的授权码
- [常见配置问题排查](TROUBLESHOOTING.md) - 故障排除指南

