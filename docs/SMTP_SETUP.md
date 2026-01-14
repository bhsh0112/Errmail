# SMTP 配置指南

## 通用规则

- **推荐使用 587 + STARTTLS**：`ERRMAIL_SMTP_PORT=587` 且 `ERRMAIL_SMTP_TLS=1`
- **如果使用 465 端口（SSL）**：设置 `ERRMAIL_SMTP_PORT=465`、`ERRMAIL_SMTP_SSL=1` 且 `ERRMAIL_SMTP_TLS=0`
- **使用授权码/应用专用密码**：不要使用网页登录密码
- **配置优先级**：命令行参数 > 环境变量 > 配置文件

## 📧 如何获取各邮箱授权码

### Gmail / Google Workspace

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

### QQ 邮箱

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

### 163 邮箱

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

### 126 邮箱

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

### Outlook / Office 365

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

### 其他邮箱服务商

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

## 安全提醒

- **不要把你的 SMTP 密码给别人**
- `~/.errmail.env` 里包含敏感信息，建议：
  - 给文件设权限（例如 `chmod 600 ~/.errmail.env`）
  - 不要提交到 git
  - 不要通过聊天工具、邮件等方式分享配置文件

## 相关文档

- [配置文件详细说明](CONFIGURATION.md) - 完整的配置项说明
- [常见配置问题排查](TROUBLESHOOTING.md) - 故障排除指南

