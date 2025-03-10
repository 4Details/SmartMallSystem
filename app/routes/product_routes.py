from flask import Blueprint, request, jsonify
from ..services.product_service import ProductService
from ..utils.exceptions import AppError
from flask_jwt_extended import jwt_required, get_jwt_identity

product_bp = Blueprint('product', __name__)

@product_bp.route('/', methods=['GET'])
def get_products():
    # 获取查询参数
    keyword = request.args.get('keyword')
    category = request.args.get('category')
    min_points = request.args.get('min_points', type=int)
    max_points = request.args.get('max_points', type=int)
    in_stock = request.args.get('in_stock')
    if in_stock is not None:
        in_stock = in_stock.lower() == 'true'

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')

    try:
        pagination = ProductService.search_products(
            keyword=keyword,
            category=category,
            min_points=min_points,
            max_points=max_points,
            in_stock=in_stock,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )

        products = [product.to_dict(include_promotions=True) for product in pagination.items]

        return jsonify({
            "products": products,
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": pagination.page
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@product_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = ProductService.get_product_by_id(product_id)
        return jsonify(product.to_dict(include_promotions=True)), 200
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@product_bp.route('/categories', methods=['GET'])
def get_categories():
    try:
        categories = ProductService.get_categories()
        return jsonify({"categories": [c[0] for c in categories if c[0]]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@product_bp.route('/<product_id>/price', methods=['GET'])
def get_product_price(product_id):
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
def create_product():
    # 这里应该有管理员权限检查
    data = request.json

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
            "product": product.to_dict()
        }), 201
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@product_bp.route('/<product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    # 这里应该有管理员权限检查
    data = request.json

    try:
        product = ProductService.update_product(product_id, **data)
        return jsonify({
            "message": "Product updated successfully",
            "product": product.to_dict()
        }), 200
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@product_bp.route('/<product_id>/stock', methods=['PUT'])
@jwt_required()
def update_stock(product_id):
    # 这里应该有管理员权限检查
    data = request.json

    try:
        product = ProductService.update_stock(
            product_id=product_id,
            quantity_change=data['quantity_change']
        )

        return jsonify({
            "message": "Stock updated successfully",
            "product": product.to_dict()
        }), 200
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@product_bp.route('/<product_id>/activate', methods=['PUT'])
@jwt_required()
def activate_product(product_id):
    # 这里应该有管理员权限检查
    try:
        product = ProductService.activate_product(product_id)
        return jsonify({
            "message": "Product activated successfully",
            "product": product.to_dict()
        }), 200
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@product_bp.route('/<product_id>/deactivate', methods=['PUT'])
@jwt_required()
def deactivate_product(product_id):
    # 这里应该有管理员权限检查
    try:
        product = ProductService.deactivate_product(product_id)
        return jsonify({
            "message": "Product deactivated successfully",
            "product": product.to_dict()
        }), 200
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@product_bp.route('/<product_id>/promotions/<promotion_id>', methods=['POST'])
@jwt_required()
def add_promotion(product_id, promotion_id):
    # 这里应该有管理员权限检查
    try:
        ProductService.add_promotion(product_id, promotion_id)
        return jsonify({
            "message": "Promotion added to product successfully"
        }), 200
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@product_bp.route('/<product_id>/promotions/<promotion_id>', methods=['DELETE'])
@jwt_required()
def remove_promotion(product_id, promotion_id):
    # 这里应该有管理员权限检查
    try:
        ProductService.remove_promotion(product_id, promotion_id)
        return jsonify({
            "message": "Promotion removed from product successfully"
        }), 200
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500