from flask import Flask, render_template, redirect, url_for, session, jsonify
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from .models import db
from .routes.user_routes import user_bp
from .routes.points_routes import points_bp
from .routes.product_routes import product_bp
from .routes.admin_routes import admin_bp
from .routes.order_routes import order_bp
import os
import logging
from datetime import timedelta

def create_app(config_name=None):
    app = Flask(__name__)

    # 导入配置
    from config import config
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app) if hasattr(config[config_name], 'init_app') else None

    # 基础配置
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///smart_mall.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS', 'False').lower() == 'true',
        JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', 'jwt_dev_key'),
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))),
        UPLOAD_FOLDER=os.environ.get('UPLOAD_FOLDER', 'uploads'),
        MAX_CONTENT_LENGTH=int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)),
        POINTS_EXPIRATION_DAYS=int(os.environ.get('POINTS_EXPIRATION_DAYS', 365)),
        DEFAULT_PAGE_SIZE=int(os.environ.get('DEFAULT_PAGE_SIZE', 20)),
        SESSION_TYPE='filesystem',
        SESSION_PERMANENT=True,
        SESSION_USE_SIGNER=True,
        PERMANENT_SESSION_LIFETIME=timedelta(hours=2),
        WTF_CSRF_CHECK_DEFAULT=False  # 禁用默认的 CSRF 检查
    )

    if config:
        app.config.update(config)

    # 初始化扩展
    db.init_app(app)
    jwt = JWTManager(app)
    migrate = Migrate(app, db)
    Session(app)
    csrf = CSRFProtect(app)

    # 豁免特定路由的 CSRF 保护
    csrf.exempt(user_bp)     # 为用户相关的路由豁免 CSRF 保护
    csrf.exempt(admin_bp)    # 为管理员相关的路由豁免 CSRF 保护
    csrf.exempt(product_bp)  # 为商品相关的路由豁免 CSRF 保护

    # JWT配置
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        if isinstance(user, str):
            return user
        return user.id if user else None

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        from .services.user_service import UserService
        identity = jwt_data["sub"]
        logging.info(f"Looking up user with identity: {identity}")
        try:
            user = UserService.get_user_by_id(identity)
            logging.info(f"User found: {user.username if user else 'None'}")
            return user
        except Exception as e:
            logging.error(f"Error looking up user: {str(e)}")
            return None

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        logging.error(f"Invalid token: {error_string}")
        return jsonify({
            'msg': 'Invalid token',
            'error': str(error_string)
        }), 401

    @jwt.unauthorized_loader
    def unauthorized_callback(error_string):
        logging.error(f"Missing Authorization Header: {error_string}")
        return jsonify({
            'msg': 'Missing Authorization Header',
            'error': str(error_string)
        }), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        logging.error(f"Token has expired: {jwt_data}")
        return jsonify({
            'msg': 'Token has expired',
            'error': 'token_expired'
        }), 401

    # 配置CORS - 允许所有源
    CORS(app, resources={
        r"/*": {
            "origins": "*",  # 允许所有源
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": [
                "Content-Type",
                "Authorization",
                "X-Requested-With",
                "Accept",
                "X-CSRFToken"
            ],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

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
    app.register_blueprint(order_bp, url_prefix='/api/orders')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # 添加管理员登录路由
    @app.route('/admin')
    def admin_root():
        return redirect(url_for('admin.admin_login'))

    # 注册前端页面路由
    register_frontend_routes(app)

    return app

def register_frontend_routes(app):
    """注册所有前端页面路由"""

    @app.route('/')
    def index():
        """首页路由"""
        return render_template('index.html')

    @app.route('/login')
    def login():
        """登录页面路由"""
        return render_template('login.html')

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
    def product_list():
        """商品列表路由"""
        return render_template('products.html')

    @app.route('/products/<product_id>')
    def product_detail(product_id):
        """商品详情路由"""
        return render_template('product_detail.html')

    @app.route('/orders')
    def orders():
        """订单列表路由"""
        return render_template('orders.html')