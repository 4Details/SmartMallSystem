from flask import Flask, render_template
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from .models import db
from .routes.user_routes import user_bp
from .routes.points_routes import points_bp
from .routes.product_routes import product_bp
import os
import logging
from datetime import timedelta

def create_app(config=None):
    app = Flask(__name__)

    # 加载配置
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///smart_mall.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS', 'False').lower() == 'true',
        JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', 'jwt_dev_key'),
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))),
        UPLOAD_FOLDER=os.environ.get('UPLOAD_FOLDER', 'uploads'),
        MAX_CONTENT_LENGTH=int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)),
        POINTS_EXPIRATION_DAYS=int(os.environ.get('POINTS_EXPIRATION_DAYS', 365)),
        DEFAULT_PAGE_SIZE=int(os.environ.get('DEFAULT_PAGE_SIZE', 20))
    )

    if config:
        app.config.update(config)

    # 初始化扩展
    db.init_app(app)
    jwt = JWTManager(app)
    migrate = Migrate(app, db)

    # 配置CORS
    cors_origins = os.environ.get('CORS_ALLOWED_ORIGINS', '*').split(',')
    CORS(app, resources={r"/api/*": {"origins": cors_origins}})

    # 配置日志
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    log_file = os.environ.get('LOG_FILE', 'logs/app.log')

    # 确保日志目录存在
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    # 注册蓝图
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(points_bp, url_prefix='/api/points')
    app.register_blueprint(product_bp, url_prefix='/api/products')

    # 注册前端页面路由
    register_frontend_routes(app)

    return app

def register_frontend_routes(app):
    """注册所有前端页面路由"""

    @app.route('/')
    def index():
        """首页路由"""
        return render_template('index.html')

    @app.route('/register')
    def register():
        """注册页面路由"""
        return render_template('register.html')

    @app.route('/user')
    def user_center():
        """用户中心路由"""
        return render_template('user_center.html')

    @app.route('/points')
    def points():
        """积分页面路由"""
        return render_template('points.html')

    @app.route('/products')
    def products():
        """商品列表路由"""
        return render_template('products.html')

    @app.route('/product/<int:product_id>')
    def product_detail(product_id):
        """商品详情路由"""
        return render_template('product_detail.html')

    @app.route('/orders')
    def orders():
        """订单列表路由"""
        return render_template('orders.html')