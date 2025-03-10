# Smart Mall System

积分商城系统后端API实现，基于Flask和SQLAlchemy。

## 功能模块

本项目实现了以下核心模块：

1. **用户管理**
   - 用户注册与登录
   - 用户信息管理
   - 会员等级系统

2. **积分管理**
   - 积分获取与消费
   - 积分交易记录
   - 积分过期管理
   - 积分转账功能

3. **商品管理**
   - 商品信息管理
   - 商品分类与搜索
   - 商品库存管理
   - 商品促销活动

## 技术栈

- **后端框架**：Flask
- **ORM**：SQLAlchemy
- **认证**：JWT (JSON Web Token)
- **数据库迁移**：Flask-Migrate
- **API设计**：RESTful API

## 项目结构

```
SmartMallSystem/
├── app/                      # 应用主目录
│   ├── models/               # 数据模型
│   ├── routes/               # API路由
│   ├── services/             # 业务逻辑服务
│   ├── utils/                # 工具类和辅助函数
│   └── __init__.py           # 应用工厂函数
├── migrations/               # 数据库迁移文件
├── tests/                    # 测试代码
├── app.py                    # 应用入口
├── init_db.py                # 数据库初始化脚本
├── requirements.txt          # 项目依赖
└── .env                      # 环境变量配置
```

## 安装与运行

### 方法 1：使用自动化脚本（推荐）

1. **克隆项目**

```bash
git clone <repository-url>
cd SmartMallSystem
```

2. **运行设置脚本**

对于 Linux/macOS 用户：
```bash
# 确保脚本有执行权限
chmod +x setup.sh
# 运行脚本
./setup.sh
```

对于 Windows 用户：
```powershell
# 在 PowerShell 中运行
.\setup.ps1
```

这个脚本会自动完成以下任务：
- 创建并激活虚拟环境
- 安装项目依赖
- 创建并配置 `.env` 文件
- 初始化数据库

3. **运行应用**

```bash
flask run
```

注意：如果你在运行脚本时遇到任何问题，请参考下面的故障排除部分。

### 方法 2：手动设置

如果你更喜欢手动控制每一步，可以按照以下步骤操作：

1. **克隆项目**

```bash
git clone <repository-url>
cd SmartMallSystem
```

2. **创建虚拟环境**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或者
venv\Scripts\activate  # Windows
```

3. **安装依赖**

```bash
pip install -r requirements.txt
```

4. **配置环境变量**

复制 `.env.example` 文件并重命名为 `.env`，然后根据你的需求修改其中的值：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置必要的环境变量。特别注意以下变量：

- `SECRET_KEY`: 设置为一个复杂的随机字符串
- `JWT_SECRET_KEY`: 设置为另一个复杂的随机字符串
- `DATABASE_URL`: 根据你的数据库设置修改

可以使用以下Python命令生成安全的随机密钥：

```python
import secrets
print(secrets.token_hex(32))
```

5. **初始化数据库**

```bash
flask db init
flask db migrate
flask db upgrade
python init_db.py
```

6. **运行应用**

```bash
flask run
```

无论使用哪种方法，应用都将在 http://127.0.0.1:5000/ 运行。

## 环境变量

详细的环境变量说明请参考 `documents/environment_setup.md` 文件。

主要的环境变量包括：

- `FLASK_APP`: Flask应用入口文件
- `FLASK_ENV`: 运行环境（development/production）
- `DATABASE_URL`: 数据库连接URL
- `SECRET_KEY`: Flask应用密钥
- `JWT_SECRET_KEY`: JWT密钥
- `CORS_ALLOWED_ORIGINS`: 允许的跨域请求源

确保在生产环境中使用安全的随机值作为密钥，并妥善保管这些敏感信息。

## API 文档

### 用户管理

- `POST /api/users/register` - 注册新用户
- `POST /api/users/login` - 用户登录
- `GET /api/users/profile` - 获取用户个人信息
- `PUT /api/users/profile` - 更新用户个人信息
- `POST /api/users/change-password` - 修改密码

### 积分管理

- `GET /api/points/balance` - 获取积分余额
- `GET /api/points/summary` - 获取积分汇总信息
- `GET /api/points/transactions` - 获取积分交易记录
- `POST /api/points/transfer` - 积分转账

### 商品管理

- `GET /api/products` - 获取商品列表
- `GET /api/products/<product_id>` - 获取商品详情
- `GET /api/products/categories` - 获取商品分类
- `GET /api/products/<product_id>/price` - 获取商品价格信息

### 管理员接口

- `POST /api/points/admin/add` - 为用户添加积分
- `POST /api/points/admin/deduct` - 从用户扣除积分
- `POST /api/points/admin/expire` - 过期积分处理
- `POST /api/products` - 创建新商品
- `PUT /api/products/<product_id>` - 更新商品信息
- `PUT /api/products/<product_id>/stock` - 更新商品库存
- `PUT /api/products/<product_id>/activate` - 激活商品
- `PUT /api/products/<product_id>/deactivate` - 停用商品

## 后续开发计划

1. 实现订单管理模块
2. 实现物流管理模块
3. 添加数据分析和报表功能
4. 实现通知系统
5. 增加单元测试和集成测试

## 故障排除

### 使用修复脚本（推荐）

我们提供了一个专门的修复脚本，可以自动解决常见的依赖问题：

```bash
python fix_dependencies.py
```

运行此脚本后，按照提示选择要修复的问题。这是解决依赖冲突最简单的方法。

### 常见错误及手动解决方法

#### ImportError: cannot import name 'url_quote' from 'werkzeug.urls'

如果在运行数据库初始化命令时遇到此错误，请尝试以下步骤：

1. 确保你使用的是兼容的 Flask 和 Werkzeug 版本。你可以在 `requirements.txt` 文件中查看指定的版本。

2. 重新安装项目依赖：

   ```bash
   pip install -r requirements.txt --upgrade
   ```

3. 如果问题仍然存在，可能需要清除并重新创建虚拟环境：

   ```bash
   deactivate  # 如果当前在虚拟环境中
   rm -rf venv  # 删除旧的虚拟环境
   python -m venv venv  # 创建新的虚拟环境
   source venv/bin/activate  # 在 Linux/Mac 上激活虚拟环境
   # 或
   venv\Scripts\activate  # 在 Windows 上激活虚拟环境
   pip install -r requirements.txt  # 重新安装依赖
   ```

#### AttributeError: module 'sqlalchemy' has no attribute '__all__'

如果遇到这个错误，通常是因为 SQLAlchemy 版本与 Flask-SQLAlchemy 不兼容。请按照以下步骤解决：

1. 确保 `requirements.txt` 文件中指定了兼容的 SQLAlchemy 版本。

2. 重新安装项目依赖：

   ```bash
   pip install -r requirements.txt --upgrade
   ```

3. 如果问题仍然存在，尝试卸载当前的 SQLAlchemy 和 Flask-SQLAlchemy，然后重新安装：

   ```bash
   pip uninstall -y sqlalchemy flask-sqlalchemy
   pip install SQLAlchemy==1.4.46
   pip install Flask-SQLAlchemy==2.5.1
   pip install -r requirements.txt
   ```

### 其他依赖问题

如果遇到其他依赖相关的问题，请尝试以下通用步骤：

1. 确保使用的是最新的 `requirements.txt` 文件。

2. 尝试在干净的虚拟环境中重新安装所有依赖：

   ```bash
   deactivate  # 如果当前在虚拟环境中
   rm -rf venv
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate  # Windows
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. 如果特定包持续出现问题，尝试先单独安装该包的兼容版本，然后再安装其他依赖。