from flask import Blueprint, request, jsonify, redirect, url_for
from ..services.points_service import PointsService
from ..utils.exceptions import AppError
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps

points_bp = Blueprint('points', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not get_jwt_identity():
            return redirect(url_for('user.login_page'))
        return f(*args, **kwargs)
    return decorated_function

@points_bp.route('/balance', methods=['GET'])
@jwt_required()
def get_balance():
    """
    获取用户积分余额的接口。

    Args:
        无

    Returns:
        - 成功时：返回一个包含用户积分余额的JSON对象，状态码为200。
        - 失败时：
            - 抛出AppError异常时，返回一个包含错误信息的JSON对象，状态码为异常的状态码。
            - 抛出其他异常时，返回一个包含通用错误信息的JSON对象，状态码为500。

    Raises:
        AppError: 当查询用户积分余额时发生应用层错误时抛出。

    """
    user_id = get_jwt_identity()
    try:
        balance = PointsService.get_user_points_balance(user_id)
        return jsonify({"points_balance": balance}), 200
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@points_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_summary():
    user_id = get_jwt_identity()
    try:
        summary = PointsService.get_user_points_summary(user_id)
        return jsonify(summary), 200
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@points_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    transaction_type = request.args.get('type')

    try:
        pagination = PointsService.get_user_transactions(
            user_id, page, per_page, transaction_type
        )

        transactions = [tx.to_dict() for tx in pagination.items]

        return jsonify({
            "transactions": transactions,
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": pagination.page
        }), 200
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@points_bp.route('/transfer', methods=['POST'])
@jwt_required()
def transfer_points():
    from_user_id = get_jwt_identity()
    data = request.json

    try:
        result = PointsService.transfer_points(
            from_user_id=from_user_id,
            to_user_id=data['to_user_id'],
            points=data['points'],
            description=data.get('description')
        )

        return jsonify({
            "message": "Points transferred successfully",
            "deduct_transaction": result['deduct_transaction'].to_dict(),
            "add_transaction": result['add_transaction'].to_dict()
        }), 200
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

# 以下接口需要管理员权限

@points_bp.route('/admin/add', methods=['POST'])
@jwt_required()
def admin_add_points():
    # 这里应该有管理员权限检查
    data = request.json

    try:
        transaction = PointsService.add_points(
            user_id=data['user_id'],
            points=data['points'],
            transaction_type=data['transaction_type'],
            description=data.get('description'),
            expires_in_days=data.get('expires_in_days'),
            related_entity_id=data.get('related_entity_id'),
            related_entity_type=data.get('related_entity_type')
        )

        return jsonify({
            "message": "Points added successfully",
            "transaction": transaction.to_dict()
        }), 200
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@points_bp.route('/admin/deduct', methods=['POST'])
@jwt_required()
def admin_deduct_points():
    # 这里应该有管理员权限检查
    data = request.json

    try:
        transaction = PointsService.deduct_points(
            user_id=data['user_id'],
            points=data['points'],
            transaction_type=data['transaction_type'],
            description=data.get('description'),
            related_entity_id=data.get('related_entity_id'),
            related_entity_type=data.get('related_entity_type')
        )

        return jsonify({
            "message": "Points deducted successfully",
            "transaction": transaction.to_dict()
        }), 200
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@points_bp.route('/admin/expire', methods=['POST'])
@jwt_required()
def admin_expire_points():
    # 这里应该有管理员权限检查
    try:
        expired_count = PointsService.expire_points()
        return jsonify({
            "message": f"Expired {expired_count} points transactions"
        }), 200
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500