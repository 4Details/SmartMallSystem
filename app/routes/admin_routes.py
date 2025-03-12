from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for, flash, current_app
from flask_wtf.csrf import CSRFProtect
from app.services.user_service import UserService
from app.services.product_service import ProductService
from app.services.points_service import PointsService
from app.models import db, User, Product, MembershipLevel
from datetime import datetime, timedelta
import logging
from functools import wraps

# 创建管理员蓝图
admin_bp = Blueprint('admin', __name__)

# 创建 CSRF 保护
csrf = CSRFProtect()

# 设置会话过期时间（例如：2小时）
SESSION_LIFETIME = timedelta(hours=2)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('admin_user_id')
        if not user_id:
            return redirect(url_for('admin.admin_login'))
        try:
            user = UserService.get_user_by_id(user_id)
            if not user or 'admin' not in [role.name for role in user.roles]:
                session.pop('admin_user_id', None)
                return redirect(url_for('admin.admin_login'))
        except Exception as e:
            logging.error(f"Error in admin_required decorator: {str(e)}")
            session.pop('admin_user_id', None)
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    """管理员登录页面和处理"""
    if request.method == 'GET':
        return render_template('admin/login.html')

    data = request.form
    logging.info(f"尝试登录: {data.get('email')}")
    try:
        user = UserService.get_user_by_email(data['email'])
        logging.info(f"用户找到: {user.id}")

        if not user.verify_password(data['password']):
            logging.warning("密码验证失败")
            flash("Invalid email or password", "error")
            return redirect(url_for('admin.admin_login'))

        # 验证是否有管理员角色
        user_roles = [role.name for role in user.roles]
        logging.info(f"用户角色: {user_roles}")

        if 'admin' not in user_roles:
            logging.warning("用户没有管理员权限")
            flash("Admin privileges required", "error")
            return redirect(url_for('admin.admin_login'))

        # 在会话中存储用户ID，并设置过期时间
        session['admin_user_id'] = str(user.id)
        session.permanent = True
        current_app.permanent_session_lifetime = SESSION_LIFETIME
        logging.info("登录成功")

        return redirect(url_for('admin.admin_dashboard'))

    except Exception as e:
        logging.error(f"登录错误: {str(e)}", exc_info=True)
        flash("An error occurred during login", "error")
        return redirect(url_for('admin.admin_login'))

@admin_bp.route('/logout')
def admin_logout():
    """管理员登出"""
    session.pop('admin_user_id', None)
    flash("You have been logged out", "info")
    return redirect(url_for('admin.admin_login'))

@admin_bp.route('/dashboard')
@admin_required
def admin_dashboard():
    """管理员仪表盘，使用会话认证"""
    logging.info("访问仪表盘...")

    # 从会话中获取用户ID
    user_id = session.get('admin_user_id')
    if not user_id:
        logging.warning("会话中没有用户ID，重定向到登录页面")
        return redirect(url_for('admin.admin_login'))

    try:
        # 获取用户信息
        user = UserService.get_user_by_id(user_id)
        if not user:
            logging.warning(f"找不到用户: {user_id}")
            session.pop('admin_user_id', None)
            return redirect(url_for('admin.admin_login'))

        # 检查用户是否为管理员
        user_roles = [role.name for role in user.roles]
        if 'admin' not in user_roles:
            logging.warning(f"用户 {user.username} 不是管理员")
            session.pop('admin_user_id', None)
            return redirect(url_for('admin.admin_login'))

        logging.info(f"管理员 {user.username} 访问仪表盘成功")
        return render_template('admin/dashboard.html', user=user)

    except Exception as e:
        logging.error(f"访问仪表盘失败: {str(e)}")
        session.pop('admin_user_id', None)
        return redirect(url_for('admin.admin_login'))

