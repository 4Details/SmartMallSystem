from flask import Blueprint, request, jsonify
from ..services.user_service import UserService
from ..utils.exceptions import AppError, AuthenticationError
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

user_bp = Blueprint('user', __name__)

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    try:
        user = UserService.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            phone=data.get('phone'),
            address=data.get('address')
        )
        return jsonify({"message": "User registered successfully", "user": user.to_dict()}), 201
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    try:
        user = UserService.get_user_by_email(data['email'])
        if user.verify_password(data['password']):
            access_token = create_access_token(identity=str(user.id))
            return jsonify(access_token=access_token), 200
        else:
            raise AuthenticationError("Invalid email or password")
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = UserService.get_user_by_id(user_id)
        return jsonify(user.to_dict(include_private=True)), 200
    except AppError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    data = request.json
    try:
        user = UserService.update_user(user_id, **data)
        return jsonify({"message": "Profile updated successfully", "user": user.to_dict()}), 200
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