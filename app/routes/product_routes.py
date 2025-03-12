from flask import Blueprint, request, jsonify, logging, url_for, redirect
from ..services.product_service import ProductService
from ..services.user_service import UserService
from ..utils.exceptions import AppError, AuthorizationError, ProductNotFoundError, InsufficientStockError, \
    InsufficientPointsError
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
import logging

product_bp = Blueprint('product', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not get_jwt_identity():
            return redirect(url_for('user.login_page'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            user_id = get_jwt_identity()
            user = UserService.get_user_by_id(user_id)
            if not user or 'admin' not in [role.name for role in user.roles]:
                raise AuthorizationError("Admin privileges required")
        except Exception as e:
            return jsonify({"error": str(e)}), 403
        return f(*args, **kwargs)
    return decorated_function

@product_bp.route('/', methods=['GET'])
def get_products():
    """获取商品列表，支持分页、搜索、排序和过滤"""
    logging.info(f"Received request for products list. Args: {dict(request.args)}")

    try:
        # 搜索和过滤参数
        keyword = request.args.get('keyword')
        category = request.args.get('category')
        min_points = request.args.get('min_points', type=int)
        max_points = request.args.get('max_points', type=int)
        in_stock = request.args.get('in_stock')
        if in_stock is not None:
            in_stock = in_stock.lower() == 'true'

        # 分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)

        # 排序参数处理
        sort = request.args.get('sort', 'newest')
        # 将前端的排序参数映射到数据库字段
        sort_mapping = {
            'newest': ('created_at', 'desc'),
            'oldest': ('created_at', 'asc'),
            'price-asc': ('points_price', 'asc'),
            'price-desc': ('points_price', 'desc')
        }
        sort_by, sort_order = sort_mapping.get(sort, ('created_at', 'desc'))

        logging.info(f"Processed sort parameters: sort_by={sort_by}, sort_order={sort_order}")

        # 检查用户是否为管理员
        is_admin = False
        try:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                user_id = get_jwt_identity()
                if user_id:
                    user = UserService.get_user_by_id(user_id)
                    if user and 'admin' in [role.name for role in user.roles]:
                        is_admin = True
        except:
            pass

        logging.info(f"User admin status: {is_admin}")

        # 获取商品列表
        pagination = ProductService.search_products(
            keyword=keyword,
            category=category,
            min_points=min_points,
            max_points=max_points,
            in_stock=in_stock,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            include_inactive=is_admin  # 只有管理员可以看到下架商品
        )

        logging.info(f"Pagination result: total={pagination.total}, pages={pagination.pages}, "
                     f"current_page={pagination.page}, per_page={pagination.per_page}")

        # 转换商品列表为字典格式
        products = [
            product.to_dict(
                include_promotions=True,  # 包含促销信息
                include_admin_info=is_admin  # 管理员可以看到更多信息
            )
            for product in pagination.items
        ]

        logging.info(f"Number of products processed: {len(products)}")

        # 返回分页数据
        response_data = {
            "products": products,  # 商品列表
            "total": pagination.total,  # 总商品数
            "pages": pagination.pages,  # 总页数
            "current_page": pagination.page,  # 当前页码
            "per_page": pagination.per_page,  # 每页数量
            "has_next": pagination.has_next,  # 是否有下一页
            "has_prev": pagination.has_prev   # 是否有上一页
        }

        logging.info(f"Response data prepared: {response_data}")
        return jsonify(response_data), 200

    except AppError as e:
        # 处理应用程序定义的错误
        logging.error(f"AppError in get_products: {str(e)}")
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        # 处理未预期的错误
        logging.error(f"Unexpected error in get_products: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@product_bp.route('/<product_id>', methods=['GET'])
def get_product_detail(product_id):
    """获取商品详情"""
    logging.info(f"Received request for product detail. Product ID: {product_id}")
    logging.info(f"Request headers: {dict(request.headers)}")
    logging.info(f"Request URL: {request.url}")

    try:
        # 获取商品详情
        logging.info("Attempting to get product details from service")
        product = ProductService.get_product_by_id(product_id)
        logging.info(f"Product retrieved: {product.id if product else 'None'}")

        if not product:
            logging.warning(f"Product not found. ID: {product_id}")
            return jsonify({
                "error": "Product not found",
                "message": "商品不存在"
            }), 404

        if not product.is_active:
            logging.info(f"Product is inactive. ID: {product_id}")
            return jsonify({
                "error": "Product inactive",
                "message": "商品已下架"
            }), 404

        # 转换为字典格式，包含所有公开信息
        logging.info("Converting product to dictionary")
        product_data = product.to_dict(include_promotions=True)

        # 添加创建时间
        if product.created_at:
            product_data['created_at'] = product.created_at.isoformat()

        # 添加兑换次数（示例数据，实际应该从订单统计）
        product_data['exchange_count'] = 0  # TODO: 实现兑换次数统计

        # 添加调试信息
        logging.info(f"Product data prepared: {product_data}")

        # 设置响应头
        response = jsonify(product_data)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'

        logging.info("Returning successful response")
        return response, 200

    except ProductNotFoundError as e:
        logging.error(f"Product not found error: {str(e)}")
        return jsonify({
            "error": "Product not found",
            "message": "商品不存在"
        }), 404
    except Exception as e:
        logging.error(f"Unexpected error in get_product_detail: {str(e)}", exc_info=True)
        return jsonify({
            "error": "An unexpected error occurred",
            "message": "获取商品详情失败，请稍后再试"
        }), 500

@product_bp.route('/<product_id>/exchange', methods=['POST', 'OPTIONS'])
@jwt_required()
def exchange_product(product_id):
    """兑换商品"""
    user_id = get_jwt_identity()
    logging.info(f"Exchange request received for product {product_id} by user {user_id}")

    # 如果是 OPTIONS 请求，直接返回成功
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response

    try:
        # 验证用户是否已登录
        if not user_id:
            logging.warning("Unauthorized access attempt")
            return jsonify({"error": "请先登录"}), 401

        # 获取请求参数
        request_data = request.get_json()
        if not request_data:
            logging.warning(f"No JSON data in request for product exchange")
            return jsonify({"error": "请求数据格式错误"}), 400

        quantity = int(request_data.get('quantity', 1))
        logging.info(f"Exchange quantity: {quantity}")

        # 调用服务进行兑换
        result = ProductService.exchange_product(user_id, product_id, quantity)
        logging.info(f"Exchange successful: {result}")

        return jsonify({
            "message": "兑换成功",
            "order_id": result['order_id'],
            "points_deducted": result['points_deducted'],
            "quantity": result['quantity'],
            "product_name": result['product_name']
        }), 200
    except ValueError as e:
        logging.warning(f"Value error in exchange_product: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except InsufficientPointsError as e:
        logging.warning(f"Insufficient points error: {str(e)}")
        return jsonify({"error": "积分不足，无法完成兑换"}), 400
    except ProductNotFoundError as e:
        logging.warning(f"Product not found error: {str(e)}")
        return jsonify({"error": "商品不存在"}), 404
    except InsufficientStockError as e:
        logging.warning(f"Insufficient stock error: {str(e)}")
        return jsonify({"error": "商品库存不足"}), 400
    except AppError as e:
        logging.error(f"Application error in exchange_product: {str(e)}")
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        logging.error(f"Unexpected error in exchange_product: {str(e)}", exc_info=True)
        return jsonify({"error": "兑换失败，请稍后再试", "details": str(e)}), 500

@product_bp.route('/<product_id>/price', methods=['GET'])
def get_product_price(product_id):
    """获取商品价格信息"""
    quantity = request.args.get('quantity', 1, type=int)
    try:
        price_info = ProductService.get_product_final_price(product_id, quantity)
        return jsonify(price_info), 200
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

# 以下接口需要管理员权限

@product_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required
def create_product():
    """创建新商品"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    required_fields = ['name', 'points_price']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    try:
        product = ProductService.create_product(
            name=data['name'],
            points_price=data['points_price'],
            description=data.get('description'),
            cash_price=data.get('cash_price'),
            stock=data.get('stock', 0),
            category=data.get('category'),
            image_url=data.get('image_url'),
            currency_id=data.get('currency_id'),
            attributes=data.get('attributes')
        )

        return jsonify({
            "message": "Product created successfully",
            "product": product.to_dict(include_admin_info=True)
        }), 201
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@product_bp.route('/<product_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_product(product_id):
    """更新商品信息"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        product = ProductService.update_product(product_id, **data)
        return jsonify({
            "message": "Product updated successfully",
            "product": product.to_dict(include_admin_info=True)
        }), 200
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@product_bp.route('/<product_id>/stock', methods=['PUT'])
@jwt_required()
@admin_required
def update_stock(product_id):
    """更新商品库存"""
    logging.info(f"Received stock update request for product {product_id}")
    data = request.json
    logging.info(f"Request data: {data}")
    if not data or 'quantity_change' not in data:
        return jsonify({"error": "Missing quantity_change in request"}), 400

    try:
        # 确保 quantity_change 是整数
        quantity_change = int(data['quantity_change'])

        # 获取当前商品信息（用于日志）
        product = ProductService.get_product_by_id(product_id)
        old_stock = product.stock

        # 更新库存
        product = ProductService.update_stock(
            product_id=product_id,
            quantity_change=quantity_change
        )

        # 记录库存变更
        logging.info(f"Stock updated for product {product_id}: {old_stock} -> {product.stock} (change: {quantity_change})")

        return jsonify({
            "message": "Stock updated successfully",
            "product": product.to_dict(include_admin_info=True),
            "stock_change": {
                "old_stock": old_stock,
                "new_stock": product.stock,
                "change": quantity_change
            }
        }), 200
    except ValueError as e:
        return jsonify({"error": "Invalid quantity_change value. Must be an integer."}), 400
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        logging.error(f"Failed to update stock for product {product_id}: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred"}), 500

@product_bp.route('/<product_id>/activate', methods=['PUT'])
@jwt_required()
@admin_required
def activate_product(product_id):
    """激活商品"""
    try:
        product = ProductService.activate_product(product_id)
        return jsonify({
            "message": "Product activated successfully",
            "product": product.to_dict(include_admin_info=True)
        }), 200
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@product_bp.route('/<product_id>/deactivate', methods=['PUT'])
@jwt_required()
@admin_required
def deactivate_product(product_id):
    """停用商品"""
    try:
        product = ProductService.deactivate_product(product_id)
        return jsonify({
            "message": "Product deactivated successfully",
            "product": product.to_dict(include_admin_info=True)
        }), 200
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500