@admin_bp.route('/users')
@admin_required
def admin_users():
    """会员管理页面"""
    # 检查会话中是否有用户ID
    user_id = session.get('admin_user_id')
    if not user_id:
        return redirect(url_for('admin.admin_login'))

    try:
        user = UserService.get_user_by_id(user_id)
        if not user or 'admin' not in [role.name for role in user.roles]:
            session.pop('admin_user_id', None)
            return redirect(url_for('admin.admin_login'))

        return render_template('admin/users.html', user=user)
    except Exception as e:
        logging.error(f"访问会员管理页面失败: {str(e)}")
        session.pop('admin_user_id', None)
        return redirect(url_for('admin.admin_login'))

@admin_bp.route('/points')
@admin_required
def points():
    """积分管理页面"""
    # 检查会话中是否有用户ID
    user_id = session.get('admin_user_id')
    if not user_id:
        return redirect(url_for('admin.admin_login'))

    try:
        user = UserService.get_user_by_id(user_id)
        if not user or 'admin' not in [role.name for role in user.roles]:
            session.pop('admin_user_id', None)
            return redirect(url_for('admin.admin_login'))

        return render_template('admin/points.html', user=user)
    except Exception as e:
        logging.error(f"访问积分管理页面失败: {str(e)}")
        session.pop('admin_user_id', None)
        return redirect(url_for('admin.admin_login'))

@admin_bp.route('/products')
@admin_required
def products():
    """商品管理页面"""
    # 检查会话中是否有用户ID
    user_id = session.get('admin_user_id')
    if not user_id:
        return redirect(url_for('admin.admin_login'))

    try:
        user = UserService.get_user_by_id(user_id)
        if not user or 'admin' not in [role.name for role in user.roles]:
            session.pop('admin_user_id', None)
            return redirect(url_for('admin.admin_login'))

        return render_template('admin/products.html', user=user)
    except Exception as e:
        logging.error(f"访问商品管理页面失败: {str(e)}")
        session.pop('admin_user_id', None)
        return redirect(url_for('admin.admin_login'))

