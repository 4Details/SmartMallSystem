from flask import Blueprint, request, jsonify, current_app, render_template, redirect, url_for
from ..services.user_service import UserService
from ..utils.exceptions import AppError, AuthenticationError
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from functools import wraps

user_bp = Blueprint('user', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not get_jwt_identity():
            return redirect(url_for('user.login_page'))
        return f(*args, **kwargs)
    return decorated_function

# 为注册和登录路由豁免 CSRF 保护
@user_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # 验证必填字段
    required_fields = ['username', 'email', 'password']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # 验证密码长度
    if len(data['password']) < 6:
        return jsonify({"error": "Password must be at least 6 characters long"}), 400

    # 验证邮箱格式
    if '@' not in data['email']:
        return jsonify({"error": "Invalid email format"}), 400

    try:
        user = UserService.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            phone=data.get('phone'),
            address=data.get('address')
        )
        # 注册成功后直接生成访问令牌
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            "message": "User registered successfully",
            "user": user.to_dict(),
            "access_token": access_token
        }), 201
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "Registration failed. Please try again."}), 500

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    current_app.logger.info(f"Login attempt for email: {data.get('email')}")

    if not data or 'email' not in data or 'password' not in data:
        current_app.logger.warning("Login attempt with missing email or password")
        return jsonify({"error": "Email and password are required"}), 400

    try:
        user = UserService.get_user_by_email(data['email'])
        if user and user.verify_password(data['password']):
            access_token = create_access_token(identity=str(user.id))
            current_app.logger.info(f"Login successful for user: {user.id}")
            return jsonify({
                "message": "Login successful",
                "access_token": access_token,
                "user": user.to_dict(include_private=False)
            }), 200
        else:
            current_app.logger.warning(f"Failed login attempt for email: {data['email']}")
            raise AuthenticationError("Invalid email or password")
    except AppError as e:
        current_app.logger.error(f"AppError during login: {str(e)}")
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        current_app.logger.error(f"Unexpected error during login: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred"}), 500

@user_bp.route('/login')
def login_page():
    return render_template('login.html')

@user_bp.route('/register')
def register_page():
    return render_template('register.html')

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = UserService.get_user_by_id(user_id)
        user_dict = user.to_dict(include_private=True)
        user_dict['points_balance'] = user.get_points_balance()  # 添加积分余额
        return jsonify(user_dict), 200
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        data = request.json

        # 验证邮箱格式
        if 'email' in data and '@' not in data['email']:
            return jsonify({"error": "Invalid email format"}), 400

        # 更新用户信息
        user = UserService.update_user(
            user_id=user_id,
            username=data.get('username'),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address')
        )

        return jsonify({
            "message": "Profile updated successfully",
            "user": user.to_dict(include_private=True)
        }), 200
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@user_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    data = request.json
    try:
        UserService.change_password(user_id, data['old_password'], data['new_password'])
        return jsonify({"message": "Password changed successfully"}), 200
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@user_bp.route('/user_center')
@login_required
def user_center():
    return render_template('user_center.html')