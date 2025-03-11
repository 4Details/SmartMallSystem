from datetime import datetime
from ..models import db
from ..models.user import User, Role, MembershipLevel
from ..utils.exceptions import UserNotFoundError, DuplicateUserError

class UserService:
    @staticmethod
    def create_user(username, email, password, phone=None, address=None):
        """创建新用户"""
        # 检查用户名和邮箱是否已存在
        if User.query.filter((User.username == username) | (User.email == email)).first():
            raise DuplicateUserError("Username or email already exists")

        user = User(
            username=username,
            email=email,
            password=password,
            phone=phone,
            address=address
        )

        # 设置默认会员等级
        default_level = MembershipLevel.query.filter_by(required_points=0).first()
        if default_level:
            user.membership_level_id = default_level.id

        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_user_by_id(user_id):
        """根据ID获取用户"""
        user = User.query.get(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        return user

    @staticmethod
    def get_user_by_email(email):
        """根据邮箱获取用户"""
        user = User.query.filter_by(email=email).first()
        if not user:
            raise UserNotFoundError(f"User with email {email} not found")
        return user

    @staticmethod
    def update_user(user_id, **kwargs):
        """更新用户信息"""
        user = UserService.get_user_by_id(user_id)

        allowed_fields = {'username', 'email', 'phone', 'address', 'avatar_url', 'preferences'}
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(user, key, value)

        user.updated_at = datetime.utcnow()
        db.session.commit()
        return user

    @staticmethod
    def change_password(user_id, old_password, new_password):
        """修改用户密码"""
        user = UserService.get_user_by_id(user_id)
        if not user.verify_password(old_password):
            raise ValueError("Invalid old password")

        user.update_password(new_password)
        db.session.commit()
        return True

    @staticmethod
    def deactivate_user(user_id):
        """停用用户账户"""
        user = UserService.get_user_by_id(user_id)
        user.is_active = False
        db.session.commit()
        return True

    @staticmethod
    def activate_user(user_id):
        """激活用户账户"""
        user = UserService.get_user_by_id(user_id)
        user.is_active = True
        db.session.commit()
        return True

    @staticmethod
    def assign_role(user_id, role_name):
        """为用户分配角色"""
        user = UserService.get_user_by_id(user_id)
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            raise ValueError(f"Role {role_name} not found")

        if role not in user.roles:
            user.roles.append(role)
            db.session.commit()
        return True

    @staticmethod
    def remove_role(user_id, role_name):
        """移除用户的角色"""
        user = UserService.get_user_by_id(user_id)
        role = Role.query.filter_by(name=role_name).first()
        if role and role in user.roles:
            user.roles.remove(role)
            db.session.commit()
        return True

    @staticmethod
    def update_membership_level(user_id):
        """更新用户会员等级"""
        user = UserService.get_user_by_id(user_id)
        points_balance = user.get_points_balance()

        # 获取用户可以达到的最高等级
        new_level = MembershipLevel.query.filter(
            MembershipLevel.required_points <= points_balance
        ).order_by(MembershipLevel.required_points.desc()).first()

        if new_level and new_level.id != user.membership_level_id:
            user.membership_level_id = new_level.id
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_all_users(page=1, per_page=20, sort_by='created_at', sort_order='desc', filter_by=None):
        """获取所有用户，支持分页、排序和过滤"""
        query = User.query

        # 应用过滤条件
        if filter_by:
            if 'username' in filter_by:
                query = query.filter(User.username.ilike(f"%{filter_by['username']}%"))
            if 'email' in filter_by:
                query = query.filter(User.email.ilike(f"%{filter_by['email']}%"))
            if 'is_active' in filter_by:
                query = query.filter(User.is_active == filter_by['is_active'])

        # 应用排序
        sort_column = getattr(User, sort_by, User.created_at)
        if sort_order.lower() == 'asc':
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # 分页
        return query.paginate(page=page, per_page=per_page, error_out=False)