# API路由
@admin_bp.route('/api/users')
@admin_required
def api_users():
    """获取用户列表API"""
    user_id = session.get('admin_user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        user = UserService.get_user_by_id(user_id)
        if not user or 'admin' not in [role.name for role in user.roles]:
            return jsonify({"error": "Admin privileges required"}), 403

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')

        # 构建过滤条件
        filter_by = {}
        if request.args.get('username'):
            filter_by['username'] = request.args.get('username')
        if request.args.get('email'):
            filter_by['email'] = request.args.get('email')
        if request.args.get('status'):
            filter_by['is_active'] = request.args.get('status').lower() == 'true'

        users_page = UserService.get_all_users(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            filter_by=filter_by
        )

        return jsonify({
            'items': [user.to_dict(include_private=True) for user in users_page.items],
            'page': users_page.page,
            'pages': users_page.pages,
            'per_page': users_page.per_page,
            'total': users_page.total
        })
    except Exception as e:
        logging.error(f"获取用户列表失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/products')
@admin_required
def api_products():
    """获取商品列表API"""
    user_id = session.get('admin_user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        user = UserService.get_user_by_id(user_id)
        if not user or 'admin' not in [role.name for role in user.roles]:
            return jsonify({"error": "Admin privileges required"}), 403

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')

        # 构建过滤条件
        filter_by = {}
        if request.args.get('name'):
            filter_by['name'] = request.args.get('name')
        if request.args.get('category'):
            filter_by['category'] = request.args.get('category')
        if request.args.get('status'):
            filter_by['is_active'] = request.args.get('status').lower() == 'true'

        products_page = ProductService.get_all_products(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            filter_by=filter_by
        )

        return jsonify({
            'items': [product.to_dict(include_admin_info=True) for product in products_page.items],
            'page': products_page.page,
            'pages': products_page.pages,
            'per_page': products_page.per_page,
            'total': products_page.total
        })
    except Exception as e:
        logging.error(f"获取商品列表失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/dashboard-stats')
@admin_required
def api_dashboard_stats():
    """获取仪表盘统计数据"""
    logging.info("开始获取仪表盘统计数据...")

    user_id = session.get('admin_user_id')
    if not user_id:
        logging.warning("未找到admin_user_id，返回401")
        return jsonify({"error": "Unauthorized"}), 401

    try:
        user = UserService.get_user_by_id(user_id)
        if not user or 'admin' not in [role.name for role in user.roles]:
            logging.warning(f"用户 {user_id} 不是管理员，返回403")
            return jsonify({"error": "Admin privileges required"}), 403

        logging.info("开始查询统计数据...")

        # 获取用户总数
        total_users = db.session.query(db.func.count(User.id)).scalar() or 0
        logging.info(f"用户总数: {total_users}")

        # 获取商品总数
        total_products = db.session.query(db.func.count(Product.id)).scalar() or 0

        # 获取今日新增用户数
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        new_users_today = db.session.query(db.func.count(User.id)).filter(
            User.created_at >= today_start
        ).scalar() or 0

        # 获取订单总数（如果有订单表的话）
        total_orders = 0
        # 注释掉订单相关代码，因为当前没有Order模型
        # if hasattr(db.Model, 'orders'):
        #     total_orders = db.session.query(db.func.count(Order.id)).scalar() or 0

        # 获取会员等级分布
        membership_stats = db.session.query(
            MembershipLevel.name,
            db.func.count(User.id)
        ).join(
            User, User.membership_level_id == MembershipLevel.id
        ).group_by(
            MembershipLevel.name
        ).all()

        # 获取最近的用户活跃度（最近7天）
        seven_days_ago = datetime.now() - timedelta(days=7)
        daily_users = db.session.query(
            db.func.date(User.created_at),
            db.func.count(User.id)
        ).filter(
            User.created_at >= seven_days_ago
        ).group_by(
            db.func.date(User.created_at)
        ).all()

        # 转换日期格式
        daily_users_dict = {}
        for date_val, count in daily_users:
            if isinstance(date_val, str):
                # 如果是字符串，尝试解析为日期
                try:
                    formatted_date = datetime.strptime(date_val, '%Y-%m-%d').strftime('%Y-%m-%d')
                except ValueError:
                    formatted_date = date_val
            else:
                # 如果是日期对象，直接格式化
                formatted_date = date_val.strftime('%Y-%m-%d')
            daily_users_dict[formatted_date] = count

        response_data = {
            "total_users": total_users,
            "total_products": total_products,
            "new_users_today": new_users_today,
            "total_orders": total_orders,
            "membership_stats": {
                name: count for name, count in membership_stats
            },
            "daily_users": daily_users_dict
        }
        logging.info("统计数据获取成功")
        return jsonify(response_data)
    except Exception as e:
        logging.error(f"获取仪表盘统计数据失败: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/add_points', methods=['POST'])
@admin_required
def api_add_points():
    """管理员给用户添加积分"""
    data = request.json
    try:
        # 通过邮箱获取用户ID
        user = UserService.get_user_by_email(data['email'])

        transaction = PointsService.add_points(
            user_id=user.id,
            points=data['points'],
            transaction_type='ADMIN_ADD',
            description=data.get('description', '管理员添加积分'),
            expires_in_days=data.get('expires_in_days')
        )

        # 更新系统积分统计
        PointsService.update_system_points_stats()

        return jsonify({
            "message": "Points added successfully",
            "transaction": transaction.to_dict()
        }), 200
    except Exception as e:
        logging.error(f"添加积分失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/deduct_points', methods=['POST'])
@admin_required
def api_deduct_points():
    """管理员从用户扣除积分"""
    data = request.json
    try:
        # 通过邮箱获取用户ID
        user = UserService.get_user_by_email(data['email'])

        transaction = PointsService.deduct_points(
            user_id=user.id,
            points=data['points'],
            transaction_type='ADMIN_DEDUCT',
            description=data.get('description', '管理员扣除积分')
        )

        # 更新系统积分统计
        PointsService.update_system_points_stats()

        return jsonify({
            "message": "Points deducted successfully",
            "transaction": transaction.to_dict()
        }), 200
    except Exception as e:
        logging.error(f"扣除积分失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/user_points_history/<user_id>')
@admin_required
def api_user_points_history(user_id):
    """获取用户积分历史记录（通过用户ID）"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        history = PointsService.get_user_points_history(user_id, page=page, per_page=per_page)

        return jsonify({
            "items": [transaction.to_dict() for transaction in history.items],
            "page": history.page,
            "pages": history.pages,
            "per_page": history.per_page,
            "total": history.total
        }), 200
    except Exception as e:
        logging.error(f"获取用户积分历史记录失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/user_points_history_by_email/<email>')
@admin_required
def api_user_points_history_by_email(email):
    """获取用户积分历史记录（通过用户邮箱）"""
    try:
        logging.info(f"获取用户积分历史记录，邮箱: {email}")
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        logging.info(f"分页参数: page={page}, per_page={per_page}")

        # 通过邮箱获取用户ID
        try:
            user = UserService.get_user_by_email(email)
            logging.info(f"找到用户: {user.id}, {user.username}")
        except Exception as e:
            logging.error(f"通过邮箱 {email} 查找用户失败: {str(e)}")
            return jsonify({"error": f"找不到邮箱为 {email} 的用户"}), 404

        try:
            history = PointsService.get_user_points_history(user.id, page=page, per_page=per_page)
            logging.info(f"获取到历史记录: {history.total} 条")
        except Exception as e:
            logging.error(f"获取用户 {user.id} 的积分历史记录失败: {str(e)}")
            return jsonify({"error": f"获取积分历史记录失败: {str(e)}"}), 500

        # 转换为字典并返回
        try:
            items = [transaction.to_dict() for transaction in history.items]
            logging.info(f"返回 {len(items)} 条历史记录")
            return jsonify({
                "items": items,
                "page": history.page,
                "pages": history.pages,
                "per_page": history.per_page,
                "total": history.total
            }), 200
        except Exception as e:
            logging.error(f"转换积分历史记录失败: {str(e)}")
            return jsonify({"error": f"转换积分历史记录失败: {str(e)}"}), 500
    except Exception as e:
        logging.error(f"获取用户积分历史记录失败: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/points_overview')
@admin_required
def api_points_overview():
    """获取系统积分总览"""
    try:
        total_points = PointsService.get_total_points_in_system()
        active_points = PointsService.get_total_active_points()
        expired_points = PointsService.get_total_expired_points()

        return jsonify({
            "total_points": total_points,
            "active_points": active_points,
            "expired_points": expired_points
        }), 200
    except Exception as e:
        logging.error(f"获取系统积分总览失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/points_rules', methods=['GET', 'POST'])
@admin_required
def api_points_rules():
    """获取或更新积分规则"""
    if request.method == 'GET':
        try:
            rules = PointsService.get_points_rules()
            return jsonify(rules), 200
        except Exception as e:
            logging.error(f"获取积分规则失败: {str(e)}")
            return jsonify({"error": str(e)}), 500
    elif request.method == 'POST':
        try:
            new_rules = request.json
            updated_rules = PointsService.update_points_rules(new_rules)
            return jsonify(updated_rules), 200
        except Exception as e:
            logging.error(f"更新积分规则失败: {str(e)}")
            return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/expire_points', methods=['POST'])
@admin_required
def api_expire_points():
    """手动触发积分过期"""
    try:
        expired_count = PointsService.expire_points()
        return jsonify({
            "message": "Points expiration process completed",
            "expired_count": expired_count
        }), 200
    except Exception as e:
        logging.error(f"手动触发积分过期失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/add_product', methods=['POST'])
@admin_required
def api_add_product():
    """添加新商品"""
    data = request.json
    logging.info(f"接收到添加商品请求: {data}")

    # 验证必填字段
    required_fields = ['name', 'points_price']
    for field in required_fields:
        if field not in data:
            error_msg = f"缺少必填字段: {field}"
            logging.error(error_msg)
            return jsonify({"error": error_msg}), 400

    try:
        # 转换数据类型
        try:
            points_price = int(data['points_price'])
            cash_price = float(data['cash_price']) if data.get('cash_price') else None
            stock = int(data.get('stock', 0))
        except (ValueError, TypeError) as e:
            error_msg = f"数据类型转换错误: {str(e)}"
            logging.error(error_msg)
            return jsonify({"error": error_msg}), 400

        product = ProductService.create_product(
            name=data['name'],
            points_price=points_price,
            description=data.get('description'),
            cash_price=cash_price,
            stock=stock,
            category=data.get('category'),
            image_url=data.get('image_url')
        )

        logging.info(f"商品添加成功: {product.id}")
        return jsonify({
            "message": "Product added successfully",
            "product": product.to_dict()
        }), 201
    except ValueError as e:
        error_msg = f"数据验证错误: {str(e)}"
        logging.error(error_msg)
        return jsonify({"error": error_msg}), 400
    except Exception as e:
        error_msg = f"添加商品失败: {str(e)}"
        logging.error(error_msg, exc_info=True)
        return jsonify({"error": error_msg}), 500

@admin_bp.route('/api/products/<product_id>', methods=['GET'])
def api_get_product(product_id):
    """获取单个商品详情"""
    try:
        product = ProductService.get_product_by_id(product_id)
        # 如果用户已登录且是管理员，返回更多信息
        include_admin_info = False
        user_id = session.get('admin_user_id')
        if user_id:
            user = UserService.get_user_by_id(user_id)
            if user and 'admin' in [role.name for role in user.roles]:
                include_admin_info = True

        return jsonify(product.to_dict(include_admin_info=include_admin_info)), 200
    except Exception as e:
        logging.error(f"获取商品详情失败: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/products/<product_id>/activate', methods=['PUT'])
@admin_required
def api_activate_product(product_id):
    """激活商品"""
    try:
        product = ProductService.activate_product(product_id)
        return jsonify({
            "message": "Product activated successfully",
            "product": product.to_dict()
        }), 200
    except Exception as e:
        logging.error(f"激活商品失败: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/products/<product_id>/deactivate', methods=['PUT'])
@admin_required
def api_deactivate_product(product_id):
    """停用商品"""
    try:
        product = ProductService.deactivate_product(product_id)
        return jsonify({
            "message": "Product deactivated successfully",
            "product": product.to_dict()
        }), 200
    except Exception as e:
        logging.error(f"停用商品失败: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/products/categories', methods=['GET'])
@admin_required
def api_product_categories():
    """获取所有商品分类"""
    try:
        categories = ProductService.get_categories()
        # 将查询结果转换为列表
        category_list = [category[0] for category in categories if category[0]]
        logging.info(f"获取到的商品分类: {category_list}")
        return jsonify(category_list), 200
    except Exception as e:
        logging.error(f"获取商品分类失败: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/products/<product_id>/stock', methods=['PUT'])
@admin_required
def api_update_product_stock(product_id):
    """更新商品库存"""
    data = request.json
    if not data or 'quantity_change' not in data:
        return jsonify({"error": "Missing quantity_change in request"}), 400

    try:
        quantity_change = int(data['quantity_change'])
        product = ProductService.update_stock(product_id, quantity_change)
        return jsonify({
            "message": "Stock updated successfully",
            "product": product.to_dict(include_admin_info=True)
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.error(f"更新商品库存失败: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500