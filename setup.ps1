# 设置积分商城系统环境脚本 (Windows PowerShell)

Write-Host "开始设置积分商城系统环境..." -ForegroundColor Green

# 检查 Python 是否安装
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
} else {
    Write-Host "错误: 未找到 Python。请安装 Python 3.6 或更高版本。" -ForegroundColor Red
    exit 1
}

Write-Host "使用 Python: $(&$pythonCmd --version)" -ForegroundColor Cyan

# 创建虚拟环境
Write-Host "创建虚拟环境..." -ForegroundColor Cyan
&$pythonCmd -m venv venv

# 激活虚拟环境
Write-Host "激活虚拟环境..." -ForegroundColor Cyan
.\venv\Scripts\Activate.ps1

# 安装依赖
Write-Host "安装项目依赖..." -ForegroundColor Cyan
pip install --upgrade pip

# 先卸载可能有冲突的包
Write-Host "处理可能的依赖冲突..." -ForegroundColor Cyan
pip uninstall -y sqlalchemy flask-sqlalchemy werkzeug alembic flask-migrate

# 安装指定版本的依赖
Write-Host "安装指定版本的依赖..." -ForegroundColor Cyan
pip install -r requirements.txt

# 复制环境变量文件
if (-not (Test-Path .env)) {
    Write-Host "创建 .env 文件..." -ForegroundColor Cyan
    Copy-Item .env.example .env

    # 生成随机密钥
    Write-Host "生成随机密钥..." -ForegroundColor Cyan
    $secretKey = &$pythonCmd -c "import secrets; print(secrets.token_hex(32))"
    $jwtSecretKey = &$pythonCmd -c "import secrets; print(secrets.token_hex(32))"

    # 更新 .env 文件中的密钥
    (Get-Content .env) -replace "SECRET_KEY=.*", "SECRET_KEY=$secretKey" | Set-Content .env
    (Get-Content .env) -replace "JWT_SECRET_KEY=.*", "JWT_SECRET_KEY=$jwtSecretKey" | Set-Content .env
}

# 初始化数据库
Write-Host "初始化数据库..." -ForegroundColor Cyan

if (Test-Path "migrations") {
    Write-Host "检测到现有的migrations文件夹，正在删除..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force migrations
}

if (Test-Path "app\smart_mall.db") {
    Write-Host "检测到现有的数据库文件，正在删除..." -ForegroundColor Yellow
    Remove-Item -Force app\smart_mall.db
}

flask db init
if ($LASTEXITCODE -ne 0) {
    Write-Host "数据库初始化失败，请检查错误信息。" -ForegroundColor Red
    exit 1
}

flask db migrate -m "Initial migration"
if ($LASTEXITCODE -ne 0) {
    Write-Host "数据库迁移失败，请检查错误信息。" -ForegroundColor Red
    exit 1
}

flask db upgrade
if ($LASTEXITCODE -ne 0) {
    Write-Host "数据库升级失败，请检查错误信息。" -ForegroundColor Red
    exit 1
}

&$pythonCmd init_db.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "数据库初始化脚本运行失败，请检查错误信息。" -ForegroundColor Red
    exit 1
}

Write-Host "设置完成！你可以使用以下命令运行应用：" -ForegroundColor Green
Write-Host "flask run" -ForegroundColor Cyan