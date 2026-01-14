# Errmail 测试使用说明

## 快速测试

### 方法 1: 使用 test_error.py 脚本

这个脚本包含了多种错误类型，可以用来测试 errmail 的邮件通知功能。

#### 测试 RuntimeError（默认）
```powershell
python -m errmail run --to bhsh0112@163.com --verbose -- python test_error.py
```

#### 测试其他错误类型
```powershell
# ValueError
python -m errmail run --to bhsh0112@163.com --verbose -- python test_error.py value

# FileNotFoundError
python -m errmail run --to bhsh0112@163.com --verbose -- python test_error.py file

# ZeroDivisionError
python -m errmail run --to bhsh0112@163.com --verbose -- python test_error.py zero
```

### 方法 2: 使用一行命令（最简单）

```powershell
# 触发 RuntimeError
python -m errmail run --to bhsh0112@163.com --verbose -- python -c "raise RuntimeError('测试错误')"

# 触发 ValueError
python -m errmail run --to bhsh0112@163.com --verbose -- python -c "int('not_a_number')"

# 触发 ZeroDivisionError
python -m errmail run --to bhsh0112@163.com --verbose -- python -c "10/0"
```

### 方法 3: 使用测试服务脚本（模拟实际服务）

```powershell
python -m errmail run --to bhsh0112@163.com --verbose -- python test_service.py
```

## 参数说明

- `--to`: 指定收件人邮箱（覆盖配置文件中的 ERRMAIL_MAIL_TO）
- `--verbose`: 显示 errmail 的内部日志
- `--`: 分隔符，后面的命令是被监控的命令

## 注意事项

1. **防刷屏机制**: errmail 有冷却时间（默认 300 秒），相同类型的错误在冷却时间内只会发送一次邮件
2. **后台发送**: 邮件在后台线程发送，不会阻塞命令执行
3. **输出不变**: stdout/stderr 的输出仍然会正常显示在终端

## 测试结果

运行测试后，你应该会：
1. 在终端看到错误信息（stderr 输出）
2. 收到邮件通知（如果配置正确）

检查你的邮箱（bhsh0112@163.com）查看是否收到错误通知邮件。

