from flask import Blueprint, request, jsonify
from ..models.order import Order
from ..services.user_service import UserService
from ..utils.exceptions import AppError, AuthorizationError
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

order_bp = Blueprint('order', __name__)

@order_bp.route('/', methods=['GET'])
@jwt_required()
def get_user_orders():
    """获取用户订单列表"""
    user_id = get_jwt_identity()

    try:
        # 分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # 查询用户订单
        orders = Order.query.filter_by(user_id=user_id)\
            .order_by(Order.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)

        # 转换为字典格式
        orders_data = {
            "orders": [order.to_dict() for order in orders.items],
            "total": orders.total,
            "pages": orders.pages,
            "current_page": orders.page,
            "per_page": orders.per_page
        }

        return jsonify(orders_data), 200

    except Exception as e:
        logging.error(f"Error in get_user_orders: {str(e)}", exc_info=True)
        return jsonify({"error": "获取订单列表失败，请稍后再试"}), 500

@order_bp.route('/<order_id>', methods=['GET'])
@jwt_required()
def get_order_detail(order_id):
    """获取订单详情"""
    user_id = get_jwt_identity()

    try:
        # 查询订单
        order = Order.query.filter_by(id=order_id).first()

        if not order:
            return jsonify({"error": "订单不存在"}), 404

        # 验证订单所有权
        if order.user_id != user_id:
            # 检查是否为管理员
            user = UserService.get_user_by_id(user_id)
            if not user or 'admin' not in [role.name for role in user.roles]:
                return jsonify({"error": "无权访问此订单"}), 403

        return jsonify(order.to_dict()), 200

    except Exception as e:
        logging.error(f"Error in get_order_detail: {str(e)}", exc_info=True)
        return jsonify({"error": "获取订单详情失败，请稍后再试"}), 500