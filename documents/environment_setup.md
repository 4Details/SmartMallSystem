# 环境变量设置指南

本文档介绍如何设置和管理积分商城系统的环境变量。

## 环境变量概述

环境变量是应用程序配置的关键部分，它们允许我们在不修改代码的情况下更改应用程序的行为。在不同的环境（开发、测试、生产）中，我们可以使用不同的环境变量值。

## .env 文件

我们使用 `.env` 文件来存储本地开发环境的环境变量。这个文件不应该提交到版本控制系统（如Git），因为它可能包含敏感信息（如密钥和密码）。

## 环境变量列表

以下是应用程序使用的主要环境变量：

### Flask 应用配置

- `FLASK_APP`: 指定Flask应用的入口文件，默认为 `app.py`
- `FLASK_ENV`: 应用程序的运行环境，可以是 `development` 或 `production`
- `FLASK_DEBUG`: 是否启用调试模式，`1` 表示启用，`0` 表示禁用

### 数据库配置

- `DATABASE_URL`: 数据库连接URL
  - SQLite示例: `sqlite:///smart_mall.db`
  - PostgreSQL示例: `postgresql://username:password@localhost/dbname`
  - MySQL示例: `mysql://username:password@localhost/dbname`
- `SQLALCHEMY_TRACK_MODIFICATIONS`: 是否跟踪模型修改，建议设置为 `False` 以提高性能

### 安全配置

- `SECRET_KEY`: Flask应用的密钥，用于加密会话数据
- `JWT_SECRET_KEY`: JWT（JSON Web Token）的密钥
- `JWT_ACCESS_TOKEN_EXPIRES`: JWT令牌的过期时间（秒）

### 应用特定配置

- `POINTS_EXPIRATION_DAYS`: 积分的有效期（天）
- `DEFAULT_PAGE_SIZE`: API返回列表数据时的默认分页大小
- `UPLOAD_FOLDER`: 文件上传目录
- `MAX_CONTENT_LENGTH`: 最大上传文件大小（字节）

### 日志配置

- `LOG_LEVEL`: 日志级别，可以是 `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- `LOG_FILE`: 日志文件路径

### 邮件配置

- `MAIL_SERVER`: SMTP服务器地址
- `MAIL_PORT`: SMTP服务器端口
- `MAIL_USE_TLS`: 是否使用TLS加密
- `MAIL_USERNAME`: 邮箱用户名
- `MAIL_PASSWORD`: 邮箱密码

### Redis配置

- `REDIS_URL`: Redis服务器的连接URL，用于缓存和会话存储

### 跨域配置

- `CORS_ALLOWED_ORIGINS`: 允许跨域请求的源，多个源用逗号分隔

## 如何设置环境变量

### 本地开发

1. 复制 `.env.example` 文件（如果存在）到 `.env`：
   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，设置适当的值。

### 生产环境

在生产环境中，应该使用服务器的环境变量管理系统设置环境变量，而不是使用 `.env` 文件。

#### Linux/Unix

```bash
export SECRET_KEY="your-secret-key"
export DATABASE_URL="your-database-url"
```

#### Windows

```cmd
set SECRET_KEY=your-secret-key
set DATABASE_URL=your-database-url
```

#### Docker

在 `docker-compose.yml` 文件中：

```yaml
services:
  web:
    environment:
      - SECRET_KEY=your-secret-key
      - DATABASE_URL=your-database-url
```

或者使用 `.env` 文件：

```yaml
services:
  web:
    env_file:
      - .env.production
```

## 生成安全密钥

为了安全起见，`SECRET_KEY` 和 `JWT_SECRET_KEY` 应该是随机生成的复杂字符串。您可以使用以下Python命令生成安全的随机密钥：

```python
import secrets
print(secrets.token_hex(32))  # 生成一个64字符的十六进制字符串
```

## 环境变量的使用

在Python代码中，您可以使用 `os.environ` 或 `python-dotenv` 库来访问环境变量：

```python
import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# 获取环境变量值，如果不存在则使用默认值
secret_key = os.environ.get('SECRET_KEY', 'default-secret-key')
```

## 环境变量最佳实践

1. **不要在版本控制中提交敏感信息**：
   - 将 `.env` 文件添加到 `.gitignore`
   - 提供一个 `.env.example` 文件作为模板，但不包含实际值

2. **使用不同的环境配置**：
   - `.env.development` 用于开发环境
   - `.env.test` 用于测试环境
   - `.env.production` 用于生产环境

3. **限制访问权限**：
   - 在生产服务器上，确保只有需要访问的进程和用户可以读取环境变量

4. **定期轮换密钥**：
   - 定期更改 `SECRET_KEY`, `JWT_SECRET_KEY` 和其他敏感信息

5. **记录所有环境变量**：
   - 确保所有环境变量都有文档说明其用途和预期值