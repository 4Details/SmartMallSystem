from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.services.user_service import UserService

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        try:
            user = UserService.get_user_by_id(current_user_id)
            # 检查用户是否有管理员角色
            has_admin_role = any(role.name == 'admin' for role in user.roles)
            if not has_admin_role:
                return jsonify({"error": "Admin privileges required"}), 403
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({"error": str(e)}), 401
    return decorated_function