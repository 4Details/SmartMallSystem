#!/bin/bash
# 设置积分商城系统环境脚本

echo "开始设置积分商城系统环境..."

# 清理 Python 缓存文件
echo "清理 Python 缓存文件..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -delete

# 检查 Python 是否安装
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "错误: 未找到 Python。请安装 Python 3.6 或更高版本。"
    exit 1
fi

echo "使用 Python: $($PYTHON_CMD --version)"

# 创建虚拟环境
echo "创建虚拟环境..."
$PYTHON_CMD -m venv venv

# 激活虚拟环境
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "激活虚拟环境 (Unix/Linux/MacOS)..."
    source venv/bin/activate
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "激活虚拟环境 (Windows)..."
    source venv/Scripts/activate
else
    echo "无法确定操作系统类型。请手动激活虚拟环境。"
    exit 1
fi

# 安装依赖
echo "安装项目依赖..."
pip install --upgrade pip

# 先卸载可能有冲突的包
echo "处理可能的依赖冲突..."
pip uninstall -y sqlalchemy flask-sqlalchemy werkzeug alembic flask-migrate || true

# 安装指定版本的依赖
echo "安装指定版本的依赖..."
pip install -r requirements.txt

# 复制环境变量文件
if [ ! -f .env ]; then
    echo "创建 .env 文件..."
    cp .env.example .env

    # 生成随机密钥
    echo "生成随机密钥..."
    SECRET_KEY=$($PYTHON_CMD -c "import secrets; print(secrets.token_hex(32))")
    JWT_SECRET_KEY=$($PYTHON_CMD -c "import secrets; print(secrets.token_hex(32))")

    # 更新 .env 文件中的密钥
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # MacOS
        sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
        sed -i '' "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$JWT_SECRET_KEY/" .env
    else
        # Linux 和 Windows
        sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
        sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$JWT_SECRET_KEY/" .env
    fi
fi

# 初始化数据库
echo "初始化数据库..."
if [ -d "migrations" ]; then
    echo "检测到现有的migrations文件夹，正在删除..."
    rm -rf migrations
fi

if [ -f "app/smart_mall.db" ]; then
    echo "检测到现有的数据库文件，正在删除..."
    rm app/smart_mall.db
fi

flask db init
if [ $? -ne 0 ]; then
    echo "数据库初始化失败，请检查错误信息。"
    exit 1
fi

flask db migrate -m "Initial migration"
if [ $? -ne 0 ]; then
    echo "数据库迁移失败，请检查错误信息。"
    exit 1
fi

flask db upgrade
if [ $? -ne 0 ]; then
    echo "数据库升级失败，请检查错误信息。"
    exit 1
fi

$PYTHON_CMD init_db.py
if [ $? -ne 0 ]; then
    echo "数据库初始化脚本运行失败，请检查错误信息。"
    exit 1
fi

echo "设置完成！你可以使用以下命令运行应用："
echo "flask run"