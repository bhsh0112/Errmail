# 常见配置问题排查

## 问题 1：`SMTP authentication failed`（SMTP 认证失败）

**可能原因**：
- 用户名或密码错误
- 使用了登录密码而不是授权码
- 授权码已过期或被撤销

**解决方法**：
1. 确认 `ERRMAIL_SMTP_USER` 填写的是完整的邮箱地址
2. 确认 `ERRMAIL_SMTP_PASS` 使用的是授权码/应用专用密码，而不是登录密码
3. 重新生成授权码并更新配置
4. 使用 `errmail test --verbose` 查看详细错误信息

---

## 问题 2：`Connection refused` 或 `Connection timeout`（连接被拒绝/超时）

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

---

## 问题 3：`SSL/TLS error`（SSL/TLS 错误）

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

---

## 问题 4：`535 Error: authentication failed`（Gmail 特有）

**可能原因**：
- 未开启两步验证
- 未生成应用专用密码
- Google 账户安全设置限制了访问

**解决方法**：
1. 确认已开启两步验证
2. 确认使用的是应用专用密码，而不是账户密码
3. 检查 Google 账户的"安全性较低的应用的访问权限"设置
4. 如果是 Google Workspace，可能需要管理员开启相关权限

---

## 问题 5：配置文件找不到

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

---

## 问题 6：测试邮件发送成功，但运行时没有收到邮件

**可能原因**：
- 命令没有产生错误
- 错误被过滤了
- 冷却时间内重复错误

**解决方法**：
1. 使用 `--verbose` 参数查看详细日志
2. 确认命令确实产生了错误（检查 stderr 输出）
3. 检查 `ERRMAIL_COOLDOWN_SECONDS` 设置，可能相同错误在冷却期内
4. 尝试手动触发错误：`errmail run --to your@email.com -- python -c "raise RuntimeError('test')"`

---

## 问题 7：授权码包含空格或特殊字符

**解决方法**：
- 授权码中的空格可以保留，直接复制粘贴到配置文件中
- 如果遇到问题，可以尝试去掉空格
- 某些邮箱的授权码可能包含连字符（如 Outlook），需要保留

---

## 调试技巧

### 1. 使用 `--verbose` 参数

```bash
errmail test --to your@email.com --verbose
errmail run --to your@email.com --verbose -- python your_script.py
```

这会显示详细的连接和发送过程，帮助定位问题。

### 2. 检查配置文件格式

- 确保每行格式为 `KEY=VALUE`
- 不要在 `=` 前后有多余空格（除非值是字符串的一部分）
- 注释行以 `#` 开头
- 确保没有语法错误

### 3. 验证配置项

```bash
# 查看配置模板
errmail init --print

# 对比你的配置文件，确保格式正确
```

### 4. 测试 SMTP 连接

使用 `errmail test` 命令测试配置：

```bash
# 基本测试
errmail test --to your@email.com

# 详细测试（显示调试信息）
errmail test --to your@email.com --verbose
```

### 5. 检查环境变量

确认环境变量是否正确设置：

```bash
# Linux/Mac
env | grep ERRMAIL

# Windows PowerShell
Get-ChildItem Env: | Where-Object Name -like "ERRMAIL*"
```

### 6. 查看日志输出

运行命令时使用 `--verbose` 参数，查看 errmail 的内部日志，这些日志会输出到 stderr，帮助你了解：
- SMTP 连接是否成功
- 邮件是否发送成功
- 错误检测是否正常工作

## 相关文档

- [配置文件详细说明](CONFIGURATION.md) - 完整的配置项说明
- [SMTP 配置指南](SMTP_SETUP.md) - 如何获取各邮箱的授权码

